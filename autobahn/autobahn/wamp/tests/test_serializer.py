###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from __future__ import absolute_import

from twisted.trial import unittest
#import unittest

from autobahn import wamp
from autobahn.wamp import message
from autobahn.wamp import serializer


class TestSerializer(unittest.TestCase):

   def setUp(self):
      self.serializers = []
      self.serializers.append(serializer.WampJsonSerializer())
      self.serializers.append(serializer.WampMsgPackSerializer())

      self.msgs = [
         message.Hello(123456),
         message.Goodbye(),
         message.Heartbeat(123, 456),
         message.Yield(123456),
         message.Yield(123456, args = [1, 2, 3], kwargs = {'foo': 23, 'bar': 'hello'}),
         message.Yield(123456, progress = True),
         message.Interrupt(123456),
         message.Interrupt(123456, mode = message.Interrupt.KILL),
         message.Invocation(123456, 789123),
         message.Invocation(123456, 789123, args = [1, 2, 3], kwargs = {'foo': 23, 'bar': 'hello'}),
         message.Invocation(123456, 789123, timeout = 10000),
         message.Result(123456),
         message.Result(123456, args = [1, 2, 3], kwargs = {'foo': 23, 'bar': 'hello'}),
         message.Result(123456, progress = True),
         message.Cancel(123456),
         message.Cancel(123456, mode = message.Cancel.KILL),
         message.Call(123456, 'com.myapp.procedure1'),
         message.Call(123456, 'com.myapp.procedure1', args = [1, 2, 3], kwargs = {'foo': 23, 'bar': 'hello'}),
         message.Call(123456, 'com.myapp.procedure1', timeout = 10000),
         message.Unregistered(123456),
         message.Unregister(123456, 789123),
         message.Registered(123456, 789123),
         message.Register(123456, 'com.myapp.procedure1'),
         message.Register(123456, 'com.myapp.procedure1', pkeys = [10, 11, 12]),
         message.Event(123456, 789123),
         message.Event(123456, 789123, args = [1, 2, 3], kwargs = {'foo': 23, 'bar': 'hello'}),
         message.Event(123456, 789123, publisher = 300),
         message.Published(123456, 789123),
         message.Publish(123456, 'com.myapp.topic1'),
         message.Publish(123456, 'com.myapp.topic1', args = [1, 2, 3], kwargs = {'foo': 23, 'bar': 'hello'}),
         message.Publish(123456, 'com.myapp.topic1', excludeMe = False, exclude = [300], eligible = [100, 200, 300], discloseMe = True),
         message.Unsubscribed(123456),
         message.Unsubscribe(123456, 789123),
         message.Subscribed(123456, 789123),
         message.Subscribe(123456, 'com.myapp.topic1'),
         message.Subscribe(123456, 'com.myapp.topic1', match = message.Subscribe.MATCH_PREFIX),
         message.Error(123456, 'com.myapp.error1'),
         message.Error(123456, 'com.myapp.error1', args = [1, 2, 3], kwargs = {'foo': 23, 'bar': 'hello'})
      ]


   def test_serialize_roundtrip(self):
      for msg in self.msgs:
         for serializer in self.serializers:
            bytes, binary = serializer.serialize(msg)
            msg2 = serializer.unserialize(bytes, binary)
            self.assertEqual(msg, msg2)


if __name__ == '__main__':
   unittest.main()
