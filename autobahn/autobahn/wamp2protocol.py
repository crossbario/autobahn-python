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

from twisted.internet.defer import Deferred, \
                                   maybeDeferred

from websocket import WebSocketProtocol, HttpException, Timings
from websocket import WebSocketServerProtocol, WebSocketClientProtocol

from httpstatus import HTTP_STATUS_CODE_BAD_REQUEST
from util import utcnow, newid

from wamp2message import *



import inspect, types

def exportRpc(arg = None):
   """
   Decorator for RPC'ed callables.
   """
   ## decorator without argument
   if type(arg) is types.FunctionType:
      arg._autobahn_rpc_id = arg.__name__
      return arg
   ## decorator with argument
   else:
      def inner(f):
         f._autobahn_rpc_id = arg
         return f
      return inner


## incoming client connections
## incoming broker connections
## outgoing broker connections

class Endpoint:
   pass


class LocalMethodEndpoint(Endpoint):
   def __init__(self, endpoint, obj, method):
      self.endpoint = endpoint
      self.obj = obj
      self.method = method

   def __call__(self, *args):
      return maybeDeferred(self.method, self.obj, *args)


class LocalProcedureEndpoint(Endpoint):
   def __init__(self, endpoint, proc):
      self.endpoint = endpoint
      self.proc = proc

   def __call__(self, *args):
      return maybeDeferred(self.proc, *args)


class RemoteEndpoint(Endpoint):
   def __init__(self, endpoint, proto):
      self.endpoint = endpoint
      self.proto = proto

   def __call__(self, *args):
      return self.proto.call(self.endpoint, *args)


class Dealer:

   def __init__(self):
      self._protos = set()
      self._endpoints = {}
      self._dealers = set()

   def add(self, proto):
      pass

   def remove(self, proto):
      pass

   def addDealer(self, proto):
      print "addDealer"
      assert(proto not in self._dealers)
      self._dealers.add(proto)

      for endpoint in self._endpoints:
         msg = WampMessageProvide(endpoint)
         bytes = proto.factory._serializer.serialize(msg)
         proto.sendMessage(bytes)


   def removeDealer(self, proto):
      assert(proto in self._dealers)
      self._dealers.remove(proto)

   def onCall(self, proto, call):

      if self._endpoints.has_key(call.endpoint):

         endpoint = self._endpoints[call.endpoint]

         cargs = tuple(call.args)

         def onSuccess(res):
            msg = WampMessageCallResult(call.callid, res)
            bytes = proto.factory._serializer.serialize(msg)
            proto.sendMessage(bytes)

         def onError(err):
            print err

         d = endpoint(*cargs)
         d.addCallbacks(onSuccess, onError)

      else:
         print "FOOOOOOOOOOO"


   def onCancelCall(self, proto, call):
      pass

   def onProvide(self, proto, provide):
      self._endpoints[provide.endpoint] = RemoteEndpoint(provide.endpoint, proto)

   def onUnprovide(self, proto, unprovide):
      pass


   def _announceEndpoint(self, endpoint):
      msg = WampMessageProvide(endpoint)
      for dealer in self._dealers:
         bytes = dealer.factory._serializer.serialize(msg)
         dealer.sendMessage(bytes)


   def register(self, endpoint, obj):
      for k in inspect.getmembers(obj.__class__, inspect.ismethod):
         if k[1].__dict__.has_key("_autobahn_rpc_id"):
            fq_endpoint = endpoint + k[1].__dict__["_autobahn_rpc_id"]
            method = k[1]
            self.registerMethod(fq_endpoint, obj, method)


   def registerMethod(self, endpoint, obj, method):
      self._endpoints[endpoint] = LocalMethodEndpoint(endpoint, obj, method)
      self._announceEndpoint(endpoint)


   def registerProcedure(self, endpoint, procedure):
      self._endpoints[endpoint] = LocalProcedureEndpoint(endpoint, procedure)
      self._announceEndpoint(endpoint)



