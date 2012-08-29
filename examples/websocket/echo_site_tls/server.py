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

import sys

from twisted.internet import reactor, ssl
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol

from autobahn.resource import WebSocketResource, HTTPChannelHixie76Aware


class EchoServerProtocol(WebSocketServerProtocol):
   
   def onMessage(self, msg, binary):
      self.sendMessage(msg, binary)


if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False
      
   contextFactory = ssl.DefaultOpenSSLContextFactory('keys/server.key',
                                                     'keys/server.crt')

   factory = WebSocketServerFactory("wss://localhost:8080",
                                    debug = debug,
                                    debugCodePaths = debug)

   factory.protocol = EchoServerProtocol
   factory.setProtocolOptions(allowHixie76 = True) # needed if Hixie76 is to be supported

   resource = WebSocketResource(factory)

   ## we server static files under "/" ..
   root = File(".")

   ## and our WebSocket server under "/ws"
   root.putChild("ws", resource)

   ## both under one Twisted Web Site
   site = Site(root)
   site.protocol = HTTPChannelHixie76Aware # needed if Hixie76 is to be supported
   
   reactor.listenSSL(8080, site, contextFactory)

   reactor.run()
