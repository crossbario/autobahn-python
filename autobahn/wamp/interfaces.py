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
from typing import Union, Dict, Any, Optional, List, Tuple, Callable

# FIXME: see ISecurityModule.__iter__
# from collections.abc import Iterator

from autobahn.util import public
from autobahn.wamp.types import Challenge, SessionDetails, CloseDetails, CallResult, RegisterOptions, \
    SubscribeOptions, Registration, Subscription, Publication, ComponentConfig, TransportDetails
from autobahn.wamp.message import Message, Welcome

__all__ = (
    'IObjectSerializer',
    'ISerializer',
    'IMessage',
    'ITransport',
    'ITransportHandler',
    'ISession',
    'IAuthenticator',
    'IKey',
    'ICryptosignKey',
    'IEthereumKey',
    'ISecurityModule',
    'IPayloadCodec',
)


@public
class IObjectSerializer(abc.ABC):
    """
    Raw Python object serialization and deserialization. Object serializers are
    used by classes implementing WAMP serializers, that is instances of
    :class:`autobahn.wamp.interfaces.ISerializer`.
    """

    @public
    @property
    @abc.abstractmethod
    def NAME(self) -> str:
        """
        Object serializer name (read-only).
        """

    @public
    @property
    @abc.abstractmethod
    def BINARY(self) -> bool:
        """
        Flag (read-only) to indicate if serializer requires a binary clean
        transport or if UTF8 transparency is sufficient.
        """

    @public
    @abc.abstractmethod
    def serialize(self, obj: Any) -> bytes:
        """
        Serialize an object to a byte string.

        :param obj: Object (any serializable type) to serialize.

        :returns: Serialized bytes.
        """

    @public
    @abc.abstractmethod
    def unserialize(self, payload: bytes) -> List[Any]:
        """
        Deserialize objects from a byte string.

        :param payload: Objects to deserialize.

        :returns: List of deserialized (raw) objects.
        """


@public
class ISerializer(abc.ABC):
    """
    WAMP message serialization and deserialization.
    """

    @public
    @property
    @abc.abstractmethod
    def MESSAGE_TYPE_MAP(self) -> Dict[int, 'IMessage']:
        """
        Mapping of WAMP message type codes to WAMP message classes.
        """

    @public
    @property
    @abc.abstractmethod
    def SERIALIZER_ID(self) -> str:
        """
        The WAMP serialization format ID as used for WebSocket, e.g. ``"json"`` (or ``"json.batched"``) for JSON.
        """

    @public
    @property
    @abc.abstractmethod
    def RAWSOCKET_SERIALIZER_ID(self) -> int:
        """
        The WAMP serialization format ID as used for RawSocket, e.g. ``1`` for JSON.
        """

    @public
    @property
    @abc.abstractmethod
    def MIME_TYPE(self) -> str:
        """
        The WAMP serialization format MIME type, e.g. ``"application/json"`` for JSON.
        """

    @public
    @abc.abstractmethod
    def serialize(self, message: 'IMessage') -> Tuple[bytes, bool]:
        """
        Serializes a WAMP message to bytes for sending over a WAMP transport.

        :param message: The WAMP message to be serialized.

        :returns: A pair ``(payload, is_binary)``.
        """

    @public
    @abc.abstractmethod
    def unserialize(self, payload: bytes, is_binary: Optional[bool] = None) -> List['IMessage']:
        """
        Deserialize bytes from a transport and parse into WAMP messages.

        :param payload: Byte string from wire.

        :param is_binary: Type of payload. True if payload is a binary string, else
            the payload is UTF-8 encoded Unicode text.

        :returns: List of WAMP messages.
        """


