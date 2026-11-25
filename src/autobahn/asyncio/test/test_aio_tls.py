###############################################################################
#
#  Copyright (C) typedef int GmbH
#  SPDX-License-Identifier: MIT
#
###############################################################################
"""
WAMP over TLS on asyncio (#2014): the TLS client certificate in the transport details,
TLS client certificate authentication (authmethod "tls"), and WAMP-cryptosign with TLS
channel binding ("tls-unique"), over WebSocket and RawSocket, on TLS 1.2 and TLS 1.3.

The same scenarios as autobahn/twisted/test/test_tx_tls.py, over real TLS connections on
the loopback interface, with certificates created for each test (see autobahn.test.tlsutil).
"""

import asyncio
import binascii
import os
import socket
import ssl
import threading

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)

if os.environ.get("USE_ASYNCIO", False):
    from autobahn.asyncio.rawsocket import (
        WampRawSocketClientFactory,
        WampRawSocketServerFactory,
    )
    from autobahn.asyncio.wamp import ApplicationSession
    from autobahn.asyncio.websocket import (
        WampWebSocketClientFactory,
        WampWebSocketServerFactory,
    )
    from autobahn.test.tlsutil import (
        CLIENT_SUBJECT,
        FakeRouterSession,
        ExamplePKI,
        expected_peer_cert,
    )
    from autobahn.wamp import cryptosign
    from autobahn.wamp.auth import AuthCryptoSign
    from autobahn.wamp.types import ComponentConfig

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
            authextra = self._authenticator.authextra if self._authenticator else None
            self.join(
                self.config.realm, authmethods=[self._authmethod], authextra=authextra
            )

        def onChallenge(self, challenge):
            return self._authenticator.on_challenge(self, challenge)

        def onJoin(self, details):
            if not self._done.done():
                self._done.set_result(
                    ("joined", details, self._require_transport().transport_details)
                )
            self.leave()

        def onLeave(self, details):
            if not self._done.done():
                self._done.set_result(("left", details, None))
            self.disconnect()

        def onDisconnect(self):
            if not self._done.done():
                self._done.set_result(("disconnected", None, None))


_TRANSPORTS = ["websocket", "rawsocket"]
_TLS_VERSIONS = [None, "1.2", "1.3"]
_PRIVKEY = b"\x01" * 32


class _Setup:
    def __init__(self, certdir):
        self.pki = ExamplePKI(certdir)
        self.observed = []
        self.principals = {
            expected_peer_cert(self.pki.client_certs["client_0"], {}, {})["sha1"]: (
                "client_0",
                "backend",
            ),
        }
        self.pubkeys = {
            cryptosign.CryptosignKey.from_bytes(_PRIVKEY).public_key(): (
                "alice",
                "frontend",
            )
        }

    def aborts(self):
        return [what for event, what in self.observed if event == "abort"]

    def hello_details(self):
        return [td for event, td in self.observed if event == "hello"][0]

    def server_context(self, tls_version):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(
            self.pki.path("server", "crt"), self.pki.path("server", "key")
        )
        ctx.load_verify_locations(self.pki.path("ca", "crt"))
        ctx.verify_mode = ssl.CERT_OPTIONAL
        if tls_version:
            version = {"1.2": ssl.TLSVersion.TLSv1_2, "1.3": ssl.TLSVersion.TLSv1_3}[
                tls_version
            ]
            ctx.minimum_version = ctx.maximum_version = version
        return ctx

    def client_context(self, client):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(self.pki.path("ca", "crt"))
        if client:
            ctx.load_cert_chain(
                self.pki.path(client, "crt"), self.pki.path(client, "key")
            )
        return ctx

    async def join(
        self, transport, client, authmethod, authenticator=None, tls_version=None
    ):
        """
        Connect a client with the TLS client certificate ``client`` (or none), join with
        ``authmethod``, and return ``(outcome, details, client transport details)``.
        """
        loop = asyncio.get_running_loop()
        server_closed = loop.create_future()
        done = loop.create_future()

        def router_session():
            return FakeRouterSession(
                principals=self.principals,
                pubkeys=self.pubkeys,
                observed=self.observed,
                on_close=lambda: server_closed.done() or server_closed.set_result(None),
            )

        def client_session():
            return _Client(ComponentConfig("realm1"), authmethod, authenticator, done)

        if transport == "websocket":
            server_factory = WampWebSocketServerFactory(router_session)
        else:
            server_factory = WampRawSocketServerFactory(router_session)

        server = await loop.create_server(
            server_factory, "127.0.0.1", 0, ssl=self.server_context(tls_version)
        )
        port = server.sockets[0].getsockname()[1]
        try:
            if transport == "websocket":
                client_factory = WampWebSocketClientFactory(
                    client_session, url=f"wss://localhost:{port}"
                )
            else:
                client_factory = WampRawSocketClientFactory(client_session)

            client_transport, _ = await loop.create_connection(
                client_factory,
                "127.0.0.1",
                port,
                ssl=self.client_context(client),
                server_hostname="localhost",
            )
            result = await asyncio.wait_for(done, 10)
            # wait until both sides closed the connection
            await asyncio.wait_for(server_closed, 10)
            client_transport.close()
            return result
        finally:
            server.close()


