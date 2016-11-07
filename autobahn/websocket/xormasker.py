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

import six


# use Cython implementation of XorMasker validator if available
##
try:
    from wsaccel.xormask import XorMaskerNull, createXorMasker

except ImportError:
    # fallback to pure Python implementation

    # http://stackoverflow.com/questions/15014310/python3-xrange-lack-hurts
    try:
        xrange
    except NameError:
        # Python 3
        # noinspection PyShadowingBuiltins
        xrange = range

    from array import array

    class XorMaskerNull(object):

        # noinspection PyUnusedLocal
        def __init__(self, mask=None):
            self.ptr = 0

        def pointer(self):
            return self.ptr

        def reset(self):
            self.ptr = 0

        def process(self, data):
            self.ptr += len(data)
            return data

    class XorMaskerSimple(object):

        def __init__(self, mask):
            assert len(mask) == 4
            self.ptr = 0
            self.msk = array('B', mask)

        def pointer(self):
            return self.ptr

        def reset(self):
            self.ptr = 0

        def process(self, data):
            dlen = len(data)
            payload = array('B', data)
            for k in xrange(dlen):
                payload[k] ^= self.msk[self.ptr & 3]
                self.ptr += 1
            if six.PY3:
                return payload.tobytes()
            else:
                return payload.tostring()

    class XorMaskerShifted1(object):

        def __init__(self, mask):
            assert len(mask) == 4
            self.ptr = 0
            self.mskarray = [array('B'), array('B'), array('B'), array('B')]
            if six.PY3:
                for j in xrange(4):
                    self.mskarray[0].append(mask[j & 3])
                    self.mskarray[1].append(mask[(j + 1) & 3])
                    self.mskarray[2].append(mask[(j + 2) & 3])
                    self.mskarray[3].append(mask[(j + 3) & 3])
            else:
                for j in xrange(4):
                    self.mskarray[0].append(ord(mask[j & 3]))
                    self.mskarray[1].append(ord(mask[(j + 1) & 3]))
                    self.mskarray[2].append(ord(mask[(j + 2) & 3]))
                    self.mskarray[3].append(ord(mask[(j + 3) & 3]))

        def pointer(self):
            return self.ptr

        def reset(self):
            self.ptr = 0

        def process(self, data):
            dlen = len(data)
            payload = array('B', data)
            msk = self.mskarray[self.ptr & 3]
            for k in xrange(dlen):
                payload[k] ^= msk[k & 3]
            self.ptr += dlen
            if six.PY3:
                return payload.tobytes()
            else:
                return payload.tostring()

    def createXorMasker(mask, length=None):
        if length is None or length < 128:
            return XorMaskerSimple(mask)
        else:
            return XorMaskerShifted1(mask)
