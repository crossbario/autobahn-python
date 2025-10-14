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

from cffi import FFI

ffi = FFI()

ffi.cdef(
    """
    void* nvx_utf8vld_new ();

    void nvx_utf8vld_reset (void* utf8vld);

    int nvx_utf8vld_validate (void* utf8vld, const uint8_t* data, size_t length);

    void nvx_utf8vld_free (void* utf8vld);

    int nvx_utf8vld_set_impl(void* utf8vld, int impl);

    int nvx_utf8vld_get_impl(void* utf8vld);

    size_t nvx_utf8vld_get_current_index (void* utf8vld);

    size_t nvx_utf8vld_get_total_index (void* utf8vld);
"""
)

if "AUTOBAHN_USE_NVX" in os.environ and os.environ["AUTOBAHN_USE_NVX"] in ["1", "true"]:
    optional = False  # :noindex:
else:
    optional = True  # :noindex:

# Detect platform/compiler and set flags
if sys.platform == "win32":
    # MSVC
    extra_compile_args = ["/O2", "/W3"]
else:
    # GCC/clang
    extra_compile_args = [
        "-std=c99",
        "-Wall",
        "-Wno-strict-prototypes",
        "-O3",
        "-march=native",
    ]

with open(os.path.join(os.path.dirname(__file__), "_utf8validator.c")) as fd:
    c_source = fd.read()
    ffi.set_source(
        "_nvx_utf8validator",
        c_source,
        libraries=[],
        extra_compile_args=extra_compile_args,
        optional=optional,
    )


class Utf8Validator:
    """
    :noindex:
    """

    def __init__(self):
        self.ffi = ffi

        from _nvx_utf8validator import lib

        self.lib = lib

        self._vld = self.ffi.gc(self.lib.nvx_utf8vld_new(), self.lib.nvx_utf8vld_free)
        # print(self.lib.nvx_utf8vld_get_impl(self._vld))

    def reset(self):
        self.lib.nvx_utf8vld_reset(self._vld)

    def validate(self, ba):
        res = self.lib.nvx_utf8vld_validate(self._vld, ba, len(ba))
        current_index = self.lib.nvx_utf8vld_get_current_index(self._vld)
        total_index = self.lib.nvx_utf8vld_get_total_index(self._vld)
        return (res >= 0, res == 0, current_index, total_index)


if __name__ == "__main__":
    ffi.compile()
