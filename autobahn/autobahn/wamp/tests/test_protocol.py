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
from twisted.internet.defer import Deferred, inlineCallbacks

from autobahn import wamp
from autobahn.wamp import message
from autobahn.wamp import serializer
from autobahn.wamp import protocol
from autobahn import util
from autobahn.wamp.exception import ApplicationError, NotAuthorized, InvalidTopic
from autobahn.wamp import options



class MockTransport:

   def __init__(self, handler):
      self._handler = handler
      self._handler.onOpen(self)
      self._serializer = serializer.JsonSerializer()

   def send(self, msg):
      bytes, isbinary = self._serializer.serialize(msg)
      print("Send: {}".format(bytes))

      reply = None

      if isinstance(msg, message.Publish):
         if msg.topic.startswith('com.myapp'):
            reply = message.Published(msg.request, util.id())
         elif len(msg.topic) == 0:
            reply = message.Error(msg.request, 'wamp.error.invalid_topic')
         else:
            reply = message.Error(msg.request, 'wamp.error.not_authorized')

      elif isinstance(msg, message.Subscribe):
         reply = message.Subscribed(msg.request, util.id())

      elif isinstance(msg, message.Unsubscribe):
         reply = message.Unsubscribed(msg.request)
         
      elif isinstance(msg, message.Register):
         reply = message.Registered(msg.request, util.id())

      elif isinstance(msg, message.Unregister):
         reply = message.Unregistered(msg.request)
         

      if reply:
         bytes, isbinary = self._serializer.serialize(reply)
         print("Receive: {}".format(bytes))
         self._handler.onMessage(reply)

   def isOpen(self):
      return True

   def close(self):
      pass

   def abort(self):
      pass



class TestPublisher(unittest.TestCase):

   @inlineCallbacks
   def test_publish(self):
      handler = protocol.WampProtocol()
      transport = MockTransport(handler)

      publication = yield handler.publish('com.myapp.topic1')
      self.assertTrue(type(publication) in (int, long))

      publication = yield handler.publish('com.myapp.topic1', 1, 2, 3)
      self.assertTrue(type(publication) in (int, long))

      publication = yield handler.publish('com.myapp.topic1', 1, 2, 3, foo = 23, bar = 'hello')
      self.assertTrue(type(publication) in (int, long))

      publication = yield handler.publish('com.myapp.topic1', options = options.Publish(excludeMe = False))
      self.assertTrue(type(publication) in (int, long))

      publication = yield handler.publish('com.myapp.topic1', 1, 2, 3, foo = 23, bar = 'hello', options = options.Publish(excludeMe = False, exclude = [100, 200, 300]))
      self.assertTrue(type(publication) in (int, long))


   @inlineCallbacks
   def test_publish_undefined_exception(self):
      handler = protocol.WampProtocol()
      transport = MockTransport(handler)

      yield self.assertFailure(handler.publish('de.myapp.topic1'), ApplicationError)
      yield self.assertFailure(handler.publish(''), ApplicationError)


   @inlineCallbacks
   def test_publish_defined_exception(self):
      handler = protocol.WampProtocol()
      transport = MockTransport(handler)

      handler.define(NotAuthorized)
      yield self.assertFailure(handler.publish('de.myapp.topic1'), NotAuthorized)

      handler.define(InvalidTopic)
      yield self.assertFailure(handler.publish(''), InvalidTopic)


   @inlineCallbacks
   def test_subscribe(self):
      handler = protocol.WampProtocol()
      transport = MockTransport(handler)

      def on_event(*args, **kwargs):
         print "got event"

      subscription = yield handler.subscribe(on_event, 'com.myapp.topic1')
      self.assertTrue(type(subscription) in (int, long))

      subscription = yield handler.subscribe(on_event, 'com.myapp.topic1', options = options.Subscribe(match = 'wildcard'))
      self.assertTrue(type(subscription) in (int, long))


   @inlineCallbacks
   def test_unsubscribe(self):
      handler = protocol.WampProtocol()
      transport = MockTransport(handler)

      def on_event(*args, **kwargs):
         print "got event"

      subscription = yield handler.subscribe(on_event, 'com.myapp.topic1')
      yield handler.unsubscribe(subscription)


   @inlineCallbacks
   def test_register(self):
      handler = protocol.WampProtocol()
      transport = MockTransport(handler)

      def on_call(*args, **kwargs):
         print "got call"

      registration = yield handler.register(on_call, 'com.myapp.procedure1')
      self.assertTrue(type(registration) in (int, long))

      registration = yield handler.register(on_call, 'com.myapp.procedure1', options = options.Register(pkeys = [0, 1, 2]))
      self.assertTrue(type(registration) in (int, long))


   # ## variant 1: works
   # def test_publish1(self):
   #    d = self.handler.publish('de.myapp.topic1')
   #    self.assertFailure(d, ApplicationError)

   # ## variant 2: works
   # @inlineCallbacks
   # def test_publish2(self):
   #    yield self.assertFailure(self.handler.publish('de.myapp.topic1'), ApplicationError)

   # ## variant 3: does NOT work
   # @inlineCallbacks
   # def test_publish3(self):
   #    with self.assertRaises(ApplicationError):
   #       yield self.handler.publish('de.myapp.topic1')


if __name__ == '__main__':
   unittest.main()
