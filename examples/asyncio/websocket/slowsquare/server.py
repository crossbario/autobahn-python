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

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory

import asyncio
import json


class SlowSquareServerProtocol(WebSocketServerProtocol):

   @asyncio.coroutine
   def slowsquare(self, x):
      if x > 5:
         raise Exception("number too large")
      else:
         yield from asyncio.sleep(1)
         return x * x

   @asyncio.coroutine
   def onMessage(self, payload, isBinary):
      if not isBinary:
         x = json.loads(payload.decode('utf8'))
         try:
            res = yield from self.slowsquare(x)
         except Exception as e:
            self.sendClose(1000, "Exception raised: {}".format(e))
         else:
            self.sendMessage(json.dumps(res).encode('utf8'))



if __name__ == '__main__':

   try:
      import asyncio
   except ImportError:
      ## Trollius >= 0.3 was renamed
      import trollius as asyncio

   factory = WebSocketServerFactory("ws://localhost:9000", debug = False)
   factory.protocol = SlowSquareServerProtocol

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
