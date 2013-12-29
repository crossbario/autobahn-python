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
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS


class BroadcastClientProtocol(WebSocketClientProtocol):
   """
   Simple client that connects to a WebSocket server, send a HELLO
   message every 2 seconds and print everything it receives.
   """

   def sendHello(self):
      self.sendMessage("Hello from Python!".encode('utf8'))
      reactor.callLater(2, self.sendHello)

   def onOpen(self):
      self.sendHello()

   def onMessage(self, payload, isBinary):
      if not isBinary:
         print("Text message received: {}".format(payload.decode('utf8')))


if __name__ == '__main__':

   if len(sys.argv) < 2:
      print "Need the WebSocket server address, i.e. ws://localhost:9000"
      sys.exit(1)

   factory = WebSocketClientFactory(sys.argv[1])
   factory.protocol = BroadcastClientProtocol
   connectWS(factory)

   reactor.run()
