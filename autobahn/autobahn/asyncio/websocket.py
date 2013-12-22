###############################################################################
##
##  Copyright 2011-2013 Tavendo GmbH
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

import asyncio

from autobahn import websocket




class WebSocketServerProtocol(websocket.WebSocketServerProtocol, asyncio.Protocol):

   def connection_made(self, transport):
      self.transport = transport
      self.peer = transport.get_extra_info('peername')
      websocket.WebSocketServerProtocol.connectionMade(self)


   def data_received(self, data):
      self.dataReceived(data)


   def _closeConnection(self, abort = False):
      self.transport.close()


   def _run_onConnect(self, connectionRequest):
      self._processHandshake_buildResponse(None)


   def registerProducer(self, producer, streaming):
      raise Exception("not implemented")



class WebSocketServerFactory(websocket.WebSocketServerFactory):

   def __init__(self, *args, **kwargs):

      websocket.WebSocketServerFactory.__init__(self, *args, **kwargs)

      if 'loop' in kwargs:
         self.loop = kwargs['loop']
      else:
         self.loop = asyncio.get_event_loop()


   def _log(self, msg):
      print(msg)


   def _callLater(self, delay, fun):
      return self.loop.call_later(delay, fun)


   def __call__(self):
      proto = self.protocol()
      proto.factory = self
      return proto
