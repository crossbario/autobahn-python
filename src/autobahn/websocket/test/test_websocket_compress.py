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
# both the Twisted (trial) and asyncio (pytest) coverage phases. The
# permessage-compress backends are shared code, so bounded-decompression must
# behave identically regardless of the networking backend.

import random
import unittest
import zlib

try:
    import tracemalloc
except ImportError:  # PyPy has no tracemalloc
    tracemalloc = None

from autobahn.exception import PayloadCorruptError, PayloadExceededError
from autobahn.websocket.compress_deflate import PerMessageDeflate


def _make_compressor_pair(name, no_context_takeover=False):
    """
    Build a (client_compressor, server_decompressor) pair for the named
    permessage-compress extension, or return None if its optional dependency
    is not installed. The server decompressor is created WITHOUT any
    extension-level max_message_size, so the bounded-decompress behaviour under
    test is driven purely by the ``max_output_len`` argument.

    ``no_context_takeover`` applies to both directions (permessage-bzip2 has
    no such parameter: it never takes over context).

    Concrete per-codec imports (rather than the union-typed extension registry)
    keep the constructor call sites resolvable for the static type checker.
    """
    if name == "permessage-deflate":
        return (
            PerMessageDeflate(
                False, no_context_takeover, no_context_takeover, 15, 15, 8
            ),
            PerMessageDeflate(
                True, no_context_takeover, no_context_takeover, 15, 15, 8
            ),
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
            PerMessageSnappy(False, no_context_takeover, no_context_takeover),
            PerMessageSnappy(True, no_context_takeover, no_context_takeover),
        )
    if name == "permessage-brotli":
        try:
            from autobahn.websocket.compress_brotli import PerMessageBrotli
        except ImportError:
            return None
        return (
            PerMessageBrotli(False, no_context_takeover, no_context_takeover),
            PerMessageBrotli(True, no_context_takeover, no_context_takeover),
        )
    return None


# The permessage-compress extensions to exercise; unavailable ones (optional
# dependency not installed) are skipped per-subtest.
_CODECS = [
    "permessage-deflate",
    "permessage-bzip2",
    "permessage-snappy",
    "permessage-brotli",
]


class BoundedDecompressMaxOutputLenTests(unittest.TestCase):
    """
    ``decompress_message_data(data, max_output_len=N)`` must bound decompressed
    output: a message that inflates beyond ``N`` is rejected cleanly with
    ``PayloadExceededError`` (never silently truncated), an under-budget message
    round-trips byte-exact, and no ``max_output_len`` (the default) keeps the
    unbounded behaviour. This must hold for every compression backend.
    """

    BIG = b"x" * 4096  # inflates well beyond the small budget, compresses tiny
    SMALL = b"y" * 64

    @staticmethod
    def _compress(compressor, payload):
        compressor.start_compress_message()
        body = compressor.compress_message_data(payload)
        body += compressor.end_compress_message()
        return body

    def test_bounded_rejects_oversized(self):
        for codec in _CODECS:
            with self.subTest(codec=codec):
                pair = _make_compressor_pair(codec)
                if pair is None:
                    continue
                compressor, decompressor = pair
                body = self._compress(compressor, self.BIG)
                decompressor.start_decompress_message()
                self.assertRaises(
                    PayloadExceededError,
                    decompressor.decompress_message_data,
                    body,
                    max_output_len=64,
                )

    def test_bounded_under_limit_roundtrips(self):
        for codec in _CODECS:
            with self.subTest(codec=codec):
                pair = _make_compressor_pair(codec)
                if pair is None:
                    continue
                compressor, decompressor = pair
                body = self._compress(compressor, self.SMALL)
                decompressor.start_decompress_message()
                out = decompressor.decompress_message_data(
                    body, max_output_len=4096
                )
                self.assertEqual(out, self.SMALL)
                decompressor.end_decompress_message()

    def test_bounded_boundary_ok(self):
        # Inflated size exactly equal to max_output_len is accepted in full:
        # the limit is "strictly greater", consistent across all backends.
        payload = b"z" * 256
        for codec in _CODECS:
            with self.subTest(codec=codec):
                pair = _make_compressor_pair(codec)
                if pair is None:
                    continue
                compressor, decompressor = pair
                body = self._compress(compressor, payload)
                decompressor.start_decompress_message()
                out = decompressor.decompress_message_data(
                    body, max_output_len=len(payload)
                )
                self.assertEqual(out, payload)
                decompressor.end_decompress_message()

    def test_unbounded_default_roundtrips(self):
        for codec in _CODECS:
            with self.subTest(codec=codec):
                pair = _make_compressor_pair(codec)
                if pair is None:
                    continue
                compressor, decompressor = pair
                body = self._compress(compressor, self.BIG)
                decompressor.start_decompress_message()
                out = decompressor.decompress_message_data(body)
                self.assertEqual(out, self.BIG)
                decompressor.end_decompress_message()


