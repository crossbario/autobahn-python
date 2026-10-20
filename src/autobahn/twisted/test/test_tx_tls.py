###############################################################################
#
#  Copyright (C) typedef int GmbH
#  SPDX-License-Identifier: MIT
#
###############################################################################
"""
WAMP over TLS on Twisted (#2014): the TLS client certificate in the transport details,
TLS client certificate authentication (authmethod "tls"), and WAMP-cryptosign with TLS
channel binding ("tls-unique"), over WebSocket and RawSocket, on TLS 1.2 and TLS 1.3.

The connections are real TLS connections on the loopback interface, with certificates
created for each test (see :mod:`autobahn.test.tlsutil`).
"""

import binascii

import txaio

txaio.use_twisted()  # noqa

from OpenSSL import crypto
from twisted.internet import reactor, ssl
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.endpoints import SSL4ClientEndpoint, SSL4ServerEndpoint
from twisted.internet.interfaces import ISSLTransport
from twisted.trial import unittest
from zope.interface import implementer

from autobahn.test.tlsutil import (
    CLIENT_SUBJECT,
    FakeRouterSession,
    ExamplePKI,
    expected_peer_cert,
)
from autobahn.twisted.rawsocket import (
    WampRawSocketClientFactory,
    WampRawSocketServerFactory,
)
from autobahn.twisted.util import extract_peer_certificate
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.websocket import (
    WampWebSocketClientFactory,
    WampWebSocketServerFactory,
)
from autobahn.wamp import cryptosign
from autobahn.wamp.auth import AuthCryptoSign
from autobahn.wamp.types import ComponentConfig

_TLS_VERSIONS = {"1.2": ssl.TLSVersion.TLSv1_2, "1.3": ssl.TLSVersion.TLSv1_3}


@implementer(ISSLTransport)
class _FakeTLSTransport:
    """
    Just enough of a TLS transport for extract_peer_certificate().
    """

    def __init__(self, cert):
        self._cert = cert

    def getPeerCertificate(self):
        return self._cert


class ExtractPeerCertificateTests(unittest.TestCase):
    """
    extract_peer_certificate() on certificates as clients present them.
    """

    def setUp(self):
        self.pki = ExamplePKI(self.mktemp())

    def _extract(self, cert):
        x509 = crypto.X509.from_cryptography(cert)
        return extract_peer_certificate(_FakeTLSTransport(x509))

    def test_certificate_with_extensions(self):
        """
        All fields of a client certificate with SAN, key usage and extended key usage.
        """
        cert = self.pki.client_certs["client_0"]
        result = self._extract(cert)

        expected = expected_peer_cert(
            cert,
            dict(CLIENT_SUBJECT, cn="client_0"),
            {"o": "Example GmbH", "cn": "Example Test CA"},
        )
        for key, value in expected.items():
            self.assertEqual(result[key], value, key)

        extensions = {ext["name"]: ext for ext in result["extensions"]}
        self.assertEqual(
            sorted(extensions), ["extendedKeyUsage", "keyUsage", "subjectAltName"]
        )
        self.assertEqual(extensions["keyUsage"]["critical"], True)
        self.assertEqual(extensions["subjectAltName"]["critical"], False)
        self.assertIn("client_0", extensions["subjectAltName"]["value"])

    def test_malformed_certificate_does_not_raise(self):
        """
        A certificate whose extensions cannot be parsed (a duplicate extension) still yields
        the certificate's other fields: this runs on peer data before authentication.
        """
        cert = self.pki.duplicate_extension_cert()
        result = self._extract(cert)
        self.assertEqual(
            result["sha1"],
            expected_peer_cert(cert, {}, {})["sha1"],
        )
        self.assertEqual(result["subject"]["cn"], "client_dup")

    def test_no_peer_certificate(self):
        self.assertIsNone(extract_peer_certificate(_FakeTLSTransport(None)))


