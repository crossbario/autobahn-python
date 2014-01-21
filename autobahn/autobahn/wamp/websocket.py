###############################################################################
##
##  Copyright (C) 2013-2014 Tavendo GmbH
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

from __future__ import absolute_import


__all__= ['WampServerProtocol',
          'WampClientProtocol',
          'WampServerFactory',
          'WampClientFactory']


from autobahn.websocket import http

from autobahn.wamp.serializer import JsonSerializer, MsgPackSerializer
from autobahn.wamp.exception import ProtocolError


def parseSubprotocolIdentifier(subprotocol):
   try:
      s = subprotocol.split('.')
      if s[0] != "wamp":
         raise Exception("invalid protocol %s" % s[0])
      version = int(s[1])
      serializerId = s[2]
      return version, serializerId
   except:
      return None, None


class WampProtocol:

   def onOpen(self):
      self._proto = self.factory._factory()
      self._proto.onOpen(self)

   def onClose(self, wasClean, code, reason):
      self._proto.onClose()
      self._proto = None

   def send(self, msg):
      bytes, isBinary = self._serializer.serialize(msg)
      self.sendMessage(bytes, isBinary)

   def onMessage(self, bytes, isBinary):
      try:
         msg = self._serializer.unserialize(bytes, isBinary)
      except ProtocolError as e:
         print("WAMP protocol error: %s" % e)
      else:
         self._proto.onMessage(msg)



class WampServerProtocol(WampProtocol):

   def onConnect(self, connectionRequest):
      headers = {}
      for subprotocol in connectionRequest.protocols:
         version, serializerId = parseSubprotocolIdentifier(subprotocol)
         if version == 2 and serializerId in self.factory._serializers.keys():
            self._serializer = self.factory._serializers[serializerId]
            return subprotocol, headers

      raise http.HttpException(http.BAD_REQUEST[0], "This server only speaks WebSocket subprotocols %s" % ', '.join(self.factory.protocols))



class WampClientProtocol(WampProtocol):

   def onConnect(self, connectionResponse):
      if connectionResponse.protocol not in self.factory.protocols:
         raise Exception("Server does not speak any of the WebSocket subprotocols we requested (%s)." % ', '.join(self.factory.protocols))

      version, serializerId = parseSubprotocolIdentifier(connectionResponse.protocol)
      self._serializer = self.factory._serializers[serializerId]



class WampServerFactory:

   def __init__(self, factory, serializers = None):

      assert(callable(factory))
      self._factory = factory

      if serializers is None:
         serializers = [MsgPackSerializer(), JsonSerializer()]

      self._serializers = {}
      for ser in serializers:
         self._serializers[ser.SERIALIZER_ID] = ser

      self._protocols = ["wamp.2.%s" % ser.SERIALIZER_ID for ser in serializers]



class WampClientFactory:

   def __init__(self, factory, serializers = None):

      assert(callable(factory))
      self._factory = factory

      if serializers is None:
         serializers = [MsgPackSerializer(), JsonSerializer()]

      self._serializers = {}
      for ser in serializers:
         self._serializers[ser.SERIALIZER_ID] = ser

      self._protocols = ["wamp.2.%s" % ser.SERIALIZER_ID for ser in serializers]
