###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

"""
Tests for HTTP header parsing in the WebSocket opening handshake (#2034).

``parseHttpHeader`` split the header block with ``str.splitlines()``, which
also splits on VT, FF, FS, GS, RS, NEL and on a bare CR or LF. A peer could
therefore make autobahn see header lines that a conforming HTTP recipient (for
example a front proxy) treats as part of a field value.

The expected behaviour follows RFC 9112 section 2.2 / 5 and RFC 9110 section 5.5:

- lines are separated by CRLF only;
- a bare LF is rejected too: RFC 9112 section 2.2 allows a recipient to accept
  it as a line terminator, but we deliberately do not, since a front proxy that
  does not split on it would see one header where autobahn sees two;
- a header block with a bare CR, a bare LF, obs-fold, whitespace before the
  colon, or a control character in a field is rejected;
- obs-text (0x80-0xFF) in field values stays allowed.

A rejected header block makes the server fail the handshake (HTTP 400), the
client fail the handshake, and the client fail an explicit proxy CONNECT.
"""

import unittest
from base64 import b64encode
from hashlib import sha1
from unittest.mock import Mock

import txaio

from autobahn.testutil import FakeTransport
from autobahn.wamp.types import TransportDetails
from autobahn.websocket.protocol import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
    WebSocketProtocol,
    WebSocketServerFactory,
    WebSocketServerProtocol,
    parseHttpHeader,
)
from autobahn.websocket.types import ConnectingRequest

# the forged header used throughout: with trustXForwardedFor, a smuggled
# X-Forwarded-For would let a client pick its own peer address
SMUGGLED = b"X-Forwarded-For: 6.6.6.6"

# header lines that must make the whole header block invalid, each carrying a
# smuggling attempt where applicable
BAD_LINES = {
    "vt": b"X-Foo: a\x0b" + SMUGGLED,
    "ff": b"X-Foo: a\x0c" + SMUGGLED,
    "fs": b"X-Foo: a\x1c" + SMUGGLED,
    "gs": b"X-Foo: a\x1d" + SMUGGLED,
    "rs": b"X-Foo: a\x1e" + SMUGGLED,
    "bare_cr": b"X-Foo: a\x0d" + SMUGGLED,
    # deliberately rejected, although RFC 9112 2.2 allows accepting it (see above)
    "bare_lf": b"X-Foo: a\x0a" + SMUGGLED,
    "obs_fold_sp": b"X-Foo: a\x0d\x0a " + SMUGGLED,
    "obs_fold_htab": b"X-Foo: a\x0d\x0a\x09" + SMUGGLED,
    "space_before_colon": b"X-Forwarded-For : 6.6.6.6",
    "htab_before_colon": b"X-Forwarded-For\x09: 6.6.6.6",
    "space_in_name": b"X Forwarded For: 6.6.6.6",
    "nul_in_value": b"X-Foo: a\x00b",
    "soh_in_value": b"X-Foo: a\x01b",
    "del_in_value": b"X-Foo: a\x7fb",
    "ctl_in_name": b"X-F\x01oo: bar",
    "no_colon": b"X-Foo bar",
    "empty_name": b": bar",
}

REQUEST_LINE = b"GET /ws HTTP/1.1"

REQUEST_HEADERS = [
    b"Host: www.example.com",
    b"Origin: http://www.example.com",
    b"Sec-WebSocket-Version: 13",
    b"Sec-WebSocket-Key: tXAxWFUqnhi86Ajj7dRY5g==",
    b"Connection: keep-alive, Upgrade",
    b"Upgrade: websocket",
]


def _block(first_line: bytes, lines: list[bytes]) -> bytes:
    return b"\x0d\x0a".join([first_line] + lines) + b"\x0d\x0a\x0d\x0a"


def _request(extra: bytes | None = None, request_line: bytes = REQUEST_LINE) -> bytes:
    lines = list(REQUEST_HEADERS)
    if extra is not None:
        lines.append(extra)
    return _block(request_line, lines)


