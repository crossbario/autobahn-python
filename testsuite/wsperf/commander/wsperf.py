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

from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               listenWS

from autobahn.wamp import exportRpc, \
                          WampServerFactory, \
                          WampServerProtocol


URI_RPC = "http://wsperf.org/api#"
URI_EVENT = "http://wsperf.org/event#"



class WsPerfProtocol(WebSocketServerProtocol):

   def onConnect(self, connectionRequest):
      self.factory.uiFactory.slaveConnected()
      return "wsperf"

   def onMessage(self, msg, binary):
      print msg


class WsPerfFactory(WebSocketServerFactory):

   protocol = WsPerfProtocol



class WsPerfUiProtocol(WampServerProtocol):

   @exportRpc
   def sum(self, list):
      return reduce(lambda x, y: x + y, list)

   def onSessionOpen(self):
      self.registerForRpc(self, URI_RPC)
      self.registerForPubSub(URI_EVENT, True)
      #reactor.callLater(1, self.slaveConnected)


class WsPerfUiFactory(WampServerFactory):

   protocol = WsPerfUiProtocol

   def slaveConnected(self):
      self._dispatchEvent(URI_EVENT + "slaveConnected", "foobar")



if __name__ == '__main__':

   log.startLogging(sys.stdout)

   ## WAMP Server for wsperf slaves
   ##
   wsperf = WsPerfFactory("ws://localhost:9090")
   #wsperf.debug = True
   listenWS(wsperf)

   ## Web Server for UI static files
   ##
   webdir = File("static")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   ## WAMP Server for UI
   ##
   wsperfUi = WsPerfUiFactory("ws://localhost:9091")
   listenWS(wsperfUi)

   ## Connect servers
   ##
   wsperf.uiFactory = wsperfUi
   wsperfUi.slaveFactory = wsperf

   ## Run everything ..
   ##
   reactor.run()
