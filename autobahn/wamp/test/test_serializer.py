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

import os
import unittest
import txaio

if os.environ.get('USE_TWISTED', False):
    txaio.use_twisted()
elif os.environ.get('USE_ASYNCIO', False):
    txaio.use_asyncio()

from autobahn.wamp import message
from autobahn.wamp import role
from autobahn.wamp import serializer


def generate_test_messages():
    """
    List of WAMP test message used for serializers. Expand this if you add more
    options or messages.

    This list of WAMP message does not contain any binary app payloads!
    """
    some_bytes = os.urandom(32)
    some_unicode = '\u3053\u3093\u306b\u3061\u306f\u4e16\u754c'

    some_uri = 'com.myapp.foobar'
    some_unicode_uri = 'com.myapp.\u4f60\u597d\u4e16\u754c.baz'

    some_args = [1, 2, 3, 'hello', some_bytes, some_unicode, {'foo': 23, 'bar': 'hello', 'baz': some_bytes, 'moo': some_unicode}]
    some_kwargs = {'foo': 23, 'bar': 'hello', 'baz': some_bytes, 'moo': some_unicode, 'arr': some_args}

    msgs = [
        message.Hello("realm1", {'subscriber': role.RoleSubscriberFeatures()}),
        message.Hello("realm1", {'publisher': role.RolePublisherFeatures()}),
        message.Hello("realm1", {'caller': role.RoleCallerFeatures()}),
        message.Hello("realm1", {'callee': role.RoleCalleeFeatures()}),
        message.Hello("realm1", {
            'subscriber': role.RoleSubscriberFeatures(),
            'publisher': role.RolePublisherFeatures(),
            'caller': role.RoleCallerFeatures(),
            'callee': role.RoleCalleeFeatures(),
        }),
        message.Goodbye(),
        message.Yield(123456),
        message.Yield(123456, args=some_args),
        message.Yield(123456, args=[], kwargs=some_kwargs),
        message.Yield(123456, args=some_args, kwargs=some_kwargs),
        message.Yield(123456, progress=True),
        message.Interrupt(123456),
        message.Interrupt(123456, mode=message.Interrupt.KILL),
        message.Invocation(123456, 789123),
        message.Invocation(123456, 789123, args=some_args),
        message.Invocation(123456, 789123, args=[], kwargs=some_kwargs),
        message.Invocation(123456, 789123, args=some_args, kwargs=some_kwargs),
        message.Invocation(123456, 789123, timeout=10000),
        message.Result(123456),
        message.Result(123456, args=some_args),
        message.Result(123456, args=[], kwargs=some_kwargs),
        message.Result(123456, args=some_args, kwargs=some_kwargs),
        message.Result(123456, progress=True),
        message.Cancel(123456),
        message.Cancel(123456, mode=message.Cancel.KILL),
        message.Call(123456, some_uri),
        message.Call(123456, some_uri, args=some_args),
        message.Call(123456, some_uri, args=[], kwargs=some_kwargs),
        message.Call(123456, some_uri, args=some_args, kwargs=some_kwargs),
        message.Call(123456, some_uri, timeout=10000),
        message.Call(123456, some_unicode_uri),
        message.Call(123456, some_unicode_uri, args=some_args),
        message.Call(123456, some_unicode_uri, args=[], kwargs=some_kwargs),
        message.Call(123456, some_unicode_uri, args=some_args, kwargs=some_kwargs),
        message.Call(123456, some_unicode_uri, timeout=10000),
        message.Unregistered(123456),
        message.Unregister(123456, 789123),
        message.Registered(123456, 789123),
        message.Register(123456, some_uri),
        message.Register(123456, some_uri, match='prefix'),
        message.Register(123456, some_uri, invoke='roundrobin'),
        message.Register(123456, some_unicode_uri),
        message.Register(123456, some_unicode_uri, match='prefix'),
        message.Register(123456, some_unicode_uri, invoke='roundrobin'),
        message.Event(123456, 789123),
        message.Event(123456, 789123, args=some_args),
        message.Event(123456, 789123, args=[], kwargs=some_kwargs),
        message.Event(123456, 789123, args=some_args, kwargs=some_kwargs),
        message.Event(123456, 789123, publisher=300),
        message.Published(123456, 789123),
        message.Publish(123456, some_uri),
        message.Publish(123456, some_uri, args=some_args),
        message.Publish(123456, some_uri, args=[], kwargs=some_kwargs),
        message.Publish(123456, some_uri, args=some_args, kwargs=some_kwargs),
        message.Publish(123456, some_uri, exclude_me=False, exclude=[300], eligible=[100, 200, 300]),
        message.Publish(123456, some_unicode_uri),
        message.Publish(123456, some_unicode_uri, args=some_args),
        message.Publish(123456, some_unicode_uri, args=[], kwargs=some_kwargs),
        message.Publish(123456, some_unicode_uri, args=some_args, kwargs=some_kwargs),
        message.Publish(123456, some_unicode_uri, exclude_me=False, exclude=[300], eligible=[100, 200, 300]),
        message.Unsubscribed(123456),
        message.Unsubscribe(123456, 789123),
        message.Subscribed(123456, 789123),
        message.Subscribe(123456, some_uri),
        message.Subscribe(123456, some_uri, match=message.Subscribe.MATCH_PREFIX),
        message.Subscribe(123456, some_unicode_uri),
        message.Subscribe(123456, some_unicode_uri, match=message.Subscribe.MATCH_PREFIX),
        message.Error(message.Call.MESSAGE_TYPE, 123456, some_uri),
        message.Error(message.Call.MESSAGE_TYPE, 123456, some_uri, args=some_args),
        message.Error(message.Call.MESSAGE_TYPE, 123456, some_uri, args=[], kwargs=some_kwargs),
        message.Error(message.Call.MESSAGE_TYPE, 123456, some_uri, args=some_args, kwargs=some_kwargs),
        message.Error(message.Call.MESSAGE_TYPE, 123456, some_unicode_uri),
        message.Error(message.Call.MESSAGE_TYPE, 123456, some_unicode_uri, args=some_args),
        message.Error(message.Call.MESSAGE_TYPE, 123456, some_unicode_uri, args=[], kwargs=some_kwargs),
        message.Error(message.Call.MESSAGE_TYPE, 123456, some_unicode_uri, args=some_args, kwargs=some_kwargs),
        message.Result(123456),
        message.Result(123456, args=some_args),
        message.Result(123456, args=some_args, kwargs=some_kwargs),
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
        msgs.append(message.Event(123456, 789123, args=[binary], kwargs={'foo': binary}))
    return [(True, msg) for msg in msgs]


def create_serializers():
    _serializers = []

    _serializers.append(serializer.JsonSerializer())
    _serializers.append(serializer.JsonSerializer(batched=True))

    _serializers.append(serializer.MsgPackSerializer())
    _serializers.append(serializer.MsgPackSerializer(batched=True))

    _serializers.append(serializer.CBORSerializer())
    _serializers.append(serializer.CBORSerializer(batched=True))

    _serializers.append(serializer.UBJSONSerializer())
    _serializers.append(serializer.UBJSONSerializer(batched=True))

    # FIXME: implement full FlatBuffers serializer for WAMP
    # WAMP-FlatBuffers currently only supports Python 3
    # _serializers.append(serializer.FlatBuffersSerializer())
    # _serializers.append(serializer.FlatBuffersSerializer(batched=True))

    return _serializers


class TestFlatBuffersSerializer(unittest.TestCase):

    def test_basic(self):
        messages = [
            message.Event(123456,
                          789123,
                          args=[1, 2, 3],
                          kwargs={'foo': 23, 'bar': 'hello'},
                          publisher=666,
                          retained=True),
            message.Publish(123456,
                            'com.example.topic1',
                            args=[1, 2, 3],
                            kwargs={'foo': 23, 'bar': 'hello'},
                            retain=True)
        ]

        ser = serializer.FlatBuffersSerializer()

        # from pprint import pprint

        for msg in messages:

            # serialize message
            payload, binary = ser.serialize(msg)

            # unserialize message again
            msg2 = ser.unserialize(payload, binary)[0]

            # pprint(msg.marshal())
            # pprint(msg2.marshal())

            # must be equal: message roundtrips via the serializer
            self.assertEqual(msg, msg2)
            # self.assertEqual(msg.subscription, msg2.subscription)
            # self.assertEqual(msg.publication, msg2.publication)


class TestSerializer(unittest.TestCase):

    def setUp(self):
        self._test_messages = generate_test_messages() + generate_test_messages_binary()
        self._test_serializers = create_serializers()
        # print('Testing WAMP serializers {} with {} WAMP test messages'.format([ser.SERIALIZER_ID for ser in self._test_serializers], len(self._test_messages)))

    def test_deep_equal_msg(self):
        """
        Test deep object equality assert (because I am paranoid).
        """
        v = os.urandom(10)
        o1 = [1, 2, {'foo': 'bar', 'bar': v, 'baz': [9, 3, 2], 'goo': {'moo': [1, 2, 3]}}, v]
        o2 = [1, 2, {'goo': {'moo': [1, 2, 3]}, 'bar': v, 'baz': [9, 3, 2], 'foo': 'bar'}, v]
        self.assertEqual(o1, o2)

    def test_roundtrip_msg(self):
        """
        Test round-tripping over each serializer.
        """
        for ser in self._test_serializers:

            for contains_binary, msg in self._test_messages:

                # serialize message
                payload, binary = ser.serialize(msg)

                # unserialize message again
                msg2 = ser.unserialize(payload, binary)

                # must be equal: message roundtrips via the serializer
                self.assertEqual([msg], msg2)

    def test_crosstrip_msg(self):
        """
        Test cross-tripping over 2 serializers (as is done by WAMP routers).
        """
        for ser1 in self._test_serializers:

            for contains_binary, msg in self._test_messages:

                # serialize message
                payload, binary = ser1.serialize(msg)

                # unserialize message again
                msg1 = ser1.unserialize(payload, binary)
                msg1 = msg1[0]

                for ser2 in self._test_serializers:

                    # serialize message
                    payload, binary = ser2.serialize(msg1)

                    # unserialize message again
                    msg2 = ser2.unserialize(payload, binary)

                    # must be equal: message crosstrips via
                    # the serializers ser1 -> ser2
                    self.assertEqual([msg], msg2)

    def test_cache_msg(self):
        """
        Test message serialization caching.
        """
        for contains_binary, msg in self._test_messages:

            # message serialization cache is initially empty
            self.assertEqual(msg._serialized, {})

            for ser in self._test_serializers:

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

    def test_initial_stats(self):
        """
        Test initial serializer stats are indeed empty.
        """
        for ser in self._test_serializers:

            stats = ser.stats(details=True)

            self.assertEqual(stats['serialized']['bytes'], 0)
            self.assertEqual(stats['serialized']['messages'], 0)
            self.assertEqual(stats['serialized']['rated_messages'], 0)

            self.assertEqual(stats['unserialized']['bytes'], 0)
            self.assertEqual(stats['unserialized']['messages'], 0)
            self.assertEqual(stats['unserialized']['rated_messages'], 0)

    def test_serialize_stats(self):
        """
        Test serializer stats are non-empty after serializing/unserializing messages.
        """
        for ser in self._test_serializers:

            for contains_binary, msg in self._test_messages:

                # serialize message
                payload, binary = ser.serialize(msg)

                # unserialize message again
                ser.unserialize(payload, binary)

            stats = ser.stats(details=False)

            self.assertTrue(stats['bytes'] > 0)
            self.assertTrue(stats['messages'] > 0)
            self.assertTrue(stats['rated_messages'] > 0)

    def test_serialize_stats_with_details(self):
        """
        Test serializer stats - with details - are non-empty after serializing/unserializing messages.
        """
        for ser in self._test_serializers:

            for contains_binary, msg in self._test_messages:

                # serialize message
                payload, binary = ser.serialize(msg)

                # unserialize message again
                ser.unserialize(payload, binary)

            stats = ser.stats(details=True)

            # {'serialized': {'bytes': 7923, 'messages': 59, 'rated_messages': 69}, 'unserialized': {'bytes': 7923, 'messages': 59, 'rated_messages': 69}}
            # print(stats)

            self.assertTrue(stats['serialized']['bytes'] > 0)
            self.assertTrue(stats['serialized']['messages'] > 0)
            self.assertTrue(stats['serialized']['rated_messages'] > 0)

            self.assertTrue(stats['unserialized']['bytes'] > 0)
            self.assertTrue(stats['unserialized']['messages'] > 0)
            self.assertTrue(stats['unserialized']['rated_messages'] > 0)

            self.assertEqual(stats['serialized']['bytes'], stats['unserialized']['bytes'])
            self.assertEqual(stats['serialized']['messages'], stats['unserialized']['messages'])
            self.assertEqual(stats['serialized']['rated_messages'], stats['unserialized']['rated_messages'])

    def test_reset_stats(self):
        """
        Test serializer stats are reset after fetching stats - depending on option.
        """
        for ser in self._test_serializers:

            for contains_binary, msg in self._test_messages:

                # serialize message
                payload, binary = ser.serialize(msg)

                # unserialize message again
                ser.unserialize(payload, binary)

            ser.stats()
            stats = ser.stats(details=True)

            self.assertEqual(stats['serialized']['bytes'], 0)
            self.assertEqual(stats['serialized']['messages'], 0)
            self.assertEqual(stats['serialized']['rated_messages'], 0)

            self.assertEqual(stats['unserialized']['bytes'], 0)
            self.assertEqual(stats['unserialized']['messages'], 0)
            self.assertEqual(stats['unserialized']['rated_messages'], 0)

    def test_auto_stats(self):
        """
        Test serializer stats are non-empty after serializing/unserializing messages.
        """
        for ser in self._test_serializers:

            def on_stats(stats):
                self.assertTrue(stats['bytes'] > 0)
                self.assertTrue(stats['messages'] > 0)
                self.assertTrue(stats['rated_messages'] > 0)

            ser.set_stats_autoreset(10, 0, on_stats)

            for contains_binary, msg in self._test_messages:

                # serialize message
                payload, binary = ser.serialize(msg)

                # unserialize message again
                ser.unserialize(payload, binary)
