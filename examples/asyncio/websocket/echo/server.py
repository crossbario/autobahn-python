###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
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

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory


import asyncio
from autobahn.websocket import http
import math

class MyServerProtocol(WebSocketServerProtocol):

   @asyncio.coroutine
   def slow_sqrt(self, x):
      yield from asyncio.sleep(0.6)
      return math.sqrt(x)

   def onConnect(self, request):
      print("Client connecting: {}".format(request.peer))
      #yield from asyncio.sleep(0.8)
      return None
      #raise Exception("denied")
      #raise http.HttpException(http.UNAUTHORIZED[0], "You are now allowed.")

   def onOpen(self):
      print("WebSocket connection open.")

   @asyncio.coroutine
   def foo(self):
      res = yield from self.slow_sqrt(2)
      self.sendMessage("hello {}".format(res).encode('utf8'))

   #@asyncio.coroutine
   def onMessage(self, payload, isBinary):
      if isBinary:
         print("Binary message received: {} bytes".format(len(payload)))
      else:
         print("Text message received: {}".format(payload.decode('utf8')))

      #asyncio.async(self.foo())
      res = yield from self.slow_sqrt(2)
      self.sendMessage("hello {}".format(res).encode('utf8'))
      ## echo back message verbatim
      self.sendMessage(payload, isBinary)

   def onClose(self, wasClean, code, reason):
      print("WebSocket connection closed: {}".format(reason))



if __name__ == '__main__':

   import asyncio

   factory = WebSocketServerFactory("ws://localhost:9000", debug = False)
   factory.protocol = MyServerProtocol

   loop = asyncio.get_event_loop()
   coro = loop.create_server(factory, '127.0.0.1', 9000)
   server = loop.run_until_complete(coro)

   try:
      loop.run_forever()
   except KeyboardInterrupt:
      pass
   finally:
      server.close()
      loop.close()
