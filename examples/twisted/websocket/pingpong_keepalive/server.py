###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
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

from autobahn.twisted.resource import WebSocketResource



if __name__ == '__main__':

   log.startLogging(sys.stdout)

   factory = WebSocketServerFactory("ws://localhost:9000", debug = False, debugCodePaths = True)
   factory.protocol = WebSocketServerProtocol

   factory.setProtocolOptions(autoPingInterval = 1, autoPingTimeout = 3, autoPingSize = 20)

   listenWS(factory)

   resource = WebSocketResource(factory)

   root = File(".")
   root.putChild("ws", resource)
   site = Site(root)

   reactor.listenTCP(8080, site)

   reactor.run()
