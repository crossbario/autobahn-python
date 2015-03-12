###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class IObjectSerializer(object):
    """
    Raw Python object serialization and deserialization. Object serializers are
    used by classes implementing WAMP serializers, that is instances of
    :class:`autobahn.wamp.interfaces.ISerializer`.
    """

    @abc.abstractproperty
    def BINARY(self):
        """
        Flag (read-only) to indicate if serializer requires a binary clean
        transport or if UTF8 transparency is sufficient.
        """

    @abc.abstractmethod
    def serialize(self, obj):
        """
        Serialize an object to a byte string.

        :param obj: Object to serialize.
        :type obj: Any serializable type.

        :returns: bytes -- Serialized byte string.
        """

    @abc.abstractmethod
    def unserialize(self, payload):
        """
        Unserialize objects from a byte string.

        :param payload: Objects to unserialize.
        :type payload: bytes

        :returns: list -- List of (raw) objects unserialized.
        """


@six.add_metaclass(abc.ABCMeta)
class IMessage(object):
    """
    A WAMP message.
    """

    @abc.abstractproperty
    def MESSAGE_TYPE(self):
        """
        WAMP message type code.
        """

    @abc.abstractmethod
    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: list -- The serialized raw message.
        """

    # @abc.abstractstaticmethod ## FIXME: this is Python 3 only
    # noinspection PyMethodParameters
    def parse(wmsg):
        """
        Factory method that parses a unserialized raw message (as returned byte
        :func:`autobahn.interfaces.ISerializer.unserialize`) into an instance
        of this class.

        :returns: obj -- An instance of this class.
        """

    @abc.abstractmethod
    def serialize(self, serializer):
        """
        Serialize this object into a wire level bytes representation and cache
        the resulting bytes. If the cache already contains an entry for the given
        serializer, return the cached representation directly.

        :param serializer: The wire level serializer to use.
        :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`

        :returns: bytes -- The serialized bytes.
        """

    @abc.abstractmethod
    def uncache(self):
        """
        Resets the serialization cache.
        """

    @abc.abstractmethod
    def __eq__(self, other):
        """
        Message equality. This does an attribute-wise comparison (but skips attributes
        that start with `_`).
        """

    @abc.abstractmethod
    def __ne__(self, other):
        """
        Message inequality (just the negate of message equality).
        """

    @abc.abstractmethod
    def __str__(self):
        """
        Returns text representation of this message.

        :returns: str -- Human readable representation (e.g. for logging or debugging purposes).
        """


@six.add_metaclass(abc.ABCMeta)
class ISerializer(object):
    """
    WAMP message serialization and deserialization.
    """

    @abc.abstractproperty
    def MESSAGE_TYPE_MAP(self):
        """
        Mapping of WAMP message type codes to WAMP message classes.
        """

    @abc.abstractproperty
    def SERIALIZER_ID(self):
        """
        The WAMP serialization format ID.
        """

    @abc.abstractmethod
    def serialize(self, message):
        """
        Serializes a WAMP message to bytes to be sent to a transport.

        :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
        :type message: obj

        :returns: tuple -- A pair ``(bytes, isBinary)``.
        """

    @abc.abstractmethod
    def unserialize(self, payload, isBinary):
        """
        Deserialize bytes from a transport and parse into WAMP messages.

        :param payload: Byte string from wire.
        :type payload: bytes

        :returns: list -- List of objects that implement :class:`autobahn.wamp.interfaces.IMessage`.
        """


@six.add_metaclass(abc.ABCMeta)
class ITransport(object):
    """
    A WAMP transport is a bidirectional, full-duplex, reliable, ordered,
    message-based channel.
    """

    @abc.abstractmethod
    def send(self, message):
        """
        Send a WAMP message over the transport to the peer. If the transport is
        not open, this raises :class:`autobahn.wamp.exception.TransportLost`.

        :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
        :type message: obj
        """

    @abc.abstractmethod
    def isOpen(self):
        """
        Check if the transport is open for messaging.

        :returns: bool -- ``True``, if the transport is open.
        """

    @abc.abstractmethod
    def close(self):
        """
        Close the transport regularly. The transport will perform any
        closing handshake if applicable. This should be used for any
        application initiated closing.
        """

    @abc.abstractmethod
    def abort(self):
        """
        Abort the transport abruptly. The transport will be destroyed as
        fast as possible, and without playing nice to the peer. This should
        only be used in case of fatal errors, protocol violations or possible
        detected attacks.
        """


@six.add_metaclass(abc.ABCMeta)
class ITransportHandler(object):

    @abc.abstractmethod
    def onOpen(self, transport):
        """
        Callback fired when transport is open.

        :param transport: An instance that implements :class:`autobahn.wamp.interfaces.ITransport`
        :type transport: obj
        """

    @abc.abstractmethod
    def onMessage(self, message):
        """
        Callback fired when a WAMP message was received.

        :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
        :type message: obj
        """

    @abc.abstractmethod
    def onClose(self, wasClean):
        """
        Callback fired when the transport has been closed.

        :param wasClean: Indicates if the transport has been closed regularly.
        :type wasClean: bool
        """


@six.add_metaclass(abc.ABCMeta)
class ISession(object):
    """
    Base interface for WAMP sessions.
    """

    @abc.abstractmethod
    def onConnect(self):
        """
        Callback fired when the transport this session will run over has
        been established.

        XXX Can I return Future/Deferred?
        """

    @abc.abstractmethod
    def join(self, realm):
        """
        Attach the session to the given realm. A session is open as soon as it is attached to a realm.
        """

    @abc.abstractmethod
    def onChallenge(self, challenge):
        """
        Callback fired when the peer demands authentication.

        XXX Can I return Future/Deferred?

        :param challenge: The authentication challenge.
        :type challenge: Instance of :class:`autobahn.wamp.types.Challenge`.
        """

    @abc.abstractmethod
    def onJoin(self, details):
        """
        Callback fired when WAMP session has been established.

        XXX Can I return Future/Deferred?

        :param details: Session information.
        :type details: Instance of :class:`autobahn.wamp.types.SessionDetails`.
        """

    @abc.abstractmethod
    def leave(self, reason=None, message=None):
        """
        Actively close this WAMP session.

        :param reason: An optional URI for the closing reason.
        :type reason: str
        :param message: An optional (human readable) closing message, intended for
                        logging purposes.
        :type message: str
        """

    @abc.abstractmethod
    def onLeave(self, details):
        """
        Callback fired when WAMP session has is closed

        XXX Can I return Future/Deferred?

        :param details: Close information.
        :type details: Instance of :class:`autobahn.wamp.types.CloseDetails`.
        """

    @abc.abstractmethod
    def disconnect(self):
        """
        Close the underlying transport.
        """

    @abc.abstractmethod
    def onDisconnect(self):
        """
        Callback fired when underlying transport has been closed.

        XXX Can I return Future/Deferred?
        """

    @abc.abstractmethod
    def define(self, exception, error=None):
        """
        Defines an exception for a WAMP error in the context of this WAMP session.

        :param exception: The exception class to define an error mapping for.
        :type exception: A class that derives of ``Exception``.
        :param error: The URI (or URI pattern) the exception class should be mapped for.
                      Iff the ``exception`` class is decorated, this must be ``None``.
        :type error: str
        """


class ICaller(ISession):
    """
    Interface for WAMP peers implementing role *Caller*.
    """

    @abc.abstractmethod
    def call(self, procedure, *args, **kwargs):
        """
        Call a remote procedure.

        This will return a Deferred/Future, that when resolved, provides the actual result
        returned by the called remote procedure.

        - If the result is a single positional return value, it'll be returned "as-is".

        - If the result contains multiple positional return values or keyword return values,
          the result is wrapped in an instance of :class:`autobahn.wamp.types.CallResult`.

        - If the call fails, the returned Deferred/Future will be rejected with an instance
          of :class:`autobahn.wamp.exception.ApplicationError`.

        If ``kwargs`` contains an ``options`` keyword argument that is an instance of
        :class:`autobahn.wamp.types.CallOptions`, this will provide specific options for
        the call to perform.

        When the *Caller* and *Dealer* implementations support canceling of calls, the call may
        be canceled by canceling the returned Deferred/Future.

        :param procedure: The URI of the remote procedure to be called, e.g. ``u"com.myapp.hello"``.
        :type procedure: unicode
        :param args: Any positional arguments for the call.
        :type args: list
        :param kwargs: Any keyword arguments for the call.
        :type kwargs: dict

        :returns: A Deferred/Future for the call result -
        :rtype: instance of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`
        """


@six.add_metaclass(abc.ABCMeta)
class IRegistration(object):
    """
    Represents a registration of an endpoint.
    """

    @abc.abstractproperty
    def id(self):
        """
        The WAMP registration ID for this registration.
        """

    @abc.abstractproperty
    def active(self):
        """
        Flag indicating if registration is active.
        """

    @abc.abstractmethod
    def unregister(self):
        """
        Unregister this registration that was previously created from
        :func:`autobahn.wamp.interfaces.ICallee.register`.

        After a registration has been unregistered successfully, no calls
        will be routed to the endpoint anymore.

        Returns an instance of :tx:`twisted.internet.defer.Deferred` (when
        running on **Twisted**) or an instance of :py:class:`asyncio.Future`
        (when running on **asyncio**).

        - If the unregistration succeeds, the returned Deferred/Future will
          *resolve* (with no return value).

        - If the unregistration fails, the returned Deferred/Future will be rejected
          with an instance of :class:`autobahn.wamp.exception.ApplicationError`.

        :returns: A Deferred/Future for the unregistration
        :rtype: instance(s) of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`
        """


class ICallee(ISession):
    """
    Interface for WAMP peers implementing role *Callee*.
    """

    @abc.abstractmethod
    def register(self, endpoint, procedure=None, options=None):
        """
        Register a procedure for remote calling.

        When ``endpoint`` is a callable (function, method or object that implements ``__call__``),
        then ``procedure`` must be provided and an instance of
        :tx:`twisted.internet.defer.Deferred` (when running on **Twisted**) or an instance
        of :py:class:`asyncio.Future` (when running on **asyncio**) is returned.

        - If the registration *succeeds* the returned Deferred/Future will *resolve* to
          an object that implements :class:`autobahn.wamp.interfaces.IRegistration`.

        - If the registration *fails* the returned Deferred/Future will *reject* with an
          instance of :class:`autobahn.wamp.exception.ApplicationError`.

        When ``endpoint`` is an object, then each of the object's methods that is decorated
        with :func:`autobahn.wamp.register` is automatically registered and a list of
        Deferreds/Futures is returned that each resolves or rejects as above.

        :param endpoint: The endpoint called under the procedure.
        :type endpoint: callable or object
        :param procedure: When ``endpoint`` is a callable, the URI (or URI pattern)
           of the procedure to register for. When ``endpoint`` is an object,
           the argument is ignored (and should be ``None``).
        :type procedure: unicode
        :param options: Options for registering.
        :type options: instance of :class:`autobahn.wamp.types.RegisterOptions`.

        :returns: A registration or a list of registrations (or errors)
        :rtype: instance(s) of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`
        """


@six.add_metaclass(abc.ABCMeta)
class IPublication(object):
    """
    Represents a publication of an event. This is used with acknowledged publications.
    """

    @abc.abstractproperty
    def id(self):
        """
        The WAMP publication ID for this publication.
        """


class IPublisher(ISession):
    """
    Interface for WAMP peers implementing role *Publisher*.
    """

    @abc.abstractmethod
    def publish(self, topic, *args, **kwargs):
        """
        Publish an event to a topic.

        If ``kwargs`` contains an ``options`` keyword argument that is an instance of
        :class:`autobahn.wamp.types.PublishOptions`, this will provide
        specific options for the publish to perform.

        .. note::
           By default, publications are non-acknowledged and the publication can
           fail silently, e.g. because the session is not authorized to publish
           to the topic.

        When publication acknowledgement is requested via ``options.acknowledge == True``,
        this function returns a Deferred/Future:

        - If the publication succeeds the Deferred/Future will resolve to an object
          that implements :class:`autobahn.wamp.interfaces.IPublication`.

        - If the publication fails the Deferred/Future will reject with an instance
          of :class:`autobahn.wamp.exception.ApplicationError`.

        :param topic: The URI of the topic to publish to, e.g. ``u"com.myapp.mytopic1"``.
        :type topic: unicode
        :param args: Arbitrary application payload for the event (positional arguments).
        :type args: list
        :param kwargs: Arbitrary application payload for the event (keyword arguments).
        :type kwargs: dict

        :returns: Acknowledgement for acknowledge publications - otherwise nothing.
        :rtype: ``None`` or instance of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`
        """


@six.add_metaclass(abc.ABCMeta)
class ISubscription(object):
    """
    Represents a subscription to a topic.
    """

    @abc.abstractproperty
    def id(self):
        """
        The WAMP subscription ID for this subscription.
        """

    @abc.abstractproperty
    def active(self):
        """
        Flag indicating if subscription is active.
        """

    @abc.abstractmethod
    def unsubscribe(self):
        """
        Unsubscribe this subscription that was previously created from
        :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`.

        After a subscription has been unsubscribed successfully, no events
        will be routed to the event handler anymore.

        Returns an instance of :tx:`twisted.internet.defer.Deferred` (when
        running on **Twisted**) or an instance of :py:class:`asyncio.Future`
        (when running on **asyncio**).

        - If the unsubscription succeeds, the returned Deferred/Future will
          *resolve* (with no return value).

        - If the unsubscription fails, the returned Deferred/Future will *reject*
          with an instance of :class:`autobahn.wamp.exception.ApplicationError`.

        :returns: A Deferred/Future for the unsubscription
        :rtype: instance(s) of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`
        """


class ISubscriber(ISession):
    """
    Interface for WAMP peers implementing role *Subscriber*.
    """

    @abc.abstractmethod
    def subscribe(self, handler, topic=None, options=None):
        """
        Subscribe to a topic for receiving events.

        When ``handler`` is a callable (function, method or object that implements ``__call__``),
        then `topic` must be provided and an instance of
        :tx:`twisted.internet.defer.Deferred` (when running on **Twisted**) or an instance
        of :class:`asyncio.Future` (when running on **asyncio**) is returned.

        - If the subscription succeeds the Deferred/Future will resolve to an object
          that implements :class:`autobahn.wamp.interfaces.ISubscription`.

        - If the subscription fails the Deferred/Future will reject with an instance
          of :class:`autobahn.wamp.exception.ApplicationError`.

        When ``handler`` is an object, then each of the object's methods that is decorated
        with :func:`autobahn.wamp.subscribe` is automatically subscribed as event handlers,
        and a list of Deferreds/Futures is returned that each resolves or rejects as above.

        :param handler: The event handler to receive events.
        :type handler: callable or object
        :param topic: When ``handler`` is a callable, the URI (or URI pattern)
           of the topic to subscribe to. When ``handler`` is an object, this
           value is ignored (and should be ``None``).
        :type topic: unicode
        :param options: Options for subscribing.
        :type options: An instance of :class:`autobahn.wamp.types.SubscribeOptions`.

        :returns: A single Deferred/Future or a list of such objects
        :rtype: instance(s) of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`
        """
