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

from __future__ import absolute_import

# from twisted.trial import unittest
import decimal
import unittest
import datetime

import six

from autobahn.wamp import message
from autobahn.wamp import role
from autobahn.wamp import serializer


def generate_test_messages():
    return [
        message.Hello(u"realm1", {u'subscriber': role.RoleSubscriberFeatures()}),
        message.Goodbye(),
        message.Yield(123456),
        message.Yield(123456, args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'}),
        message.Yield(123456, progress=True),
        message.Interrupt(123456),
        message.Interrupt(123456, mode=message.Interrupt.KILL),
        message.Invocation(123456, 789123),
        message.Invocation(123456, 789123, args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'}),
        message.Invocation(123456, 789123, timeout=10000),
        message.Result(123456),
        message.Result(123456, args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'}),
        message.Result(123456, progress=True),
        message.Cancel(123456),
        message.Cancel(123456, mode=message.Cancel.KILL),
        message.Call(123456, u'com.myapp.procedure1'),
        message.Call(123456, u'com.myapp.procedure1', args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'}),
        message.Call(123456, u'com.myapp.procedure1', timeout=10000),
        message.Unregistered(123456),
        message.Unregister(123456, 789123),
        message.Registered(123456, 789123),
        message.Register(123456, u'com.myapp.procedure1'),
        message.Register(123456, u'com.myapp.procedure1', match=u'prefix'),
        message.Register(123456, u'com.myapp.procedure1', invoke=u'roundrobin'),
        message.Event(123456, 789123),
        message.Event(123456, 789123, args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'}),
        message.Event(123456, 789123, publisher=300),
        message.Published(123456, 789123),
        message.Publish(123456, u'com.myapp.topic1'),
        message.Publish(123456, u'com.myapp.topic1', args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'}),
        message.Publish(123456, u'com.myapp.topic1', exclude_me=False, exclude=[300], eligible=[100, 200, 300], disclose_me=True),
        message.Unsubscribed(123456),
        message.Unsubscribe(123456, 789123),
        message.Subscribed(123456, 789123),
        message.Subscribe(123456, u'com.myapp.topic1'),
        message.Subscribe(123456, u'com.myapp.topic1', match=message.Subscribe.MATCH_PREFIX),
        message.Error(message.Call.MESSAGE_TYPE, 123456, u'com.myapp.error1'),
        message.Error(message.Call.MESSAGE_TYPE, 123456, u'com.myapp.error1', args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'}),
        message.Call(123456, u'com.myapp.\u4f60\u597d\u4e16\u754c', args=[1, 2, 3]),
        message.Result(123456, args=[1, 2, 3], kwargs={u'en': u'Hello World', u'jp': u'\u3053\u3093\u306b\u3061\u306f\u4e16\u754c'})
    ]


def generate_test_messages_with_custom_types():
    return [
        message.Yield(datetime.datetime(2015, 3, 22, 8, 23, 17), args=[
            datetime.date(2015, 3, 22), decimal.Decimal('27.012')
        ]),
        message.Yield(datetime.datetime(2015, 3, 22, 8, 23, 17), datetime.date(2015, 3, 22))
    ]


class TestSerializer(unittest.TestCase):

    def setUp(self):
        self.serializers = []

        # JSON serializer is always available
        self.serializers.append(serializer.JsonSerializer())
        self.serializers.append(serializer.JsonSerializer(batched=True))

        # MsgPack serializers are optional
        if hasattr(serializer, 'MsgPackSerializer'):
            self.serializers.append(serializer.MsgPackSerializer())
            self.serializers.append(serializer.MsgPackSerializer(batched=True))

    def test_roundtrip(self):
        for msg in generate_test_messages():
            for ser in self.serializers:

                # serialize message
                payload, binary = ser.serialize(msg)

                # unserialize message again
                msg2 = ser.unserialize(payload, binary)

                # must be equal: message roundtrips via the serializer
                self.assertEqual([msg], msg2)

    def test_caching(self):
        for msg in generate_test_messages():
            # message serialization cache is initially empty
            self.assertEqual(msg._serialized, {})
            for ser in self.serializers:

                # verify message serialization is not yet cached
                self.assertFalse(ser._serializer in msg._serialized)
                payload, binary = ser.serialize(msg)

                # now the message serialization must be cached
                self.assertTrue(ser._serializer in msg._serialized)
                self.assertEqual(msg._serialized[ser._serializer], payload)

                # and after resetting the serialization cache, message
                # serialization is gone
                msg.uncache()
                self.assertFalse(ser._serializer in msg._serialized)


if hasattr(serializer, 'MsgPackSerializer'):
    from msgpack import ExtType

    class TestMsgpackCustomTypes(unittest.TestCase):

        @staticmethod
        def default(obj):
            if isinstance(obj, datetime.datetime):
                return ExtType(1, obj.strftime(u"%Y%m%dT%H:%M:%S.%f").encode())
            if isinstance(obj, datetime.date):
                return ExtType(2, obj.strftime(u"%Y%m%d").encode())
            if isinstance(obj, decimal.Decimal):
                return ExtType(3, six.text_type(obj).encode())
            raise TypeError("Cannot serialize type %s" % obj.__class__.__name__)

        @staticmethod
        def ext_hook(code, data):
            if code == 1:
                return datetime.datetime.strptime(data.decode(), "%Y%m%dT%H:%M:%S.%f")
            if code == 2:
                return datetime.datetime.strptime(data.decode(), "%Y%m%d").date()
            if code == 3:
                return decimal.Decimal(data.decode())
            raise TypeError("Unknown type code %d" % code)

        def setUp(self):
            pack_kwargs = {'default': self.default}
            unpack_kwargs = {'ext_hook': self.ext_hook}
            self.serializers = [serializer.MsgPackSerializer(pack_kwargs=pack_kwargs,
                                                             unpack_kwargs=unpack_kwargs),
                                serializer.MsgPackSerializer(batched=True, pack_kwargs=pack_kwargs,
                                                             unpack_kwargs=unpack_kwargs)]

        def test_roundtrip(self):
            msg = message.Yield(123456, args=[
                datetime.datetime(2015, 3, 22, 8, 23, 17), datetime.date(2015, 3, 22),
                decimal.Decimal('27.012')
            ])

            for ser in self.serializers:
                # serialize message
                payload, binary = ser.serialize(msg)

                # unserialize message again
                msg2 = ser.unserialize(payload, binary)

                # must be equal: message roundtrips via the serializer
                self.assertEqual([msg], msg2)


if __name__ == '__main__':
    unittest.main()
