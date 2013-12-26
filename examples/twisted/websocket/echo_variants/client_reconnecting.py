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
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log

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


class EchoClientFactory(ReconnectingClientFactory, WebSocketClientFactory):
   
   protocol = EchoClientProtocol

   ## http://twistedmatrix.com/documents/current/api/twisted.internet.protocol.ReconnectingClientFactory.html
   ##
   maxDelay = 10
   maxRetries = 5

   def startedConnecting(self, connector):
     print 'Started to connect.'

   def clientConnectionLost(self, connector, reason):
      print 'Lost connection.  Reason:', reason
      ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

   def clientConnectionFailed(self, connector, reason):
      print 'Connection failed. Reason:', reason
      ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)



if __name__ == '__main__':

   if len(sys.argv) < 2:
      print "Need the WebSocket server address, i.e. ws://localhost:9000"
      sys.exit(1)

   if len(sys.argv) > 2 and sys.argv[2] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = EchoClientFactory(sys.argv[1],
                               debug = debug,
                               debugCodePaths = debug)

   # uncomment to use Hixie-76 protocol
   #factory.setProtocolOptions(allowHixie76 = True, version = 0)
   connectWS(factory)

   reactor.run()
