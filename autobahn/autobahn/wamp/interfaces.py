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


import zope
from zope.interface import Interface, Attribute


class IObjectSerializer(Interface):
   """
   Raw object serialization and unserialization.
   """

   BINARY = Attribute("""Flag to indicate if serializer requires a binary clean
      transport (or if UTF8 transparency is sufficient).""")

   def serialize(obj):
      """
      Serialize an object to a byte string.

      :param obj: Object to serialize.
      :type obj: Any serializable type.

      :returns str -- Serialized byte string.
      """

   def unserialize(bytes):
      """
      Unserialize an object from a byte string.

      :param bytes: Object to serialize.
      :type bytes: Any serializable type.

      :returns obj -- Any type that can be unserialized.
      """


class IMessage(Interface):
   """
   A WAMP message.
   """

   MESSAGE_TYPE = Attribute("""WAMP message type code.""")


   def marshal():
      """
      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns list -- The serialized raw message.
      """
   
   def serialize(serializer):
      """
      Serialize this object into a wire level bytestring representation.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`
      :returns bytes -- The serialized bytes.
      """

   def reset_cache():
      """
      Resets the serialization cache.
      """

   def __eq__(other):
      """
      Message equality. This does an attribute-wise comparison (but skips attributes
      that start with "_").
      """

   def __ne__(other):
      """
      Message inequality: just the negate of message equality.
      """

   def __str__():
      """
      Returns text representation of this message.

      :returns str -- Human readable representation (e.g. for logging or debugging purposes).
      """


class ISerializer(Interface):
   """
   WAMP message serialization and unserialization.
   """

   MESSAGE_TYPE_MAP = Attribute("""Mapping of WAMP message type codes to WAMP message classes.""")

   SERIALIZER_ID = Attribute("""The WAMP serialization format ID.""")


   def serialize(message):
      """
      Serializes a WAMP message to bytes to be sent to a transport.

      :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
      :type message: obj
      :returns tuple -- A pair `(bytes, isBinary)`.
      """

   def unserialize(bytes, isBinary):
      """
      Unserializes bytes from a transport and parses a WAMP message.

      :param bytes: Byte string from wire.
      :type bytes: bytes
      :returns obj -- An instance that implements :class:`autobahn.wamp.interfaces.IMessage`.
      """




class IMessageTransport(Interface):

   def send(message):
      """
      """

   def isOpen():
      """
      """

   def close():
      """
      """

   def abort():
      """
      """


class IMessageTransportHandler(Interface):

   def onOpen(transport):
      """
      Called fired when transport is open.

      :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
      :type message: obj      
      """

   def onMessage(message):
      """
      Callback fired when a WAMP message was received.

      :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
      :type message: obj
      """

   def onClose():
      """
      """



class IWampDealer(Interface):
   """
   """

   def register(self, endpoint, obj):
      """
      """

   def registerMethod(self, endpoint, obj, method):
      """
      """

   def registerProcedure(self, endpoint, procedure):
      """
      """

   def unregister(self, endpoint):
      """
      """


class IWampBroker(Interface):
   """
   """

   def register(self, topic, prefix = False, publish = True, subscribe = True):
      """
      """

   def unregister(self, topic):
      """
      """


# class IWampPublishOptions(Interface):

#    excludeMe = Attribute("Exclude me, the publisher, from receiving the event (even though I may be subscribed).")



class IWampSession(Interface):
   """
   """

   def call(self, *args):
      """
      """

   def subscribe(self, topic, handler):
      """
      """

   def unsubscribe(self, topic, handler = None):
      """
      """

   def publish(self, topic, event,
               excludeMe = None,
               exclude = None,
               eligible = None,
               discloseMe = None):
      """
      """

   def setDealer(self, dealer = None):
      """
      """

   def setBroker(self, broker = None):
      """
      """



class IPeer(Interface):
   """
   Base interface for WAMP peers.
   """

   def process(self, msg):
      """
      """


   def define(self, exception, error = None):
      """
      Defines an exception for a WAMP error in the context of this WAMP session.

      :param exception: The exception class to define an error mapping for.
      :type exception: A class that derives of `Exception`.
      :param error: The URI (or URI pattern) the exception class should be mapped for.
                    Iff the `exception` class is decorated, this must be `None`.
      :type error: str
      """


class ICaller(IPeer):
   """
   Interface for WAMP peers implementing role "Caller".
   """

   def call(procedure, *args, **kwargs):
      """
      Call a remote procedure.

      This will return a deferred/future, that when resolved, provides the actual result.
      If the result is a single positional return value, it'll be returned "as-is". If the
      result contains multiple positional return values or keyword return values,
      the result is wrapped in an instance of :class:`autobahn.wamp.types.CallResult`.

      If the call fails, the returned deferred/future will be rejected with an instance
      of :class:`autobahn.wamp.error.CallError`.

      If the Caller and Dealer implementations support cancelling of calls, the call may
      be canceled by canceling the returned deferred/future.

      :param procedure: The URI of the remote procedure to be called, e.g. "com.myapp.hello" or
                        a procedure object specifying details on the call to be performed.
      :type procedure: str or an instance of :class:`autobahn.wamp.types.Call`

      :returns: obj -- A deferred/future for the call -
                       an instance of :class:`twisted.internet.defer.Deferred` (when running under Twisted) or
                       an instance of :class:`asyncio.Future` (when running under asyncio).
      """



