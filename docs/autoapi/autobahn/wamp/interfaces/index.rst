:mod:`autobahn.wamp.interfaces`
===============================

.. py:module:: autobahn.wamp.interfaces


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.interfaces.IObjectSerializer
   autobahn.wamp.interfaces.ISerializer
   autobahn.wamp.interfaces.IMessage
   autobahn.wamp.interfaces.ITransport
   autobahn.wamp.interfaces.ITransportHandler
   autobahn.wamp.interfaces.ISession
   autobahn.wamp.interfaces.IPayloadCodec



.. class:: IObjectSerializer

   Bases: :class:`abc.ABC`

   Raw Python object serialization and deserialization. Object serializers are
   used by classes implementing WAMP serializers, that is instances of
   :class:`autobahn.wamp.interfaces.ISerializer`.

   .. method:: BINARY(self)
      :abstractmethod:

      Flag (read-only) to indicate if serializer requires a binary clean
      transport or if UTF8 transparency is sufficient.


   .. method:: serialize(self, obj)
      :abstractmethod:

      Serialize an object to a byte string.

      :param obj: Object to serialize.
      :type obj: any (serializable type)

      :returns: Serialized bytes.
      :rtype: bytes


   .. method:: unserialize(self, payload)
      :abstractmethod:

      Unserialize objects from a byte string.

      :param payload: Objects to unserialize.
      :type payload: bytes

      :returns: List of (raw) objects unserialized.
      :rtype: list



.. class:: ISerializer

   Bases: :class:`abc.ABC`

   WAMP message serialization and deserialization.

   .. method:: MESSAGE_TYPE_MAP(self)
      :abstractmethod:

      Mapping of WAMP message type codes to WAMP message classes.


   .. method:: SERIALIZER_ID(self)
      :abstractmethod:

      The WAMP serialization format ID.


   .. method:: serialize(self, message)
      :abstractmethod:

      Serializes a WAMP message to bytes for sending over a transport.

      :param message: The WAMP message to be serialized.
      :type message: object implementing :class:`autobahn.wamp.interfaces.IMessage`

      :returns: A pair ``(payload, isBinary)``.
      :rtype: tuple


   .. method:: unserialize(self, payload, isBinary)
      :abstractmethod:

      Deserialize bytes from a transport and parse into WAMP messages.

      :param payload: Byte string from wire.
      :type payload: bytes

      :param is_binary: Type of payload. True if payload is a binary string, else
          the payload is UTF-8 encoded Unicode text.
      :type is_binary: bool

      :returns: List of ``a.w.m.Message`` objects.
      :rtype: list



.. class:: IMessage

   Bases: :class:`abc.ABC`

   
   .. method:: MESSAGE_TYPE(self)
      :abstractmethod:

      WAMP message type code.


   .. method:: parse(wmsg)
      :staticmethod:
      :abstractmethod:

      Factory method that parses a unserialized raw message (as returned byte
      :func:`autobahn.interfaces.ISerializer.unserialize`) into an instance
      of this class.

      :returns: The parsed WAMP message.
      :rtype: object implementing :class:`autobahn.wamp.interfaces.IMessage`


   .. method:: serialize(self, serializer)
      :abstractmethod:

      Serialize this object into a wire level bytes representation and cache
      the resulting bytes. If the cache already contains an entry for the given
      serializer, return the cached representation directly.

      :param serializer: The wire level serializer to use.
      :type serializer: object implementing :class:`autobahn.wamp.interfaces.ISerializer`

      :returns: The serialized bytes.
      :rtype: bytes


   .. method:: uncache(self)
      :abstractmethod:

      Resets the serialization cache for this message.



.. class:: ITransport

   Bases: :class:`abc.ABC`

   A WAMP transport is a bidirectional, full-duplex, reliable, ordered,
   message-based channel.

   .. method:: send(self, message)
      :abstractmethod:

      Send a WAMP message over the transport to the peer. If the transport is
      not open, this raises :class:`autobahn.wamp.exception.TransportLost`.
      Returns a deferred/future when the message has been processed and more
      messages may be sent. When send() is called while a previous deferred/future
      has not yet fired, the send will fail immediately.

      :param message: The WAMP message to send over the transport.
      :type message: object implementing :class:`autobahn.wamp.interfaces.IMessage`

      :returns: obj -- A Deferred/Future


   .. method:: isOpen(self)
      :abstractmethod:

      Check if the transport is open for messaging.

      :returns: ``True``, if the transport is open.
      :rtype: bool


   .. method:: close(self)
      :abstractmethod:

      Close the transport regularly. The transport will perform any
      closing handshake if applicable. This should be used for any
      application initiated closing.


   .. method:: abort(self)
      :abstractmethod:

      Abort the transport abruptly. The transport will be destroyed as
      fast as possible, and without playing nice to the peer. This should
      only be used in case of fatal errors, protocol violations or possible
      detected attacks.


   .. method:: get_channel_id(self)
      :abstractmethod:

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



