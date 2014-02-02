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

from zope.interface import Interface, Attribute



class IObjectSerializer(Interface):
   """
   Raw Python object serialization and unserialization. Object serializers are
   used by classes implementing WAMP serializers, that is instances of
   :class:`autobahn.wamp.interfaces.ISerializer`.
   """

   BINARY = Attribute("""Flag to indicate if serializer requires a binary clean
      transport or if UTF8 transparency is sufficient.""")


   def serialize(obj):
      """
      Serialize an object to a byte string.

      :param obj: Object to serialize.
      :type obj: Any serializable type.

      :returns: str -- Serialized byte string.
      """

   def unserialize(bytes):
      """
      Unserialize an object from a byte string.

      :param bytes: Object to serialize.
      :type bytes: Any serializable type.

      :returns: obj -- Any type that can be unserialized.
      """



class IMessage(Interface):
   """
   A WAMP message.
   """

   MESSAGE_TYPE = Attribute("""WAMP message type code.""")


   def marshal():
      """
      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: list -- The serialized raw message.
      """

   def parse(wmsg):
      """
      Factory method that parses a unserialized raw message (as returned byte
      :func:`autobahn.interfaces.ISerializer.unserialize`) into an instance
      of this class.

      :returns: obj -- An instance of this class. 
      """
   
   def serialize(serializer):
      """
      Serialize this object into a wire level bytestring representation and cache
      the resulting bytestring. If the cache already contains an entry for the given
      serializer, return the cached representation directly.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`

      :returns: bytes -- The serialized bytes.
      """

   def uncache():
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
      Message inequality (just the negate of message equality).
      """

   def __str__():
      """
      Returns text representation of this message.

      :returns: str -- Human readable representation (e.g. for logging or debugging purposes).
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

      :returns: tuple -- A pair `(bytes, isBinary)`.
      """

   def unserialize(bytes, isBinary):
      """
      Unserializes bytes from a transport and parses a WAMP message.

      :param bytes: Byte string from wire.
      :type bytes: bytes

      :returns: obj -- An instance that implements :class:`autobahn.wamp.interfaces.IMessage`.
      """



class ITransport(Interface):
   """
   A WAMP transport is a bidirectional, full-duplex, reliable, ordered,
   message-based channel.
   """

   def send(message):
      """
      Send a WAMP message over the transport to the peer. If the transport is
      not open, this raises :class:`autobahn.wamp.exception.TransportLost`.

      :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
      :type message: obj      
      """

   def isOpen():
      """
      Check if the transport is open for messaging.

      :returns: bool -- `True`, if the transport is open.
      """

   def close():
      """
      Close the transport regularily. The transport will perform any
      closing handshake if applicable. This should be used for any
      application initiated closing.
      """

   def abort():
      """
      Abort the transport abruptly. The transport will be destroyed as
      fast as possible, and without playing nice to the peer. This should
      only be used in case of fatal errors, protocol violations or possible
      detected attacks.
      """



class ITransportHandler(Interface):

   def onOpen(transport):
      """
      Callback fired when transport is open.

      :param transport: An instance that implements :class:`autobahn.wamp.interfaces.ITransport`
      :type transport: obj      
      """

   def onMessage(message):
      """
      Callback fired when a WAMP message was received.

      :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
      :type message: obj
      """

   def onClose(wasClean):
      """
      Callback fired when the transport has been closed.

      :param wasClean: Indicates if the transport has been closed regularily.
      :type wasClean: bool
      """



class ISession(Interface):
   """
   Base interface for WAMP sessions.
   """

   def onSessionOpen(details):
      """
      Callback fired when WAMP session has been established.

      :param details: Session information.
      :type details: Instance of :class:`autobahn.wamp.types.SessionDetails`.
      """


   def closeSession(reason = None, message = None):
      """
      Actively close this WAMP session.

      :param reason: An optional URI for the closing reason.
      :type reason: str
      :param message: An optional (human readable) closing message, intended for
                      logging purposes.
      :type message: str
      """


   def onSessionClose(details):
      """
      Callback fired when WAMP session has is closed

      :param details: Close information.
      :type details: Instance of :class:`autobahn.wamp.types.CloseDetails`.
      """


   def define(exception, error = None):
      """
      Defines an exception for a WAMP error in the context of this WAMP session.

      :param exception: The exception class to define an error mapping for.
      :type exception: A class that derives of `Exception`.
      :param error: The URI (or URI pattern) the exception class should be mapped for.
                    Iff the `exception` class is decorated, this must be `None`.
      :type error: str
      """



class ICaller(ISession):
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



class IRegistration(Interface):
   """
   Represents a registration.
   """
   id = Attribute("The WAMP registration ID for this registration.")

   active = Attribute("Flag indicating if registration is active.")

   def unregister():
      """
      Unregister this registration that was previously created from
      :func:`autobahn.wamp.interfaces.ICallee.register`.

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



