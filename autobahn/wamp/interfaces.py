###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
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

__all__ = (
    'IObjectSerializer',
    'ISerializer',
    'ITransport',
    'ITransportHandler',
    'ISession',
    'IApplicationSession',
)


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
        Serializes a WAMP message to bytes for sending over a transport.

        :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
        :type message: obj

        :returns: tuple -- A pair ``(payload, is_binary)``.
        """

    @abc.abstractmethod
    def unserialize(self, payload, is_binary):
        """
        Deserialize bytes from a transport and parse into WAMP messages.

        :param payload: Byte string from wire.
        :type payload: bytes
        :param is_binary: Type of payload. True if payload is a binary string, else
            the payload is UTF-8 encoded Unicode text.
        :type is_binary: bool

        :returns: list -- List of ``a.w.m.Message`` objects.
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
        Returns a deferred/future when the message has been processed and more
        messages may be sent. When send() is called while a previous deferred/future
        has not yet fired, the send will fail immediately.

        :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
        :type message: obj

        :returns: obj -- A Deferred/Future
        """

    @abc.abstractmethod
    def is_open(self):
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

    @abc.abstractmethod
    def get_channel_id(self):
        """
        Return the unique channel ID of the underlying transport. This is used to
        mitigate credential forwarding man-in-the-middle attacks when running
        application level authentication (eg WAMP-cryptosign) which are decoupled
        from the underlying transport.

        The channel ID is only available when running over TLS (either WAMP-WebSocket
        or WAMP-RawSocket). It is not available for non-TLS transports (plain TCP or
        Unix domain sockets). It is also not available for WAMP-over-HTTP/Longpoll.
        Further, it is currently unimplemented for asyncio (only works on Twisted).

        The channel ID is computed as follows:

           - for a client, the SHA256 over the "TLS Finished" message sent by the client
             to the server is returned.

           - for a server, the SHA256 over the "TLS Finished" message the server expected
             the client to send

        Note: this is similar to `tls-unique` as described in RFC5929, but instead
        of returning the raw "TLS Finished" message, it returns a SHA256 over such a
        message. The reason is that we use the channel ID mainly with WAMP-cryptosign,
        which is based on Ed25519, where keys are always 32 bytes. And having a channel ID
        which is always 32 bytes (independent of the TLS ciphers/hashfuns in use) allows
        use to easily XOR channel IDs with Ed25519 keys and WAMP-cryptosign challenges.

        WARNING: For safe use of this (that is, for safely binding app level authentication
        to the underlying transport), you MUST use TLS, and you SHOULD deactivate both
        TLS session renegotiation and TLS session resumption.

        References:

           - https://tools.ietf.org/html/rfc5056
           - https://tools.ietf.org/html/rfc5929
           - http://www.pyopenssl.org/en/stable/api/ssl.html#OpenSSL.SSL.Connection.get_finished
           - http://www.pyopenssl.org/en/stable/api/ssl.html#OpenSSL.SSL.Connection.get_peer_finished

        :returns: The channel ID (if available) of the underlying WAMP transport. The
            channel ID is a 32 bytes value.
        :rtype: binary or None
        """


@six.add_metaclass(abc.ABCMeta)
class ITransportHandler(object):

    @abc.abstractproperty
    def transport(self):
        """
        When the transport this handler is attached to is currently open, this property
        can be read from. The property should be considered read-only. When the transport
        is gone, this property is set to None.
        """

    @abc.abstractmethod
    def on_open(self, transport):
        """
        Callback fired when transport is open. May run asynchronously. The transport
        is considered running and is_open() would return true, as soon as this callback
        has completed successfully.

        :param transport: An instance that implements :class:`autobahn.wamp.interfaces.ITransport`
        :type transport: obj
        """

    @abc.abstractmethod
    def on_message(self, message):
        """
        Callback fired when a WAMP message was received. May run asynchronously. The callback
        should return or fire the returned deferred/future when it's done processing the message.
        In particular, an implementation of this callback must not access the message afterwards.

        :param message: An instance that implements :class:`autobahn.wamp.interfaces.IMessage`
        :type message: obj
        """

    @abc.abstractmethod
    def on_close(self, was_clean):
        """
        Callback fired when the transport has been closed.

        :param was_clean: Indicates if the transport has been closed regularly.
        :type was_clean: bool
        """


@six.add_metaclass(abc.ABCMeta)
class ISession(object):
    """
    Base interface for WAMP sessions.
    """

    @abc.abstractmethod
    def on_connect(self):
        """
        Callback fired when the transport this session will run over has been established.
        """

    @abc.abstractmethod
    def join(self, realm):
        """
        Attach the session to the given realm. A session is open as soon as it is attached to a realm.
        """

    @abc.abstractmethod
    def on_challenge(self, challenge):
        """
        Callback fired when the peer demands authentication.

        May return a Deferred/Future.

        :param challenge: The authentication challenge.
        :type challenge: Instance of :class:`autobahn.wamp.types.Challenge`.
        """

    @abc.abstractmethod
    def on_join(self, details):
        """
        Callback fired when WAMP session has been established.

        May return a Deferred/Future.

        :param details: Session information.
        :type details: Instance of :class:`autobahn.wamp.types.SessionDetails`.
        """

    @abc.abstractmethod
    def leave(self, reason=None, message=None):
        """
        Actively close this WAMP session.

        :param reason: An optional URI for the closing reason. If you
            want to permanently log out, this should be `wamp.close.logout`
        :type reason: str

        :param message: An optional (human readable) closing message, intended for
                        logging purposes.
        :type message: str

        :return: may return a Future/Deferred that fires when we've disconnected
        """

    @abc.abstractmethod
    def on_leave(self, details):
        """
        Callback fired when WAMP session has is closed

        :param details: Close information.
        :type details: Instance of :class:`autobahn.wamp.types.CloseDetails`.
        """

    @abc.abstractmethod
    def disconnect(self):
        """
        Close the underlying transport.
        """

    @abc.abstractmethod
    def is_connected(self):
        """
        Check if the underlying transport is connected.
        """

    @abc.abstractmethod
    def is_attached(self):
        """
        Check if the session has currently joined a realm.
        """

    @abc.abstractmethod
    def on_disconnect(self):
        """
        Callback fired when underlying transport has been closed.
        """


@six.add_metaclass(abc.ABCMeta)
class IApplicationSession(ISession):
    """
    Interface for WAMP client peers implementing the four different
    WAMP roles (caller, callee, publisher, subscriber).
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
        with :func:`autobahn.wamp.register` is automatically registered and a (single)
        DeferredList or Future is returned that gathers all individual underlying Deferreds/Futures.

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
