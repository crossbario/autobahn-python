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


# XorMaskerNull: pass-through implementation (no masking applied)
# Shared by all implementations (NVX, pure Python)
class XorMaskerNull(object):
    __slots__ = ("_ptr",)

    # noinspection PyUnusedLocal
    def __init__(self, mask=None):
        self._ptr = 0

    def pointer(self):
        return self._ptr

    def reset(self):
        self._ptr = 0

    def process(self, data):
        self._ptr += len(data)
        return data


# Import USES_NVX flag from parent module
from autobahn.websocket import USES_NVX

if USES_NVX:
    # Use NVX native implementation (CFFI-based, works on CPython and PyPy)
    from autobahn.nvx._xormasker import create_xor_masker
else:
    # Use pure Python fallback implementation

    # http://stackoverflow.com/questions/15014310/python3-xrange-lack-hurts
    try:
        # noinspection PyUnresolvedReferences
        xrange
    except NameError:
        # Python 3
        # noinspection PyShadowingBuiltins
        xrange = range

    from array import array

    class XorMaskerSimple(object):
        __slots__ = ("_ptr", "_msk")

        def __init__(self, mask):
            assert len(mask) == 4
            self._ptr = 0
            self._msk = array("B", mask)

        def pointer(self):
            return self._ptr

        def reset(self):
            self._ptr = 0

        def process(self, data):
            dlen = len(data)
            payload = array("B", data)
            for k in xrange(dlen):
                payload[k] ^= self._msk[self._ptr & 3]
                self._ptr += 1
            return payload.tobytes()

    class XorMaskerShifted1(object):
        __slots__ = ("_ptr", "_mskarray")

        def __init__(self, mask):
            assert len(mask) == 4
            self._ptr = 0
            self._mskarray = [array("B"), array("B"), array("B"), array("B")]
            for j in xrange(4):
                self._mskarray[0].append(mask[j & 3])
                self._mskarray[1].append(mask[(j + 1) & 3])
                self._mskarray[2].append(mask[(j + 2) & 3])
                self._mskarray[3].append(mask[(j + 3) & 3])

        def pointer(self):
            return self._ptr

        def reset(self):
            self._ptr = 0

        def process(self, data):
            dlen = len(data)
            payload = array("B", data)
            msk = self._mskarray[self._ptr & 3]
            for k in xrange(dlen):
                payload[k] ^= msk[k & 3]
            self._ptr += dlen
            return payload.tobytes()

    def create_xor_masker(mask, length=None):
        if length is None or length < 128:
            return XorMaskerSimple(mask)
        else:
            return XorMaskerShifted1(mask)