class DecompressBudgetUniformTests(unittest.TestCase):
    """
    Every compression backend must enforce the ``max_output_len`` budget the
    same way (#1986): "over budget" and "budget already 0" both raise
    ``PayloadExceededError``, and the backend must stop inflating at the
    budget instead of inflating a whole frame first and checking afterwards.
    """

    BUDGET = 64 * 1024
    # A run of zeros inflates far beyond BUDGET from a few bytes on the wire
    # (except snappy, whose format caps expansion at about 21:1).
    BOMB = b"\0" * (32 * 1024 * 1024)
    # Peak allocation allowed while rejecting BOMB, on top of one copy of the
    # input (snappy buffers it): generous against BUDGET (library buffers,
    # CPython brotli's block-granular output limit, one snappy framing chunk),
    # and still a 32x margin below inflating BOMB.
    PEAK_LIMIT = 1024 * 1024

    @staticmethod
    def _compress(compressor, payload):
        compressor.start_compress_message()
        body = compressor.compress_message_data(payload)
        body += compressor.end_compress_message()
        return body

    def _pairs(self):
        for codec in _CODECS:
            pair = _make_compressor_pair(codec)
            if pair is not None:
                yield codec, pair

    def test_budget_zero_rejects(self):
        # No budget left: any further output is over budget - including a
        # single octet, which a 1-octet output cap would let through.
        for codec in _CODECS:
            for size in (1, 16):
                with self.subTest(codec=codec, size=size):
                    pair = _make_compressor_pair(codec)
                    if pair is None:
                        continue
                    compressor, decompressor = pair
                    body = self._compress(compressor, b"x" * size)
                    decompressor.start_decompress_message()
                    self.assertRaises(
                        PayloadExceededError,
                        decompressor.decompress_message_data,
                        body,
                        max_output_len=0,
                    )

    def test_one_octet_over_budget_rejects(self):
        payload = random.Random(1986).randbytes(4096)
        for codec, (compressor, decompressor) in self._pairs():
            with self.subTest(codec=codec):
                body = self._compress(compressor, payload)
                decompressor.start_decompress_message()
                self.assertRaises(
                    PayloadExceededError,
                    decompressor.decompress_message_data,
                    body,
                    max_output_len=len(payload) - 1,
                )

    def test_over_budget_across_frames_rejects(self):
        # The protocol passes the REMAINING budget for each frame of a message.
        payload = b"x" * 8192
        budget = 4096
        for codec, (compressor, decompressor) in self._pairs():
            with self.subTest(codec=codec):
                body = self._compress(compressor, payload)
                half = len(body) // 2
                decompressor.start_decompress_message()
                got = 0
                with self.assertRaises(PayloadExceededError):
                    for frame in (body[:half], body[half:]):
                        out = decompressor.decompress_message_data(
                            frame, max_output_len=budget - got
                        )
                        got += len(out)
                self.assertLessEqual(got, budget)

    @unittest.skipIf(tracemalloc is None, "tracemalloc not available (PyPy)")
    def test_bomb_inflation_bounded_by_budget(self):
        # Black-box check, independent of how a backend bounds its output:
        # rejecting an over-budget frame must not allocate the inflated frame.
        for codec, (compressor, decompressor) in self._pairs():
            with self.subTest(codec=codec):
                body = self._compress(compressor, self.BOMB)
                decompressor.start_decompress_message()
                tracemalloc.start()
                try:
                    with self.assertRaises(PayloadExceededError):
                        decompressor.decompress_message_data(
                            body, max_output_len=self.BUDGET
                        )
                    peak = tracemalloc.get_traced_memory()[1]
                finally:
                    tracemalloc.stop()
                self.assertLess(
                    peak,
                    self.PEAK_LIMIT + len(body),
                    f"{codec}: {len(body)} octets on the wire allocated "
                    f"{peak} octets against a budget of {self.BUDGET}",
                )


