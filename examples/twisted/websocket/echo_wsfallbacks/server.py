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
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol, \
                                       listenWS

from autobahn.twisted.flashpolicy import FlashPolicyFactory



class EchoServerProtocol(WebSocketServerProtocol):

   def onMessage(self, payload, isBinary):
      self.sendMessage(payload, isBinary)



if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   wsPort = 9000

   ## Our WebSocket server
   ##
   factory = WebSocketServerFactory("ws://localhost:%d" % wsPort,
                                    debug = debug,
                                    debugCodePaths = debug)

   factory.protocol = EchoServerProtocol
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)

   ## We need to start a "Flash Policy Server" on TCP/843
   ## which Adobe Flash player will contact to check if
   ## it is allowed to connect to the WebSocket port.
   ##
   flashPolicyFactory = FlashPolicyFactory()
   reactor.listenTCP(843, flashPolicyFactory)

   ## Static Web server
   ##
   webdir = File("./web")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
