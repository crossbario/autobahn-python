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


from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol



class EchoClientProtocol(WebSocketClientProtocol):
   """
   Example WebSocket client protocol. This is where you define your application
   specific protocol and logic.
   """ 

   def sendHello(self):
      self.sendMessage("Hello, world!")

   def onOpen(self):
      self.sendHello()

   def onMessage(self, msg, binary):
      print "Got echo: " + msg
      self.factory.reactor.callLater(1, self.sendHello)



class EchoClientFactory(WebSocketClientFactory):
   """
   Example WebSocket client factory. This creates a new instance of our protocol
   when the client connects to the server.
   """

   protocol = EchoClientProtocol



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
   wsfactory = EchoClientFactory(args.wsurl, debug = args.debug)
   wsclient = clientFromString(reactor, args.websocket)
   wsclient.connect(wsfactory)


   ## now enter the Twisted reactor loop
   ##
   reactor.run()