@pytest.fixture
def setup(tmp_path):
    return _Setup(str(tmp_path / "certs"))


# TLS client certificate authentication (authmethod "tls")


@pytest.mark.asyncio
@pytest.mark.parametrize("tls_version", _TLS_VERSIONS)
@pytest.mark.parametrize("transport", _TRANSPORTS)
async def test_tls_auth_accepted(setup, transport, tls_version):
    outcome, details, _ = await setup.join(
        transport, "client_0", "tls", tls_version=tls_version
    )
    assert setup.aborts() == []
    assert outcome == "joined"
    assert (details.authid, details.authrole, details.authmethod) == (
        "client_0",
        "backend",
        "tls",
    )

    # what the router sees: the client certificate, after the TLS handshake
    peer_cert = setup.hello_details().peer_cert
    cert = setup.pki.client_certs["client_0"]
    expected = expected_peer_cert(
        cert,
        dict(CLIENT_SUBJECT, cn="client_0"),
        {"o": "Example GmbH", "cn": "Example Test CA"},
    )
    for key, value in expected.items():
        assert peer_cert[key] == value, key


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", _TRANSPORTS)
async def test_tls_auth_unknown_certificate(setup, transport):
    """
    A client certificate the CA signed, but that is not a principal: denied, for that reason.
    """
    outcome, _, _ = await setup.join(transport, "client_1", "tls")
    assert outcome == "left"
    sha1 = expected_peer_cert(setup.pki.client_certs["client_1"], {}, {})["sha1"]
    assert setup.aborts() == [f"client certificate {sha1} not accepted"]


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", _TRANSPORTS)
async def test_tls_auth_no_certificate(setup, transport):
    outcome, _, _ = await setup.join(transport, None, "tls")
    assert outcome == "left"
    assert setup.aborts() == ["no client certificate presented"]
    assert setup.hello_details().peer_cert is None


# WAMP-cryptosign with TLS channel binding


@pytest.mark.asyncio
@pytest.mark.parametrize("client", [None, "client_0"])
@pytest.mark.parametrize("tls_version", ["1.2"])
@pytest.mark.parametrize("transport", _TRANSPORTS)
async def test_cryptosign_channel_binding(setup, transport, tls_version, client):
    """
    With and without a TLS client certificate: on TLS <= 1.2 the router side of a TLS
    connection is secure and has the same, non-zero tls-unique channel ID as the client
    side. The asyncio backend can channel-bind only on TLS <= 1.2 (tls-unique): on TLS 1.3
    it cannot (the stdlib ssl module has no tls-exporter), see the test below (#2078).
    """
    authenticator = AuthCryptoSign(
        privkey=binascii.b2a_hex(_PRIVKEY).decode(),
        authextra={"channel_binding": "tls-unique"},
    )
    outcome, details, client_td = await setup.join(
        transport, client, "cryptosign", authenticator, tls_version
    )
    assert setup.aborts() == []
    assert outcome == "joined"
    assert (details.authid, details.authmethod) == ("alice", "cryptosign")

    server_td = setup.hello_details()
    assert server_td.is_secure
    assert server_td.channel_id["tls-unique"] == client_td.channel_id["tls-unique"]
    assert server_td.channel_id["tls-unique"] != FakeRouterSession.ZERO_CHANNEL_ID


@pytest.mark.asyncio
@pytest.mark.parametrize("client", [None, "client_0"])
@pytest.mark.parametrize("transport", _TRANSPORTS)
async def test_cryptosign_channel_binding_unavailable_on_tls13(setup, transport, client):
    """
    On the asyncio backend, WAMP-cryptosign channel binding is not available on TLS 1.3:
    tls-unique (RFC 5929) is rejected on TLS 1.3 (#2078 version guard) and tls-exporter
    (RFC 9266) is not exposed by the stdlib ssl module, so TransportDetails.channel_id is
    empty. A client that requests channel binding therefore fails closed - the router
    denies it for want of a TLS channel ID - rather than silently binding to a bogus value
    (a TLS 1.3 asyncio peer must use the Twisted backend, or TLS <= 1.2, to channel-bind).
    """
    authenticator = AuthCryptoSign(
        privkey=binascii.b2a_hex(_PRIVKEY).decode(),
        authextra={"channel_binding": "tls-unique"},
    )
    outcome, _, _ = await setup.join(
        transport, client, "cryptosign", authenticator, "1.3"
    )
    # fail closed: the router aborts because it has no TLS channel ID to bind to
    assert outcome != "joined"
    assert setup.aborts() == ["channel binding requested, but no TLS channel ID"]