@public
class IMessage(abc.ABC):
    """
    A WAMP message, e.g. one of the messages defined in the WAMP specification
    `here <https://wamp-proto.org/_static/gen/wamp_latest_ietf.html#rfc.section.6.5>`_.
    """

    @public
    @property
    @abc.abstractmethod
    def MESSAGE_TYPE(self) -> int:
        """
        WAMP message type code.
        """

    # the following requires Python 3.3+ and exactly this order of decorators
    # http://stackoverflow.com/questions/4474395/staticmethod-and-abc-abstractmethod-will-it-blend
    @public
    @staticmethod
    @abc.abstractmethod
    def parse(wmsg) -> 'IMessage':
        """
        Factory method that parses a unserialized raw message (as returned byte
        :func:`autobahn.interfaces.ISerializer.unserialize`) into an instance
        of this class.

        :returns: The parsed WAMP message.
        """

    @public
    @abc.abstractmethod
    def serialize(self, serializer: ISerializer) -> bytes:
        """
        Serialize this object into a wire level bytes representation and cache
        the resulting bytes. If the cache already contains an entry for the given
        serializer, return the cached representation directly.

        :param serializer: The wire level serializer to use.

        :returns: The serialized bytes.
        """

    @public
    @abc.abstractmethod
    def uncache(self):
        """
        Resets the serialization cache for this message.
        """


IMessage.register(Message)


@public
class ITransport(abc.ABC):
    """
    A WAMP transport is a bidirectional, full-duplex, reliable, ordered,
    message-based channel.
    """

    @public
    @abc.abstractmethod
    def send(self, message: IMessage):
        """
        Send a WAMP message over the transport to the peer. If the transport is
        not open, this raises :class:`autobahn.wamp.exception.TransportLost`.
        Returns a deferred/future when the message has been processed and more
        messages may be sent. When send() is called while a previous deferred/future
        has not yet fired, the send will fail immediately.

        :param message: The WAMP message to send over the transport.
        """

    @public
    @abc.abstractmethod
    def isOpen(self) -> bool:
        """
        Check if the transport is open for messaging.

        :returns: ``True``, if the transport is open.
        """

    @public
    @property
    @abc.abstractmethod
    def transport_details(self) -> Optional[TransportDetails]:
        """
        Return details about the transport (when the transport is open).
        """

    @public
    @abc.abstractmethod
    def close(self):
        """
        Close the transport regularly. The transport will perform any
        closing handshake if applicable. This should be used for any
        application initiated closing.
        """

    @public
    @abc.abstractmethod
    def abort(self):
        """
        Abort the transport abruptly. The transport will be destroyed as
        fast as possible, and without playing nice to the peer. This should
        only be used in case of fatal errors, protocol violations or possible
        detected attacks.
        """


@public
class ITransportHandler(abc.ABC):

    @public
    @abc.abstractmethod
    def onOpen(self, transport: ITransport):
        """
        Callback fired when transport is open. May run asynchronously. The transport
        is considered running and is_open() would return true, as soon as this callback
        has completed successfully.

        :param transport: The WAMP transport.
        """

    @public
    @abc.abstractmethod
    def onMessage(self, message: IMessage):
        """
        Callback fired when a WAMP message was received. May run asynchronously. The callback
        should return or fire the returned deferred/future when it's done processing the message.
        In particular, an implementation of this callback must not access the message afterwards.

        :param message: The WAMP message received.
        """

    @public
    @abc.abstractmethod
    def onClose(self, wasClean: bool):
        """
        Callback fired when the transport has been closed.

        :param wasClean: Indicates if the transport has been closed regularly.
        """


# ISession.register collides with the abc.ABCMeta.register method
class _ABC(abc.ABC):
    abc_register = abc.ABC.register


