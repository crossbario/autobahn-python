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

from twisted.internet.defer import Deferred, \
                                   maybeDeferred

from autobahn.websocket import WebSocketProtocol, HttpException, Timings
from autobahn.websocket import WebSocketServerProtocol, \
                               WebSocketServerFactory, \
                               WebSocketClientProtocol, \
                               WebSocketClientFactory

from autobahn.httpstatus import HTTP_STATUS_CODE_BAD_REQUEST
from autobahn.util import newid

from message import WampMessageHello, \
                    WampMessageHeartbeat, \
                    WampMessageRoleChange, \
                    WampMessageSubscribe, \
                    WampMessageSubscription, \
                    WampMessageSubscribeError, \
                    WampMessageUnsubscribe, \
                    WampMessagePublish, \
                    WampMessageEvent, \
                    WampMessageMetaEvent, \
                    WampMessageProvide, \
                    WampMessageUnprovide, \
                    WampMessageCall, \
                    WampMessageCancelCall, \
                    WampMessageCallProgress, \
                    WampMessageCallResult, \
                    WampMessageCallError

from error import WampProtocolError
from serializer import WampJsonSerializer, WampMsgPackSerializer


class WampProtocol:

   def sendWampMessage(self, msg):
      bytes, isbinary = self._serializer.serialize(msg)
      self.sendMessage(bytes, isbinary)


   def onSessionOpen(self):
      pass


   def onSessionClose(self):
      pass


   def setBroker(self, broker = None):
      if self._broker and not broker:
         msg = WampMessageRoleChange(WampMessageRoleChange.ROLE_CHANGE_OP_REMOVE, WampMessageRoleChange.ROLE_CHANGE_ROLE_BROKER)
         bytes, isbinary = self._serializer.serialize(msg)
         self.sendMessage(bytes, isbinary)

      if not self._broker and broker:
         msg = WampMessageRoleChange(WampMessageRoleChange.ROLE_CHANGE_OP_ADD, WampMessageRoleChange.ROLE_CHANGE_ROLE_BROKER)
         bytes, isbinary = self._serializer.serialize(msg)
         self.sendMessage(bytes, isbinary)

      if self._broker:
         self._broker.remove(self)

      self._broker = broker
      
      if self._broker:
         self._broker.add(self)


   def setDealer(self, dealer = None):
      if self._dealer and not dealer:
         msg = WampMessageRoleChange(WampMessageRoleChange.ROLE_CHANGE_OP_REMOVE, WampMessageRoleChange.ROLE_CHANGE_ROLE_DEALER)
         bytes, isbinary = self._serializer.serialize(msg)
         self.sendMessage(bytes, isbinary)

      if not self._dealer and dealer:
         msg = WampMessageRoleChange(WampMessageRoleChange.ROLE_CHANGE_OP_ADD, WampMessageRoleChange.ROLE_CHANGE_ROLE_DEALER)
         bytes, isbinary = self._serializer.serialize(msg)
         self.sendMessage(bytes, isbinary)

      if self._dealer:
         self._dealer.remove(self)

      self._dealer = dealer
      
      if self._dealer:
         self._dealer.add(self)


   def onOpen(self):
      self._this_sessionid = newid()
      self._peer_sessionid = None

      self._subscriptions = {}
      self._broker = None
      self._peer_is_broker = False

      self._calls = {}
      self._dealer = None
      self._peer_is_dealer = False

      self._subscribes = {}

      msg = WampMessageHello(self._this_sessionid)
      bytes, isbinary = self._serializer.serialize(msg)
      self.sendMessage(bytes, isbinary)


   def onClose(self, wasClean, code, reason):
      self.onSessionClose()


   def onMessage(self, bytes, isBinary):
      #print bytes
      try:
         msg = self._serializer.unserialize(bytes, isBinary)
      except WampProtocolError, e:
         print "WAMP protocol error", e
      else:
         if self._peer_sessionid is not None:

            #print msg.__class__
            #print msg

            if isinstance(msg, WampMessageRoleChange):
               if msg.op == WampMessageRoleChange.ROLE_CHANGE_OP_ADD and msg.role == WampMessageRoleChange.ROLE_CHANGE_ROLE_BROKER:
                  if self._broker:
                     self._broker.addBroker(self)

               if msg.op == WampMessageRoleChange.ROLE_CHANGE_OP_ADD and msg.role == WampMessageRoleChange.ROLE_CHANGE_ROLE_DEALER:
                  if self._dealer:
                     self._dealer.addDealer(self)

            elif isinstance(msg, WampMessageSubscription):
               d, handler = self._subscribes.pop(msg.subscribeid, None)
               if d:
                  self._subscriptions[msg.subscriptionid] = handler
                  d.callback(msg.subscriptionid)
               else:
                  pass

            elif isinstance(msg, WampMessageSubscribeError):
               d, _ = self._subscribes.pop(msg.requestid, None)
               if d:
                  e = WampCallException(msg.error, msg.message, msg.value)
                  d.errback(e)
               else:
                  pass

            elif isinstance(msg, WampMessageEvent):
               if self._subscriptions.has_key(msg.subscriptionid):
                  handler = self._subscriptions[msg.subscriptionid]
                  handler(msg.topic, msg.event)
                  # for handler in self._subscriptions[msg.topic]:
                  #    handler(msg.topic, msg.event)
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

            elif isinstance(msg, WampMessageCall):
               if self._dealer:
                  self._dealer.onCall(self, msg)
               else:
                  raise Exception("no dealer")

            elif isinstance(msg, WampMessageCancelCall):
               if self._dealer:
                  self._dealer.onCancelCall(self, msg)
               else:
                  raise Exception("no dealer")

            elif isinstance(msg, WampMessageProvide):
               if self._dealer:
                  self._dealer.onProvide(self, msg)
               else:
                  raise Exception("no dealer")

            elif isinstance(msg, WampMessageUnprovide):
               if self._dealer:
                  self._dealer.onUnprovide(self, msg)
               else:
                  raise Exception("no dealer")

            elif isinstance(msg, WampMessagePublish):
               if self._broker:
                  self._broker.onPublish(self, msg)
               else:
                  raise Exception("no broker")

            elif isinstance(msg, WampMessageSubscribe):
               if self._broker:
                  self._broker.onSubscribe(self, msg)
               else:
                  raise Exception("no broker")

            elif isinstance(msg, WampMessageUnsubscribe):
               if self._broker:
                  self._broker.onUnsubscribe(self, msg)
               else:
                  raise Exception("no broker")

            else:
               raise Exception("not implemented")

         else:
            if isinstance(msg, WampMessageHello):
               self._peer_sessionid = msg.sessionid
               self.onSessionOpen()
            else:
               raise Exception("not handshaked")


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
         bytes, isbinary = self._serializer.serialize(msg)
      except Exception, e:
         print "X"*100, e
         raise Exception("call argument(s) not serializable")

      def canceller(_d):
         msg = WampMessageCancelCall(callid)
         bytes, isbinary = self._serializer.serialize(msg)
         self.sendMessage(bytes, isbinary)

      d = Deferred(canceller)
      self._calls[callid] = d

      self.sendMessage(bytes, isbinary)
      return d


   def subscribe(self, topic, handler):
      """
      Subscribe to topic.
      """
      while True:
         subscribeid = newid()
         if not self._subscribes.has_key(subscribeid):
            break

      d = Deferred()
      self._subscribes[subscribeid] = (d, handler)

      self.sendWampMessage(WampMessageSubscribe(subscribeid, topic))

      return d


   def subscribe2(self, topic, handler):
      """
      Subscribe to topic.
      """
      if not self._subscriptions.has_key(topic):
         #self._subscriptions[topic] = set()
         self._subscriptions[topic] = []
         self.sendWampMessage(WampMessageSubscribe(topic))

      if not handler in self._subscriptions[topic]:
         #self._subscriptions[topic].add(handler)
         self._subscriptions[topic].append(handler)


   def unsubscribe(self, topic, handler = None):
      """
      Unsubscribe from topic.
      """
      if self._subscriptions.has_key(topic):
         if handler is not None and handler in self._subscriptions[topic]:
            self._subscriptions[topic].remove(handler)
         if handler is None or len(self._subscriptions[topic]) == 0:
            msg = WampMessageUnsubscribe(topic)
            bytes = self._serializer.serialize(msg)
            self.sendMessage(bytes, isbinary)


   def publish(self, topic, event, excludeMe = None, exclude = None, eligible = None, discloseMe = None):
      """
      Publish to topic.
      """
      msg = WampMessagePublish(topic, event, excludeMe = excludeMe, exclude = exclude, eligible = eligible, discloseMe = discloseMe)
      self.sendWampMessage(msg)