# tls-exporter (RFC 9266) on the asyncio backend: fail fast


@pytest.mark.skipif(
    "tls-exporter" in ssl.CHANNEL_BINDING_TYPES,
    reason="stdlib ssl exposes tls-exporter on this build; the fail-fast path no longer applies",
)
def test_tls_exporter_not_implemented_on_asyncio():
    """
    The asyncio backend uses the Python stdlib ssl module, which (through 3.14)
    exposes only "tls-unique" in ``ssl.CHANNEL_BINDING_TYPES`` and never
    "tls-exporter" (RFC 9266). Requesting tls-exporter on asyncio must therefore
    fail fast with ``NotImplementedError`` (pointing at the Twisted backend), rather
    than raise a generic error or silently fall back. The skip above lets the real
    support path take over automatically should a future CPython add tls-exporter to
    ``ssl.CHANNEL_BINDING_TYPES``.
    """
    from autobahn.asyncio.util import transport_channel_id

    with pytest.raises(NotImplementedError):
        transport_channel_id(None, False, "tls-exporter")


# tls-unique (RFC 5929) on TLS 1.3: the version guard (#2078)


class _FakeAsyncioTLSTransport:
    """
    Just enough of an asyncio TLS transport for transport_channel_id(): it exposes the
    SSL object under ``get_extra_info("ssl_object")``, as a real asyncio TLS transport does.
    """

    def __init__(self, ssl_object):
        self._ssl_object = ssl_object

    def get_extra_info(self, name, default=None):
        return self._ssl_object if name == "ssl_object" else default


def _tls13_loopback_server_ssl_object(pki):
    """
    Complete a real TLS 1.3 handshake on the loopback interface and return the server
    side SSL socket (whose ``version()`` is ``"TLSv1.3"``), so a channel-binding
    extraction can be exercised against a genuine TLS 1.3 connection.
    """
    server_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_ctx.load_cert_chain(pki.path("server", "crt"), pki.path("server", "key"))
    server_ctx.minimum_version = server_ctx.maximum_version = ssl.TLSVersion.TLSv1_3

    client_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    client_ctx.load_verify_locations(pki.path("ca", "crt"))
    client_ctx.minimum_version = client_ctx.maximum_version = ssl.TLSVersion.TLSv1_3

    listener = socket.create_server(("127.0.0.1", 0))
    holder = {}

    def serve():
        conn, _ = listener.accept()
        tls_conn = server_ctx.wrap_socket(conn, server_side=True)
        # TLS 1.3: exchange application data so both ends settle post-handshake
        tls_conn.sendall(b"x")
        tls_conn.recv(1)
        holder["ssl"] = tls_conn

    thread = threading.Thread(target=serve)
    thread.start()
    with socket.create_connection(listener.getsockname()) as sock:
        with client_ctx.wrap_socket(sock, server_hostname="localhost") as tls_socket:
            tls_socket.recv(1)
            tls_socket.sendall(b"x")
    thread.join(timeout=10)
    listener.close()
    return holder["ssl"]


def test_tls_unique_rejected_on_tls13(tmp_path):
    """
    On TLS 1.3, tls-unique (RFC 5929) is not a valid channel binding: the stdlib
    ``ssl`` module's ``get_channel_binding("tls-unique")`` does not fail there, it
    silently returns the (longer) TLS 1.3 Finished message, which would yield a
    non-standard binding that only happens to match between two stdlib peers. autobahn
    must reject tls-unique on a TLS 1.3 connection (#2078 version guard) so a TLS 1.3
    peer uses tls-exporter (Twisted) or no binding, never a bogus tls-unique.
    """
    from autobahn.test.tlsutil import ExamplePKI
    from autobahn.asyncio.util import transport_channel_id

    pki = ExamplePKI(str(tmp_path / "certs"))
    ssl_object = _tls13_loopback_server_ssl_object(pki)
    try:
        assert ssl_object.version() == "TLSv1.3"
        transport = _FakeAsyncioTLSTransport(ssl_object)
        with pytest.raises(RuntimeError):
            transport_channel_id(transport, True, "tls-unique")
    finally:
        ssl_object.close()
