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

from zope.interface import implementer

import autobahn
from autobahn.websocket import protocol
from autobahn.websocket import http

from autobahn.wamp.interfaces import ITransport, ISerializer
from autobahn.wamp.exception import ProtocolError, SerializationError, TransportLost



@implementer(ITransport)
class WampWebSocketProtocol:
   """
   Base class for WAMP-over-WebSocket transport mixins.
   """

   def onOpen(self):
      """
      Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onOpen`
      """
      ## WebSocket connection established - now let the
      ## user WAMP session factory create a new WAMP session ..
      self._session = self.factory._factory()

      ## and fire off WAMP session open callback
      try:
         self._session.onOpen(self)
      except Exception as e:
         ## Exceptions raised in onOpen are fatal ..
         reason = "WAMP Internal Error ({})".format(e)
         self.failConnection(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_INTERNAL_ERROR, reason = reason)


   def onClose(self, wasClean, code, reason):
      """
      Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onClose`
      """
      ## WebSocket connection lost - fire off the WAMP
      ## session close callback
      try:
#         print("WebSocket Transport lost ({}, {}, {})".format(wasClean, code, reason))
         self._session.onClose(wasClean)
      except Exception as e:
         ## silently ignore exceptions raised here ..
         pass
      self._session = None


   def onMessage(self, bytes, isBinary):
      """
      Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessage`
      """
      try:
         msg = self._serializer.unserialize(bytes, isBinary)
         self._session.onMessage(msg)

      except ProtocolError as e:
         reason = "WAMP Protocol Error ({})".format(e)
         self.failConnection(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, reason = reason)

      except Exception as e:
         reason = "WAMP Internal Error ({})".format(e)
         self.failConnection(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_INTERNAL_ERROR, reason = reason)


   def send(self, msg):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransport.send`
      """
      if self.isOpen():
         try:
            bytes, isBinary = self._serializer.serialize(msg)
         except Exception as e:
            ## all exceptions raised from above should be serialization errors ..
            raise SerializationError("Unable to serialize WAMP application payload ({})".format(e))
         else:
            self.sendMessage(bytes, isBinary)
      else:
         raise TransportLost()


   def isOpen(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransport.isOpen`
      """
      return self._session is not None


   def close(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransport.close`
      """
      if self.isOpen():
         self.sendClose(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_NORMAL)
      else:
         raise TransportLost()


   def abort(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransport.abort`
      """
      if self.isOpen():
         self.failConnection(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_GOING_AWAY, reason = reason)
      else:
         raise TransportLost()



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



class WampWebSocketServerProtocol(WampWebSocketProtocol):
   """
   Mixin for WAMP-over-WebSocket server transports.
   """

   STRICT_PROTOCOL_NEGOTIATION = True

   def onConnect(self, request):
      """
      Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onConnect`
      """
      headers = {}
      for subprotocol in request.protocols:
         version, serializerId = parseSubprotocolIdentifier(subprotocol)
         if version == 2 and serializerId in self.factory._serializers.keys():
            self._serializer = self.factory._serializers[serializerId]
            return subprotocol, headers

      if self.STRICT_PROTOCOL_NEGOTIATION:
         raise http.HttpException(http.BAD_REQUEST[0], "This server only speaks WebSocket subprotocols %s" % ', '.join(self.factory.protocols))
      else:
         ## assume wamp.2.json
         self._serializer = self.factory._serializers['json']
         return None, headers



class WampWebSocketClientProtocol(WampWebSocketProtocol):
   """
   Mixin for WAMP-over-WebSocket client transports.
   """

   STRICT_PROTOCOL_NEGOTIATION = True

   def onConnect(self, response):
      """
      Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onConnect`
      """
      if response.protocol not in self.factory.protocols:
         if self.STRICT_PROTOCOL_NEGOTIATION:
            raise Exception("Server does not speak any of the WebSocket subprotocols we requested (%s)." % ', '.join(self.factory.protocols))
         else:
            ## assume wamp.2.json
            serializerId = 'json'
      else:
         version, serializerId = parseSubprotocolIdentifier(response.protocol)
      
      self._serializer = self.factory._serializers[serializerId]



class WampWebSocketFactory:
   """
   Base class for WAMP-over-WebSocket transport factory mixins.
   """

   def __init__(self, factory, serializers = None):
      """
      :param factory: A callable that produces instances that implement
                      :class:`autobahn.wamp.interfaces.ITransportHandler`
      :type factory: callable
      :param serializers: A list of WAMP serializers to use (or None for default
                          serializers). Serializers must implement
                         :class:`autobahn.wamp.interfaces.ISerializer`.
      type serializers: list
      """
      assert(callable(factory))
      self._factory = factory

      if serializers is None:
         serializers = []

         ## try MsgPack WAMP serializer
         try:
            from autobahn.wamp.serializer import MsgPackSerializer
            serializers.append(MsgPackSerializer())
         except:
            pass

         ## try JSON WAMP serializer
         try:
            from autobahn.wamp.serializer import JsonSerializer
            serializers.append(JsonSerializer())
         except:
            pass

         if not serializers:
            raise Exception("could not import any WAMP serializers")

      self._serializers = {}
      for ser in serializers:
         self._serializers[ser.SERIALIZER_ID] = ser

      self._protocols = ["wamp.2.%s" % ser.SERIALIZER_ID for ser in serializers]



class WampWebSocketServerFactory(WampWebSocketFactory):
   """
   Mixin for WAMP-over-WebSocket server transport factories.
   """



class WampWebSocketClientFactory(WampWebSocketFactory):
   """
   Mixin for WAMP-over-WebSocket client transport factories.
   """
