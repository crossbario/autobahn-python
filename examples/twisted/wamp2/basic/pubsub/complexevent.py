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

import random

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.wamp.protocol import WampAppSession
from autobahn.wamp.types import SubscribeOptions



class ComplexEventTestBackend(WampAppSession):
   """
   An application component that publishes events with no payload
   and with complex payloads every second.
   """

   @inlineCallbacks
   def onSessionOpen(self, details):

      counter = 0
      while True:
         self.publish('com.myapp.heartbeat')

         obj = {'counter': counter, 'foo': [1, 2, 3]}
         self.publish('com.myapp.topic2', random.randint(0, 100), 23, c = "Hello", d = obj)

         counter += 1
         yield sleep(1)



class ComplexEventTestFrontend(WampAppSession):
   """
   An application component that subscribes and receives events
   of no payload and of complex payload, and stops after 5 seconds.
   """

   @inlineCallbacks
   def onSessionOpen(self, details):

      self.received = 0

      def on_heartbeat(details = None):
         print("Got heartbeat (publication ID {})".format(details.publication))

      yield self.subscribe(on_heartbeat, 'com.myapp.heartbeat', options = SubscribeOptions(details_arg = 'details'))


      def on_topic2(a, b, c = None, d = None):
         print("Got event: {} {} {} {}".format(a, b, c, d))

      yield self.subscribe(on_topic2, 'com.myapp.topic2')


      reactor.callLater(5, self.closeSession)


   def onSessionClose(self, details):
      reactor.stop()
