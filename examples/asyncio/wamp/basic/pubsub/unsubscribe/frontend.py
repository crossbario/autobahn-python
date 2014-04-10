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

import asyncio

from autobahn.asyncio.wamp import ApplicationSession



class Component(ApplicationSession):
   """
   An application component that subscribes and receives events.
   After receiving 5 events, it unsubscribes, sleeps and then
   resubscribes for another run. Then it stops.
   """

   @asyncio.coroutine
   def test(self):

      self.received = 0

      #@asyncio.coroutine
      def on_event(i):
         print("Got event: {}".format(i))
         self.received += 1
         if self.received > 5:
            self.runs += 1
            if self.runs > 1:
               self.leave()
            else:
               self.subscription.unsubscribe()
               #yield from self.subscription.unsubscribe()
               print("Unsubscribed .. continue in 2s ..")

               ## FIXME
               asyncio.get_event_loop().call_later(2, self.test)

      self.subscription = yield from self.subscribe(on_event, 'com.myapp.topic1')
      print("Subscribed with subscription ID {}".format(self.subscription.id))


   def onConnect(self):
      self.join("realm1")


   @asyncio.coroutine
   def onJoin(self, details):

      self.runs = 0
      yield from self.test()


   def onLeave(self, details):
      self.disconnect()


   def onDisconnect(self):
      asyncio.get_event_loop().stop()
