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
from optparse import OptionParser

from twisted.python import log
from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS



class EchoClientProtocol(WebSocketClientProtocol):

   def sendHello(self):
      self.sendMessage("Hello, world!")

   def onOpen(self):
      self.sendHello()

   def onMessage(self, msg, binary):
      print "Got echo: " + msg
      reactor.callLater(1, self.sendHello)



if __name__ == '__main__':

   log.startLogging(sys.stdout)

   parser = OptionParser()
   parser.add_option("-u", "--url", dest = "url", help = "The WebSocket URL", default = "wss://localhost:9000")
   (options, args) = parser.parse_args()

   ## create a WS server factory with our protocol
   ##
   factory = WebSocketClientFactory(options.url, debug = False)
   factory.protocol = EchoClientProtocol

   ## SSL client context: default
   ##
   if factory.isSecure:
      contextFactory = ssl.ClientContextFactory()
   else:
      contextFactory = None

   connectWS(factory, contextFactory)
   reactor.run()