def parseWampSubprotocolIdentifier(subprotocol):
   try:
      s = subprotocol.split('.')
      if s[0] != "wamp":
         raise Exception()
      version = int(s[1])
      serializerId = s[2]
      return version, serializerId
   except:
      return None, None



class WampServerProtocol(WampProtocol, WebSocketServerProtocol):

   def onConnect(self, connectionRequest):
      headers = {}
      for subprotocol in connectionRequest.protocols:
         version, serializerId = parseWampSubprotocolIdentifier(subprotocol)
         if version == 2 and serializerId in self.factory._serializers.keys():
            self._serializer = self.factory._serializers[serializerId]
            return subprotocol, headers

      raise HttpException(HTTP_STATUS_CODE_BAD_REQUEST[0], "This server only speaks WebSocket subprotocols %s" % ', '.join(self.factory.protocols))


   # def connectionMade(self):
   #    WebSocketServerProtocol.connectionMade(self)
   #    WampProtocol.connectionMade(self)


   # def connectionLost(self, reason):
   #    WampProtocol.connectionLost(self, reason)
   #    WebSocketServerProtocol.connectionLost(self, reason)



class WampClientProtocol(WampProtocol, WebSocketClientProtocol):

   def onConnect(self, connectionResponse):
      if connectionResponse.protocol not in self.factory.protocols:
         raise Exception("Server does not speak any of the WebSocket subprotocols we requested (%s)." % ', '.join(self.factory.protocols))

      version, serializerId = parseWampSubprotocolIdentifier(connectionResponse.protocol)
      self._serializer = self.factory._serializers[serializerId]


   # def connectionMade(self):
   #    WebSocketClientProtocol.connectionMade(self)
   #    WampProtocol.connectionMade(self)


   # def connectionLost(self, reason):
   #    Wamp2Protocol.connectionLost(self, reason)
   #    WebSocketClientProtocol.connectionLost(self, reason)