@public
class ISession(_ABC):
    """
    Interface for WAMP sessions.
    """

    @public
    @property
    @abc.abstractmethod
    def config(self) -> ComponentConfig:
        """
        Configuration for session.
        """

    @public
    @property
    @abc.abstractmethod
    def transport(self) -> Optional[ITransport]:
        """
        When the transport this session is attached to is currently open, this property
        can be read from. The property should be considered read-only. When the transport
        is gone, this property is set to None.
        """

    @public
    @property
    @abc.abstractmethod
    def session_details(self) -> Optional[SessionDetails]:
        """
        Return details about the session, the same as initially provided to the
        :meth:`ISession.onJoin` callback on an implementation.
        """

    @public
    @abc.abstractmethod
    def onUserError(self, fail, msg):
        """
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
        """

    @public
    @abc.abstractmethod
    def onConnect(self):
        """
        Callback fired when the transport this session will run over has been established.
        """

    @public
    @abc.abstractmethod
    def join(self,
             realm: str,
             authmethods: Optional[List[str]] = None,
             authid: Optional[str] = None,
             authrole: Optional[str] = None,
             authextra: Optional[Dict[str, Any]] = None,
             resumable: Optional[bool] = None,
             resume_session: Optional[int] = None,
             resume_token: Optional[str] = None):
        """
        Attach the session to the given realm. A session is open as soon as it is attached to a realm.
        """

    @public
    @abc.abstractmethod
    def onChallenge(self, challenge: Challenge) -> str:
        """
        Callback fired when the peer demands authentication.

        May return a Deferred/Future.

        :param challenge: The authentication challenge.
        """

    @public
    @abc.abstractmethod
    def onWelcome(self, welcome: Welcome) -> Optional[str]:
        """
        Callback fired after the peer has successfully authenticated. If
        this returns anything other than None/False, the session is
        aborted and the return value is used as an error message.

        May return a Deferred/Future.

        .. note::
            Before we let user code see the session -- that is, before we fire "join"
            we give authentication instances a chance to abort the session. Usually
            this would be for "mutual authentication" scenarios. For example, WAMP-SCRAM
            uses this to confirm the server-signature.

        :param welcome: The WELCOME message received from the server

        :return: None, or an error message (using a fixed error URI
            ``wamp.error.cannot_authenticate``).
        """

    @public
    @abc.abstractmethod
    def onJoin(self, details: SessionDetails):
        """
        Callback fired when WAMP session has been established.

        May return a Deferred/Future.

        :param details: Session information.
        """

    @public
    @abc.abstractmethod
    def leave(self, reason: Optional[str] = None, message: Optional[str] = None):
        """
        Actively close this WAMP session.

        :param reason: An optional URI for the closing reason. If you
            want to permanently log out, this should be ``wamp.close.logout``.

        :param message: An optional (human-readable) closing message, intended for
            logging purposes.

        :return: may return a Future/Deferred that fires when we've disconnected
        """

    @public
    @abc.abstractmethod
    def onLeave(self, details: CloseDetails):
        """
        Callback fired when WAMP session has is closed

        :param details: Close information for session.
        """

    @public
    @abc.abstractmethod
    def disconnect(self):
        """
        Close the underlying transport.
        """

    @public
    @abc.abstractmethod
    def onDisconnect(self):
        """
        Callback fired when underlying transport has been closed.
        """

    @public
    @abc.abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the underlying transport is connected.
        """

    @public
    @abc.abstractmethod
    def is_attached(self) -> bool:
        """
        Check if the session has currently joined a realm.
        """

    @public
    @abc.abstractmethod
    def set_payload_codec(self, payload_codec: Optional['IPayloadCodec']):
        """
        Set a payload codec on the session. To remove a previously set payload codec,
        set the codec to ``None``.

        Payload codecs are used with WAMP payload transparency mode.

        :param payload_codec: The payload codec that should process application
            payload of the given encoding.
        """

    @public
    @abc.abstractmethod
    def get_payload_codec(self) -> Optional['IPayloadCodec']:
        """
        Get the current payload codec (if any) for the session.

        Payload codecs are used with WAMP payload transparency mode.

        :returns: The current payload codec or ``None`` if no codec is active.
        """

    @public
    @abc.abstractmethod
    def define(self, exception: Exception, error: Optional[str] = None):
        """
        Defines an exception for a WAMP error in the context of this WAMP session.

        :param exception: The exception class to define an error mapping for.

        :param error: The URI (or URI pattern) the exception class should be mapped for.
            Iff the ``exception`` class is decorated, this must be ``None``.
        """

    @public
    @abc.abstractmethod
    def call(self, procedure: str, *args, **kwargs) -> Union[Any, CallResult]:
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

        :param procedure: The URI of the remote procedure to be called, e.g. ``"com.myapp.hello"``.

        :param args: Any positional arguments for the call.

        :param kwargs: Any keyword arguments for the call.

        :returns: A Deferred/Future for the call result.
        """

    @public
    @abc.abstractmethod
    def register(self, endpoint: Union[Callable, Any], procedure: Optional[str] = None,
                 options: Optional[RegisterOptions] = None, prefix: Optional[str] = None,
                 check_types: Optional[bool] = None) -> Union[Registration, List[Registration]]:
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

        :param procedure: When ``endpoint`` is a callable, the URI (or URI pattern)
           of the procedure to register for. When ``endpoint`` is an object,
           the argument is ignored (and should be ``None``).

        :param options: Options for registering.

        :param prefix: if not None, this specifies a prefix to prepend
            to all URIs registered for this class. So if there was an
            @wamp.register('method_foo') on a method and
            prefix='com.something.' then a method
            'com.something.method_foo' would ultimately be registered.

        :param check_types: Enable automatic type checking against (Python 3.5+) type hints
            specified on the ``endpoint`` callable. Types are checked at run-time on each
            invocation of the ``endpoint`` callable. When a type mismatch occurs, the error
            is forwarded to the callee code in ``onUserError`` override method of
            :class:`autobahn.wamp.protocol.ApplicationSession`. An error
            of type :class:`autobahn.wamp.exception.TypeCheckError` is also raised and
            returned to the caller (via the router).

        :returns: A registration or a list of registrations (or errors)
        """

    @public
    @abc.abstractmethod
    def publish(self, topic: str, *args, **kwargs) -> Optional[Publication]:
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

        :param topic: The URI of the topic to publish to, e.g. ``"com.myapp.mytopic1"``.

        :param args: Arbitrary application payload for the event (positional arguments).

        :param kwargs: Arbitrary application payload for the event (keyword arguments).

        :returns: Acknowledgement for acknowledge publications - otherwise nothing.
        """

    @public
    @abc.abstractmethod
    def subscribe(self, handler: Union[Callable, Any], topic: Optional[str] = None,
                  options: Optional[SubscribeOptions] = None, check_types: Optional[bool] = None) -> \
            Union[Subscription, List[Subscription]]:
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

        :param topic: When ``handler`` is a callable, the URI (or URI pattern)
           of the topic to subscribe to. When ``handler`` is an object, this
           value is ignored (and should be ``None``).

        :param options: Options for subscribing.

        :param check_types: Enable automatic type checking against (Python 3.5+) type hints
            specified on the ``endpoint`` callable. Types are checked at run-time on each
            invocation of the ``endpoint`` callable. When a type mismatch occurs, the error
            is forwarded to the subscriber code in ``onUserError`` override method of
            :class:`autobahn.wamp.protocol.ApplicationSession`.

        :returns: A single Deferred/Future or a list of such objects
        """


class IAuthenticator(abc.ABC):
    """
    Experimental authentication API.
    """

    @abc.abstractmethod
    def on_challenge(self, session: ISession, challenge: Challenge):
        """
        Formulate a challenge response for the given session and Challenge
        instance. This is sent to the server in the AUTHENTICATE
        message.
        """

    @abc.abstractmethod
    def on_welcome(self, authextra: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        This hook is called when the onWelcome/on_welcome hook is invoked
        in the protocol, with the 'authextra' dict extracted from the
        Welcome message. Usually this is used to verify the final
        message from the server (e.g. for mutual authentication).

        :return: None if the session is successful or an error-message
        """


