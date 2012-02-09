###############################################################################
##
##  Copyright 2012 Tavendo GmbH
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
from autobahn.websocket import listenWS
from autobahn.wamp import exportRpc, WampServerFactory, WampServerProtocol


class MyServerProtocol(WampServerProtocol):

   @exportRpc
   def echo(self, msg):
      return msg

   def onSessionOpen(self):
      self.registerForRpc(self, "http://example.com/api#")
      self.registerForPubSub("http://example.com/event#", True)


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   factory = WampServerFactory("ws://localhost:9000", debug = False, debugCodePaths = False, debugWamp = True)
   factory.protocol = MyServerProtocol
   listenWS(factory)

   webdir = File(".")
   webdir.putChild("autobahn.js", File("../../lib/javascript/autobahn.js"))
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
