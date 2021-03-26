:mod:`autobahn.wamp.message`
============================

.. py:module:: autobahn.wamp.message


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.message.Message
   autobahn.wamp.message.Hello
   autobahn.wamp.message.Welcome
   autobahn.wamp.message.Abort
   autobahn.wamp.message.Challenge
   autobahn.wamp.message.Authenticate
   autobahn.wamp.message.Goodbye
   autobahn.wamp.message.Error
   autobahn.wamp.message.Publish
   autobahn.wamp.message.Published
   autobahn.wamp.message.Subscribe
   autobahn.wamp.message.Subscribed
   autobahn.wamp.message.Unsubscribe
   autobahn.wamp.message.Unsubscribed
   autobahn.wamp.message.Event
   autobahn.wamp.message.Call
   autobahn.wamp.message.Cancel
   autobahn.wamp.message.Result
   autobahn.wamp.message.Register
   autobahn.wamp.message.Registered
   autobahn.wamp.message.Unregister
   autobahn.wamp.message.Unregistered
   autobahn.wamp.message.Invocation
   autobahn.wamp.message.Interrupt
   autobahn.wamp.message.Yield



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.message.is_valid_enc_algo
   autobahn.wamp.message.is_valid_enc_serializer
   autobahn.wamp.message.check_or_raise_uri
   autobahn.wamp.message.check_or_raise_id


.. data:: PAYLOAD_ENC_CRYPTO_BOX
   :annotation: = cryptobox

   

.. data:: PAYLOAD_ENC_MQTT
   :annotation: = mqtt

   

.. data:: PAYLOAD_ENC_STANDARD_IDENTIFIERS
   

   

.. function:: is_valid_enc_algo(enc_algo)

   For WAMP payload transparency mode, check if the provided ``enc_algo``
   identifier in the WAMP message is a valid one.

   Currently defined standard identifiers are:

   * ``"cryptobox"``
   * ``"mqtt"``
   * ``"xbr"``

   Users can select arbitrary identifiers too, but these MUST start with ``"x_"``.

   :param enc_algo: The payload transparency algorithm identifier to check.
   :type enc_algo: str

   :returns: Returns ``True`` if and only if the payload transparency
       algorithm identifier is valid.
   :rtype: bool


.. function:: is_valid_enc_serializer(enc_serializer)

   For WAMP payload transparency mode, check if the provided ``enc_serializer``
   identifier in the WAMP message is a valid one.

   Currently, the only standard defined identifier are

   * ``"json"``
   * ``"msgpack"``
   * ``"cbor"``
   * ``"ubjson"``
   * ``"flatbuffers"``

   Users can select arbitrary identifiers too, but these MUST start with ``"x_"``.

   :param enc_serializer: The payload transparency serializer identifier to check.
   :type enc_serializer: str

   :returns: Returns ``True`` if and only if the payload transparency
       serializer identifier is valid.
   :rtype: bool


.. function:: check_or_raise_uri(value, message='WAMP message invalid', strict=False, allow_empty_components=False, allow_last_empty=False, allow_none=False)

   Check a value for being a valid WAMP URI.

   If the value is not a valid WAMP URI is invalid, raises :class:`autobahn.wamp.exception.ProtocolError`.
   Otherwise return the value.

   :param value: The value to check.
   :type value: str or None

   :param message: Prefix for message in exception raised when value is invalid.
   :type message: str

   :param strict: If ``True``, do a strict check on the URI (the WAMP spec SHOULD behavior).
   :type strict: bool

   :param allow_empty_components: If ``True``, allow empty URI components (for pattern based
      subscriptions and registrations).
   :type allow_empty_components: bool

   :param allow_none: If ``True``, allow ``None`` for URIs.
   :type allow_none: bool

   :returns: The URI value (if valid).
   :rtype: str

   :raises: instance of :class:`autobahn.wamp.exception.ProtocolError`


.. function:: check_or_raise_id(value, message='WAMP message invalid')

   Check a value for being a valid WAMP ID.

   If the value is not a valid WAMP ID, raises :class:`autobahn.wamp.exception.ProtocolError`.
   Otherwise return the value.

   :param value: The value to check.
   :type value: int

   :param message: Prefix for message in exception raised when value is invalid.
   :type message: str

   :returns: The ID value (if valid).
   :rtype: int

   :raises: instance of :class:`autobahn.wamp.exception.ProtocolError`