@public
class IKey(abc.ABC):
    """
    Interface to an asymmetric verification key, e.g. a WAMP-Cryptosign client or server authentication
    public key (with Ed25519), or a WAMP-XBR data transaction signature public key or address (with Ethereum).

    The key implementation can use various methods, such as a key read from a file, database table
    or a key residing in a hardware device.
    """

    @property
    @abc.abstractmethod
    def security_module(self) -> Optional['ISecurityModule']:
        """
        When this key is hosted by a security module, return a reference.
        If the key is freestanding (exists of its own outside any security
        module or key store), return ``None``.

        :return: The security module of the key if the key is hosted.
        """

    @property
    @abc.abstractmethod
    def key_no(self) -> Optional[int]:
        """
        When this key is hosted by a security module, return an identifier
        to refer to this key within the security module.
        If the key is freestanding (exists of its own outside any security
        module or key store), return ``None``.

        :return: The identifier of this key within the security
            module if this key is hosted.
        """

    @property
    @abc.abstractmethod
    def key_type(self) -> str:
        """
        Type of key and signature scheme, currently one of:

        * ``ed25519``: Ed25519, that is **EdDSA** signing algo with **Curve25519** elliptic curve and **SHA-512** hash,
                used with WAMP-cryptosign session authentication
        * ``eth``: Ethereum, that is **ECDSA** signing algo, **secp256k1** elliptic curve and **Keccak-256** hash,
                used with WAMP-XBR data and transaction signatures

        :return: Key type, one of ``ed25519`` or ``eth``.
        """

    @abc.abstractmethod
    def public_key(self, binary: bool = False) -> Union[str, bytes]:
        """
        Returns the public key part of a signing key or the (public) verification key.

        :param binary: If the return type should be binary instead of hex
        :return: The public key in hex or byte encoding.
        """

    @abc.abstractmethod
    def can_sign(self) -> bool:
        """
        Check if the key can be used to sign and create new signatures, or only to verify signatures.

        :returns: ``True``, if the key can be used for signing.
        """

    @abc.abstractmethod
    def sign(self, data: bytes) -> bytes:
        """
        Sign the given data, only available if ``can_sign == True``. This method (always) runs asynchronously.

        :param data: The data to be signed.

        :return: The signature, that is a future object that resolves to bytes.
        """

    @abc.abstractmethod
    def recover(self, data: bytes, signature: bytes) -> bytes:
        """
        Recover the signer from the data signed, and the signature given. This method (always) runs asynchronously.

        :param data: The data that was signed.
        :param signature: The signature over the data.

        :return: The signer public key that signed the data to create the signature given.
        """


