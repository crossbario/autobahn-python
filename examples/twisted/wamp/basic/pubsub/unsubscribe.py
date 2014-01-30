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

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.wamp.protocol import WampAppSession
from autobahn.twisted.util import sleep



class UnsubscribeTestBackend(WampAppSession):
   """
   An application component that publishes an event every second.
   """

   @inlineCallbacks
   def onSessionOpen(self, details):

      counter = 0
      while True:
         self.publish('com.myapp.topic1', counter)
         counter += 1
         yield sleep(1)



class UnsubscribeTestFrontend(WampAppSession):
   """
   An application component that subscribes and receives events.
   After receiving 5 events, it unsubscribes, sleeps and then
   resubscribes for another run. Then it stops.
   """

   @inlineCallbacks
   def test(self):

      self.received = 0

      @inlineCallbacks
      def on_event(i):
         print("Got event: {}".format(i))
         self.received += 1
         if self.received > 5:
            self.runs += 1
            if self.runs > 1:
               self.closeSession()
            else:
               yield self.subscription.unsubscribe()
               print("Unsubscribed .. continue in 2s ..")
               reactor.callLater(2, self.test)

      self.subscription = yield self.subscribe(on_event, 'com.myapp.topic1')
      print("Subscribed with subscription ID {}".format(self.subscription.id))


   @inlineCallbacks
   def onSessionOpen(self, details):

      self.runs = 0
      yield self.test()


   def onSessionClose(self, details):
      reactor.stop()