.. class:: Message(from_fbs=None)


   Bases: :class:`object`

   WAMP message base class.

   .. note:: This is not supposed to be instantiated, but subclassed only.

   .. attribute:: MESSAGE_TYPE
      

      WAMP message type code.


   .. attribute:: __slots__
      :annotation: = ['_from_fbs', '_serialized', '_correlation_id', '_correlation_uri', '_correlation_is_anchor', '_correlation_is_last', '_router_internal']

      

   .. method:: correlation_id(self)
      :property:


   .. method:: correlation_uri(self)
      :property:


   .. method:: correlation_is_anchor(self)
      :property:


   .. method:: correlation_is_last(self)
      :property:


   .. method:: __eq__(self, other)

      Compare this message to another message for equality.

      :param other: The other message to compare with.
      :type other: obj

      :returns: ``True`` iff the messages are equal.
      :rtype: bool


   .. method:: __ne__(self, other)

      Compare this message to another message for inequality.

      :param other: The other message to compare with.
      :type other: obj

      :returns: ``True`` iff the messages are not equal.
      :rtype: bool


   .. method:: parse(wmsg)
      :staticmethod:
      :abstractmethod:

      Factory method that parses a unserialized raw message (as returned byte
      :func:`autobahn.interfaces.ISerializer.unserialize`) into an instance
      of this class.

      :returns: An instance of this class.
      :rtype: obj


   .. method:: marshal(self)
      :abstractmethod:


   .. method:: cast(buf)
      :staticmethod:
      :abstractmethod:


   .. method:: build(self, builder)
      :abstractmethod:


   .. method:: uncache(self)

      Resets the serialization cache.


   .. method:: serialize(self, serializer)

      Serialize this object into a wire level bytes representation and cache
      the resulting bytes. If the cache already contains an entry for the given
      serializer, return the cached representation directly.

      :param serializer: The wire level serializer to use.
      :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`

      :returns: The serialized bytes.
      :rtype: bytes



.. class:: Hello(realm, roles, authmethods=None, authid=None, authrole=None, authextra=None, resumable=None, resume_session=None, resume_token=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``HELLO`` message.

   Format: ``[HELLO, Realm|uri, Details|dict]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 1

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['realm', 'roles', 'authmethods', 'authid', 'authrole', 'authextra', 'resumable', 'resume_session', 'resume_token']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Return a string representation of this message.



.. class:: Welcome(session, roles, realm=None, authid=None, authrole=None, authmethod=None, authprovider=None, authextra=None, resumed=None, resumable=None, resume_token=None, custom=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``WELCOME`` message.

   Format: ``[WELCOME, Session|id, Details|dict]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 2

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['session', 'roles', 'realm', 'authid', 'authrole', 'authmethod', 'authprovider', 'authextra', 'resumed', 'resumable', 'resume_token', 'custom']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Abort(reason, message=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``ABORT`` message.

   Format: ``[ABORT, Details|dict, Reason|uri]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 3

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['reason', 'message']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Challenge(method, extra=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``CHALLENGE`` message.

   Format: ``[CHALLENGE, Method|string, Extra|dict]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 4

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['method', 'extra']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Authenticate(signature, extra=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``AUTHENTICATE`` message.

   Format: ``[AUTHENTICATE, Signature|string, Extra|dict]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 5

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['signature', 'extra']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Goodbye(reason=DEFAULT_REASON, message=None, resumable=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``GOODBYE`` message.

   Format: ``[GOODBYE, Details|dict, Reason|uri]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 6

      The WAMP message code for this type of message.


   .. attribute:: DEFAULT_REASON
      :annotation: = wamp.close.normal

      Default WAMP closing reason.


   .. attribute:: __slots__
      :annotation: = ['reason', 'message', 'resumable']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Error(request_type, request, error, args=None, kwargs=None, payload=None, enc_algo=None, enc_key=None, enc_serializer=None, callee=None, callee_authid=None, callee_authrole=None, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``ERROR`` message.

   Formats:

   * ``[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri]``
   * ``[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list]``
   * ``[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list, ArgumentsKw|dict]``
   * ``[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri, Payload|binary]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 8

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request_type', 'request', 'error', 'args', 'kwargs', 'payload', 'enc_algo', 'enc_key', 'enc_serializer', 'callee', 'callee_authid', 'callee_authrole', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Publish(request=None, topic=None, args=None, kwargs=None, payload=None, acknowledge=None, exclude_me=None, exclude=None, exclude_authid=None, exclude_authrole=None, eligible=None, eligible_authid=None, eligible_authrole=None, retain=None, enc_algo=None, enc_key=None, enc_serializer=None, forward_for=None, from_fbs=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``PUBLISH`` message.

   Formats:

   * ``[PUBLISH, Request|id, Options|dict, Topic|uri]``
   * ``[PUBLISH, Request|id, Options|dict, Topic|uri, Arguments|list]``
   * ``[PUBLISH, Request|id, Options|dict, Topic|uri, Arguments|list, ArgumentsKw|dict]``
   * ``[PUBLISH, Request|id, Options|dict, Topic|uri, Payload|binary]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 16

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['_request', '_topic', '_args', '_kwargs', '_payload', '_enc_algo', '_enc_serializer', '_enc_key', '_acknowledge', '_exclude_me', '_exclude', '_exclude_authid', '_exclude_authrole', '_eligible', '_eligible_authid', '_eligible_authrole', '_retain', '_forward_for']

      

   .. method:: __eq__(self, other)

      Compare this message to another message for equality.

      :param other: The other message to compare with.
      :type other: obj

      :returns: ``True`` iff the messages are equal.
      :rtype: bool


   .. method:: __ne__(self, other)

      Compare this message to another message for inequality.

      :param other: The other message to compare with.
      :type other: obj

      :returns: ``True`` iff the messages are not equal.
      :rtype: bool


   .. method:: request(self)
      :property:


   .. method:: topic(self)
      :property:


   .. method:: args(self)
      :property:


   .. method:: kwargs(self)
      :property:


   .. method:: payload(self)
      :property:


   .. method:: acknowledge(self)
      :property:


   .. method:: exclude_me(self)
      :property:


   .. method:: exclude(self)
      :property:


   .. method:: exclude_authid(self)
      :property:


   .. method:: exclude_authrole(self)
      :property:


   .. method:: eligible(self)
      :property:


   .. method:: eligible_authid(self)
      :property:


   .. method:: eligible_authrole(self)
      :property:


   .. method:: retain(self)
      :property:


   .. method:: enc_algo(self)
      :property:


   .. method:: enc_key(self)
      :property:


   .. method:: enc_serializer(self)
      :property:


   .. method:: forward_for(self)
      :property:


   .. method:: cast(buf)
      :staticmethod:


   .. method:: build(self, builder)


   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal_options(self)


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Published(request, publication)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``PUBLISHED`` message.

   Format: ``[PUBLISHED, PUBLISH.Request|id, Publication|id]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 17

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'publication']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Subscribe(request, topic, match=None, get_retained=None, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``SUBSCRIBE`` message.

   Format: ``[SUBSCRIBE, Request|id, Options|dict, Topic|uri]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 32

      The WAMP message code for this type of message.


   .. attribute:: MATCH_EXACT
      :annotation: = exact

      

   .. attribute:: MATCH_PREFIX
      :annotation: = prefix

      

   .. attribute:: MATCH_WILDCARD
      :annotation: = wildcard

      

   .. attribute:: __slots__
      :annotation: = ['request', 'topic', 'match', 'get_retained', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal_options(self)


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Subscribed(request, subscription)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``SUBSCRIBED`` message.

   Format: ``[SUBSCRIBED, SUBSCRIBE.Request|id, Subscription|id]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 33

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'subscription']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Unsubscribe(request, subscription, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``UNSUBSCRIBE`` message.

   Formats:

   * ``[UNSUBSCRIBE, Request|id, SUBSCRIBED.Subscription|id]``
   * ``[UNSUBSCRIBE, Request|id, SUBSCRIBED.Subscription|id, Options|dict]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 34

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'subscription', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Unsubscribed(request, subscription=None, reason=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``UNSUBSCRIBED`` message.

   Formats:

   * ``[UNSUBSCRIBED, UNSUBSCRIBE.Request|id]``
   * ``[UNSUBSCRIBED, UNSUBSCRIBE.Request|id, Details|dict]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 35

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'subscription', 'reason']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Event(subscription=None, publication=None, args=None, kwargs=None, payload=None, publisher=None, publisher_authid=None, publisher_authrole=None, topic=None, retained=None, x_acknowledged_delivery=None, enc_algo=None, enc_key=None, enc_serializer=None, forward_for=None, from_fbs=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``EVENT`` message.

   Formats:

   * ``[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict]``
   * ``[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list]``
   * ``[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list, PUBLISH.ArgumentsKw|dict]``
   * ``[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Payload|binary]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 36

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['_subscription', '_publication', '_args', '_kwargs', '_payload', '_enc_algo', '_enc_serializer', '_enc_key', '_publisher', '_publisher_authid', '_publisher_authrole', '_topic', '_retained', '_x_acknowledged_delivery', '_forward_for']

      

   .. method:: __eq__(self, other)

      Compare this message to another message for equality.

      :param other: The other message to compare with.
      :type other: obj

      :returns: ``True`` iff the messages are equal.
      :rtype: bool


   .. method:: __ne__(self, other)

      Compare this message to another message for inequality.

      :param other: The other message to compare with.
      :type other: obj

      :returns: ``True`` iff the messages are not equal.
      :rtype: bool


   .. method:: subscription(self)
      :property:


   .. method:: publication(self)
      :property:


   .. method:: args(self)
      :property:


   .. method:: kwargs(self)
      :property:


   .. method:: payload(self)
      :property:


   .. method:: publisher(self)
      :property:


   .. method:: publisher_authid(self)
      :property:


   .. method:: publisher_authrole(self)
      :property:


   .. method:: topic(self)
      :property:


   .. method:: retained(self)
      :property:


   .. method:: x_acknowledged_delivery(self)
      :property:


   .. method:: enc_algo(self)
      :property:


   .. method:: enc_key(self)
      :property:


   .. method:: enc_serializer(self)
      :property:


   .. method:: forward_for(self)
      :property:


   .. method:: cast(buf)
      :staticmethod:


   .. method:: build(self, builder)


   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Call(request, procedure, args=None, kwargs=None, payload=None, timeout=None, receive_progress=None, enc_algo=None, enc_key=None, enc_serializer=None, caller=None, caller_authid=None, caller_authrole=None, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``CALL`` message.

   Formats:

   * ``[CALL, Request|id, Options|dict, Procedure|uri]``
   * ``[CALL, Request|id, Options|dict, Procedure|uri, Arguments|list]``
   * ``[CALL, Request|id, Options|dict, Procedure|uri, Arguments|list, ArgumentsKw|dict]``
   * ``[CALL, Request|id, Options|dict, Procedure|uri, Payload|binary]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 48

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'procedure', 'args', 'kwargs', 'payload', 'timeout', 'receive_progress', 'enc_algo', 'enc_key', 'enc_serializer', 'caller', 'caller_authid', 'caller_authrole', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal_options(self)


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Cancel(request, mode=None, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``CANCEL`` message.

   Format: ``[CANCEL, CALL.Request|id, Options|dict]``

   See: https://wamp-proto.org/static/rfc/draft-oberstet-hybi-crossbar-wamp.html#rfc.section.14.3.4

   .. attribute:: MESSAGE_TYPE
      :annotation: = 49

      The WAMP message code for this type of message.


   .. attribute:: SKIP
      :annotation: = skip

      

   .. attribute:: KILL
      :annotation: = kill

      

   .. attribute:: KILLNOWAIT
      :annotation: = killnowait

      

   .. attribute:: __slots__
      :annotation: = ['request', 'mode', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Result(request, args=None, kwargs=None, payload=None, progress=None, enc_algo=None, enc_key=None, enc_serializer=None, callee=None, callee_authid=None, callee_authrole=None, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``RESULT`` message.

   Formats:

   * ``[RESULT, CALL.Request|id, Details|dict]``
   * ``[RESULT, CALL.Request|id, Details|dict, YIELD.Arguments|list]``
   * ``[RESULT, CALL.Request|id, Details|dict, YIELD.Arguments|list, YIELD.ArgumentsKw|dict]``
   * ``[RESULT, CALL.Request|id, Details|dict, Payload|binary]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 50

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'args', 'kwargs', 'payload', 'progress', 'enc_algo', 'enc_key', 'enc_serializer', 'callee', 'callee_authid', 'callee_authrole', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Register(request, procedure, match=None, invoke=None, concurrency=None, force_reregister=None, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``REGISTER`` message.

   Format: ``[REGISTER, Request|id, Options|dict, Procedure|uri]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 64

      The WAMP message code for this type of message.


   .. attribute:: MATCH_EXACT
      :annotation: = exact

      

   .. attribute:: MATCH_PREFIX
      :annotation: = prefix

      

   .. attribute:: MATCH_WILDCARD
      :annotation: = wildcard

      

   .. attribute:: INVOKE_SINGLE
      :annotation: = single

      

   .. attribute:: INVOKE_FIRST
      :annotation: = first

      

   .. attribute:: INVOKE_LAST
      :annotation: = last

      

   .. attribute:: INVOKE_ROUNDROBIN
      :annotation: = roundrobin

      

   .. attribute:: INVOKE_RANDOM
      :annotation: = random

      

   .. attribute:: INVOKE_ALL
      :annotation: = all

      

   .. attribute:: __slots__
      :annotation: = ['request', 'procedure', 'match', 'invoke', 'concurrency', 'force_reregister', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal_options(self)


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Registered(request, registration)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``REGISTERED`` message.

   Format: ``[REGISTERED, REGISTER.Request|id, Registration|id]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 65

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'registration']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Unregister(request, registration, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP `UNREGISTER` message.

   Formats:

   * ``[UNREGISTER, Request|id, REGISTERED.Registration|id]``
   * ``[UNREGISTER, Request|id, REGISTERED.Registration|id, Options|dict]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 66

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'registration', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Unregistered(request, registration=None, reason=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``UNREGISTERED`` message.

   Formats:

   * ``[UNREGISTERED, UNREGISTER.Request|id]``
   * ``[UNREGISTERED, UNREGISTER.Request|id, Details|dict]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 67

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'registration', 'reason']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Invocation(request, registration, args=None, kwargs=None, payload=None, timeout=None, receive_progress=None, caller=None, caller_authid=None, caller_authrole=None, procedure=None, enc_algo=None, enc_key=None, enc_serializer=None, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``INVOCATION`` message.

   Formats:

   * ``[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict]``
   * ``[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, CALL.Arguments|list]``
   * ``[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, CALL.Arguments|list, CALL.ArgumentsKw|dict]``
   * ``[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, Payload|binary]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 68

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'registration', 'args', 'kwargs', 'payload', 'timeout', 'receive_progress', 'caller', 'caller_authid', 'caller_authrole', 'procedure', 'enc_algo', 'enc_key', 'enc_serializer', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Interrupt(request, mode=None, reason=None, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``INTERRUPT`` message.

   Format: ``[INTERRUPT, INVOCATION.Request|id, Options|dict]``

   See: https://wamp-proto.org/static/rfc/draft-oberstet-hybi-crossbar-wamp.html#rfc.section.14.3.4

   .. attribute:: MESSAGE_TYPE
      :annotation: = 69

      The WAMP message code for this type of message.


   .. attribute:: KILL
      :annotation: = kill

      

   .. attribute:: KILLNOWAIT
      :annotation: = killnowait

      

   .. attribute:: __slots__
      :annotation: = ['request', 'mode', 'reason', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



.. class:: Yield(request, args=None, kwargs=None, payload=None, progress=None, enc_algo=None, enc_key=None, enc_serializer=None, callee=None, callee_authid=None, callee_authrole=None, forward_for=None)


   Bases: :class:`autobahn.wamp.message.Message`

   A WAMP ``YIELD`` message.

   Formats:

   * ``[YIELD, INVOCATION.Request|id, Options|dict]``
   * ``[YIELD, INVOCATION.Request|id, Options|dict, Arguments|list]``
   * ``[YIELD, INVOCATION.Request|id, Options|dict, Arguments|list, ArgumentsKw|dict]``
   * ``[YIELD, INVOCATION.Request|id, Options|dict, Payload|binary]``

   .. attribute:: MESSAGE_TYPE
      :annotation: = 70

      The WAMP message code for this type of message.


   .. attribute:: __slots__
      :annotation: = ['request', 'args', 'kwargs', 'payload', 'progress', 'enc_algo', 'enc_key', 'enc_serializer', 'callee', 'callee_authid', 'callee_authrole', 'forward_for']

      

   .. method:: parse(wmsg)
      :staticmethod:

      Verifies and parses an unserialized raw message into an actual WAMP message instance.

      :param wmsg: The unserialized raw message.
      :type wmsg: list

      :returns: An instance of this class.


   .. method:: marshal(self)

      Marshal this object into a raw message for subsequent serialization to bytes.

      :returns: The serialized raw message.
      :rtype: list


   .. method:: __str__(self)

      Returns string representation of this message.



