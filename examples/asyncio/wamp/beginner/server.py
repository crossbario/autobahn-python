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
import asyncio

from autobahn.wamp import router
from autobahn.asyncio import wamp, websocket



class MyBackendComponent(wamp.ApplicationSession):
   """
   Application code goes here. This is an example component that provides
   a simple procedure which can be called remotely from any WAMP peer.
   It also publishes an event every second to some topic.
   """
   def onConnect(self):
      self.join(u"realm1")

   @asyncio.coroutine
   def onJoin(self, details):
      ## register a procedure for remote calling
      ##
      def utcnow():
         print("Someone is calling me;)")
         now = datetime.datetime.utcnow()
         return six.u(now.strftime("%Y-%m-%dT%H:%M:%SZ"))

      reg = yield from self.register(utcnow, u'com.timeservice.now')
      print("Registered procedure: {}".format(reg.id))

      ## publish events to a topic
      ##
      counter = 0
      while True:
         self.publish(u'com.myapp.topic1', counter)
         print("Published event.")
         counter += 1
         yield from asyncio.sleep(1)


if __name__ == '__main__':

   ## 1) create a WAMP router factory
   router_factory = router.RouterFactory()

   ## 2) create a WAMP router session factory
   session_factory = wamp.RouterSessionFactory(router_factory)

   ## 3) Optionally, add embedded WAMP application sessions to the router
   session_factory.add(MyBackendComponent())

   ## 4) create a WAMP-over-WebSocket transport server factory
   transport_factory = websocket.WampWebSocketServerFactory(session_factory,
                                                            debug = False,
                                                            debug_wamp = False)

   ## 5) start the server
   loop = asyncio.get_event_loop()
   coro = loop.create_server(transport_factory, '127.0.0.1', 8080)
   server = loop.run_until_complete(coro)

   try:
      ## 6) now enter the asyncio event loop
      loop.run_forever()
   except KeyboardInterrupt:
      pass
   finally:
      server.close()
      loop.close()
