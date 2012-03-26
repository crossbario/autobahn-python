###############################################################################
##
##  Copyright 2011 Tavendo GmbH
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
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

class EchoServerProtocol(WebSocketServerProtocol):

   def sendHello(self):
      if self.send_hello:
         for i in xrange(0, 3):
            self.sendMessage("*" * (self.count * 5))
         self.count += 1
         reactor.callLater(1, self.sendHello)

   def onOpen(self):
      print "CONNECTED " + self.peerstr
      self.count = 1
      self.send_hello = True
      #self.sendHello()

   def onMessage(self, msg, binary):
      print msg
      self.sendMessage(msg, binary)

   def connectionLost(self, reason):
      print "LOST " + self.peerstr
      WebSocketServerProtocol.connectionLost(self, reason)
      self.send_hello = False


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WebSocketServerFactory("ws://localhost:9000", debug = True, debugCodePaths = True)
   factory.protocol = EchoServerProtocol
   listenWS(factory)
   reactor.run()
