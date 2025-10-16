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
import sys
import platform

from cffi import FFI

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

# Detect platform/compiler and set flags
#
# IMPORTANT: Architecture baseline selection (fixes #1717)
#
# We DO NOT use -march=native because it creates CPU-specific binaries
# that crash with SIGILL on older CPUs lacking the instructions used at
# build time. Instead, we target safe "modern" baselines:
#
# For x86-64:
#   -march=x86-64-v2 (microarchitecture level 2, 2009+)
#   Includes: SSE4.2, POPCNT, SSSE3, SSE4.1
#   Compatible with: Intel Nehalem+, AMD Bulldozer+ (2009+)
#   Coverage: ~99% of x86-64 CPUs from 2010 onwards
#
# For ARM64:
#   -march=armv8-a (baseline ARMv8-A architecture)
#   Compatible with: Raspberry Pi 4/5, AWS Graviton, Apple M1/M2, etc.
#   Coverage: All 64-bit ARM CPUs
#
# This provides good SIMD acceleration (current C code uses SSE2 on x86-64)
# while maintaining broad compatibility. Future enhancements can add AVX2
# with runtime CPU detection.
#
if sys.platform == "win32":
    # MSVC on Windows
    extra_compile_args = ["/O2", "/W3"]
else:
    # GCC/Clang on POSIX (Linux, macOS, *BSD)
    machine = platform.machine().lower()

    # Base flags for all POSIX platforms
    extra_compile_args = [
        "-std=c99",
        "-Wall",
        "-Wno-strict-prototypes",
        "-O3",
    ]

    # Architecture-specific optimization flags
    if machine in ("x86_64", "amd64", "x64"):
        # x86-64: Use microarchitecture level 2 (2009+ CPUs)
        extra_compile_args.append("-march=x86-64-v2")
    elif machine in ("aarch64", "arm64"):
        # ARM64: Use ARMv8-A baseline (all 64-bit ARM)
        extra_compile_args.append("-march=armv8-a")
    else:
        # Unknown architecture: let compiler use safe defaults
        # (no -march flag = generic code for the architecture)
        pass

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
            self.lib.nvx_xormask_new(self._mask_buffer),
            self.lib.nvx_xormask_free
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
