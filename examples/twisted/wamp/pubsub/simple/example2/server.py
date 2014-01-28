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

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import listenWS

from autobahn.wamp1.protocol import WampServerFactory, \
                                    WampServerProtocol


class MyServerProtocol(WampServerProtocol):

   def onSessionOpen(self):

      ## register a single, fixed URI as PubSub topic
      self.registerForPubSub("http://example.com/simple")

      ## register a URI and all URIs having the string as prefix as PubSub topic
      self.registerForPubSub("http://example.com/event#", True)

      ## register any URI (string) as topic
      #self.registerForPubSub("", True)


if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WampServerFactory("ws://localhost:9000", debugWamp = True)
   factory.protocol = MyServerProtocol
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
