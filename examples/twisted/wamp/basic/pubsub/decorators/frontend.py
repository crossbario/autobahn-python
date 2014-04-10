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

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession



class Component(ApplicationSession):
   """
   An application component that subscribes and receives events,
   and stop after having received 5 events.
   """

   @inlineCallbacks
   def onJoin(self, details):

      ## subscribe all methods on this object decorated with "@wamp.topic"
      ## as PubSub event handlers
      ##
      results = yield self.subscribe(self)
      for success, res in results:
         if success:
            ## res is an Subscription instance
            print("Ok, subscribed handler with subscription ID {}".format(res.id))
         else:
            ## res is an Failure instance
            print("Failed to subscribe handler: {}".format(res.value))


   @wamp.topic('com.myapp.topic1')
   def onEvent1(self, i):
      print("Got event on topic1: {}".format(i))
      self.received += 1
      if self.received > 5:
         self.leave()


   @wamp.topic('com.myapp.topic2')
   def onEvent2(self, msg):
      print("Got event on topic2: {}".format(msg))


   def onDisconnect(self):
      reactor.stop()
