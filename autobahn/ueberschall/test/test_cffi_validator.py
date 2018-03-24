###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
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

from __future__ import absolute_import

from txaio import use_twisted
use_twisted()

from cffi import FFI


class Utf8ValidatorCFFI:
    def __init__(self, ffi):
        self._ffi = ffi
        self._vld = ffi.gc(ffi.ueberschall.ueberschall_utf8vld_new(),
                           ffi.ueberschall.ueberschall_utf8vld_free)
        self.reset()

    def reset(self):
        self._ffi.ueberschall.ueberschall_utf8vld_reset(self._vld)

    def validate(self, ba):
        res = self._ffi.ueberschall.ueberschall_utf8vld_validate(
            self._vld, ba, len(ba))
        return res >= 0, \
            res == 0, \
            None, \
            None


from case6_x_x import test_utf8, test_utf8_incremental
from autobahn.websocket.utf8validator import Utf8Validator


import time
import gc


def test_gc(ffi):
    validator = Utf8ValidatorCFFI(ffi)

    print("1")
    time.sleep(1)
    validator = None
    print("2")
    time.sleep(1)
    gc.collect()
    print("3")
    time.sleep(1)


def test_testsuite(ffi):
    validator = Utf8ValidatorCFFI(ffi)
    test_utf8(validator)
    test_utf8_incremental(validator, withPositions=True)


def test_unaligned(ffi):
    validator = Utf8ValidatorCFFI(ffi)
    s = b"*" * 32
    res = validator.validate(s)
    print(res)


if __name__ == '__main__':

    ffi = FFI()

    ffi.cdef("""
      void* ueberschall_utf8vld_new ();
      void ueberschall_utf8vld_reset (void* utf8vld);
      int ueberschall_utf8vld_validate (void* utf8vld, const uint8_t* data, size_t length);
      void ueberschall_utf8vld_free (void* utf8vld);
   """)

    DLNAME = 'libueberschall.so'
    DLNAME = '_ueberschall_validator.abi3.so'

    ffi.ueberschall = ffi.dlopen(DLNAME)

    #validator = Utf8Validator()
    #validator = Utf8ValidatorCFFI(ffi)

    test_unaligned(ffi)