class DecompressCorruptInputUniformTests(unittest.TestCase):
    """
    Every compression backend must report input it cannot decompress the
    same way (#1986): as ``PayloadCorruptError``, never as the library's own
    exception (``zlib.error``, ``OSError``, ``brotli.error``, ...), and never
    by silently returning nothing.
    """

    @staticmethod
    def _compress(compressor, payload):
        compressor.start_compress_message()
        body = compressor.compress_message_data(payload)
        body += compressor.end_compress_message()
        return body

    @staticmethod
    def _decompress(decompressor, frames, max_output_len=None):
        decompressor.start_decompress_message()
        out = b"".join(
            decompressor.decompress_message_data(f, max_output_len=max_output_len)
            for f in frames
        )
        decompressor.end_decompress_message()
        return out

    def test_corrupt_input_raises_payload_corrupt(self):
        for codec in _CODECS:
            for max_output_len in (None, 1024 * 1024):
                with self.subTest(codec=codec, max_output_len=max_output_len):
                    pair = _make_compressor_pair(codec)
                    if pair is None:
                        continue
                    _, decompressor = pair
                    # raised when the data is processed, or - for a backend
                    # that buffers incomplete input (snappy) - at message end
                    self.assertRaises(
                        PayloadCorruptError,
                        self._decompress,
                        decompressor,
                        [b"\xff" * 64],
                        max_output_len,
                    )

    def test_truncated_message_raises_payload_corrupt(self):
        # bzip2, brotli and snappy send each message as complete streams or
        # chunks, so a truncated message is detectable at message end. A
        # deflate message ends with a sync flush, not a stream end, so
        # truncation is not detectable there in general.
        payload = random.Random(1986).randbytes(8192)
        for codec in ("permessage-bzip2", "permessage-brotli", "permessage-snappy"):
            for max_output_len in (None, 1024 * 1024):
                with self.subTest(codec=codec, max_output_len=max_output_len):
                    pair = _make_compressor_pair(codec)
                    if pair is None:
                        continue
                    compressor, decompressor = pair
                    body = self._compress(compressor, payload)
                    self.assertRaises(
                        PayloadCorruptError,
                        self._decompress,
                        decompressor,
                        [body[:-8]],
                        max_output_len,
                    )

    def test_split_frames_roundtrip(self):
        # A message split over two frames at any octet, also inside a snappy
        # chunk header, must decompress byte-exact.
        payload = random.Random(1986).randbytes(2 * 65536 + 123)
        for codec in _CODECS:
            pair = _make_compressor_pair(codec)
            if pair is None:
                continue
            compressor, _ = pair
            body = self._compress(compressor, payload)
            for split in (1, 3, 4, 5, 11, 12, 13, len(body) // 2, len(body) - 1):
                for max_output_len in (None, len(payload)):
                    with self.subTest(
                        codec=codec, split=split, max_output_len=max_output_len
                    ):
                        _, decompressor = _make_compressor_pair(codec)
                        out = self._decompress(
                            decompressor,
                            [body[:split], body[split:]],
                            max_output_len,
                        )
                        self.assertEqual(out, payload)


class MultiMessageRoundtripTests(unittest.TestCase):
    """
    One compressor / decompressor pair must carry any number of messages,
    with and without context takeover (the default is context takeover).
    The other tests in this module build a fresh pair per message, which
    hides a backend that cannot be reused after its first message.
    """

    def test_messages_roundtrip_on_one_pair(self):
        rng = random.Random(1986)
        payloads = [
            b"Hello, world! " * 100,
            rng.randbytes(5000),
            b"",
            b"x" * 70000,
            rng.randbytes(3),
        ]
        for codec in _CODECS:
            for no_context_takeover in (False, True):
                for max_output_len in (None, 1024 * 1024):
                    with self.subTest(
                        codec=codec,
                        no_context_takeover=no_context_takeover,
                        max_output_len=max_output_len,
                    ):
                        pair = _make_compressor_pair(codec, no_context_takeover)
                        if pair is None:
                            continue
                        compressor, decompressor = pair
                        for i, payload in enumerate(payloads):
                            body = DecompressCorruptInputUniformTests._compress(
                                compressor, payload
                            )
                            out = DecompressCorruptInputUniformTests._decompress(
                                decompressor, [body], max_output_len
                            )
                            self.assertEqual(out, payload, f"message {i}")


class PerMessageDeflateMaxMessageSizeTests(unittest.TestCase):
    """
    The permessage-deflate extension-level ``max_message_size`` cap (relocated
    here from test_websocket_frame.py so it runs under both backends). This is
    the deflate-negotiated whole-message cap; ``max_output_len`` above is the
    per-call cap the protocol layer passes.
    """

    @staticmethod
    def _decoder(max_message_size=None):
        return PerMessageDeflate(
            is_server=False,
            server_no_context_takeover=False,
            client_no_context_takeover=False,
            server_max_window_bits=15,
            client_max_window_bits=15,
            mem_level=8,
            max_message_size=max_message_size,
        )

    @staticmethod
    def _compress(payload, window_bits=15):
        # Produce the permessage-deflate wire body for `payload`: raw
        # DEFLATE, Z_SYNC_FLUSH, with the trailing 0x00 0x00 0xff 0xff
        # stripped (mirrors PerMessageDeflate.end_compress_message()).
        compressor = zlib.compressobj(
            zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -window_bits
        )
        return (
            compressor.compress(payload) + compressor.flush(zlib.Z_SYNC_FLUSH)
        )[:-4]

    def test_max_size_rejects_oversized(self):
        # A message that inflates beyond max_message_size must be rejected
        # cleanly (PayloadExceededError), NOT silently truncated to the cap.
        decoder = self._decoder(max_message_size=10)
        body = self._compress(b"x" * 2000)
        decoder.start_decompress_message()
        self.assertRaises(
            PayloadExceededError, decoder.decompress_message_data, body
        )

    def test_max_size_boundary_ok(self):
        # A message whose inflated size is exactly max_message_size is
        # accepted and returned in full (the limit is "strictly greater").
        decoder = self._decoder(max_message_size=2000)
        body = self._compress(b"x" * 2000)
        decoder.start_decompress_message()
        data = decoder.decompress_message_data(body)
        self.assertEqual(data, b"x" * 2000)

    def test_under_max_size_roundtrips_without_corruption(self):
        # Under the cap: full data returned AND end_decompress_message()
        # must not raise. The old truncation left the stream mid-token,
        # so the sync-flush trailer raised zlib error -3.
        decoder = self._decoder(max_message_size=2000)
        payload = b"x" * 1000
        body = self._compress(payload)
        decoder.start_decompress_message()
        data = decoder.decompress_message_data(body)
        self.assertEqual(data, payload)
        decoder.end_decompress_message()

    def test_max_size_cumulative_across_frames(self):
        # The cap bounds the whole message, not each frame: a message
        # delivered in two frame-sized chunks whose combined inflated size
        # exceeds the cap must be rejected, not truncated.
        decoder = self._decoder(max_message_size=1500)
        body = self._compress(b"x" * 2000)
        half = len(body) // 2
        decoder.start_decompress_message()

        def feed_both():
            decoder.decompress_message_data(body[:half])
            decoder.decompress_message_data(body[half:])

        self.assertRaises(PayloadExceededError, feed_both)

    def test_no_max_size(self):
        decoder = self._decoder(max_message_size=None)
        body = self._compress(b"x" * 2000)
        decoder.start_decompress_message()
        data = decoder.decompress_message_data(body)
        self.assertEqual(data, b"x" * 2000)
