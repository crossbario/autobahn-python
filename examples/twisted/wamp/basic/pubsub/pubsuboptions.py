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

from autobahn.wamp.types import PublishOptions, EventDetails, SubscribeOptions
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession



class PubSubOptionsTestBackend(ApplicationSession):
   """
   An application component that publishes an event every second.
   """

   def onConnect(self):
      self.join("realm1")


   @inlineCallbacks
   def onJoin(self, details):
      counter = 0
      while True:
         publication = yield self.publish('com.myapp.topic1', counter,
               options = PublishOptions(acknowledge = True, discloseMe = True))
         print("Event published with publication ID {}".format(publication.id))
         counter += 1
         yield sleep(1)



class PubSubOptionsTestFrontend(ApplicationSession):
   """
   An application component that subscribes and receives events,
   and stop after having received 5 events.
   """

   def onConnect(self):
      self.join("realm1")


   @inlineCallbacks
   def onJoin(self, details):

      self.received = 0

      def on_event(i, details = None):
         print("Got event, publication ID {}, publisher {}: {}".format(details.publication, details.publisher, i))
         self.received += 1
         if self.received > 5:
            self.leave()

      yield self.subscribe(on_event, 'com.myapp.topic1',
                              options = SubscribeOptions(details_arg = 'details'))


   def onLeave(self, details):
      self.disconnect()


   def onDisconnect(self):
      reactor.stop()
