###############################################################################
#
# The MIT License (MIT)
# 
# Copyright (c) Tavendo GmbH
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

import binascii

from autobahn.util import newid
from autobahn.wamp2.serializer import JsonSerializer, MsgPackSerializer, WampSerializer
from autobahn.wamp2.message import *


if __name__ == '__main__':
    serializers = [WampSerializer(JsonSerializer()), WampSerializer(MsgPackSerializer())]
    totals = {}

    EVENT1 = ["Hello, world!", 0.123456789, {'foo': 23, 'bar': 'baz', 'moo': True}, [True, True, False]]
    msgs = [
        WampMessagePublish("http://myapp.com/topic1", EVENT1),
        WampMessagePublish("http://myapp.com/topic1", EVENT1, excludeMe=False),
        WampMessagePublish("http://myapp.com/topic1", EVENT1, eligible=[newid(), newid(), newid()]),
        WampMessagePublish("http://myapp.com/topic1", EVENT1, discloseMe=True, excludeMe=True, exclude=[newid()]),
    ]

    for msg_out in msgs:
        for ser in serializers:

            bytes, isbinary = ser.serialize(msg_out)

            if ser._serializer not in totals:
                totals[ser._serializer] = 0

            totals[ser._serializer] += len(bytes)

            if isbinary:
                print len(bytes), binascii.hexlify(bytes)
            else:
                print len(bytes), bytes

            msg_in = ser.unserialize(bytes, isbinary)
            print msg_in
            print
            assert(msg_in == msg_out)

    for k, v in totals.items():
        print k, v