class ICallee(IPeer):
   """
   Interface for WAMP peers implementing role "Callee".
   """

   def register(endpoint, procedure = None, options = None):
      """
      Register an endpoint on a procedure to (subsequently) receive calls
      calling that procedure.

      This will return a deferred/future, that when resolved provides
      an instance of :class:`autobahn.wamp.types.Registration`.

      If the registration fails, the returned deferred/future will be rejected
      with an instance of :class:`autobahn.wamp.error.ApplicationError`.

      :param procedure: The URI (or URI pattern) of the procedure to register for,
                        e.g. "com.myapp.myprocedure1".
      :type procedure: str
      :param endpoint: The endpoint called under the procedure.
      :type endpoint: callable
      :param options: Options for registering.
      :type options: An instance of :class:`autobahn.wamp.types.RegisterOptions`.

      :returns: obj -- A deferred/future for the registration -
                       an instance of :class:`twisted.internet.defer.Deferred`
                       (when running under Twisted) or an instance of
                       :class:`asyncio.Future` (when running under asyncio).
      """


   def unregister(registration):
      """
      Unregister the endpoint registration that was previously registered.

      After a registration has been unregistered, calls won't get routed
      to the endpoint any more.

      This will return a deferred/future, that when resolved signals
      successful unregistration.

      If the unregistration fails, the returned deferred/future will be rejected
      with an instance of :class:`autobahn.wamp.error.ApplicationError`.

      :param registration: The registration to unregister from.
      :type registration: An instance of :class:`autobahn.wamp.types.Registration`
                          that was previously registered.

      :returns: obj -- A deferred/future for the unregistration -
                       an instance of :class:`twisted.internet.defer.Deferred` (when running under Twisted)
                       or an instance of :class:`asyncio.Future` (when running under asyncio).
      """



class IPublisher(IPeer):
   """
   Interface for WAMP peers implementing role "Publisher".
   """

   def publish(topic, *args, **kwargs):
      """
      Publish an event to a topic.

      This will return a deferred/future, that when resolved provides the publication ID
      for the published event.

      If the publication fails, the returned deferred/future will be rejected with an instance
      of :class:`autobahn.wamp.error.ApplicationError`.

      :param topic: The URI of the topic to publish to, e.g. "com.myapp.mytopic1".
      :type topic: str
      :param payload: The payload for the event to be published.
      :type payload: obj
      :param options: Options for publishing.
      :type options: None or an instance of :class:`autobahn.wamp.types.PublishOptions`

      :returns: obj -- A deferred/future for the publication -
                       an instance of :class:`twisted.internet.defer.Deferred` (when running under Twisted)
                       or an instance of :class:`asyncio.Future` (when running under asyncio).
      """



class ISubscriber(IPeer):
   """
   Interface for WAMP peers implementing role "Subscriber".
   """

   def subscribe(handler, topic = None, options = None):
      """
      Subscribe to a topic and subsequently receive events published to that topic.

      If `handler` is a callable (function, method or object that implements `__call__`),
      then `topic` must be provided and an instance of
      :class:`twisted.internet.defer.Deferred` (when running on Twisted) or an instance
      of :class:`asyncio.Future` (when running on asyncio) is returned.
      If the subscription succeeds the Deferred/Future will resolve to an instance
      of :class:`autobahn.wamp.types.Subscription`. If the subscription fails the
      Deferred/Future will reject with an instance of :class:`autobahn.error.RuntimeError`.

      If `handler` is an object, then each of the object's methods that are decorated
      with :func:`autobahn.wamp.topic` are subscribed as event handlers, and a list of
      Deferreds/Futures is returned that each resolves or rejects as above.

      :param handler: The event handler or handler object to receive events.
      :type handler: callable or obj
      :param topic: When `handler` is a single event handler, the URI (or URI pattern)
                    of the topic to subscribe to. When `handler` is an event handler
                    object, this value is ignored (and should be `None`).
      :type topic: str
      :param options: Options for subscribing.
      :type options: An instance of :class:`autobahn.wamp.types.SubscribeOptions`.

      :returns: obj -- A (list of) Deferred(s)/Future(s) for the subscription(s) -
                       instance(s) of :class:`twisted.internet.defer.Deferred` (when
                       running under Twisted) or instance(s) of :class:`asyncio.Future`
                       (when running under asyncio).
      """


   def unsubscribe(subscription):
      """
      Unsubscribe a subscription that was previously created with
      :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`.

      After a subscription has been unsubscribed, watchers won't get notified
      any more, and you cannot use the subscription anymore.

      This will return a deferred/future, that when resolved signales
      successful unsubscription.

      If the unsubscription fails, the returned deferred/future will be rejected
      with an instance of :class:`autobahn.wamp.error.ApplicationError`.

      :param subscription: The subscription to unscribe from.
      :type subscription: An instance of :class:`autobahn.wamp.types.Subscription`
                          that was previously subscribed.

      :returns: obj -- A (list of) Deferred(s)/Future(s) for the unsubscription(s) -
                       instance(s) of :class:`twisted.internet.defer.Deferred` (when
                       running under Twisted) or instance(s) of :class:`asyncio.Future`
                       (when running under asyncio).
      """