class WampFactory:

   def __init__(self, serializers):
      self._serializers = {}
      for ser in serializers:
         self._serializers[ser.SERIALIZER_ID] = ser



class WampServerFactory(WebSocketServerFactory, WampFactory):

   protocol = WampServerProtocol

   def __init__(self,
                url,
                debug = False,
                serializers = None,
                reactor = None):

      if serializers is None:
         serializers = [WampMsgPackSerializer(), WampJsonSerializer()]

      protocols = ["wamp.2.%s" % ser.SERIALIZER_ID for ser in serializers]

      WebSocketServerFactory.__init__(self,
                                      url,
                                      debug = debug,
                                      protocols = protocols,
                                      reactor = reactor)

      WampFactory.__init__(self, serializers)



class WampClientFactory(WebSocketClientFactory, WampFactory):

   protocol = WampClientProtocol

   def __init__(self,
                url,
                debug = False,
                serializers = None,
                reactor = None):

      if serializers is None:
         serializers = [WampMsgPackSerializer(), WampJsonSerializer()]

      protocols = ["wamp.2.%s" % ser.SERIALIZER_ID for ser in serializers]

      WebSocketClientFactory.__init__(self,
                                      url,
                                      debug = debug,
                                      protocols = protocols,
                                      reactor = reactor)

      WampFactory.__init__(self, serializers)
