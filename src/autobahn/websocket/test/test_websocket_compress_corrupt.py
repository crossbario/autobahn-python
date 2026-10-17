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
# shared WebSocket protocol handling on both networking backends.

import unittest

from autobahn.websocket.protocol import WebSocketProtocol
from autobahn.websocket.test.test_websocket_max_message_size import (
    _CODECS,
    _build_compressed_body_frame,
    _make_compressor_pair,
    _make_server,
)

# Not a valid compressed stream for any of the backends.
_CORRUPT_BODY = b"\xff" * 64


class CorruptCompressedFrameTests(unittest.TestCase):
    """
    A compressed frame that does not decompress must fail the WebSocket
    connection cleanly, the same way for every compression backend (#1986):
    no decoder exception escapes the protocol, the connection is failed with
    close code 1007 (invalid frame payload data), and nothing is delivered to
    the application.
    """

    LIMIT = 1024 * 1024

    def _assert_failed_cleanly(self, streaming, fail_by_drop=True):
        for codec in _CODECS:
            with self.subTest(codec=codec):
                pair = _make_compressor_pair(codec)
                if pair is None:
                    continue
                _, server_decompressor = pair
                proto = _make_server(
                    server_decompressor, self.LIMIT, streaming=streaming
                )
                proto.failByDrop = fail_by_drop
                # no closing-handshake timer: it would outlive the test
                proto.closeHandshakeTimeout = 0
                try:
                    proto._dataReceived(_build_compressed_body_frame(_CORRUPT_BODY))
                except Exception as e:
                    self.fail(
                        f"{codec}: decoder exception escaped the protocol: "
                        f"{type(e).__module__}.{type(e).__name__}: {e}"
                    )
                self.assertTrue(proto.failedByMe, f"{codec}: connection not failed")
                if fail_by_drop:
                    self.assertTrue(proto.was_dropped, f"{codec}: connection not dropped")
                else:
                    self.assertEqual(
                        proto.localCloseCode,
                        WebSocketProtocol.CLOSE_STATUS_CODE_INVALID_PAYLOAD,
                        f"{codec}: wrong close code",
                    )
                self.assertEqual(proto.delivered, [], f"{codec}: message was delivered")
                self.assertEqual(proto.streamed, [], f"{codec}: frame was delivered")

    def test_message_mode_corrupt_frame_fails_connection(self):
        self._assert_failed_cleanly(streaming=False)

    def test_streaming_mode_corrupt_frame_fails_connection(self):
        self._assert_failed_cleanly(streaming=True)

    def test_corrupt_frame_closes_with_1007(self):
        # failByDrop=False: the connection is failed with a closing handshake,
        # which carries the close code.
        self._assert_failed_cleanly(streaming=False, fail_by_drop=False)
