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

# Backend-neutral: this module is NOT gated on USE_TWISTED, so it runs under
# both the Twisted (trial) and asyncio (pytest) coverage phases, exercising the
# shared WebSocket protocol enforcement on both networking backends.

import unittest

import txaio

from autobahn.testutil import FakeTransport
from autobahn.wamp.types import TransportDetails
from autobahn.websocket.protocol import (
    WebSocketProtocol,
    WebSocketServerFactory,
    WebSocketServerProtocol,
)


def _make_compressor_pair(name):
    """
    Build a (client_compressor, server_decompressor) pair for the named
    permessage-compress extension, or return None if its optional dependency
    is not installed. The server decompressor is created WITHOUT any
    extension-level max_message_size, so that enforcement is exercised purely
    at the protocol level via maxMessagePayloadSize.

    Concrete per-codec imports (rather than the union-typed extension registry)
    keep the constructor call sites resolvable for the static type checker.
    """
    if name == "permessage-deflate":
        from autobahn.websocket.compress_deflate import PerMessageDeflate

        return (
            PerMessageDeflate(False, False, False, 15, 15, 8),
            PerMessageDeflate(True, False, False, 15, 15, 8),
        )
    if name == "permessage-bzip2":
        try:
            from autobahn.websocket.compress_bzip2 import PerMessageBzip2
        except ImportError:
            return None
        return (PerMessageBzip2(False, 9, 9), PerMessageBzip2(True, 9, 9))
    if name == "permessage-snappy":
        try:
            from autobahn.websocket.compress_snappy import PerMessageSnappy
        except ImportError:
            return None
        return (
            PerMessageSnappy(False, False, False),
            PerMessageSnappy(True, False, False),
        )
    if name == "permessage-brotli":
        try:
            from autobahn.websocket.compress_brotli import PerMessageBrotli
        except ImportError:
            return None
        return (
            PerMessageBrotli(False, False, False),
            PerMessageBrotli(True, False, False),
        )
    return None


def _build_compressed_frame(client_compressor, payload, opcode=0x02):
    """
    Encode a single masked, permessage-compressed, FIN client->server frame
    (RSV1 set) carrying `payload`. opcode 0x02 = binary (avoids UTF-8
    validation of the decompressed bytes).
    """
    client_compressor.start_compress_message()
    body = client_compressor.compress_message_data(payload)
    body += client_compressor.end_compress_message()
    return _build_compressed_body_frame(body, opcode)


def _build_compressed_body_frame(body, opcode=0x02):
    """
    Encode a single masked, FIN client->server frame with RSV1 (compressed)
    set, carrying `body` as is - e.g. a corrupt compressed body.
    """
    mask = b"\x11\x22\x33\x44"
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(body))
    n = len(body)
    b0 = 0x80 | 0x40 | opcode  # FIN + RSV1 (compressed) + opcode
    if n <= 125:
        header = bytes([b0, 0x80 | n])
    elif n <= 0xFFFF:
        header = bytes([b0, 0x80 | 126]) + n.to_bytes(2, "big")
    else:
        header = bytes([b0, 0x80 | 127]) + n.to_bytes(8, "big")
    return header + mask + masked