class _Client(ApplicationSession):
    """
    A WAMP client that joins with one authmethod and reports the outcome.
    """

    def __init__(self, config, authmethod, authenticator, done):
        ApplicationSession.__init__(self, config)
        self._authmethod = authmethod
        self._authenticator = authenticator
        self._done = done

    def onConnect(self):
        authextra = None
        if self._authenticator:
            authextra = self._authenticator.authextra
        self.join(
            self.config.realm, authmethods=[self._authmethod], authextra=authextra
        )

    def onChallenge(self, challenge):
        return self._authenticator.on_challenge(self, challenge)

    def onJoin(self, details):
        if not self._done.called:
            self._done.callback(("joined", details, self._transport.transport_details))
        self.leave()

    def onLeave(self, details):
        if not self._done.called:
            self._done.callback(("left", details, None))
        self.disconnect()

    def onDisconnect(self):
        if not self._done.called:
            self._done.callback(("disconnected", None, None))


class _TlsWampTests:
    """
    WAMP authentication over TLS; mixed into one test case per transport (WebSocket, RawSocket).
    """

    transport = None
    timeout = 20

    def setUp(self):
        self.pki = ExamplePKI(self.mktemp())
        self.observed = []
        self.cryptosign_key = cryptosign.CryptosignKey.from_bytes(b"\x01" * 32)
        self.principals = {
            expected_peer_cert(self.pki.client_certs["client_0"], {}, {})["sha1"]: (
                "client_0",
                "backend",
            ),
        }
        self.pubkeys = {self.cryptosign_key.public_key(): ("alice", "frontend")}

    def _server_options(self, tls_version):
        server = ssl.PrivateCertificate.loadPEM(
            self.pki.pem("server", "crt") + self.pki.pem("server", "key")
        )
        ca = ssl.Certificate.loadPEM(self.pki.pem("ca", "crt"))
        kwargs = {}
        if tls_version:
            kwargs = dict(
                raiseMinimumTo=_TLS_VERSIONS[tls_version],
                lowerMaximumSecurityTo=_TLS_VERSIONS[tls_version],
            )
        return ssl.CertificateOptions(
            privateKey=server.privateKey.original,
            certificate=server.original,
            verify=True,
            caCerts=[ca.original],
            requireCertificate=False,
            **kwargs,
        )

    def _client_options(self, client):
        ca = ssl.Certificate.loadPEM(self.pki.pem("ca", "crt"))
        client_cert = None
        if client:
            client_cert = ssl.PrivateCertificate.loadPEM(
                self.pki.pem(client, "crt") + self.pki.pem(client, "key")
            )
        return ssl.optionsForClientTLS(
            "localhost", trustRoot=ca, clientCertificate=client_cert
        )

    @inlineCallbacks
    def _join(self, client, authmethod, authenticator=None, tls_version=None):
        """
        Connect a client with the TLS client certificate ``client`` (or none), join with
        ``authmethod``, and return ``(outcome, details, client transport details)``.
        """
        server_closed = Deferred()

        def router_session():
            return FakeRouterSession(
                principals=self.principals,
                pubkeys=self.pubkeys,
                observed=self.observed,
                on_close=lambda: server_closed.called or server_closed.callback(None),
            )

        done = Deferred()

        def client_session():
            return _Client(ComponentConfig("realm1"), authmethod, authenticator, done)

        if self.transport == "websocket":
            server_factory = WampWebSocketServerFactory(router_session)
        else:
            server_factory = WampRawSocketServerFactory(router_session)

        endpoint = SSL4ServerEndpoint(
            reactor, 0, self._server_options(tls_version), interface="127.0.0.1"
        )
        port = yield endpoint.listen(server_factory)
        self.addCleanup(port.stopListening)
        portno = port.getHost().port

        if self.transport == "websocket":
            client_factory = WampWebSocketClientFactory(
                client_session, url=f"wss://localhost:{portno}"
            )
        else:
            client_factory = WampRawSocketClientFactory(client_session)

        client_endpoint = SSL4ClientEndpoint(
            reactor, "127.0.0.1", portno, self._client_options(client)
        )
        proto = yield client_endpoint.connect(client_factory)

        result = yield done
        # wait until both sides closed the connection
        yield server_closed
        if proto.transport.connected:
            proto.transport.loseConnection()
        return result

    def _aborts(self):
        return [what for event, what in self.observed if event == "abort"]

    def _hello_details(self):
        return [td for event, td in self.observed if event == "hello"][0]

    # TLS client certificate authentication (authmethod "tls")

    @inlineCallbacks
    def _check_tls_auth_accepted(self, tls_version):
        outcome, details, _ = yield self._join(
            "client_0", "tls", tls_version=tls_version
        )
        self.assertEqual(self._aborts(), [])
        self.assertEqual(outcome, "joined")
        self.assertEqual(
            (details.authid, details.authrole, details.authmethod),
            ("client_0", "backend", "tls"),
        )

        # what the router sees: the client certificate, after the TLS handshake
        peer_cert = self._hello_details().peer_cert
        cert = self.pki.client_certs["client_0"]
        self.assertEqual(peer_cert["sha1"], expected_peer_cert(cert, {}, {})["sha1"])
        self.assertEqual(peer_cert["subject"]["cn"], "client_0")

    def test_tls_auth_accepted(self):
        return self._check_tls_auth_accepted(None)

    def test_tls_auth_accepted_tls12(self):
        return self._check_tls_auth_accepted("1.2")

    def test_tls_auth_accepted_tls13(self):
        return self._check_tls_auth_accepted("1.3")

    @inlineCallbacks
    def test_tls_auth_unknown_certificate(self):
        """
        A client certificate the CA signed, but that is not a principal: denied, for that reason.
        """
        outcome, details, _ = yield self._join("client_1", "tls")
        self.assertEqual(outcome, "left")
        sha1 = expected_peer_cert(self.pki.client_certs["client_1"], {}, {})["sha1"]
        self.assertEqual(self._aborts(), [f"client certificate {sha1} not accepted"])

    @inlineCallbacks
    def test_tls_auth_no_certificate(self):
        outcome, details, _ = yield self._join(None, "tls")
        self.assertEqual(outcome, "left")
        self.assertEqual(self._aborts(), ["no client certificate presented"])
        self.assertIsNone(self._hello_details().peer_cert)

    # WAMP-cryptosign with TLS channel binding

    @inlineCallbacks
    def _check_cryptosign_channel_binding(self, tls_version):
        authenticator = AuthCryptoSign(
            privkey=binascii.b2a_hex(b"\x01" * 32).decode(),
            authextra={"channel_binding": "tls-unique"},
        )
        outcome, details, client_td = yield self._join(
            None, "cryptosign", authenticator, tls_version=tls_version
        )
        self.assertEqual(self._aborts(), [])
        self.assertEqual(outcome, "joined")
        self.assertEqual((details.authid, details.authmethod), ("alice", "cryptosign"))

        # both ends of the connection have the same, non-zero channel ID
        server_td = self._hello_details()
        self.assertTrue(server_td.is_secure)
        self.assertEqual(
            server_td.channel_id["tls-unique"], client_td.channel_id["tls-unique"]
        )
        self.assertNotEqual(
            server_td.channel_id["tls-unique"], FakeRouterSession.ZERO_CHANNEL_ID
        )

    def test_cryptosign_channel_binding(self):
        return self._check_cryptosign_channel_binding(None)

    def test_cryptosign_channel_binding_tls12(self):
        return self._check_cryptosign_channel_binding("1.2")

    def test_cryptosign_channel_binding_tls13(self):
        return self._check_cryptosign_channel_binding("1.3")

    @inlineCallbacks
    def test_cryptosign_channel_binding_with_client_certificate(self):
        """
        Channel binding also works when the client presents a TLS client certificate.
        """
        authenticator = AuthCryptoSign(
            privkey=binascii.b2a_hex(b"\x01" * 32).decode(),
            authextra={"channel_binding": "tls-unique"},
        )
        outcome, details, _ = yield self._join("client_0", "cryptosign", authenticator)
        self.assertEqual(self._aborts(), [])
        self.assertEqual(outcome, "joined")


class TlsWebSocketTests(_TlsWampTests, unittest.TestCase):
    transport = "websocket"


class TlsRawSocketTests(_TlsWampTests, unittest.TestCase):
    transport = "rawsocket"