@public
class ICryptosignKey(IKey):
    """
    Interface to a WAMP-Cryptosign client authentication (or server verification) key.
    """

    @abc.abstractmethod
    def sign_challenge(self, challenge: Challenge, channel_id: Optional[bytes] = None,
                       channel_id_type: Optional[str] = None) -> bytes:
        """
        Sign the data from the given WAMP challenge message, and the optional TLS channel ID
        using this key and return a valid signature that can be used in a WAMP-cryptosign
        authentication handshake.

        :param challenge: The WAMP challenge message as sent or received during the WAMP-cryptosign
            authentication handshake. This can be used by WAMP clients to compute the signature
            returned in the handshake, or by WAMP routers to verify the signature returned by clients,
            during WAMP-cryptosign client authentication.

        :param channel_id: Optional TLS channel ID. Using this binds the WAMP session authentication
            to the underlying TLS channel, and thus prevents authentication-forwarding attacks.
        :param channel_id_type: Optional TLS channel ID type, e.g. ``"tls-unique"``.

        :return: The signature, that is a future object that resolves to bytes.
        """

    @abc.abstractmethod
    def verify_challenge(self, challenge: Challenge, signature: bytes, channel_id: Optional[bytes] = None,
                         channel_id_type: Optional[str] = None) -> bool:
        """
        Verify the data from the given WAMP challenge message, and the optional TLS channel ID
        to be signed by this key.

        :param challenge: The WAMP challenge message as sent or received during the WAMP-cryptosign
            authentication handshake. This can be used by WAMP clients to compute the signature
            returned within the handshake, or by WAMP routers to verify the signature returned by clients,
            during WAMP-cryptosign client authentication.
        :param signature: The signature to verify.
        :param channel_id: Optional TLS channel ID. Using this binds the WAMP session authentication
            to the underlying TLS channel, and thus prevents authentication-forwarding attacks.
        :param channel_id_type: Optional TLS channel ID type, e.g. ``"tls-unique"``.

        :return: Returns ``True`` if the signature over the data matches this key.
        """