class ParseHttpHeaderValidTests(unittest.TestCase):
    """
    Header blocks that are valid must keep parsing as before.
    """

    def test_valid_request(self):
        status, headers, counts = parseHttpHeader(_request())
        self.assertEqual(status, "GET /ws HTTP/1.1")
        self.assertEqual(headers["host"], "www.example.com")
        self.assertEqual(headers["upgrade"], "websocket")
        self.assertEqual(headers["connection"], "keep-alive, Upgrade")
        self.assertEqual(counts["host"], 1)
        self.assertNotIn("x-forwarded-for", headers)

    def test_ows_is_trimmed(self):
        _, headers, _ = parseHttpHeader(_request(b"X-Foo:  \x09bar\x09 "))
        self.assertEqual(headers["x-foo"], "bar")

    def test_htab_inside_value(self):
        _, headers, _ = parseHttpHeader(_request(b"X-Foo: a\x09b"))
        self.assertEqual(headers["x-foo"], "a\x09b")

    def test_obs_text_in_value(self):
        # RFC 9110 5.5: field-vchar = VCHAR / obs-text
        _, headers, _ = parseHttpHeader(_request(b"X-Foo: caf\xe9"))
        self.assertEqual(headers["x-foo"], "caf\xe9")

    def test_repeated_header(self):
        data = _block(REQUEST_LINE, REQUEST_HEADERS + [b"X-Foo: a", b"x-foo: b"])
        _, headers, counts = parseHttpHeader(data)
        self.assertEqual(headers["x-foo"], "a, b")
        self.assertEqual(counts["x-foo"], 2)

    def test_nel_does_not_split(self):
        # 0x85 is obs-text, which RFC 9110 allows in a field value: it may be
        # kept in the value or the block may be rejected, but it must never
        # start a new header line
        try:
            _, headers, _ = parseHttpHeader(_request(b"X-Foo: a\x85" + SMUGGLED))
        except Exception:
            return
        self.assertNotIn("x-forwarded-for", headers)
        self.assertEqual(headers["x-foo"], "a\x85X-Forwarded-For: 6.6.6.6")


class ParseHttpHeaderInvalidTests(unittest.TestCase):
    """
    Header blocks that are invalid must be rejected (raise).
    """

    def _assert_rejected(self, data: bytes):
        with self.assertRaises(Exception):
            parseHttpHeader(data)

    def test_reject_vt(self):
        self._assert_rejected(_request(BAD_LINES["vt"]))

    def test_reject_ff(self):
        self._assert_rejected(_request(BAD_LINES["ff"]))

    def test_reject_fs(self):
        self._assert_rejected(_request(BAD_LINES["fs"]))

    def test_reject_gs(self):
        self._assert_rejected(_request(BAD_LINES["gs"]))

    def test_reject_rs(self):
        self._assert_rejected(_request(BAD_LINES["rs"]))

    def test_reject_bare_cr(self):
        self._assert_rejected(_request(BAD_LINES["bare_cr"]))

    def test_reject_bare_lf(self):
        # deliberately stricter than RFC 9112 2.2 (see module docstring)
        self._assert_rejected(_request(BAD_LINES["bare_lf"]))

    def test_reject_obs_fold_sp(self):
        self._assert_rejected(_request(BAD_LINES["obs_fold_sp"]))

    def test_reject_obs_fold_htab(self):
        self._assert_rejected(_request(BAD_LINES["obs_fold_htab"]))

    def test_reject_space_before_colon(self):
        self._assert_rejected(_request(BAD_LINES["space_before_colon"]))

    def test_reject_htab_before_colon(self):
        self._assert_rejected(_request(BAD_LINES["htab_before_colon"]))

    def test_reject_space_in_name(self):
        self._assert_rejected(_request(BAD_LINES["space_in_name"]))

    def test_reject_nul_in_value(self):
        self._assert_rejected(_request(BAD_LINES["nul_in_value"]))

    def test_reject_soh_in_value(self):
        self._assert_rejected(_request(BAD_LINES["soh_in_value"]))

    def test_reject_del_in_value(self):
        self._assert_rejected(_request(BAD_LINES["del_in_value"]))

    def test_reject_ctl_in_name(self):
        self._assert_rejected(_request(BAD_LINES["ctl_in_name"]))

    def test_reject_no_colon(self):
        # was silently skipped before #2034
        self._assert_rejected(_request(BAD_LINES["no_colon"]))

    def test_reject_empty_name(self):
        self._assert_rejected(_request(BAD_LINES["empty_name"]))

    def test_reject_ctl_in_request_line(self):
        # the request line itself must not be able to start a header line
        self._assert_rejected(_request(request_line=b"GET /ws HTTP/1.1\x0b" + SMUGGLED))


