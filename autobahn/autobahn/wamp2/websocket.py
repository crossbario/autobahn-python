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

__all__= ['WampWebSocketServerProtocol',
          'WampWebSocketClientProtocol',
          'WampWebSocketServerFactory',
          'WampWebSocketClientFactory']


from autobahn.websocket import WebSocketServerProtocol, \
                               WebSocketServerFactory, \
                               WebSocketClientProtocol, \
                               WebSocketClientFactory

from autobahn.websocket import HttpException
from autobahn.httpstatus import HTTP_STATUS_CODE_BAD_REQUEST

from protocol import WampProtocol
from serializer import WampJsonSerializer, WampMsgPackSerializer



def _parse_subprotocol(subprotocol):
   try:
      s = subprotocol.split('.')
      if s[0] != "wamp":
         raise Exception()
      version = int(s[1])
      serializerId = s[2]
      return version, serializerId
   except:
      return None, None



class WampWebSocketServerProtocol(WampProtocol, WebSocketServerProtocol):

   def onConnect(self, connectionRequest):
      headers = {}
      for subprotocol in connectionRequest.protocols:
         version, serializerId = _parse_subprotocol(subprotocol)
         if version == 2 and serializerId in self.factory._serializers.keys():
            self._serializer = self.factory._serializers[serializerId]
            return subprotocol, headers

      raise HttpException(HTTP_STATUS_CODE_BAD_REQUEST[0], "This server only speaks WebSocket subprotocols %s" % ', '.join(self.factory.protocols))




class WampWebSocketClientProtocol(WampProtocol, WebSocketClientProtocol):

   def onConnect(self, connectionResponse):
      if connectionResponse.protocol not in self.factory.protocols:
         raise Exception("Server does not speak any of the WebSocket subprotocols we requested (%s)." % ', '.join(self.factory.protocols))

      version, serializerId = _parse_subprotocol(connectionResponse.protocol)
      self._serializer = self.factory._serializers[serializerId]



class WampWebSocketServerFactory(WebSocketServerFactory):

   protocol = WampWebSocketServerProtocol

   def __init__(self,
                url,
                debug = False,
                serializers = None,
                reactor = None):

      if serializers is None:
         serializers = [WampMsgPackSerializer(), WampJsonSerializer()]

      self._serializers = {}
      for ser in serializers:
         self._serializers[ser.SERIALIZER_ID] = ser

      protocols = ["wamp.2.%s" % ser.SERIALIZER_ID for ser in serializers]

      WebSocketServerFactory.__init__(self,
                                      url,
                                      debug = debug,
                                      protocols = protocols,
                                      reactor = reactor)



class WampWebSocketClientFactory(WebSocketClientFactory):

   protocol = WampWebSocketClientProtocol

   def __init__(self,
                url,
                debug = False,
                serializers = None,
                reactor = None):

      if serializers is None:
         serializers = [WampMsgPackSerializer(), WampJsonSerializer()]

      self._serializers = {}
      for ser in serializers:
         self._serializers[ser.SERIALIZER_ID] = ser

      protocols = ["wamp.2.%s" % ser.SERIALIZER_ID for ser in serializers]

      WebSocketClientFactory.__init__(self,
                                      url,
                                      debug = debug,
                                      protocols = protocols,
                                      reactor = reactor)