@public
class IEthereumKey(IKey):
    """
    Interface to an Ethereum signing (or transaction verification) key, used for WAMP-XBR transaction
    signing (or verification).
    """

    @abc.abstractmethod
    def address(self, binary: bool = False) -> Union[str, bytes]:
        """
        Returns the Ethereum (public) address of the key (which is derived from
        the public key).

        :param binary: Return address as 160 bits (20 bytes) binary instead of
            the ``0x`` prefixed hex, check-summed address as a string.
        :return: The address in hex or byte encoding.
        """

    @abc.abstractmethod
    def sign_typed_data(self, data: Dict[str, Any]) -> bytes:
        """
        Sign the given typed data according to `EIP712 <https://eips.ethereum.org/EIPS/eip-712>`_
        and create an Ethereum signature.

        :param data: The data to be signed. This must follow EIP712.

        :return: The signature, that is a future object that resolves to bytes.
        """

    @abc.abstractmethod
    def verify_typed_data(self, data: Dict[str, Any], signature: bytes, signer_address: Union[str, bytes]) -> bool:
        """
        Verify the given typed data according to `EIP712 <https://eips.ethereum.org/EIPS/eip-712>`_
        to be signed by this key.

        :param data: The data to be signed. This must follow EIP712.
        :param signature: The signature to be verified.
        :param signer_address: Address against which the signature is verified.

        :return: Returns ``True`` if the signature over the data matches this key.
        """


