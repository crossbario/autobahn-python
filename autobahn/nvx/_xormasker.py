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

import os

from cffi import FFI

# Try normal import first (works when package is installed or in editable mode)
try:
    from autobahn.nvx._compile_args import get_compile_args
except ImportError:
    # Fallback for CFFI build time (before package installation)
    # CFFI's setuptools integration runs builder modules via execfile() outside
    # of package context, so normal imports fail. Use importlib to dynamically
    # load the module from file path as a workaround.
    import importlib.util
    import sys

    _path = os.path.join(os.path.dirname(__file__), "_compile_args.py")
    spec = importlib.util.spec_from_file_location("autobahn.nvx._compile_args", _path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    get_compile_args = mod.get_compile_args

ffi = FFI()

ffi.cdef(
    """
    void* nvx_xormask_new (const uint8_t* mask);

    void nvx_xormask_reset (void* xormask);

    size_t nvx_xormask_pointer (void* xormask);

    void nvx_xormask_process (void* xormask, uint8_t* data, size_t length);

    void nvx_xormask_free (void* xormask);

    int nvx_xormask_set_impl(void* xormask, int impl);

    int nvx_xormask_get_impl(void* xormask);
"""
)

if "AUTOBAHN_USE_NVX" in os.environ and os.environ["AUTOBAHN_USE_NVX"] in ["1", "true"]:
    optional = False  # :noindex:
else:
    optional = True  # :noindex:

# Get appropriate compiler flags for this build context
# See autobahn.nvx._compile_args for details on architecture baseline selection
# and build context detection (wheel distribution vs. local source install)
extra_compile_args = get_compile_args()

with open(os.path.join(os.path.dirname(__file__), "_xormasker.c")) as fd:
    c_source = fd.read()
    ffi.set_source(
        "_nvx_xormasker",
        c_source,
        libraries=[],
        extra_compile_args=extra_compile_args,
        optional=optional,
    )


class XorMaskerNvx:
    """
    XOR masker using native NVX acceleration.
    :noindex:
    """

    __slots__ = ("ffi", "lib", "_masker", "_mask_buffer")

    def __init__(self, mask, use_simd=True):
        assert len(mask) == 4, "Mask must be exactly 4 bytes"

        from _nvx_xormasker import ffi as _ffi, lib as _lib

        self.ffi = _ffi
        self.lib = _lib

        # Keep mask buffer alive for the lifetime of the masker
        self._mask_buffer = self.ffi.new("uint8_t[4]", mask)
        self._masker = self.ffi.gc(
            self.lib.nvx_xormask_new(self._mask_buffer), self.lib.nvx_xormask_free
        )

        # Set implementation: 1=Simple (scalar), 2=SSE2 (SIMD)
        if use_simd:
            self.lib.nvx_xormask_set_impl(self._masker, 2)  # XOR_MASKER_SSE2
        else:
            self.lib.nvx_xormask_set_impl(self._masker, 1)  # XOR_MASKER_SIMPLE

    def pointer(self):
        return self.lib.nvx_xormask_pointer(self._masker)

    def reset(self):
        self.lib.nvx_xormask_reset(self._masker)

    def process(self, data):
        # Create a mutable copy of the data
        data_len = len(data)
        data_buffer = self.ffi.new("uint8_t[]", data_len)
        self.ffi.memmove(data_buffer, data, data_len)

        # Process in-place
        self.lib.nvx_xormask_process(self._masker, data_buffer, data_len)

        # Convert back to bytes
        return bytes(self.ffi.buffer(data_buffer, data_len))


class XorMaskerSimple(XorMaskerNvx):
    """
    Simple scalar XOR masker for small payloads.
    :noindex:
    """

    def __init__(self, mask):
        super().__init__(mask, use_simd=False)


class XorMaskerShifted1(XorMaskerNvx):
    """
    SIMD-optimized XOR masker for large payloads.
    :noindex:
    """

    def __init__(self, mask):
        super().__init__(mask, use_simd=True)


def create_xor_masker(mask, length=None):
    """
    Factory function to create XOR masker with optimal implementation.

    :param mask: 4-byte masking key
    :param length: Payload length hint - uses scalar for < 128 bytes, SIMD for >= 128
    :return: XorMaskerSimple or XorMaskerShifted1 instance
    """
    if length is None or length < 128:
        return XorMaskerSimple(mask)
    else:
        return XorMaskerShifted1(mask)


if __name__ == "__main__":
    ffi.compile()
