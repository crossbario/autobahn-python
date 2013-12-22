###############################################################################
##
##  Copyright 2013 Tavendo GmbH
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



class MyServerProtocol(WebSocketServerProtocol):

   def onMessage(self, payload, isBinary):
      print("message received")
      self.sendMessage(payload)

   def onConnect(self, connectionRequest):
      return None


class MyServerFactory(WebSocketServerFactory):

   protocol = MyServerProtocol



if __name__ == '__main__':

   import asyncio

   factory = MyServerFactory()

   loop = asyncio.get_event_loop()
   coro = loop.create_server(factory, '127.0.0.1', 8888)
   server = loop.run_until_complete(coro)

   print('serving on {}'.format(server.sockets[0].getsockname()))

   try:
      loop.run_forever()
   except KeyboardInterrupt:
      print("exit")
   finally:
      server.close()
      loop.close()
