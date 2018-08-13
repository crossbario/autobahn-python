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

import os
import unittest
import six

from autobahn.wamp import message
from autobahn.wamp import role
from autobahn.wamp import serializer


# FIXME: autobahn.wamp.serializer.JsonObjectSerializer uses a patched JSON
# encoder/decoder - however, the patching currently only works on Python 3!
def must_skip(ser, contains_binary):
    if contains_binary and ser.SERIALIZER_ID.startswith(u'json') and six.PY2:
        return True
    else:
        return False


def generate_test_messages():
    """
    List of WAMP test message used for serializers. Expand this if you add more
    options or messages.

    This list of WAMP message does not contain any binary app payloads!
    """
    msgs = [
        message.Hello(u"realm1", {u'subscriber': role.RoleSubscriberFeatures()}),
        message.Goodbye(),
        message.Yield(123456),
        message.Yield(123456, args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'}),
        message.Yield(123456, args=[u'hello']),
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
        message.Publish(123456, u'com.myapp.topic1', exclude_me=False, exclude=[300], eligible=[100, 200, 300]),
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
    return [(False, msg) for msg in msgs]


def generate_test_messages_binary():
    """
    Generate WAMP test messages which contain binary app payloads.

    With the JSON serializer, this currently only works on Python 3 (both CPython3 and PyPy3),
    because even on Python 3, we need to patch the stdlib JSON, and on Python 2, the patching
    would be even hackier.
    """
    msgs = []
    for binary in [b'',
                   b'\x00',
                   b'\30',
                   os.urandom(4),
                   os.urandom(16),
                   os.urandom(128),
                   os.urandom(256),
                   os.urandom(512),
                   os.urandom(1024)]:
        msgs.append(message.Event(123456, 789123, args=[binary]))
        msgs.append(message.Event(123456, 789123, args=[binary], kwargs={u'foo': binary}))
    return [(True, msg) for msg in msgs]


class TestSerializer(unittest.TestCase):

    def setUp(self):
        self._test_messages = generate_test_messages() + generate_test_messages_binary()

        self._test_serializers = []

        # JSON serializer is always available
        self._test_serializers.append(serializer.JsonSerializer())
        self._test_serializers.append(serializer.JsonSerializer(batched=True))

        # MsgPack serializer is optional
        if hasattr(serializer, 'MsgPackSerializer'):
            self._test_serializers.append(serializer.MsgPackSerializer())
            self._test_serializers.append(serializer.MsgPackSerializer(batched=True))

        # CBOR serializer is optional
        if hasattr(serializer, 'CBORSerializer'):
            self._test_serializers.append(serializer.CBORSerializer())
            self._test_serializers.append(serializer.CBORSerializer(batched=True))

        # UBJSON serializer is optional
        if hasattr(serializer, 'UBJSONSerializer'):
            self._test_serializers.append(serializer.UBJSONSerializer())
            self._test_serializers.append(serializer.UBJSONSerializer(batched=True))

        print('Testing WAMP serializers {} with {} WAMP test messages'.format([ser.SERIALIZER_ID for ser in self._test_serializers], len(self._test_messages)))

    def test_deep_equal(self):
        """
        Test deep object equality assert (because I am paranoid).
        """
        v = os.urandom(10)
        o1 = [1, 2, {u'foo': u'bar', u'bar': v, u'baz': [9, 3, 2], u'goo': {u'moo': [1, 2, 3]}}, v]
        o2 = [1, 2, {u'goo': {u'moo': [1, 2, 3]}, u'bar': v, u'baz': [9, 3, 2], u'foo': u'bar'}, v]
        self.assertEqual(o1, o2)

    def test_roundtrip(self):
        """
        Test round-tripping over each serializer.
        """
        for ser in self._test_serializers:

            for contains_binary, msg in self._test_messages:

                if not must_skip(ser, contains_binary):
                    # serialize message
                    payload, binary = ser.serialize(msg)

                    # unserialize message again
                    msg2 = ser.unserialize(payload, binary)

                    # must be equal: message roundtrips via the serializer
                    self.assertEqual([msg], msg2)

    def test_crosstrip(self):
        """
        Test cross-tripping over 2 serializers (as is done by WAMP routers).
        """
        for ser1 in self._test_serializers:

            for contains_binary, msg in self._test_messages:

                if not must_skip(ser1, contains_binary):
                    # serialize message
                    payload, binary = ser1.serialize(msg)

                    # unserialize message again
                    msg1 = ser1.unserialize(payload, binary)
                    msg1 = msg1[0]

                    for ser2 in self._test_serializers:

                        if not must_skip(ser2, contains_binary):
                            # serialize message
                            payload, binary = ser2.serialize(msg1)

                            # unserialize message again
                            msg2 = ser2.unserialize(payload, binary)

                            # must be equal: message crosstrips via
                            # the serializers ser1 -> ser2
                            self.assertEqual([msg], msg2)

    def test_caching(self):
        """
        Test message serialization caching.
        """
        for contains_binary, msg in self._test_messages:

            # message serialization cache is initially empty
            self.assertEqual(msg._serialized, {})

            for ser in self._test_serializers:

                if not must_skip(ser, contains_binary):

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
