###############################################################################
##
##  Copyright 2011-2013 Tavendo GmbH
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

from websocket import WebSocketProtocol, HttpException, Timings
from websocket import WebSocketClientProtocol, WebSocketClientFactory
from websocket import WebSocketServerFactory, WebSocketServerProtocol

from httpstatus import HTTP_STATUS_CODE_BAD_REQUEST
from util import utcnow, newid

from wamp2factory import *
from wamp2protocol import *
from wamp2message import *

from twisted.python import log
from twisted.internet import reactor

from websocket import connectWS, listenWS



def test1():

   serializer = JsonDefaultSerializer()

   wampSerializer = WampSerializer(serializer)

   wampMsg = WampMessageSubscribe("http://myapp.com/topic1", match = WampMessageSubscribe.MATCH_PREFIX)
   wampMsg = WampMessageUnsubscribe("http://myapp.com/topic1", match = WampMessageSubscribe.MATCH_PREFIX)
   wampMsg = WampMessagePublish("http://myapp.com/topic1", "Hello, world!")

   bytes = wampSerializer.serialize(wampMsg)

   print bytes

   wampMsg2 = wampSerializer.unserialize(bytes)

   print wampMsg2.__class__
   print wampMsg2



def test_server(wsuri, wsuri2 = None):

   broker = Broker()

   class MyPubSubServerProtocol(Wamp2ServerProtocol):

      def onSessionOpen(self):
         self.setBroker(broker)

   wampFactory = Wamp2ServerFactory(wsuri)
   wampFactory.protocol = MyPubSubServerProtocol
   listenWS(wampFactory)

   if wsuri2:
      class MyPubSubClientProtocol(Wamp2ClientProtocol):

         def onSessionOpen(self):
            self.setBroker(broker)

      factory = Wamp2ClientFactory(wsuri2)
      factory.protocol = MyPubSubClientProtocol
      connectWS(factory)


def test_client(wsuri, dopub):

   class MyPubSubClientProtocol(Wamp2ClientProtocol):

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

         if dopub:
            sendMyEvent1()


      def onClose(self, wasClean, code, reason):
         print "Connection closed", reason
         reactor.stop()

   factory = Wamp2ClientFactory(wsuri)
   factory.protocol = MyPubSubClientProtocol
   connectWS(factory)


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   mode = sys.argv[1]
   wsuri = sys.argv[2]

   if mode == 'server' and len(sys.argv) > 3:
      wsuri2 = sys.argv[3]
   else:
      wsuri2 = None

   if mode == 'client' and len(sys.argv) > 3:
      dopub = sys.argv[3] == "pub"
   else:
      dopub = False

   if mode == 'client':
      test_client(wsuri, dopub)
   elif mode == 'server':
      test_server(wsuri, wsuri2)
   else:
      raise Exception("illegal mode")

   #test1()

   reactor.run()