class _ProtocolTestMixin:
    protocol: WebSocketProtocol

    def tearDown(self):
        for call in [
            self.protocol.autoPingPendingCall,
            self.protocol.autoPingTimeoutCall,
            self.protocol.openHandshakeTimeoutCall,
            self.protocol.closeHandshakeTimeoutCall,
        ]:
            if call is not None:
                call.cancel()


class ServerHandshakeTests(_ProtocolTestMixin, unittest.TestCase):
    """
    The server fails the opening handshake on an invalid request header block,
    and a smuggled X-Forwarded-For never replaces the peer address.
    """

    def setUp(self):
        f = WebSocketServerFactory()
        f.log = txaio.make_logger()
        f.setProtocolOptions(trustXForwardedFor=1)
        p = WebSocketServerProtocol()
        p.log = txaio.make_logger()
        p.factory = f
        p.transport = FakeTransport()
        p._connectionMade()
        p.peer = "tcp4:10.0.0.1:50000"
        p.failHandshake = Mock()
        # usually provided by the Twisted or asyncio specific subclass
        p._onOpen = Mock()
        self.protocol = p

    def _assert_handshake_failed(self, extra: bytes):
        self.protocol.data = _request(extra)
        self.protocol.processHandshake()
        self.assertTrue(
            self.protocol.failHandshake.called,
            "invalid request header block must fail the opening handshake",
        )
        self.assertEqual(self.protocol.peer, "tcp4:10.0.0.1:50000")

    def test_trusted_xff_still_works(self):
        self.protocol.data = _request(b"X-Forwarded-For: 1.2.3.4")
        self.protocol.processHandshake()
        self.assertEqual(self.protocol.peer, "1.2.3.4")

    def test_fail_vt(self):
        self._assert_handshake_failed(BAD_LINES["vt"])

    def test_fail_ff(self):
        self._assert_handshake_failed(BAD_LINES["ff"])

    def test_fail_fs(self):
        self._assert_handshake_failed(BAD_LINES["fs"])

    def test_fail_gs(self):
        self._assert_handshake_failed(BAD_LINES["gs"])

    def test_fail_rs(self):
        self._assert_handshake_failed(BAD_LINES["rs"])

    def test_fail_bare_cr(self):
        self._assert_handshake_failed(BAD_LINES["bare_cr"])

    def test_fail_bare_lf(self):
        self._assert_handshake_failed(BAD_LINES["bare_lf"])

    def test_fail_obs_fold(self):
        self._assert_handshake_failed(BAD_LINES["obs_fold_sp"])

    def test_fail_space_before_colon(self):
        self._assert_handshake_failed(BAD_LINES["space_before_colon"])

    def test_nel_does_not_set_peer(self):
        self.protocol.data = _request(b"X-Foo: a\x85" + SMUGGLED)
        self.protocol.processHandshake()
        self.assertEqual(self.protocol.peer, "tcp4:10.0.0.1:50000")