class Broker:

   def __init__(self):
      ## FIXME: maintain 2 maps: topic => protos (subscribers), proto => topics
      self._protos = set()
      self._subscribers = {}
      self._brokers = set()

   def addBroker(self, proto):
      assert(proto not in self._brokers)
      self._brokers.add(proto)

      # def on_publish(topic, event):

      # for topic in self._subscribers:
      #    proto.subscribe()
      #    msg = WampMessageEvent(publish.topic, publish.event)
      #    bytes = proto.factory._serializer.serialize(msg)
      #    for proto in receivers:
      #       proto.sendMessage(bytes)


   def removeBroker(self, proto):
      assert(proto in self._brokers)
      self._brokers.remove(proto)

   def add(self, proto):
      assert(proto not in self._protos)
      self._protos.add(proto)

   def remove(self, proto):
      assert(proto in self._protos)
      self._protos.remove(proto)
      for subscribers in self._subscribers:
         subscribers.discard(proto)


   def onPublish(self, proto, publish):
      assert(proto in self._protos)

      for broker_proto in self._brokers:
         if broker_proto != proto:
            bytes = broker_proto.factory._serializer.serialize(publish)
            broker_proto.sendMessage(bytes)

      if self._subscribers.has_key(publish.topic):
         receivers = self._subscribers[publish.topic]
         if len(receivers) > 0:
            msg = WampMessageEvent(publish.topic, publish.event)
            bytes = proto.factory._serializer.serialize(msg)
            for proto in receivers:
               proto.sendMessage(bytes)


   def onSubscribe(self, proto, subscribe):
      assert(proto in self._protos)

      if not self._subscribers.has_key(subscribe.topic):
         self._subscribers[subscribe.topic] = set()

      if not proto in self._subscribers[subscribe.topic]:
         self._subscribers[subscribe.topic].add(proto)


   def onUnsubscribe(self, proto, unsubscribe):
      assert(proto in self._protos)

      if self._subscribers.has_key(unsubscribe.topic):
         if proto in self._subscribers[unsubscribe.topic]:
            self._subscribers[unsubscribe.topic].discard(proto)



class Wamp2Protocol:

   def onSessionOpen(self):
      pass


   def setBroker(self, broker = None):
      if self._broker and not broker:
         msg = WampMessageRoleChange(WampMessageRoleChange.ROLE_CHANGE_OP_REMOVE, WampMessageRoleChange.ROLE_CHANGE_ROLE_BROKER)
         bytes = self.factory._serializer.serialize(msg)
         self.sendMessage(bytes)

      if not self._broker and broker:
         msg = WampMessageRoleChange(WampMessageRoleChange.ROLE_CHANGE_OP_ADD, WampMessageRoleChange.ROLE_CHANGE_ROLE_BROKER)
         bytes = self.factory._serializer.serialize(msg)
         self.sendMessage(bytes)

      if self._broker:
         self._broker.remove(self)

      self._broker = broker
      
      if self._broker:
         self._broker.add(self)


   def setDealer(self, dealer = None):
      if self._dealer and not dealer:
         msg = WampMessageRoleChange(WampMessageRoleChange.ROLE_CHANGE_OP_REMOVE, WampMessageRoleChange.ROLE_CHANGE_ROLE_DEALER)
         bytes = self.factory._serializer.serialize(msg)
         self.sendMessage(bytes)

      if not self._dealer and dealer:
         msg = WampMessageRoleChange(WampMessageRoleChange.ROLE_CHANGE_OP_ADD, WampMessageRoleChange.ROLE_CHANGE_ROLE_DEALER)
         bytes = self.factory._serializer.serialize(msg)
         self.sendMessage(bytes)

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

      msg = WampMessageHello(self._this_sessionid)
      bytes = self.factory._serializer.serialize(msg)
      self.sendMessage(bytes)


   def onClose(self, wasClean, code, reason):
      pass


   def onMessage(self, bytes, binary):
      print bytes
      try:
         msg = self.factory._serializer.unserialize(bytes)
      except WampProtocolError, e:
         print "WAMP protocol error", e
      else:
         if self._peer_sessionid is not None:

            print msg.__class__
            print msg

            if isinstance(msg, WampMessageRoleChange):
               if msg.op == WampMessageRoleChange.ROLE_CHANGE_OP_ADD and msg.role == WampMessageRoleChange.ROLE_CHANGE_ROLE_BROKER:
                  if self._broker:
                     self._broker.addBroker(self)

               if msg.op == WampMessageRoleChange.ROLE_CHANGE_OP_ADD and msg.role == WampMessageRoleChange.ROLE_CHANGE_ROLE_DEALER:
                  if self._dealer:
                     self._dealer.addDealer(self)

            elif isinstance(msg, WampMessageEvent):
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
         bytes = self.factory._serializer.serialize(msg)
      except Exception, e:
         print "X"*100, e
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
         #self._subscriptions[topic] = set()
         self._subscriptions[topic] = []
         msg = WampMessageSubscribe(topic)
         bytes = self.factory._serializer.serialize(msg)
         self.sendMessage(bytes)

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
