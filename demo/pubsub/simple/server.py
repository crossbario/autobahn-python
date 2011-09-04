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

import sys, math
from twisted.python import log
from twisted.internet import reactor, defer
from autobahn.autobahn import exportRpc, AutobahnServerFactory, AutobahnServerProtocol


class SomeService:

   @exportSub("event1")
   def subscribeEvent1(self):
      return True
   
   @exportPub("event1")
   def publishEvent1(self, event):
      pass


class Tiles:
   
   @exportPub("tile-erased")
   def subscribeTileErased(self, tilemapUri, sectorX, sectorY):
      pass

   @exportPub("tile-erased")
   def publishTileErased(self, tilemapUri, tileX, tileY):
      sectorX = tileX / 16
      sectorY = tileY / 16

   
class SimpleServerProtocol(AutobahnServerProtocol):

   BASEURI = "http://resource.example.com/schema/event#"
   
   def onConnect(self, connectionRequest):
      
      ## register a URI as topic
      self.registerForPubSub(SimpleServerProtocol.BASEURI + "event0")

      ## register a service handler to provide topic
      self.someservice = SomeService()
      self.registerForPubSub(self.someservice, SimpleServerProtocol.BASEURI)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = AutobahnServerFactory(debug = False)
   factory.protocol = SimpleServerProtocol
   reactor.listenTCP(9000, factory)
   reactor.run()
