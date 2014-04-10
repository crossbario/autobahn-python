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
import datetime

import asyncio

from autobahn.wamp.router import RouterFactory

from autobahn.asyncio.wamp import ApplicationSession
from autobahn.asyncio.wamp import RouterSessionFactory
from autobahn.asyncio.websocket import WampWebSocketServerFactory


class MyBackendComponent(ApplicationSession):
   """
   Application code goes here. This is an example component that provides
   a simple procedure which can be called remotely from any WAMP peer.
   It also publishes an event every second to some topic.
   """
   def onConnect(self):
      print("aaaa")
      self.join(u"realm1")
      print("6666")

   def onJoin2(self, details):
      print("555")

      ## register a procedure for remote calling
      ##
      def utcnow():
         print("Someone is calling me;)")
         now = datetime.datetime.utcnow()
         return now.strftime("%Y-%m-%dT%H:%M:%SZ")

      self.register(utcnow, u'com.timeservice.now')


   @asyncio.coroutine
   def onJoin(self, details):
      print("555")

      ## register a procedure for remote calling
      ##
      def utcnow():
         print("Someone is calling me;)")
         now = datetime.datetime.utcnow()
         return now.strftime("%Y-%m-%dT%H:%M:%SZ")

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

   import asyncio

   ## 1) create a WAMP router factory
   router_factory = RouterFactory()

   ## 2) create a WAMP router session factory
   session_factory = RouterSessionFactory(router_factory)

   ## 3) Optionally, add embedded WAMP application sessions to the router
   session_factory.add(MyBackendComponent())

   ## 4) create a WAMP-over-WebSocket transport server factory
   transport_factory = WampWebSocketServerFactory(session_factory, debug = True, debug_wamp = True)

   ## 5) start the server
   loop = asyncio.get_event_loop()
   coro = loop.create_server(transport_factory, '127.0.0.1', 8080)
   server = loop.run_until_complete(coro)

   try:
      print("sdfsdf")
      ## 6) now enter the asyncio event loop
      loop.run_forever()
   except KeyboardInterrupt:
      pass
   finally:
      server.close()
      loop.close()
