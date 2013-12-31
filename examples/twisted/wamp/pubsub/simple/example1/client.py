###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
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

from autobahn.twisted.websocket import connectWS
from autobahn.wamp import WampClientFactory, \
                          WampClientProtocol


class MyPubSubClientProtocol(WampClientProtocol):
   """
   Protocol class for our simple demo WAMP client.
   """

   def onSessionOpen(self):

      print "Connected!"

      def onMyEvent1(topic, event):
         print "Received event", topic, event

      self.subscribe("http://example.com/myEvent1", onMyEvent1)

      self.counter = 0

      def sendMyEvent1():
         self.counter += 1
         self.publish("http://example.com/myEvent1",
            {
               "msg": "Hello from Python!",
               "counter": self.counter
            }
         )
         reactor.callLater(2, sendMyEvent1)

      sendMyEvent1()


   def onClose(self, wasClean, code, reason):
      print "Connection closed", reason
      reactor.stop()



if __name__ == '__main__':

   log.startLogging(sys.stdout)

   if len(sys.argv) > 1:
      wsuri = sys.argv[1]
   else:
      wsuri = "ws://localhost:9000"

   print "Connecting to", wsuri

   ## our WAMP/WebSocket client
   ##
   factory = WampClientFactory(wsuri, debugWamp = False)
   factory.protocol = MyPubSubClientProtocol
   connectWS(factory)

   ## run the Twisted network reactor
   ##
   reactor.run()
