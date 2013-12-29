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
from twisted.python import log

from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS

from autobahn.websocket.compress import PerMessageDeflateOffer, \
                                        PerMessageDeflateResponse, \
                                        PerMessageDeflateResponseAccept



class EchoClientProtocol(WebSocketClientProtocol):

   def onConnect(self, response):
      print("WebSocket extensions in use: {}".format(response.extensions))

   def sendHello(self):
      msg = "Hello, world!" * 100
      self.sendMessage(msg.encode('utf8'))

   def onOpen(self):
      self.sendHello()

   def onMessage(self, payload, isBinary):
      if not isBinary:
         print("Text message received: {}".format(payload.decode('utf8')))
      reactor.callLater(1, self.sendHello)


if __name__ == '__main__':

   if len(sys.argv) < 2:
      print("Need the WebSocket server address, i.e. ws://localhost:9000")
      sys.exit(1)

   if len(sys.argv) > 2 and sys.argv[2] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WebSocketClientFactory(sys.argv[1],
                                    debug = debug,
                                    debugCodePaths = debug)

   factory.protocol = EchoClientProtocol


   ## Enable WebSocket extension "permessage-deflate".
   ##

   ## The extensions offered to the server ..
   offers = [PerMessageDeflateOffer()]
   factory.setProtocolOptions(perMessageCompressionOffers = offers)

   ## Function to accept responses from the server ..
   def accept(response):
      if isinstance(response, PerMessageDeflateResponse):
         return PerMessageDeflateResponseAccept(response)

   factory.setProtocolOptions(perMessageCompressionAccept = accept)


   ## run client
   ##
   connectWS(factory)
   reactor.run()
