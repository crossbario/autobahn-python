###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
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

import os, socket, binascii

from twisted.internet import reactor

from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol


class BroadcastServerProtocol(WebSocketServerProtocol):

   def onOpen(self):
      self.factory.register(self)

   def onClose(self, wasClean, code, reason):
      self.factory.unregister(self)

   def onMessage(self, msg, binary):
      self.factory.broadcast(msg, binary)


class BroadcastServerFactory(WebSocketServerFactory):

   protocol = BroadcastServerProtocol

   def startFactory(self):
      self.clients = set()
      self.tickcount = 0
      self.tick()

#   def stopFactory(self):
#      reactor.stop()

   def register(self, client):
      self.clients.add(client)

   def unregister(self, client):
      self.clients.discard(client)

   def broadcast(self, msg, binary = False):
      for c in self.clients:
         c.sendMessage(msg, binary)

   def tick(self):
      self.tickcount += 1
      self.broadcast("tick %d" % self.tickcount)
      reactor.callLater(1, self.tick)


class BroadcastClientProtocol(WebSocketClientProtocol):

   def sendHello(self):
      self.sendMessage("hello from %s[%d]" % (socket.gethostname(), os.getpid()))
      reactor.callLater(2, self.sendHello)

   def onOpen(self):
      self.sendHello()

   def onMessage(self, msg, binary):
      if binary:
         print "received: ", binascii.b2a_hex(msg)
      else:
         print "received: ", msg

class BroadcastClientFactory(WebSocketClientFactory):

   protocol = BroadcastClientProtocol

#   def clientConnectionLost(self, connector, reason):
#      reactor.stop()
