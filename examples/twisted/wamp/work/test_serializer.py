###############################################################################
##
# Copyright (C) 2013 Tavendo GmbH
##
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
##
# http://www.apache.org/licenses/LICENSE-2.0
##
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##
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
