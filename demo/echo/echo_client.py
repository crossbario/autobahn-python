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

from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol

class EchoClientProtocol(WebSocketClientProtocol):

   def sendHello(self):
      self.sendMessage("Hello, world!")

   def onOpen(self):
      self.sendHello()

   def onMessage(self, msg, binary):
      print "Got echo: " + msg
      reactor.callLater(2, self.sendHello)


class EchoClientFactory(WebSocketClientFactory):

   protocol = EchoClientProtocol


if __name__ == '__main__':

   factory = EchoClientFactory()
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
