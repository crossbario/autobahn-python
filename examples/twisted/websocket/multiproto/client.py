###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
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
from twisted.python import log

from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS


class EchoClientProtocol(WebSocketClientProtocol):

   def sendHello(self):
      self.sendMessage("Hello, world!".encode('utf8'))

   def onOpen(self):
      self.sendHello()

   def onClose(self, wasClean, code, reason):
      print(reason)

   def onMessage(self, payload, isBinary):
      if not isBinary:
         print("Text message received: {}".format(payload.decode('utf8')))
      reactor.callLater(1, self.sendHello)


class EchoClientFactory(WebSocketClientFactory):

   protocol = EchoClientProtocol

   def clientConnectionLost(self, connector, reason):
      print(reason)
      reactor.stop()

   def clientConnectionFailed(self, connector, reason):
      print(reason)
      reactor.stop()


if __name__ == '__main__':

   if len(sys.argv) < 2:
      print("Need the WebSocket server address, i.e. ws://localhost:9000/echo1")
      sys.exit(1)

   factory = EchoClientFactory(sys.argv[1])
   connectWS(factory)

   reactor.run()