.. class:: ITransportHandler

   Bases: :class:`abc.ABC`

   Helper class that provides a standard way to create an ABC using
   inheritance.

   .. method:: transport(self)
      :abstractmethod:

      When the transport this handler is attached to is currently open, this property
      can be read from. The property should be considered read-only. When the transport
      is gone, this property is set to None.


   .. method:: onOpen(self, transport)
      :abstractmethod:

      Callback fired when transport is open. May run asynchronously. The transport
      is considered running and is_open() would return true, as soon as this callback
      has completed successfully.

      :param transport: The WAMP transport.
      :type transport: object implementing :class:`autobahn.wamp.interfaces.ITransport`


   .. method:: onMessage(self, message)
      :abstractmethod:

      Callback fired when a WAMP message was received. May run asynchronously. The callback
      should return or fire the returned deferred/future when it's done processing the message.
      In particular, an implementation of this callback must not access the message afterwards.

      :param message: The WAMP message received.
      :type message: object implementing :class:`autobahn.wamp.interfaces.IMessage`


   .. method:: onClose(self, wasClean)
      :abstractmethod:

      Callback fired when the transport has been closed.

      :param wasClean: Indicates if the transport has been closed regularly.
      :type wasClean: bool



.. class:: ISession(config=None)


   Bases: :class:`abc.ABC`

   Interface for WAMP sessions.

   .. method:: onUserError(self, fail, msg)
      :abstractmethod:

      This is called when we try to fire a callback, but get an
      exception from user code -- for example, a registered publish
      callback or a registered method. By default, this prints the
      current stack-trace and then error-message to stdout.

      ApplicationSession-derived objects may override this to
      provide logging if they prefer. The Twisted implemention does
      this. (See :class:`autobahn.twisted.wamp.ApplicationSession`)

      :param fail: The failure that occurred.
      :type fail: instance implementing txaio.IFailedFuture

      :param msg: an informative message from the library. It is
          suggested you log this immediately after the exception.
      :type msg: str


   .. method:: onConnect(self)
      :abstractmethod:

      Callback fired when the transport this session will run over has been established.


   .. method:: join(self, realm, authmethods=None, authid=None, authrole=None, authextra=None, resumable=None, resume_session=None, resume_token=None)
      :abstractmethod:

      Attach the session to the given realm. A session is open as soon as it is attached to a realm.


   .. method:: onChallenge(self, challenge)
      :abstractmethod:

      Callback fired when the peer demands authentication.

      May return a Deferred/Future.

      :param challenge: The authentication challenge.
      :type challenge: Instance of :class:`autobahn.wamp.types.Challenge`.


   .. method:: onWelcome(self, welcome_msg)
      :abstractmethod:

      Callback fired after the peer has successfully authenticated. If
      this returns anything other than None/False, the session is
      aborted and the return value is used as an error message.

      May return a Deferred/Future.

      :param welcome_msg: The WELCOME message received from the server
      :type challenge: Instance of :class:`autobahn.wamp.message.Welcome`.

      :return: None, or an error message


   .. method:: onJoin(self, details)
      :abstractmethod:

      Callback fired when WAMP session has been established.

      May return a Deferred/Future.

      :param details: Session information.
      :type details: Instance of :class:`autobahn.wamp.types.SessionDetails`.


   .. method:: leave(self, reason=None, message=None)
      :abstractmethod:

      Actively close this WAMP session.

      :param reason: An optional URI for the closing reason. If you
          want to permanently log out, this should be `wamp.close.logout`
      :type reason: str

      :param message: An optional (human readable) closing message, intended for
                      logging purposes.
      :type message: str

      :return: may return a Future/Deferred that fires when we've disconnected


   .. method:: onLeave(self, details)
      :abstractmethod:

      Callback fired when WAMP session has is closed

      :param details: Close information.
      :type details: Instance of :class:`autobahn.wamp.types.CloseDetails`.


   .. method:: disconnect(self)
      :abstractmethod:

      Close the underlying transport.


   .. method:: onDisconnect(self)
      :abstractmethod:

      Callback fired when underlying transport has been closed.


   .. method:: is_connected(self)
      :abstractmethod:

      Check if the underlying transport is connected.


   .. method:: is_attached(self)
      :abstractmethod:

      Check if the session has currently joined a realm.


   .. method:: set_payload_codec(self, payload_codec)
      :abstractmethod:

      Set a payload codec on the session. To remove a previously set payload codec,
      set the codec to ``None``.

      Payload codecs are used with WAMP payload transparency mode.

      :param payload_codec: The payload codec that should process application
          payload of the given encoding.
      :type payload_codec: object
          implementing :class:`autobahn.wamp.interfaces.IPayloadCodec` or ``None``


   .. method:: get_payload_codec(self)
      :abstractmethod:

      Get the current payload codec (if any) for the session.

      Payload codecs are used with WAMP payload transparency mode.

      :returns: The current payload codec or ``None`` if no codec is active.
      :rtype: object implementing
          :class:`autobahn.wamp.interfaces.IPayloadCodec` or ``None``


   .. method:: define(self, exception, error=None)
      :abstractmethod:

      Defines an exception for a WAMP error in the context of this WAMP session.

      :param exception: The exception class to define an error mapping for.
      :type exception: A class that derives of ``Exception``.

      :param error: The URI (or URI pattern) the exception class should be mapped for.
          Iff the ``exception`` class is decorated, this must be ``None``.
      :type error: str


   .. method:: call(self, procedure, *args, **kwargs)
      :abstractmethod:

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

      :param procedure: The URI of the remote procedure to be called, e.g. ``"com.myapp.hello"``.
      :type procedure: unicode

      :param args: Any positional arguments for the call.
      :type args: list

      :param kwargs: Any keyword arguments for the call.
      :type kwargs: dict

      :returns: A Deferred/Future for the call result -
      :rtype: instance of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`


   .. method:: register(self, endpoint, procedure=None, options=None, prefix=None, check_types=None)
      :abstractmethod:

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


      :param prefix: if not None, this specifies a prefix to prepend
          to all URIs registered for this class. So if there was an
          @wamp.register('method_foo') on a method and
          prefix='com.something.' then a method
          'com.something.method_foo' would ultimately be registered.
      :type prefix: str

      :param check_types: Enable automatic type checking against (Python 3.5+) type hints
          specified on the ``endpoint`` callable. Types are checked at run-time on each
          invocation of the ``endpoint`` callable. When a type mismatch occurs, the error
          is forwarded to the callee code in ``onUserError`` override method of
          :class:`autobahn.wamp.protocol.ApplicationSession`. An error
          of type :class:`autobahn.wamp.exception.TypeCheckError` is also raised and
          returned to the caller (via the router).
      :type check_types: bool

      :returns: A registration or a list of registrations (or errors)
      :rtype: instance(s) of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`


   .. method:: publish(self, topic, *args, **kwargs)
      :abstractmethod:

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

      :param topic: The URI of the topic to publish to, e.g. ``"com.myapp.mytopic1"``.
      :type topic: unicode

      :param args: Arbitrary application payload for the event (positional arguments).
      :type args: list

      :param kwargs: Arbitrary application payload for the event (keyword arguments).
      :type kwargs: dict

      :returns: Acknowledgement for acknowledge publications - otherwise nothing.
      :rtype: ``None`` or instance of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`


   .. method:: subscribe(self, handler, topic=None, options=None, check_types=None)
      :abstractmethod:

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

      :param check_types: Enable automatic type checking against (Python 3.5+) type hints
          specified on the ``endpoint`` callable. Types are checked at run-time on each
          invocation of the ``endpoint`` callable. When a type mismatch occurs, the error
          is forwarded to the subscriber code in ``onUserError`` override method of
          :class:`autobahn.wamp.protocol.ApplicationSession`.
      :type check_types: bool

      :returns: A single Deferred/Future or a list of such objects
      :rtype: instance(s) of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`



