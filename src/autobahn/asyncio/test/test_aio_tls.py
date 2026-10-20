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
import ssl

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
                    ("joined", details, self._transport.transport_details)
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
@pytest.mark.parametrize("tls_version", _TLS_VERSIONS)
@pytest.mark.parametrize("transport", _TRANSPORTS)
async def test_cryptosign_channel_binding(setup, transport, tls_version, client):
    """
    With and without a TLS client certificate: the router side of a TLS connection is secure
    and has the same, non-zero channel ID as the client side.
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
