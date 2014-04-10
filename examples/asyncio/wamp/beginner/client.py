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

import sys

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import clientFromString

from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.wamp import ApplicationSessionFactory
from autobahn.twisted.websocket import WampWebSocketClientFactory


class MyFrontendComponent(ApplicationSession):
   """
   Application code goes here. This is an example component that calls
   a remote procedure on a WAMP peer, subscribes to a topic to receive
   events, and then stops the world after some events.
   """
   def onConnect(self):
      self.join("realm1")

   @inlineCallbacks
   def onJoin(self, details):

      ## call a remote procedure
      ##
      try:
         now = yield self.call(u'com.timeservice.now')
      except Exception as e:
         print("Error: {}".format(e))
      else:
         print("Current time from time service: {}".format(now))

      ## subscribe to a topic
      ##
      self.received = 0

      def on_event(i):
         print("Got event: {}".format(i))
         self.received += 1
         if self.received > 5:
            self.leave()

      yield self.subscribe(on_event, u'com.myapp.topic1')

   def onLeave(self, details):
      self.disconnect()

   def onDisconnect(self):
      reactor.stop()


if __name__ == '__main__':

   ## 0) start logging to console
   log.startLogging(sys.stdout)

   ## 1) create a WAMP application session factory
   session_factory = ApplicationSessionFactory()
   session_factory.session = MyFrontendComponent

   ## 2) create a WAMP-over-WebSocket transport client factory
   transport_factory = WampWebSocketClientFactory(session_factory, debug = False, debug_wamp = True)

   ## 3) start the client from a Twisted endpoint
   client = clientFromString(reactor, "tcp:127.0.0.1:8080")
   client.connect(transport_factory)

   ## 4) now enter the Twisted reactor loop
   reactor.run()