class ICallee(ISession):
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



class IPublication(Interface):
   """
   """
   id = Attribute("The WAMP publication ID for this publication.")




class IPublisher(ISession):
   """
   Interface for WAMP peers implementing role "Publisher".
   """

   def publish(topic, *args, **kwargs):
      """
      Publish an event to a topic.

      If `kwargs` contains an `options` keyword argument that is an instance of
      :class:`autobahn.wamp.types.PublishOptions`, this will provide
      specific options for the publish to perform.

      If publication acknowledgement is requested via `options.acknowledgement == True`,
      this function returns a Deferred/Future:

        - if the publication succeeds the Deferred/Future will resolve to an object
          that implements :class:`autobahn.wamp.interfaces.IPublication`.

        - if the publication fails the Deferred/Future will reject with an instance
          of :class:`autobahn.error.RuntimeError`.

      :param topic: The URI of the topic to publish to, e.g. "com.myapp.mytopic1".
      :type topic: str
      :param args: Arbitrary application payload for the event (positional arguments).
      :type args: list
      :param kwargs: Arbitrary application payload for the event (keyword arguments).
      :type kwargs: dict

      :returns: obj -- `None` for non-acknowledged publications or,
                       for non-acknowledged publications, an instance of
                       :class:`twisted.internet.defer.Deferred` (when running under Twisted)
                       or an instance of :class:`asyncio.Future` (when running under asyncio).
      """



class ISubscription(Interface):
   """
   Represents a subscription.
   """
   id = Attribute("The WAMP subscription ID for this subscription.")

   active = Attribute("Flag indicating if subscription is active.")

   def unsubscribe():
      """
      Unsubscribe this subscription that was previously created from
      :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`.

      After a subscription has been unsubscribed, events won't get
      routed to the handler anymore.

      This will return a deferred/future, that when resolved signals
      successful unsubscription.

      If the unsubscription fails, the returned deferred/future will be rejected
      with an instance of :class:`autobahn.wamp.error.ApplicationError`.

      :returns: obj -- A deferred/future for the unsubscription -
                       an instance of :class:`twisted.internet.defer.Deferred` (when running under Twisted)
                       or an instance of :class:`asyncio.Future` (when running under asyncio).
      """



class ISubscriber(ISession):
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

      If the subscription succeeds the Deferred/Future will resolve to an object
      that implements :class:`autobahn.wamp.interfaces.ISubscription`.

      If the subscription fails the Deferred/Future will reject with an instance
      of :class:`autobahn.error.RuntimeError`.

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



class IRouter(Interface):
   """
   WAMP router interface. Routers are either Brokers or Dealers.
   """

   def addSession(session):
      """
      Add a WAMP application session to this router.

      :param session: Application session to add.
      :type session: An instance that implements :class:`autobahn.wamp.interfaces.ISession`
      """


   def removeSession(session):
      """
      Remove a WAMP application session from this router.

      :param session: Application session to remove.
      :type session: An instance that implements :class:`autobahn.wamp.interfaces.ISession`
      """


   def processMessage(session, message):
      """
      Process an incoming message on an application session previously
      added to this router.

      :param session: Application session to remove.
      :type session: An instance that implements :class:`autobahn.wamp.interfaces.ISession`     
      :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
      :type message: obj
      """



class IBroker(IRouter):
   """
   WAMP broker interface. Brokers are responsible for event routing and
   must process the following WAMP messages in :func:`autobahn.wamp.interfaces.IRouter.processMessage`:

    * :class:`autobahn.wamp.message.Publish`
    * :class:`autobahn.wamp.message.Subscribe`
    * :class:`autobahn.wamp.message.Unsubscribe`
   """



class IDealer(IRouter):
   """
   WAMP dealer interface. Dealers are responsible for call routing and
   must process the following WAMP messages in :func:`autobahn.wamp.interfaces.IRouter.processMessage`:

    * :class:`autobahn.wamp.message.Register`
    * :class:`autobahn.wamp.message.Unregister`
    * :class:`autobahn.wamp.message.Call`
    * :class:`autobahn.wamp.message.Cancel`
    * :class:`autobahn.wamp.message.Yield`
    * :class:`autobahn.wamp.message.Error`
   """


##
## completely decouple transports and routers:
##  - multiple WAMP sessions over different transports attached to same router
##  - multiple WAMP sessions over a single transport attached to different routers
##
class ISessionN(Interface):

   def send(message):
      """
      """


class IRouterFactory(Interface):

   def get(realm):
      """
      Get router for given realm.
      """


class IRouterN(Interface):

   realm = Attribute("The WAMP realm this router handles.")

   def attach(session):
      """
      Attach a WAMP application session to this router.
      """

   def detach(session):
      """
      Detach a WAMP application session from this router.
      """

   def process(session, message):
      """
      Process a WAMP message received on the given session.
      """
