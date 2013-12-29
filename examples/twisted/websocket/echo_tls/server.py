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

from twisted.internet import reactor, ssl
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol, \
                                       listenWS


class EchoServerProtocol(WebSocketServerProtocol):

   def onMessage(self, payload, isBinary):
      self.sendMessage(payload, isBinary)


if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   ## SSL server context: load server key and certificate
   ## We use this for both WS and Web!
   ##
   contextFactory = ssl.DefaultOpenSSLContextFactory('keys/server.key',
                                                     'keys/server.crt')

   factory = WebSocketServerFactory("wss://localhost:9000",
                                    debug = debug,
                                    debugCodePaths = debug)

   factory.protocol = EchoServerProtocol
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory, contextFactory)

   webdir = File(".")
   webdir.contentTypes['.crt'] = 'application/x-x509-ca-cert'
   web = Site(webdir)
   #reactor.listenSSL(8080, web, contextFactory)
   reactor.listenTCP(8080, web)

   reactor.run()