class ClientHandshakeTests(_ProtocolTestMixin, unittest.TestCase):
    """
    The client fails the opening handshake on an invalid response header
    block, even when a smuggled line would complete the handshake.
    """

    def setUp(self):
        f = WebSocketClientFactory()
        f.log = txaio.make_logger()
        p = WebSocketClientProtocol()
        p.log = txaio.make_logger()
        p.factory = f
        p.transport = FakeTransport()
        p._transport_details = TransportDetails()
        p._connectionMade()
        p.websocket_version = 18
        p.websocket_protocols = []
        p.websocket_extensions = []
        p.peer = Mock()
        p._onConnect = Mock()
        p._onOpen = Mock()
        p._closeConnection = Mock()
        p.failHandshake = Mock()
        p._actuallyStartHandshake(
            ConnectingRequest(host="example.com", port=80, resource="/ws")
        )
        self.protocol = p
        key = p.websocket_key + WebSocketProtocol._WS_MAGIC
        self.accept = b"Sec-Websocket-Accept: " + b64encode(sha1(key).digest())

    def _response(self, lines: list[bytes]) -> bytes:
        return _block(
            b"HTTP/1.1 101 Switching Protocols",
            [b"Upgrade: websocket", b"Connection: upgrade"] + lines,
        )

    def test_valid_response(self):
        self.protocol.data = self._response([self.accept])
        self.protocol.processHandshake()
        self.assertFalse(self.protocol.failHandshake.called)
        self.assertEqual(self.protocol.state, WebSocketProtocol.STATE_OPEN)

    def _assert_handshake_failed(self, sep: bytes):
        # the only Sec-WebSocket-Accept is carried in a smuggled line
        self.protocol.data = self._response([b"X-Foo: a" + sep + self.accept])
        self.protocol.processHandshake()
        self.assertTrue(
            self.protocol.failHandshake.called,
            "invalid response header block must fail the opening handshake",
        )
        self.assertNotEqual(self.protocol.state, WebSocketProtocol.STATE_OPEN)
        self.assertFalse(self.protocol._onOpen.called)

    def test_fail_vt(self):
        self._assert_handshake_failed(b"\x0b")

    def test_fail_ff(self):
        self._assert_handshake_failed(b"\x0c")

    def test_fail_fs(self):
        self._assert_handshake_failed(b"\x1c")

    def test_fail_bare_cr(self):
        self._assert_handshake_failed(b"\x0d")

    def test_fail_bare_lf(self):
        self._assert_handshake_failed(b"\x0a")

    def test_fail_obs_fold(self):
        self._assert_handshake_failed(b"\x0d\x0a ")


class ClientProxyConnectTests(_ProtocolTestMixin, unittest.TestCase):
    """
    The client fails an explicit proxy CONNECT on an invalid response header
    block, instead of raising out of processProxyConnect.
    """

    def setUp(self):
        f = WebSocketClientFactory()
        f.log = txaio.make_logger()
        p = WebSocketClientProtocol()
        p.log = txaio.make_logger()
        p.factory = f
        p.transport = FakeTransport()
        p._transport_details = TransportDetails()
        p._connectionMade()
        p.state = WebSocketProtocol.STATE_PROXY_CONNECTING
        p.failProxyConnect = Mock()
        p.startHandshake = Mock()
        self.protocol = p

    def _connect(self, lines: list[bytes]):
        self.protocol.data = _block(b"HTTP/1.1 200 Connection established", lines)
        self.protocol.processProxyConnect()

    def test_valid_response(self):
        self._connect([b"X-Foo: bar"])
        self.assertFalse(self.protocol.failProxyConnect.called)
        self.assertTrue(self.protocol.startHandshake.called)

    def _assert_connect_failed(self, line: bytes):
        self._connect([line])
        self.assertTrue(
            self.protocol.failProxyConnect.called,
            "invalid proxy response header block must fail the proxy connect",
        )
        self.assertFalse(self.protocol.startHandshake.called)

    def test_fail_vt(self):
        self._assert_connect_failed(BAD_LINES["vt"])

    def test_fail_bare_cr(self):
        self._assert_connect_failed(BAD_LINES["bare_cr"])

    def test_fail_nul_in_value(self):
        self._assert_connect_failed(BAD_LINES["nul_in_value"])
