###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
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


from autobahn.wamp2.websocket import WampWebSocketClientProtocol, \
                                     WampWebSocketClientFactory

from autobahn.wamp2.serializer import WampJsonSerializer, WampMsgPackSerializer


class PubSubClientProtocol(WampWebSocketClientProtocol):
   """
   """ 

   def onSessionOpen(self):
      print "WAMP session opened", self.websocket_protocol_in_use

      def onMyEvent1(topic, event):
         print "Received event:", event

      d = self.subscribe("http://example.com/myEvent1", onMyEvent1)

      def subscribeSuccess(subscriptionid):
         print "Subscribe Success", subscriptionid

      def subscribeError(error):
         print "Subscribe Error", error

      d.addCallbacks(subscribeSuccess, subscribeError)

      if self.factory.period:

         self.counter = 0

         def sendMyEvent1():
            self.counter += 1
            self.publish("http://example.com/myEvent1",
               {
                  "msg": "Hello from Python!",
                  "counter": self.counter
               }
            )
            reactor.callLater(self.factory.period, sendMyEvent1)

         sendMyEvent1()


   def onSessionClose(self):
      print "WAMP session closed"
      self.factory.reactor.stop()



class PubSubClientFactory(WampWebSocketClientFactory):
   """
   """

   protocol = PubSubClientProtocol

   def __init__(self, url, serializers = None, period = 0, debug = False):
      WampWebSocketClientFactory.__init__(self, url, serializers = serializers, debug = debug)
      self.period = period



if __name__ == '__main__':

   import sys, argparse

   from twisted.python import log
   from twisted.internet.endpoints import clientFromString


   ## parse command line arguments
   ##
   parser = argparse.ArgumentParser()

   parser.add_argument("-d", "--debug", action = "store_true",
                       help = "Enable debug output.")

   parser.add_argument("--websocket", default = "tcp:localhost:9000",
                       help = 'WebSocket client Twisted endpoint descriptor, e.g. "tcp:localhost:9000" or "unix:/tmp/mywebsocket".')

   parser.add_argument("--wsurl", default = "ws://localhost:9000",
                       help = 'WebSocket URL (must suit the endpoint), e.g. "ws://localhost:9000".')

   parser.add_argument("--period", type = float, default = 2,
                       help = 'Auto-publication period in seconds.')

   parser.add_argument("--serializers", type = str, default = None,
                       help = 'If set, use this (comma separated) list of WAMP serializers, e.g. "json" or "msgpack,json"')

   #parser.add_argument("--period", type = float, default = 2,
   #                    help = 'Auto-publication period in seconds.')

   args = parser.parse_args()


   ## start Twisted logging to stdout
   ##
   log.startLogging(sys.stdout)


   ## we use an Autobahn utility to import the "best" available Twisted reactor
   ##
   from autobahn.choosereactor import install_reactor
   reactor = install_reactor()
   print "Running on reactor", reactor


   ## start a WebSocket client
   ##
   if args.serializers:
      serializers = []
      for id in args.serializers.split(','):
         if id.strip() == WampJsonSerializer.SERIALIZER_ID:
            serializers.append(WampJsonSerializer())
         elif id.strip() == WampMsgPackSerializer.SERIALIZER_ID:
            serializers.append(WampMsgPackSerializer())
         else:
            raise Exception("unknown WAMP serializer %s" % id)
      if len(serializers) == 0:
         raise Exception("no WAMP serializers selected")
   else:
      serializers = [WampMsgPackSerializer(), WampJsonSerializer()]
   wsfactory = PubSubClientFactory(args.wsurl, serializers = serializers, period = args.period, debug = args.debug)
   wsclient = clientFromString(reactor, args.websocket)
   d = wsclient.connect(wsfactory)

   def connected(proto):
      print "Endpoint connected:", proto

   def disconnected(err):
      print "Endpoint disconnected:", err
      reactor.stop()

   d.addCallbacks(connected, disconnected)


   ## now enter the Twisted reactor loop
   ##
   reactor.run()
