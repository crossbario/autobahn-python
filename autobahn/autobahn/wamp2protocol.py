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
      self._subscriptions = {}
      self._calls = {}
      self.onSessionOpen()


   def onClose(self, wasClean, code, reason):
      pass


   def onMessage(self, bytes, binary):
      #print bytes
      try:
         msg = self.factory._serializer.unserialize(bytes)
      except WampProtocolError, e:
         print "WAMP protocol error", e
      else:
         if isinstance(msg, WampMessageEvent):
            if self._subscriptions.has_key(msg.topic):
               for handler in self._subscriptions[msg.topic]:
                  handler(msg.topic, msg.event)
            else:
               pass

         elif isinstance(msg, WampMessageCallProgress):
            pass

         elif isinstance(msg, WampMessageCallResult):
            d = self._calls.pop(msg.callid, None)
            if d:
               d.callback(msg.result)
            else:
               pass

         elif isinstance(msg, WampMessageCallError):
            d = self._calls.pop(msg.callid, None)
            if d:
               e = WampCallException(msg.error, msg.message, msg.value)
               d.errback(e)
            else:
               pass

         else:
            raise Exception("not implemented")


   def call(self, *args):
      """
      Call an endpoint.
      """
      if len(args) < 1:
         raise Exception("missing RPC endpoint URI")

      endpoint = args[0]

      while True:
         callid = newid()
         if not self._calls.has_key(callid):
            break

      msg = WampMessageCall(callid, endpoint, args = args[1:])
      try:
         bytes = self.factory._serializer.serialize(msg)
      except:
         raise Exception("call argument(s) not serializable")

      def canceller(_d):
         msg = WampMessageCancelCall(callid)
         bytes = self.factory._serializer.serialize(msg)
         self.sendMessage(bytes)

      d = Deferred(canceller)
      self._calls[callid] = d

      self.sendMessage(bytes)
      return d


   def subscribe(self, topic, handler):
      """
      Subscribe to topic.
      """
      if not self._subscriptions.has_key(topic):
         #self._subscriptions = set()
         self._subscriptions = []
         msg = WampMessageSubscribe(topic)
         bytes = self.factory._serializer.serialize(msg)
         self.sendMessage(bytes)

      if not handler in self._subscriptions[topic]:
         #self._subscriptions.add(handler)
         self._subscriptions.append(handler)


   def unsubscribe(self, topic, handler = None):
      """
      Unsubscribe from topic.
      """
      if self._subscriptions.has_key(topic):
         if handler is not None and handler in self._subscriptions[topic]:
            self._subscriptions[topic].remove(handler)
         if handler is None or len(self._subscriptions[topic]) == 0:
            msg = WampMessageUnsubscribe(topic)
            bytes = self.factory._serializer.serialize(msg)
            self.sendMessage(bytes)


   def publish(self, topic, event, excludeMe = None, exclude = None, eligible = None, discloseMe = None):
      """
      Publish to topic.
      """
      msg = WampMessagePublish(topic, event, excludeMe = excludeMe, exclude = exclude, eligible = eligible, discloseMe = discloseMe)
      bytes = self.factory._serializer.serialize(msg)
      self.sendMessage(bytes)



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
