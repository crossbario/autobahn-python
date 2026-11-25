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
import hashlib
import socket
import ssl as stdlib_ssl

import txaio

txaio.use_twisted()  # noqa

from OpenSSL import crypto
from twisted.internet import reactor, ssl
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.endpoints import SSL4ClientEndpoint, SSL4ServerEndpoint
from twisted.internet.interfaces import IHandshakeListener, ISSLTransport
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.threads import deferToThread
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
    WampRawSocketClientProtocol,
    WampRawSocketServerFactory,
    WampRawSocketServerProtocol,
)
from autobahn.twisted.util import extract_peer_certificate, transport_channel_id
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.websocket import (
    WampWebSocketClientFactory,
    WampWebSocketClientProtocol,
    WampWebSocketServerFactory,
    WampWebSocketServerProtocol,
)
from autobahn.util import tls_unique
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
            # mirror Session.onConnect: let the authenticator finalize its authextra
            # against the connected transport (cryptosign selects the channel-binding
            # type by negotiated TLS version) before reading authextra for HELLO (#2078)
            on_connect = getattr(self._authenticator, "on_connect", None)
            if on_connect is not None:
                on_connect(self)
            authextra = self._authenticator.authextra
        self.join(
            self.config.realm, authmethods=[self._authmethod], authextra=authextra
        )

    def onChallenge(self, challenge):
        return self._authenticator.on_challenge(self, challenge)

    def onJoin(self, details):
        if not self._done.called:
            self._done.callback(
                ("joined", details, self._require_transport().transport_details)
            )
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

        # both ends of the connection have the same, non-zero channel ID, bound under the
        # version-correct type (tls-unique on TLS <= 1.2, tls-exporter on TLS 1.3, #2078)
        server_td = self._hello_details()
        self.assertTrue(server_td.is_secure)
        (binding_type,) = server_td.channel_id.keys()
        self.assertEqual(
            server_td.channel_id[binding_type], client_td.channel_id[binding_type]
        )
        self.assertNotEqual(
            server_td.channel_id[binding_type], FakeRouterSession.ZERO_CHANNEL_ID
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

    # the channel-binding map in TransportDetails.channel_id follows the negotiated TLS
    # version (hard split, #2078): tls-unique (RFC 5929) on TLS <= 1.2, tls-exporter
    # (RFC 9266) on TLS 1.3 - and only that one; the other must be absent.

    @inlineCallbacks
    def _check_tls_exporter_populated(self, tls_version, expect_exporter):
        authenticator = AuthCryptoSign(
            privkey=binascii.b2a_hex(b"\x01" * 32).decode(),
            authextra={"channel_binding": "tls-unique"},
        )
        outcome, details, client_td = yield self._join(
            None, "cryptosign", authenticator, tls_version=tls_version
        )
        self.assertEqual(self._aborts(), [])
        self.assertEqual(outcome, "joined")
        server_td = self._hello_details()

        if expect_exporter:
            # TLS 1.3: tls-exporter is the only valid binding (32 bytes, symmetric, both
            # ends equal); tls-unique (RFC 5929) is not defined for TLS 1.3 and the version
            # guard (#2078) keeps it out of the map entirely (no non-standard binding).
            self.assertNotIn("tls-unique", server_td.channel_id)
            self.assertNotIn("tls-unique", client_td.channel_id)
            self.assertIn("tls-exporter", server_td.channel_id)
            self.assertIn("tls-exporter", client_td.channel_id)
            self.assertEqual(len(server_td.channel_id["tls-exporter"]), 32)
            self.assertEqual(
                server_td.channel_id["tls-exporter"],
                client_td.channel_id["tls-exporter"],
            )
        else:
            # TLS <= 1.2: tls-unique is the only valid binding; tls-exporter (RFC 9266)
            # is not applicable and must not be populated.
            self.assertIn("tls-unique", server_td.channel_id)
            self.assertIn("tls-unique", client_td.channel_id)
            self.assertNotIn("tls-exporter", server_td.channel_id)
            self.assertNotIn("tls-exporter", client_td.channel_id)

    def test_tls_exporter_populated_tls13(self):
        return self._check_tls_exporter_populated("1.3", expect_exporter=True)

    def test_tls_exporter_not_populated_tls12(self):
        return self._check_tls_exporter_populated("1.2", expect_exporter=False)

    # WAMP-cryptosign selects the channel-binding type by negotiated TLS version (#2078)

    def _channel_binding_sent(self):
        # the channel-binding type the client put in HELLO.authextra, as recorded by
        # FakeRouterSession (i.e. what the router binds the client's signature to)
        return [cb for event, cb in self.observed if event == "channel_binding"][0]

    @inlineCallbacks
    def _check_cryptosign_binding_selected(self, tls_version, expected_binding):
        # the client requests channel binding with the legacy explicit "tls-unique";
        # autobahn must select the version-correct type and send that in HELLO:
        # tls-exporter on TLS 1.3, tls-unique on TLS <= 1.2 (hard split).
        authenticator = AuthCryptoSign(
            privkey=binascii.b2a_hex(b"\x01" * 32).decode(),
            authextra={"channel_binding": "tls-unique"},
        )
        outcome, details, _ = yield self._join(
            None, "cryptosign", authenticator, tls_version=tls_version
        )
        self.assertEqual(self._aborts(), [])
        self.assertEqual(outcome, "joined")
        self.assertEqual(self._channel_binding_sent(), expected_binding)

    def test_cryptosign_binding_selected_tls13(self):
        return self._check_cryptosign_binding_selected("1.3", "tls-exporter")

    def test_cryptosign_binding_selected_tls12(self):
        return self._check_cryptosign_binding_selected("1.2", "tls-unique")


class TlsWebSocketTests(_TlsWampTests, unittest.TestCase):
    transport = "websocket"


class TlsRawSocketTests(_TlsWampTests, unittest.TestCase):
    transport = "rawsocket"


_STDLIB_TLS_VERSIONS = {
    "1.2": stdlib_ssl.TLSVersion.TLSv1_2,
    "1.3": stdlib_ssl.TLSVersion.TLSv1_3,
}


def _stdlib_channel_id(tls_socket):
    # what autobahn uses on asyncio: Python's ssl module, which implements RFC 5929
    # (on PyPy with a workaround, see autobahn.util.tls_unique())
    return hashlib.sha256(tls_unique(tls_socket)).digest()


class TlsUniqueTests(unittest.TestCase):
    """
    The TLS channel ID ``tls-unique`` (RFC 5929) is the first TLS Finished message of the
    handshake, in a full handshake the client's. On both sides of a connection, Twisted must
    compute the same channel ID as Python's ``ssl`` module (which autobahn uses on asyncio),
    so that WAMP-cryptosign with channel binding works between Twisted and asyncio peers.
    """

    timeout = 20

    def setUp(self):
        self.pki = ExamplePKI(self.mktemp())

    @inlineCallbacks
    def _check_twisted_server(self, tls_version, expect_reject=False):
        handshake = Deferred()
        closed = Deferred()

        @implementer(IHandshakeListener)
        class Server(Protocol):
            def handshakeCompleted(self_):
                try:
                    channel_id = transport_channel_id(
                        self_.transport, True, "tls-unique"
                    )
                    handshake.callback(("ok", channel_id))
                except Exception as e:
                    handshake.callback(("raised", e))

            def connectionLost(self_, reason):
                closed.callback(None)

        server = ssl.PrivateCertificate.loadPEM(
            self.pki.pem("server", "crt") + self.pki.pem("server", "key")
        )
        version = _TLS_VERSIONS[tls_version]
        options = ssl.CertificateOptions(
            privateKey=server.privateKey.original,
            certificate=server.original,
            raiseMinimumTo=version,
            lowerMaximumSecurityTo=version,
        )
        port = yield SSL4ServerEndpoint(
            reactor, 0, options, interface="127.0.0.1"
        ).listen(Factory.forProtocol(Server))
        self.addCleanup(port.stopListening)

        def stdlib_client():
            ctx = stdlib_ssl.SSLContext(stdlib_ssl.PROTOCOL_TLS_CLIENT)
            ctx.load_verify_locations(self.pki.path("ca", "crt"))
            ctx.minimum_version = ctx.maximum_version = _STDLIB_TLS_VERSIONS[
                tls_version
            ]
            with socket.create_connection(("127.0.0.1", port.getHost().port)) as sock:
                with ctx.wrap_socket(sock, server_hostname="localhost") as tls_socket:
                    # TLS 1.3: the server completes the handshake on the client's Finished
                    tls_socket.sendall(b"x")
                    return _stdlib_channel_id(tls_socket)

        client_id = yield deferToThread(stdlib_client)
        kind, server_result = yield handshake
        yield closed
        if expect_reject:
            # on TLS 1.3, tls-unique is not a valid channel binding and must be rejected
            # (#2078 version guard), rather than return the (non-standard) TLS 1.3 Finished
            self.assertEqual(kind, "raised")
            self.assertIsInstance(server_result, RuntimeError)
        else:
            self.assertEqual(kind, "ok")
            self.assertEqual(server_result, client_id)

    def test_twisted_server_tls12(self):
        return self._check_twisted_server("1.2")

    def test_twisted_server_tls13(self):
        return self._check_twisted_server("1.3", expect_reject=True)

    @inlineCallbacks
    def _check_twisted_client(self, tls_version, expect_reject=False):
        handshake = Deferred()
        closed = Deferred()

        @implementer(IHandshakeListener)
        class Client(Protocol):
            def handshakeCompleted(self_):
                try:
                    channel_id = transport_channel_id(
                        self_.transport, False, "tls-unique"
                    )
                    handshake.callback(("ok", channel_id))
                except Exception as e:
                    handshake.callback(("raised", e))
                assert self_.transport is not None
                self_.transport.loseConnection()

            def connectionLost(self_, reason):
                closed.callback(None)

        ctx = stdlib_ssl.SSLContext(stdlib_ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(
            self.pki.path("server", "crt"), self.pki.path("server", "key")
        )
        ctx.minimum_version = ctx.maximum_version = _STDLIB_TLS_VERSIONS[tls_version]
        listener = socket.create_server(("127.0.0.1", 0))
        self.addCleanup(listener.close)

        def stdlib_server():
            conn, _ = listener.accept()
            with ctx.wrap_socket(conn, server_side=True) as tls_socket:
                channel_id = _stdlib_channel_id(tls_socket)
                # wait for the client to close the connection
                while True:
                    try:
                        if not tls_socket.recv(1):
                            break
                    except (OSError, stdlib_ssl.SSLError):
                        break
                return channel_id

        d_server = deferToThread(stdlib_server)
        options = ssl.optionsForClientTLS(
            "localhost", trustRoot=ssl.Certificate.loadPEM(self.pki.pem("ca", "crt"))
        )
        endpoint = SSL4ClientEndpoint(
            reactor, "127.0.0.1", listener.getsockname()[1], options
        )
        yield endpoint.connect(Factory.forProtocol(Client))
        kind, client_result = yield handshake
        server_id = yield d_server
        yield closed
        if expect_reject:
            # on TLS 1.3, tls-unique is not a valid channel binding and must be rejected
            # (#2078 version guard), rather than return the (non-standard) TLS 1.3 Finished
            self.assertEqual(kind, "raised")
            self.assertIsInstance(client_result, RuntimeError)
        else:
            self.assertEqual(kind, "ok")
            self.assertEqual(client_result, server_id)

    def test_twisted_client_tls12(self):
        return self._check_twisted_client("1.2")

    def test_twisted_client_tls13(self):
        return self._check_twisted_client("1.3", expect_reject=True)

    def test_wamp_protocols_know_their_side(self):
        """
        The channel ID depends on the side of the connection, which the transport details take
        from the protocol's ``is_server``.
        """
        self.assertIs(WampWebSocketServerProtocol.is_server, True)
        self.assertIs(WampWebSocketClientProtocol.is_server, False)
        self.assertIs(WampRawSocketServerProtocol.is_server, True)
        self.assertIs(WampRawSocketClientProtocol.is_server, False)


# RFC 9266 label and length for the "tls-exporter" channel binding.
_TLS_EXPORTER_LABEL = b"EXPORTER-Channel-Binding"
_TLS_EXPORTER_LENGTH = 32


class TlsExporterTests(unittest.TestCase):
    """
    The TLS channel ID ``tls-exporter`` (RFC 9266) is the exported keying material for the
    label ``EXPORTER-Channel-Binding``. Unlike ``tls-unique`` it is symmetric (client and
    server derive the same value) and defined for TLS 1.3. On the Twisted (pyOpenSSL) side
    autobahn must derive the same value a peer computes directly via
    ``OpenSSL.SSL.Connection.export_keying_material()`` (#1584).
    """

    timeout = 20

    def setUp(self):
        self.pki = ExamplePKI(self.mktemp())

    @inlineCallbacks
    def test_twisted_server_tls13(self):
        handshake = Deferred()
        closed = Deferred()

        @implementer(IHandshakeListener)
        class Server(Protocol):
            def handshakeCompleted(self_):
                handshake.callback(
                    transport_channel_id(self_.transport, True, "tls-exporter")
                )

            def connectionLost(self_, reason):
                closed.callback(None)

        server = ssl.PrivateCertificate.loadPEM(
            self.pki.pem("server", "crt") + self.pki.pem("server", "key")
        )
        version = _TLS_VERSIONS["1.3"]
        options = ssl.CertificateOptions(
            privateKey=server.privateKey.original,
            certificate=server.original,
            raiseMinimumTo=version,
            lowerMaximumSecurityTo=version,
        )
        port = yield SSL4ServerEndpoint(
            reactor, 0, options, interface="127.0.0.1"
        ).listen(Factory.forProtocol(Server))
        self.addCleanup(port.stopListening)

        def pyopenssl_client():
            from OpenSSL import SSL

            ctx = SSL.Context(SSL.TLS_CLIENT_METHOD)
            ctx.set_min_proto_version(SSL.TLS1_3_VERSION)
            ctx.set_max_proto_version(SSL.TLS1_3_VERSION)
            ctx.load_verify_locations(self.pki.path("ca", "crt"))
            ctx.set_verify(SSL.VERIFY_PEER)
            with socket.create_connection(("127.0.0.1", port.getHost().port)) as sock:
                conn = SSL.Connection(ctx, sock)
                conn.set_tlsext_host_name(b"localhost")
                conn.set_connect_state()
                conn.do_handshake()
                # TLS 1.3: let the server see application data so it finishes the handshake
                conn.send(b"x")
                exporter = conn.export_keying_material(
                    _TLS_EXPORTER_LABEL, _TLS_EXPORTER_LENGTH, b""
                )
                try:
                    conn.shutdown()
                except SSL.Error:
                    pass
                sock.close()
                return exporter

        client_id = yield deferToThread(pyopenssl_client)
        server_id = yield handshake
        yield closed
        self.assertEqual(len(server_id), _TLS_EXPORTER_LENGTH)
        self.assertEqual(server_id, client_id)
