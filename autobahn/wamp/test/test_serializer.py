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

import unittest2 as unittest
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
        message.Register(123456, u'com.myapp.procedure1', invoke=u'balance'),
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


class TestSerializer(unittest.TestCase):

    def setUp(self):
        self.serializers = []

        # JSON serializer is always available
        self.serializers.append(serializer.JsonSerializer())
        self.serializers.append(serializer.JsonSerializer(batched=True))

        # MsgPack serializer is optional
        if hasattr(serializer, 'MsgPackSerializer'):
            self.serializers.append(serializer.MsgPackSerializer())
            self.serializers.append(serializer.MsgPackSerializer(batched=True))

        # CBOR serializer is optional
        if hasattr(serializer, 'CBORSerializer'):
            self.serializers.append(serializer.CBORSerializer())
            self.serializers.append(serializer.CBORSerializer(batched=True))

    def test_dict_keys_msgpack(self):
        """
        dict keys should always be strings. the data provided is from
        calling msgpack encode on a dict in python2 with
        `use_bin_type=True` and the following message:

            print(ser.serialize(
                message.Call(
                    123456, u"com.myapp.procedure1",
                    args=(),
                    kwargs={u'unicode': 23, 'str': 42}
                )
            ))
        """

        if not hasattr(serializer, 'MsgPackSerializer'):
            self.skipTest("no msgpack")

        ser = serializer.MsgPackSerializer()
        payload = b'\x960\xce\x00\x01\xe2@\x80\xb4com.myapp.procedure1\x90\x82\xc4\x03str*\xa7unicode\x17'
        msg_out = ser.unserialize(payload, True)[0]

        for k in msg_out.kwargs.keys():
            self.assertEqual(type(k), six.text_type)
        self.assertTrue('str' in msg_out.kwargs)
        self.assertTrue('unicode' in msg_out.kwargs)

    def test_dict_keys_msgpack_batched(self):
        """
        dict keys should always be strings. the data provided is from
        calling msgpack encode on a dict in python2 with
        `use_bin_type=True`
        """
        if not hasattr(serializer, 'MsgPackSerializer'):
            self.skipTest("no msgpack")

        ser = serializer.MsgPackSerializer(batched=True)
        payload = b'\x00\x00\x00-\x960\xce\x00\x01\xe2@\x80\xb4com.myapp.procedure1\x90\x82\xa7unicode\x17\xa3str*'
        msg_out = ser.unserialize(payload, True)[0]
        for k in msg_out.kwargs.keys():
            self.assertEqual(type(k), six.text_type)
        self.assertTrue('str' in msg_out.kwargs)
        self.assertTrue('unicode' in msg_out.kwargs)

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
