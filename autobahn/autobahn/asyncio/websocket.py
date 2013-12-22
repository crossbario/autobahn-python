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

from autobahn.websocket import protocol



class WebSocketServerProtocol(protocol.WebSocketServerProtocol, asyncio.Protocol):

   def connection_made(self, transport):
      self.transport = transport

      peer = transport.get_extra_info('peername')
      try:
         self.peer = "%s:%d" % (peer[0], peer[1])
      except:
         ## eg Unix Domain sockets don't have host/port
         self.peer = str(peer)

      protocol.WebSocketServerProtocol.connectionMade(self)


   def connection_lost(self, exc):
      self.connectionLost(exc)


   def data_received(self, data):
      self.dataReceived(data)


   def _closeConnection(self, abort = False):
      self.transport.close()


   def _run_onConnect(self, connectionRequest):
      res = self.onConnect(connectionRequest)
      self._processHandshake_buildResponse(res)


   def registerProducer(self, producer, streaming):
      raise Exception("not implemented")



class WebSocketServerFactory(protocol.WebSocketServerFactory):

   def __init__(self, *args, **kwargs):

      protocol.WebSocketServerFactory.__init__(self, *args, **kwargs)

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
