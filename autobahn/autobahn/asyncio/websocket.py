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

__all__ = ['WebSocketServerProtocol',
           'WebSocketServerFactory',
           'WebSocketClientProtocol',
           'WebSocketClientFactory']

import asyncio
import inspect
from collections import deque

from autobahn.websocket import protocol
from autobahn.websocket import http


def yields(value):
   """
   Return True iff the value yields.

   See: http://stackoverflow.com/questions/20730248/maybedeferred-analog-with-asyncio
   """
   return isinstance(value, asyncio.futures.Future) or inspect.isgenerator(value)



class WebSocketServerProtocol(protocol.WebSocketServerProtocol, asyncio.Protocol):
   """
   Base class for Asyncio WebSocket server protocols.
   """

   def connection_made(self, transport):
      self.transport = transport

      self.receive_queue = deque()
      asyncio.Task(self._consume())

      peer = transport.get_extra_info('peername')
      try:
         self.peer = "%s:%d" % (peer[0], peer[1])
      except:
         ## eg Unix Domain sockets don't have host/port
         self.peer = str(peer)

      protocol.WebSocketServerProtocol.connectionMade(self)


   def connection_lost(self, exc):
      self.connectionLost(exc)


   def _consume(self):
      while True:
         self.waiter = asyncio.Future()
         yield from self.waiter
         while len(self.receive_queue):
            data = self.receive_queue.popleft()
            if self.transport:
               try:
                  self.dataReceived(data)
               except Exception as e:
                  raise e


   def data_received(self, data):
      self.receive_queue.append(data)
      if not self.waiter.done():
         self.waiter.set_result(None)


   def _closeConnection(self, abort = False):
      self.transport.close()


   def _onConnect(self, connectionRequest):
      ## onConnect() will return the selected subprotocol or None
      ## or a pair (protocol, headers) or raise an HttpException
      ##
      try:
         res = self.onConnect(connectionRequest)
         #if yields(res):
         #  res = yield from res
      except http.HttpException as exc:
         self.failHandshake(exc.reason, exc.code)
      except Exception as exc:
         self.failHandshake(http.INTERNAL_SERVER_ERROR[1], http.INTERNAL_SERVER_ERROR[0])
      else:
         self.succeedHandshake(res)


   def _onOpen(self):
      res = self.onOpen()
      if yields(res):
         asyncio.async(res)


   def _onMessage(self, payload, isBinary):
      res = self.onMessage(payload, isBinary)
      if yields(res):
         asyncio.async(res)


   def _onClose(self, wasClean, code, reason):
      res = self.onClose(self, wasClean, code, reason)
      if yields(res):
         asyncio.async(res)


   def registerProducer(self, producer, streaming):
      raise Exception("not implemented")



class WebSocketServerFactory(protocol.WebSocketServerFactory):
   """
   Base class for Asyncio WebSocket server factories.
   """

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



class WebSocketClientProtocol(protocol.WebSocketClientProtocol, asyncio.Protocol):
   """
   Base class for Asyncio WebSocket client protocols.
   """

   def connection_made(self, transport):
      self.transport = transport

      peer = transport.get_extra_info('peername')
      try:
         self.peer = "%s:%d" % (peer[0], peer[1])
      except:
         ## eg Unix Domain sockets don't have host/port
         self.peer = str(peer)

      protocol.WebSocketClientProtocol.connectionMade(self)


   def connection_lost(self, exc):
      self.connectionLost(exc)


   def data_received(self, data):
      self.dataReceived(data)


   def _closeConnection(self, abort = False):
      self.transport.close()


   def registerProducer(self, producer, streaming):
      raise Exception("not implemented")



class WebSocketClientFactory(protocol.WebSocketClientFactory):
   """
   Base class for Asyncio WebSocket client factories.
   """

   def __init__(self, *args, **kwargs):

      protocol.WebSocketClientFactory.__init__(self, *args, **kwargs)

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