.. class:: IPayloadCodec

   Bases: :class:`abc.ABC`

   WAMP payload codecs are used with WAMP payload transparency mode.

   In payload transparency mode, application payloads are transmitted "raw",
   as binary strings, without any processing at the WAMP router.

   Payload transparency can be used eg for these use cases:

   * end-to-end encryption of application payloads (WAMP-cryptobox)
   * using serializers with custom user types, where the serializer and
     the serializer implementation has native support for serializing
     custom types (such as CBOR)
   * transmitting MQTT payloads within WAMP, when the WAMP router is
     providing a MQTT-WAMP bridge

   .. method:: encode(self, is_originating, uri, args=None, kwargs=None)
      :abstractmethod:

      Encodes application payload.

      :param is_originating: Flag indicating whether the encoding
          is to be done from an originator (a caller or publisher).
      :type is_originating: bool

      :param uri: The WAMP URI associated with the WAMP message for which
          the payload is to be encoded (eg topic or procedure).
      :type uri: str

      :param args: Positional application payload.
      :type args: list or None

      :param kwargs: Keyword-based application payload.
      :type kwargs: dict or None

      :returns: The encoded application payload or None to
          signal no encoding should be used.
      :rtype: instance of :class:`autobahn.wamp.types.EncodedPayload`


   .. method:: decode(self, is_originating, uri, encoded_payload)
      :abstractmethod:

      Decode application payload.

      :param is_originating: Flag indicating whether the encoding
          is to be done from an originator (a caller or publisher).
      :type is_originating: bool

      :param uri: The WAMP URI associated with the WAMP message for which
          the payload is to be encoded (eg topic or procedure).
      :type uri: str

      :param payload: The encoded application payload to be decoded.
      :type payload: instance of :class:`autobahn.wamp.types.EncodedPayload`

      :returns: A tuple with the decoded positional and keyword-based
          application payload: ``(uri, args, kwargs)``
      :rtype: tuple