class _CapturingServerProtocol(WebSocketServerProtocol):
    """
    Minimal server protocol that captures delivered messages/frames instead of
    driving a real transport. The _on* hooks are the trivial pass-throughs a
    backend subclass would normally supply.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delivered = []  # whole reassembled messages (message mode)
        self.streamed = []  # per-frame payloads (streaming/frame mode)
        self.was_dropped = False

    def _onMessageBegin(self, isBinary):
        self.onMessageBegin(isBinary)

    def _onMessageFrameBegin(self, length):
        self.onMessageFrameBegin(length)

    def _onMessageFrameData(self, payload):
        self.onMessageFrameData(payload)

    def _onMessageFrameEnd(self):
        self.onMessageFrameEnd()

    def _onMessageFrame(self, payload):
        self.onMessageFrame(payload)

    def _onMessageEnd(self):
        self.onMessageEnd()

    def _onMessage(self, payload, isBinary):
        self.delivered.append(payload)

    def sendData(self, data, sync=False, chopsize=None):
        pass

    def dropConnection(self, abort=True):
        self.was_dropped = True
        self.droppedByMe = True
        self.state = WebSocketProtocol.STATE_CLOSED


class _StreamingServerProtocol(_CapturingServerProtocol):
    """A frame-API (streaming) consumer: captures each frame instead of
    buffering into a whole message."""

    def onMessageFrame(self, payload):
        if not self.failedByMe:
            self.streamed.append(b"".join(payload))


def _make_server(server_decompressor, max_message_size, streaming=False):
    factory = WebSocketServerFactory()
    factory.log = txaio.make_logger()
    cls = _StreamingServerProtocol if streaming else _CapturingServerProtocol
    proto = cls()
    proto.log = txaio.make_logger()
    proto.factory = factory
    proto.transport = FakeTransport()
    proto._transport_details = TransportDetails()
    proto._connectionMade()
    # _connectionMade() unconditionally schedules the opening-handshake timeout
    # on the reactor. These tests drive protocol bytes directly and never
    # complete a real handshake, so that DelayedCall would otherwise outlive
    # the test and Twisted's trial would report a dirty reactor. The
    # enforcement path fails the connection via dropConnection() (failByDrop
    # defaults True), so the closing-handshake timeout is not scheduled today -
    # but cancel both handshake timers defensively (mirroring _connectionLost),
    # so a future variant that drives a real close cannot silently leak one.
    if proto.openHandshakeTimeoutCall is not None:
        proto.openHandshakeTimeoutCall.cancel()
        proto.openHandshakeTimeoutCall = None
    if proto.closeHandshakeTimeoutCall is not None:
        proto.closeHandshakeTimeoutCall.cancel()
        proto.closeHandshakeTimeoutCall = None
    proto.state = WebSocketProtocol.STATE_OPEN
    proto.websocket_version = 13
    # normally set up when the opening handshake completes:
    proto.current_frame = None
    proto.inside_message = False
    proto._perMessageCompress = server_decompressor
    proto.maxMessagePayloadSize = max_message_size
    return proto


# The permessage-compress extensions to exercise; unavailable ones (optional
# dependency not installed) are skipped per-test.
_CODECS = [
    "permessage-deflate",
    "permessage-bzip2",
    "permessage-snappy",
    "permessage-brotli",
]


class WebSocketMaxMessagePayloadSizeTests(unittest.TestCase):
    """
    A compressed WebSocket message must be bounded by maxMessagePayloadSize
    against its UNCOMPRESSED (reassembled) size, not the compressed wire size.
    A small compressed frame that inflates beyond the limit must be rejected
    before delivery, for every compression backend and in both message and
    streaming processing modes.
    """

    # The compressed frame must be under LIMIT, and its inflated size over it:
    # BIG compresses to a few octets (snappy, at most about 21:1: 222 octets).
    LIMIT = 1024
    BIG = b"x" * 4096

    def _run(self, codec, streaming):
        pair = _make_compressor_pair(codec)
        if pair is None:
            self.skipTest(f"{codec} not available")
        client_compressor, server_decompressor = pair
        proto = _make_server(
            server_decompressor, self.LIMIT, streaming=streaming
        )
        frame = _build_compressed_frame(client_compressor, self.BIG)
        # sanity: the compressed frame is under the limit, so any pre-inflation
        # (compressed-size) check would let it through.
        self.assertLess(len(frame), self.LIMIT)
        proto._dataReceived(frame)
        return proto

    def _assert_rejected(self, codec, streaming):
        proto = self._run(codec, streaming)
        self.assertTrue(
            proto.wasMaxMessagePayloadSizeExceeded,
            f"{codec}: oversized message not flagged",
        )
        self.assertTrue(proto.was_dropped, f"{codec}: connection not dropped")
        self.assertEqual(proto.delivered, [], f"{codec}: message was delivered")
        self.assertEqual(proto.streamed, [], f"{codec}: frame was delivered")

    def test_message_mode_rejects_oversized(self):
        for codec in _CODECS:
            with self.subTest(codec=codec):
                self._assert_rejected(codec, streaming=False)

    def test_streaming_mode_rejects_oversized(self):
        for codec in _CODECS:
            with self.subTest(codec=codec):
                self._assert_rejected(codec, streaming=True)

    def test_under_limit_delivered_intact(self):
        payload = b"y" * 64  # inflated size 64 < LIMIT
        for codec in _CODECS:
            with self.subTest(codec=codec):
                pair = _make_compressor_pair(codec)
                if pair is None:
                    continue
                client_compressor, server_decompressor = pair
                proto = _make_server(server_decompressor, self.LIMIT)
                proto._dataReceived(
                    _build_compressed_frame(client_compressor, payload)
                )
                self.assertFalse(proto.wasMaxMessagePayloadSizeExceeded)
                self.assertEqual(proto.delivered, [payload])
