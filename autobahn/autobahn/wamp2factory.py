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

from websocket import WebSocketServerFactory, WebSocketClientFactory

from wamp2protocol import Wamp2ServerProtocol, Wamp2ClientProtocol
from wamp2message import JsonDefaultSerializer, WampSerializer



class Wamp2Factory:

   def __init__(self, serializer = None):
      if serializer is None:
         serializer = JsonDefaultSerializer()
      self._serializer = WampSerializer(serializer)



class Wamp2ServerFactory(WebSocketServerFactory, Wamp2Factory):

   protocol = Wamp2ServerProtocol

   def __init__(self,
                url,
                debugWs = False,
                serializer = None,
                reactor = None):
      WebSocketServerFactory.__init__(self,
                                      url,
                                      debug = debugWs,
                                      protocols = ["wamp2"],
                                      reactor = reactor)
      Wamp2Factory.__init__(self, serializer)



class Wamp2ClientFactory(WebSocketClientFactory, Wamp2Factory):

   protocol = Wamp2ClientProtocol

   def __init__(self,
                url,
                debugWs = False,
                serializer = None,
                reactor = None):
      WebSocketClientFactory.__init__(self,
                                      url,
                                      debug = debugWs,
                                      protocols = ["wamp2"],
                                      reactor = reactor)
      Wamp2Factory.__init__(self, serializer)
