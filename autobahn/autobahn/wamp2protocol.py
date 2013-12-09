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

from websocket import WebSocketProtocol, HttpException, Timings
from websocket import WebSocketServerProtocol, WebSocketClientProtocol

from httpstatus import HTTP_STATUS_CODE_BAD_REQUEST
from util import utcnow, newid

from wamp2message import *


## incoming client connections
## incoming broker connections
## outgoing broker connections

class Wamp2Protocol:

   def onSessionOpen(self):
      """
      Callback fired when WAMP session was fully established.
      """
      pass

   def onOpen(self):
      print "X"*100
      self._sessionid = newid()
      self.onSessionOpen()

   def onClose(self, wasClean, code, reason):
      pass

   def onMessage(self, bytes, binary):
      #print bytes
      msg = self.factory._serializer.unserialize(bytes)
      #print msg.__class__
      print msg


   def subscribe(self, topic, handler):
      #print topic, handler
      msg = WampMessageSubscribe(topic)
      bytes = self.factory._serializer.serialize(msg)
      self.sendMessage(bytes)


   def publish(self, topic, event):
      print topic, event
      msg = WampMessagePublish(topic, event)
      bytes = self.factory._serializer.serialize(msg)
      self.sendMessage(bytes)


   # def connectionMade(self):
   #    pass


   # def connectionLost(self, reason):
   #    pass



class Wamp2ServerProtocol(Wamp2Protocol, WebSocketServerProtocol):

   def onConnect(self, connectionRequest):
      """
      Default implementation for WAMP connection acceptance:
      check if client announced WAMP subprotocol, and only accept connection
      if client did so.
      """
      if 'wamp2' in connectionRequest.protocols:
         return ('wamp2', {}) # (protocol, headers)
      else:
         raise HttpException(HTTP_STATUS_CODE_BAD_REQUEST[0], "this server only speaks WAMP2")


   # def connectionMade(self):
   #    WebSocketServerProtocol.connectionMade(self)
   #    Wamp2Protocol.connectionMade(self)


   # def connectionLost(self, reason):
   #    Wamp2Protocol.connectionLost(self, reason)
   #    WebSocketServerProtocol.connectionLost(self, reason)





class Wamp2ClientProtocol(Wamp2Protocol, WebSocketClientProtocol):

   def onConnect(self, connectionResponse):
      if connectionResponse.protocol not in self.factory.protocols:
         raise Exception("server does not speak WAMP2")


   # def connectionMade(self):
   #    WebSocketClientProtocol.connectionMade(self)
   #    Wamp2Protocol.connectionMade(self)


   # def connectionLost(self, reason):
   #    Wamp2Protocol.connectionLost(self, reason)
   #    WebSocketClientProtocol.connectionLost(self, reason)
