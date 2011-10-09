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

import random
from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol


class BroadcastClientProtocol(WebSocketClientProtocol):

   def sendHello(self):
      self.sendMessage("Hello from Python!")
      reactor.callLater(random.random()*5, self.sendHello)

   def onOpen(self):
      self.sendHello()

   def onMessage(self, msg, binary):
      print "Got message: " + msg


if __name__ == '__main__':

   factory = WebSocketClientFactory()
   factory.protocol = BroadcastClientProtocol
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
