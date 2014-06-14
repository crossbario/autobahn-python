###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
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
import six
import datetime

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import serverFromString
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.wamp import router, types
from autobahn.twisted.util import sleep
from autobahn.twisted import wamp, websocket
from autobahn.twisted.resource import WebSocketResource
from autobahn.wamp.http import WampHttpResource



class MyBackendComponent(wamp.ApplicationSession):

   @inlineCallbacks
   def onJoin(self, details):

      counter = 0
      while True:
         self.publish(u'com.myapp.topic1', counter)
         print("Published event.")
         counter += 1
         yield sleep(2)



if __name__ == '__main__':

   log.startLogging(sys.stdout)

   router_factory = router.RouterFactory()
   session_factory = wamp.RouterSessionFactory(router_factory)

   component_config = types.ComponentConfig(realm = "realm1")
   component_session = MyBackendComponent(component_config)
   session_factory.add(component_session)

   ws_factory = websocket.WampWebSocketServerFactory(session_factory, \
                                                     debug = False, \
                                                     debug_wamp = False)
   ws_factory.startFactory()

   ws_resource = WebSocketResource(ws_factory)
   lp_resource = WampHttpResource(session_factory, debug = True, debug_session_id = "kjmd3sBLOUnb3Fyr")

   root = File(".")
   root.putChild("ws", ws_resource)
   root.putChild("lp", lp_resource)

   web_factory = Site(root)
   web_factory.noisy = False

   server = serverFromString(reactor, "tcp:8080")
   server.listen(web_factory)

   reactor.run()