@public
class ISecurityModule(abc.ABC):
    """
    Interface for key security modules, which

    * include filesystem and HSM backed persistent key implementations, and
    * provides secure key signature generation and verification with
    * two key types and signature schemes

    The two key types and signature schemes support WAMP-cryptosign based authentication
    for WAMP sessions, and WAMP-XBR based signed transactions and data encryption.

    References:

    * `SE050 APDU Specification (AN12413) <https://www.nxp.com/docs/en/application-note/AN12413.pdf>`_
    * https://neuromancer.sk/std/secg/secp256r1
    * https://neuromancer.sk/std/secg/secp256k1
    * https://asecuritysite.com/curve25519/eddsa2
    * https://asecuritysite.com/secp256k1/ecdsa
    * https://safecurves.cr.yp.to/
    * https://www.ietf.org/rfc/rfc3279.txt
    * https://crypto.stackexchange.com/questions/70927/naming-convention-for-nist-elliptic-curves-in-openssl
    * https://www.johndcook.com/blog/2018/08/21/a-tale-of-two-elliptic-curves/
    """

    @abc.abstractmethod
    def __len__(self) -> int:
        """
        Get number of key pairs currently stored within the security module.

        :return: Current number of keys stored in security module.
        """

    @abc.abstractmethod
    def __contains__(self, key_no: int) -> bool:
        """

        :param key_no:
        :return:
        """

    # FIXME: the following works on CPy 3.9+, but fails on CPy 3.7 and PyPy 3.8
    #   AttributeError: type object 'Iterator' has no attribute '__class_getitem__'
    #   See also:
    #       - https://docs.python.org/3/library/abc.html#abc.ABCMeta.__subclasshook__
    #       - https://docs.python.org/3/library/stdtypes.html#container.__iter__
    #
    # @abc.abstractmethod
    # def __iter__(self) -> Iterator[Union[ICryptosignKey, IEthereumKey]]:
    #     """
    #     Return an iterator object over all keys accessible in this security module.
    #
    #     :return:
    #     """

    @abc.abstractmethod
    def __getitem__(self, key_no: int) -> Union[ICryptosignKey, IEthereumKey]:
        """
        Get a key from the security module given the key number.

        :param key_no: Number of key to get.

        :return: The key, either a :class:`ICryptosignKey` or :class:`IEthereumKey` instance.
        """

    @abc.abstractmethod
    def __setitem__(self, key_no: int, key: Union[ICryptosignKey, IEthereumKey]) -> None:
        """

        :param key_no:
        :param key:
        :return:
        """

    @abc.abstractmethod
    def __delitem__(self, key_no: int) -> None:
        """

        :param key_no:
        :return:
        """

    @abc.abstractmethod
    def open(self):
        """
        Open this security module. This method (always) runs asynchronously.
        """

    @abc.abstractmethod
    def close(self):
        """
        Close this security module. This method (always) runs asynchronously.
        """

    @property
    @abc.abstractmethod
    def is_open(self) -> bool:
        """
        Check if the security module is currently opened. Security module operations
        can only be run when the module is opened.

        :return: Flag indicating whether the security module is currently opened.
        """

    @property
    @abc.abstractmethod
    def can_lock(self) -> bool:
        """
        Flag indicating whether this security module can be locked, e.g. by a
        user passphrase or PIN.

        :return: Flag indicating whether the security module can be locked/unlocked at all.
        """

    @property
    @abc.abstractmethod
    def is_locked(self) -> bool:
        """
        Check if this security module is currently locked.

        :return: Flag indicating whether the security module is currently locked.
        """

    @abc.abstractmethod
    def lock(self):
        """
        Lock this security module. This method (always) runs asynchronously.
        """

    @abc.abstractmethod
    def unlock(self):
        """
        Unlock this security module. This method (always) runs asynchronously.
        """

    @abc.abstractmethod
    def create_key(self, key_type: str) -> int:
        """
        Create a new public-private asymmetric key pair, stored within the security module.

        :param key_type: Type of key to generate, e.g. ``"cryptosign"`` or ``"ethereum"``.

        :return: ID of new key.
        """

    @abc.abstractmethod
    def delete_key(self, key_no: int):
        """
        Delete an existing key pair stored within the security module.

        :param key_no: ID of key to delete.
        """

    @abc.abstractmethod
    def get_random(self, octets: int) -> bytes:
        """
        Generate random bytes within the security module.

        :param octets: Number of bytes (octets) to generate.

        :return: Random bytes, generated within the security module, e.g. in a HW RNG.
        """

    @abc.abstractmethod
    def get_counter(self, counter_no: int) -> int:
        """
        Return current value of the given persistent counter.

        :param counter_no: Counter to access.

        :return: Current value of counter, or ``0`` to indicate the counter does not
            exist (was never incremented).
        """

    @abc.abstractmethod
    def increment_counter(self, counter_no: int) -> int:
        """
        Increment the given persistent counter and return the new value.

        :param counter_no: Counter to increment and access.

        :return: New value of counter, e.g. ``1`` once a counter was first incremented.
        """


@public
class IPayloadCodec(abc.ABC):
    """
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
    """

    @public
    @abc.abstractmethod
    def encode(self, is_originating, uri, args=None, kwargs=None):
        """
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
        """

    @public
    @abc.abstractmethod
    def decode(self, is_originating, uri, encoded_payload):
        """
        Decode application payload.

        :param is_originating: Flag indicating whether the encoding
            is to be done from an originator (a caller or publisher).
        :type is_originating: bool

        :param uri: The WAMP URI associated with the WAMP message for which
            the payload is to be encoded (eg topic or procedure).
        :type uri: str

        :param encoded_payload: The encoded application payload to be decoded.
        :type encoded_payload: instance of :class:`autobahn.wamp.types.EncodedPayload`

        :returns: A tuple with the decoded positional and keyword-based
            application payload: ``(uri, args, kwargs)``
        :rtype: tuple
        """
