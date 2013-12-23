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


   #@asyncio.coroutine
   def _onConnect(self, connectionRequest):
      ## onConnect() will return the selected subprotocol or None
      ## or a pair (protocol, headers) or raise an HttpException
      ##
      try:
         print("-"*10)
         #res = yield from self.onConnect(connectionRequest)
         res = self.onConnect(connectionRequest)
         print(res)
         print("*"*10)
         #if yields(res):
         #   print("here")
         #   res = yield from res
         #else:
         #   print("NOOO")
      except http.HttpException as exc:
         print(exc)
         self.failHandshake(exc.reason, exc.code)
      except Exception as exc:
         print(exc)
         self.failHandshake(http.INTERNAL_SERVER_ERROR[1], http.INTERNAL_SERVER_ERROR[0])
      else:
         self.succeedHandshake(res)


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
