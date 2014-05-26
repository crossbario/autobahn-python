###############################################################################
##
##  Copyright (C) 2013-2014 Tavendo GmbH
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
from twisted.web.server import Site
from twisted.web.static import Data

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource



class Echo1ServerProtocol(WebSocketServerProtocol):

   def onMessage(self, payload, isBinary):
      if not isBinary:
         msg = "Echo 1 - {}".format(payload.decode('utf8'))
         print(msg)
         self.sendMessage(msg.encode('utf8'))



class Echo2ServerProtocol(WebSocketServerProtocol):

   def onMessage(self, payload, isBinary):
      if not isBinary:
         msg = "Echo 2 - {}".format(payload.decode('utf8'))
         print(msg)
         self.sendMessage(msg.encode('utf8'))



if __name__ == '__main__':

   log.startLogging(sys.stdout)

   factory1 = WebSocketServerFactory()
   factory1.protocol = Echo1ServerProtocol
   resource1 = WebSocketResource(factory1)

   factory2 = WebSocketServerFactory()
   factory2.protocol = Echo2ServerProtocol
   resource2 = WebSocketResource(factory2)

   ## Establish a dummy root resource
   root = Data("", "text/plain")

   ## and our WebSocket servers under different paths ..
   root.putChild("echo1", resource1)
   root.putChild("echo2", resource2)

   ## both under one Twisted Web Site
   site = Site(root)
   reactor.listenTCP(9000, site)

   reactor.run()
