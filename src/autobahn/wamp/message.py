###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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

import binascii
import re
import textwrap
from pprint import pformat
from typing import Any, Dict, Optional

import autobahn
from autobahn.util import hlval
from autobahn.wamp.exception import InvalidUriError, ProtocolError
from autobahn.wamp.role import ROLE_NAME_TO_CLASS

try:
    import cbor2
    from autobahn import flatbuffers

    from autobahn.wamp import message_fbs
except ImportError:
    _HAS_WAMP_FLATBUFFERS = False
else:
    _HAS_WAMP_FLATBUFFERS = True

__all__ = (
    "PAYLOAD_ENC_CRYPTO_BOX",
    "PAYLOAD_ENC_MQTT",
    "PAYLOAD_ENC_STANDARD_IDENTIFIERS",
    "Abort",
    "Authenticate",
    "Call",
    "Cancel",
    "Challenge",
    "Error",
    "Event",
    "Goodbye",
    "Hello",
    "Interrupt",
    "Invocation",
    "Message",
    "MessageWithAppPayload",
    "MessageWithForwardFor",
    "Publish",
    "Published",
    "Register",
    "Registered",
    "Result",
    "Subscribe",
    "Subscribed",
    "Unregister",
    "Unregistered",
    "Unsubscribe",
    "Unsubscribed",
    "Welcome",
    "Yield",
    "check_or_raise_extra",
    "check_or_raise_id",
    "check_or_raise_realm_name",
    "check_or_raise_uri",
    "identify_realm_name_category",
    "is_valid_enc_algo",
    "is_valid_enc_serializer",
)

# all realm names in Autobahn/Crossbar.io must match this
_URI_PAT_REALM_NAME = re.compile(r"^[A-Za-z][A-Za-z\d_\-@\.]{2,254}$")

# if Ethereum addresses are enabled, realm names which are "0x" prefixed Ethereum addresses are also valid
_URI_PAT_REALM_NAME_ETH = re.compile(r"^0x([A-Fa-f\d]{40})$")

# realms names might also specifically match ENS URIs
_URI_PAT_REALM_NAME_ENS = re.compile(r"^([a-z\d_\-@\.]{2,250})\.eth$")

# since WAMP recommends using reverse dotted notation, reverse ENS names can be checked with this pattern
_URI_PAT_REALM_NAME_ENS_REVERSE = re.compile(r"^eth\.([a-z\d_\-@\.]{2,250})$")

# strict URI check allowing empty URI components
_URI_PAT_STRICT_EMPTY = re.compile(r"^(([\da-z_]+\.)|\.)*([\da-z_]+)?$")

# loose URI check allowing empty URI components
_URI_PAT_LOOSE_EMPTY = re.compile(r"^(([^\s\.#]+\.)|\.)*([^\s\.#]+)?$")

# strict URI check disallowing empty URI components
_URI_PAT_STRICT_NON_EMPTY = re.compile(r"^([\da-z_]+\.)*([\da-z_]+)$")

# loose URI check disallowing empty URI components
_URI_PAT_LOOSE_NON_EMPTY = re.compile(r"^([^\s\.#]+\.)*([^\s\.#]+)$")

# strict URI check disallowing empty URI components in all but the last component
_URI_PAT_STRICT_LAST_EMPTY = re.compile(r"^([\da-z_]+\.)*([\da-z_]*)$")

# loose URI check disallowing empty URI components in all but the last component
_URI_PAT_LOOSE_LAST_EMPTY = re.compile(r"^([^\s\.#]+\.)*([^\s\.#]*)$")

# custom (=implementation specific) WAMP attributes (used in WAMP message details/options)
_CUSTOM_ATTRIBUTE = re.compile(r"^x_([a-z][\da-z_]+)?$")

# Value for algo attribute in end-to-end encrypted messages using cryptobox, which
# is a scheme based on Curve25519, SHA512, Salsa20 and Poly1305.
# See: http://cr.yp.to/highspeed/coolnacl-20120725.pdf
PAYLOAD_ENC_CRYPTO_BOX = "cryptobox"

# Payload transparency identifier for MQTT payloads (which are arbitrary binary).
PAYLOAD_ENC_MQTT = "mqtt"

# Payload transparency identifier for XBR payloads
PAYLOAD_ENC_XBR = "xbr"

# Payload transparency algorithm identifiers from the WAMP spec.
PAYLOAD_ENC_STANDARD_IDENTIFIERS = [
    PAYLOAD_ENC_CRYPTO_BOX,
    PAYLOAD_ENC_MQTT,
    PAYLOAD_ENC_XBR,
]

# Payload transparency serializer identifiers from the WAMP spec.
PAYLOAD_ENC_STANDARD_SERIALIZERS = ["json", "msgpack", "cbor", "ubjson", "flatbuffers"]

ENC_ALGO_NONE = 0
ENC_ALGO_CRYPTOBOX = 1
ENC_ALGO_MQTT = 2
ENC_ALGO_XBR = 3

ENC_ALGOS = {
    ENC_ALGO_NONE: "null",
    ENC_ALGO_CRYPTOBOX: "cryptobox",
    ENC_ALGO_MQTT: "mqtt",
    ENC_ALGO_XBR: "xbr",
}

ENC_ALGOS_FROMSTR = {key: value for value, key in ENC_ALGOS.items()}

ENC_SER_NONE = 0
ENC_SER_JSON = 1
ENC_SER_MSGPACK = 2
ENC_SER_CBOR = 3
ENC_SER_UBJSON = 4
ENC_SER_OPAQUE = 5
ENC_SER_FLATBUFFERS = 6

ENC_SERS = {
    ENC_SER_NONE: "null",
    ENC_SER_JSON: "json",
    ENC_SER_MSGPACK: "msgpack",
    ENC_SER_CBOR: "cbor",
    ENC_SER_UBJSON: "ubjson",
    ENC_SER_OPAQUE: "opaque",
    ENC_SER_FLATBUFFERS: "flatbuffers",
}

ENC_SERS_FROMSTR = {key: value for value, key in ENC_SERS.items()}


def is_valid_enc_algo(enc_algo):
    """
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
    """
    return type(enc_algo) == str and (
        enc_algo in PAYLOAD_ENC_STANDARD_IDENTIFIERS
        or _CUSTOM_ATTRIBUTE.match(enc_algo)
    )


def is_valid_enc_serializer(enc_serializer):
    """
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
    """
    return type(enc_serializer) == str and (
        enc_serializer in PAYLOAD_ENC_STANDARD_SERIALIZERS
        or _CUSTOM_ATTRIBUTE.match(enc_serializer)
    )


def b2a(data, max_len=40):
    if type(data) == str:
        s = data
    elif type(data) == bytes:
        s = binascii.b2a_hex(data).decode("ascii")
    elif data is None:
        s = "-"
    else:
        s = "{}".format(data)
    if len(s) > max_len:
        return s[:max_len] + ".."
    else:
        return s


def identify_realm_name_category(value: Any) -> Optional[str]:
    """
    Identify the real name category of the given value:

    * ``"standalone"``: A normal, standalone WAMP realm name, e.g. ``"realm1"``.
    * ``"eth"``: An Ethereum address, e.g. ``"0xe59C7418403CF1D973485B36660728a5f4A8fF9c"``.
    * ``"ens"``: An Ethereum ENS name, e.g. ``"wamp-proto.eth"``.
    * ``"reverse_ens"``: An Ethereum ENS name in reverse notation, e.g. ``"eth.wamp-proto"``.
    * ``None``: The value is not a WAMP realm name.

    :param value: The value for which to identify realm name category.
    :return: The category identified, one of ``["standalone", "eth", "ens", "reverse-ens"]``
        or ``None``.
    """
    if type(value) != str:
        return None
    if _URI_PAT_REALM_NAME.match(value):
        if _URI_PAT_REALM_NAME_ENS.match(value):
            return "ens"
        elif _URI_PAT_REALM_NAME_ENS_REVERSE.match(value):
            return "reverse_ens"
        else:
            return "standalone"
    elif _URI_PAT_REALM_NAME_ETH.match(value):
        return "eth"
    else:
        return None


def check_or_raise_uri(
    value: Any,
    message: str = "WAMP message invalid",
    strict: bool = False,
    allow_empty_components: bool = False,
    allow_last_empty: bool = False,
    allow_none: bool = False,
) -> str:
    """
    Check a value for being a valid WAMP URI.

    If the value is not a valid WAMP URI is invalid, raises :class:`autobahn.wamp.exception.InvalidUriError`,
    otherwise returns the value.

    :param value: The value to check.
    :param message: Prefix for message in exception raised when value is invalid.
    :param strict: If ``True``, do a strict check on the URI (the WAMP spec SHOULD behavior).
    :param allow_empty_components: If ``True``, allow empty URI components (for pattern based
       subscriptions and registrations).
    :param allow_last_empty: If ``True``, allow the last URI component to be empty (for prefix based
       subscriptions and registrations).
    :param allow_none: If ``True``, allow ``None`` for URIs.
    :returns: The URI value (if valid).
    :raises: instance of :class:`autobahn.wamp.exception.InvalidUriError`
    """
    if value is None:
        if allow_none:
            return
        else:
            raise InvalidUriError("{0}: URI cannot be null".format(message))

    if type(value) != str:
        if not (value is None and allow_none):
            raise InvalidUriError(
                "{0}: invalid type {1} for URI".format(message, type(value))
            )

    if strict:
        if allow_last_empty:
            pat = _URI_PAT_STRICT_LAST_EMPTY
        elif allow_empty_components:
            pat = _URI_PAT_STRICT_EMPTY
        else:
            pat = _URI_PAT_STRICT_NON_EMPTY
    else:
        if allow_last_empty:
            pat = _URI_PAT_LOOSE_LAST_EMPTY
        elif allow_empty_components:
            pat = _URI_PAT_LOOSE_EMPTY
        else:
            pat = _URI_PAT_LOOSE_NON_EMPTY

    if not pat.match(value):
        raise InvalidUriError(
            '{0}: invalid value "{1}" for URI (did not match pattern "{2}" with options strict={3}, allow_empty_components={4}, allow_last_empty={5}, allow_none={6})'.format(
                message,
                value,
                pat.pattern,
                strict,
                allow_empty_components,
                allow_last_empty,
                allow_none,
            )
        )
    else:
        return value


def check_or_raise_realm_name(value, message="WAMP message invalid", allow_eth=True):
    """
    Check a value for being a valid WAMP URI.

    If the value is not a valid WAMP URI is invalid, raises :class:`autobahn.wamp.exception.InvalidUriError`,
    otherwise returns the value.

    :param value: The value to check, e.g. ``"realm1"`` or ``"com.example.myapp"`` or ``"eth.example"``.
    :param message: Prefix for message in exception raised when value is invalid.
    :param allow_eth: If ``True``, allow Ethereum addresses as realm names,
        e.g. ``"0xe59C7418403CF1D973485B36660728a5f4A8fF9c"``.
    :returns: The URI value (if valid).
    :raises: instance of :class:`autobahn.wamp.exception.InvalidUriError`
    """
    if value is None:
        raise InvalidUriError("{0}: realm name cannot be null".format(message))

    if type(value) != str:
        raise InvalidUriError(
            "{0}: invalid type {1} for realm name".format(message, type(value))
        )

    if allow_eth:
        if _URI_PAT_REALM_NAME.match(value) or _URI_PAT_REALM_NAME_ETH.match(value):
            return value
        else:
            raise InvalidUriError(
                '{0}: invalid value "{1}" for realm name (did not match patterns '
                '"{2}" or "{3}")'.format(
                    message,
                    value,
                    _URI_PAT_REALM_NAME.pattern,
                    _URI_PAT_REALM_NAME_ETH.pattern,
                )
            )
    else:
        if _URI_PAT_REALM_NAME.match(value):
            return value
        else:
            raise InvalidUriError(
                '{0}: invalid value "{1}" for realm name (did not match pattern '
                '"{2}")'.format(message, value, _URI_PAT_REALM_NAME.pattern)
            )


def check_or_raise_id(value: Any, message: str = "WAMP message invalid") -> int:
    """
    Check a value for being a valid WAMP ID.

    If the value is not a valid WAMP ID, raises :class:`autobahn.wamp.exception.ProtocolError`,
    otherwise return the value.

    :param value: The value to check.
    :param message: Prefix for message in exception raised when value is invalid.
    :returns: The ID value (if valid).
    :raises: instance of :class:`autobahn.wamp.exception.ProtocolError`
    """
    if type(value) != int:
        raise ProtocolError("{0}: invalid type {1} for ID".format(message, type(value)))
    # the value 0 for WAMP IDs is possible in certain WAMP messages, e.g. UNREGISTERED with
    # router revocation signaling!
    if value < 0 or value > 9007199254740992:  # 2**53
        raise ProtocolError("{0}: invalid value {1} for ID".format(message, value))
    return value


def check_or_raise_extra(
    value: Any, message: str = "WAMP message invalid"
) -> Dict[str, Any]:
    """
    Check a value for being a valid WAMP extra dictionary.

    If the value is not a valid WAMP extra dictionary, raises :class:`autobahn.wamp.exception.ProtocolError`,
    otherwise return the value.

    :param value: The value to check.
    :param message: Prefix for message in exception raised when value is invalid.
    :returns: The extra dictionary (if valid).
    :raises: instance of :class:`autobahn.wamp.exception.ProtocolError`
    """
    if type(value) != dict:
        raise ProtocolError(
            "{0}: invalid type {1} for WAMP extra".format(message, type(value))
        )
    for k in value.keys():
        if not isinstance(k, str):
            raise ProtocolError(
                "{0}: invalid type {1} for key in WAMP extra ('{2}')".format(
                    message, type(k), k
                )
            )
    return value


def _validate_kwargs(kwargs, message="WAMP message invalid"):
    """
    Check a value for being a valid WAMP kwargs dictionary.

    If the value is not a valid WAMP kwargs dictionary,
    raises :class:`autobahn.wamp.exception.ProtocolError`.
    Otherwise return the kwargs.

    The WAMP spec requires that the keys in kwargs are proper
    strings (unicode), not bytes. Note that the WAMP spec
    says nothing about keys in application payload. Key in the
    latter can be potentially of other type (if that is really
    wanted).

    :param kwargs: The keyword arguments to check.
    :type kwargs: dict

    :param message: Prefix for message in exception raised when
        value is invalid.
    :type message: str

    :returns: The kwargs dictionary (if valid).
    :rtype: dict

    :raises: instance of
        :class:`autobahn.wamp.exception.ProtocolError`
    """
    if kwargs is not None:
        if type(kwargs) != dict:
            raise ProtocolError(
                "{0}: invalid type {1} for WAMP kwargs".format(message, type(kwargs))
            )
        for k in kwargs.keys():
            if not isinstance(k, str):
                raise ProtocolError(
                    "{0}: invalid type {1} for key in WAMP kwargs ('{2}')".format(
                        message, type(k), k
                    )
                )
        return kwargs


class Message(object):
    """
    WAMP message base class.

    .. note:: This is not supposed to be instantiated, but subclassed only.
    """

    MESSAGE_TYPE = None
    """
    WAMP message type code.
    """

    __slots__ = (
        "_from_fbs",
        "_serialized",
        "_correlation_id",
        "_correlation_uri",
        "_correlation_is_anchor",
        "_correlation_is_last",
        "_router_internal",
    )

    def __init__(self, from_fbs=None):
        # only filled in case this object has flatbuffers underlying
        self._from_fbs = from_fbs

        # serialization cache: mapping from ISerializer instances to serialized bytes
        self._serialized = {}

        # user attributes for message correlation (mainly for message tracing)
        self._correlation_id = None
        self._correlation_uri = None
        self._correlation_is_anchor = None
        self._correlation_is_last = None

        # non-serialized 'internal' attributes (used by Crossbar router)
        self._router_internal = None

    @property
    def correlation_id(self):
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, value):
        assert value is None or type(value) == str
        self._correlation_id = value

    @property
    def correlation_uri(self):
        return self._correlation_uri

    @correlation_uri.setter
    def correlation_uri(self, value):
        assert value is None or type(value) == str
        self._correlation_uri = value

    @property
    def correlation_is_anchor(self):
        return self._correlation_is_anchor

    @correlation_is_anchor.setter
    def correlation_is_anchor(self, value):
        assert value is None or type(value) == bool
        self._correlation_is_anchor = value

    @property
    def correlation_is_last(self):
        return self._correlation_is_last

    @correlation_is_last.setter
    def correlation_is_last(self, value):
        assert value is None or type(value) == bool
        self._correlation_is_last = value

    def __eq__(self, other):
        """
        Compare this message to another message for equality.

        :param other: The other message to compare with.
        :type other: obj

        :returns: ``True`` iff the messages are equal.
        :rtype: bool
        """
        if not isinstance(other, self.__class__):
            return False
        # we only want the actual message data attributes (not eg _serialize)
        for k in self.__slots__:
            if k not in [
                "_serialized",
                "_correlation_id",
                "_correlation_uri",
                "_correlation_is_anchor",
                "_correlation_is_last",
            ] and not k.startswith("_"):
                if not getattr(self, k) == getattr(other, k):
                    return False
        return True

    def __ne__(self, other):
        """
        Compare this message to another message for inequality.

        :param other: The other message to compare with.
        :type other: obj

        :returns: ``True`` iff the messages are not equal.
        :rtype: bool
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        return "{}\n{}".format(
            hlval(self.__class__.__name__.upper() + "::", color="blue", bold=True),
            hlval(
                textwrap.indent(pformat(self.marshal()), "    "),
                color="blue",
                bold=False,
            ),
        )

    @staticmethod
    def parse(wmsg):
        """
        Factory method that parses a unserialized raw message (as returned byte
        :func:`autobahn.interfaces.ISerializer.unserialize`) into an instance
        of this class.

        :returns: An instance of this class.
        :rtype: obj
        """
        raise NotImplementedError()

    def marshal(self):
        raise NotImplementedError()

    @staticmethod
    def cast(buf):
        raise NotImplementedError()

    def build(self, builder, serializer=None):
        """
        Build a FlatBuffers representation of this message.

        :param builder: A FlatBuffers builder to serialize into.
        :type builder: flatbuffers.Builder
        :param serializer: The transport serializer (ISerializer) to use for
            application payload serialization. Uses PAYLOAD_SERIALIZER_ID to
            determine how to serialize args/kwargs/payload.
        :type serializer: ISerializer or None
        :returns: Offset to the serialized message in the builder.
        """
        raise NotImplementedError()

    def uncache(self):
        """
        Resets the serialization cache.
        """
        self._serialized = {}

    def serialize(self, serializer):
        """
        Serialize this object into a wire level bytes representation and cache
        the resulting bytes. If the cache already contains an entry for the given
        serializer, return the cached representation directly.

        :param serializer: The wire level serializer to use.
        :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`

        :returns: The serialized bytes.
        :rtype: bytes
        """
        # only serialize if not cached ..
        if serializer not in self._serialized:
            if serializer.NAME == "flatbuffers":
                # flatbuffers get special treatment ..
                builder = flatbuffers.Builder(1024)

                # Get parent ISerializer to access payload serialization
                parent_serializer = getattr(serializer, "_parent_serializer", None)

                # this is the core method writing out this message (self) to a (new) flatbuffer
                # FIXME: implement this method for all classes derived from Message
                obj = self.build(builder, parent_serializer)

                builder.Finish(obj)
                buf = builder.Output()
                self._serialized[serializer] = bytes(buf)
            else:
                # all other serializers first marshal() the object and then serialize the latter
                self._serialized[serializer] = serializer.serialize(self.marshal())

        # cache is filled now: return serialized, cached bytes
        return self._serialized[serializer]


class MessageWithAppPayload(object):
    """
    Mixin for WAMP messages carrying application payload (Category 4).

    The 7 data plane messages: PUBLISH, EVENT, CALL, INVOCATION, YIELD, RESULT, ERROR

    Attributes (the "6-set"):
        args, kwargs, payload, enc_algo, enc_key, enc_serializer

    These six attributes form an inseparable unit. In E2EE mode, attributes
    enc_algo/enc_key/enc_serializer must all be present or all be None.

    Note on __slots__:
        This mixin has __slots__ = () (empty tuple). This is REQUIRED for multiple
        inheritance with __slots__. DO NOT REMOVE! Empty __slots__ means "I add no
        new slots but allow derived classes to use slots". Without this, the class
        would get a __dict__ and break the slots chain. See docs/wamp/message-design.rst
        for detailed explanation.

    Note on initialization:
        Uses _init_app_payload() method instead of __init__() to avoid complex super()
        chains in multiple inheritance. Concrete classes call this method explicitly.
    """

    __slots__ = ()  # REQUIRED: Empty slots for mixin pattern. DO NOT REMOVE!

    def _init_app_payload(
        self,
        args=None,
        kwargs=None,
        payload=None,
        enc_algo=None,
        enc_key=None,
        enc_serializer=None,
    ):
        """
        Initialize application payload attributes.

        Note: This is NOT __init__() to avoid super() complexity in multiple inheritance.
        Concrete message classes call this method explicitly after Message.__init__().

        :param args: Positional arguments (list/tuple)
        :param kwargs: Keyword arguments (dict)
        :param payload: Opaque payload bytes (for E2EE)
        :param enc_algo: Encoding/encryption algorithm identifier
        :param enc_key: Key identifier for decryption
        :param enc_serializer: Payload serializer ID (e.g., "cbor", "json")
        """
        self._args = args
        self._kwargs = _validate_kwargs(kwargs)
        self._payload = payload
        self._enc_algo = enc_algo
        self._enc_key = enc_key
        self._enc_serializer = enc_serializer

    def _get_payload_serializer_id(self):
        """
        Get the serializer ID to use for payload deserialization.

        Returns the enc_serializer if set, otherwise defaults to "cbor"
        for backward compatibility.
        """
        return self._enc_serializer if self._enc_serializer else "cbor"

    def _deserialize_payload(self, data_bytes, ser_id):
        """
        Deserialize payload data using the specified serializer.

        Uses memoryview (zero-copy) where possible. Converts to bytes
        only for JSON and FlexBuffers which don't support memoryview.

        :param data_bytes: memoryview of the serialized data
        :param ser_id: Serializer ID string ("json", "cbor", "msgpack", etc.)
        :return: Deserialized Python object (list, dict, etc.)
        """
        # Special case: FlexBuffers (quasi-dynamic typing)
        if ser_id == "flexbuffers":
            from autobahn.flatbuffers import flexbuffers

            root = flexbuffers.GetRoot(bytes(data_bytes))
            return root

        # Import the appropriate deserializer
        if ser_id == "json":
            import json

            # JSON requires bytes() conversion
            return json.loads(bytes(data_bytes))
        elif ser_id == "cbor":
            import cbor2

            # cbor2 supports memoryview (zero-copy)
            return cbor2.loads(data_bytes)
        elif ser_id == "msgpack":
            import msgpack

            # msgpack supports memoryview (zero-copy)
            return msgpack.unpackb(data_bytes)
        elif ser_id == "ubjson":
            import ubjson

            # ubjson supports memoryview (zero-copy)
            return ubjson.loadb(data_bytes)
        else:
            # Fallback to CBOR for unknown serializers
            import cbor2

            return cbor2.loads(data_bytes)

    @property
    def args(self):
        """Lazy deserialization of args from FlatBuffers"""
        if self._args is None and self._from_fbs:
            if self._from_fbs.ArgsLength():
                ser_id = self._get_payload_serializer_id()
                args_bytes = self._from_fbs.ArgsAsBytes()  # Returns memoryview

                if ser_id == "flexbuffers":
                    root = self._deserialize_payload(args_bytes, ser_id)
                    self._args = root.AsVector.Value  # Returns Python list
                else:
                    self._args = self._deserialize_payload(args_bytes, ser_id)
        return self._args

    @args.setter
    def args(self, value):
        assert value is None or type(value) in [list, tuple]
        self._args = value

    @property
    def kwargs(self):
        """Lazy deserialization of kwargs from FlatBuffers"""
        if self._kwargs is None and self._from_fbs:
            if self._from_fbs.KwargsLength():
                ser_id = self._get_payload_serializer_id()
                kwargs_bytes = self._from_fbs.KwargsAsBytes()  # Returns memoryview

                if ser_id == "flexbuffers":
                    root = self._deserialize_payload(kwargs_bytes, ser_id)
                    self._kwargs = root.AsMap.Value  # Returns Python dict
                else:
                    self._kwargs = self._deserialize_payload(kwargs_bytes, ser_id)
        return self._kwargs

    @kwargs.setter
    def kwargs(self, value):
        assert value is None or type(value) == dict
        self._kwargs = value

    @property
    def payload(self):
        """Lazy deserialization of payload from FlatBuffers"""
        if self._payload is None and self._from_fbs:
            if self._from_fbs.PayloadLength():
                self._payload = self._from_fbs.PayloadAsBytes()
        return self._payload

    @payload.setter
    def payload(self, value):
        assert value is None or type(value) == bytes
        self._payload = value

    @property
    def enc_algo(self):
        """Lazy deserialization of enc_algo from FlatBuffers"""
        if self._enc_algo is None and self._from_fbs:
            enc_algo = self._from_fbs.PptScheme()
            if enc_algo:
                # Convert FlatBuffers enum integer to string
                self._enc_algo = ENC_ALGOS.get(enc_algo)
        return self._enc_algo

    @enc_algo.setter
    def enc_algo(self, value):
        assert value is None or is_valid_enc_algo(value)
        self._enc_algo = value

    @property
    def enc_key(self):
        """Lazy deserialization of enc_key from FlatBuffers"""
        if self._enc_key is None and self._from_fbs:
            self._enc_key = self._from_fbs.PptKeyid()
        return self._enc_key

    @enc_key.setter
    def enc_key(self, value):
        assert value is None or type(value) == str
        self._enc_key = value

    @property
    def enc_serializer(self):
        """Lazy deserialization of enc_serializer from FlatBuffers"""
        if self._enc_serializer is None and self._from_fbs:
            enc_serializer = self._from_fbs.PptSerializer()
            if enc_serializer:
                # Convert FlatBuffers enum integer to string
                self._enc_serializer = ENC_SERS.get(enc_serializer)
        return self._enc_serializer

    @enc_serializer.setter
    def enc_serializer(self, value):
        assert value is None or is_valid_enc_serializer(value)
        self._enc_serializer = value


class MessageWithForwardFor(object):
    """
    Mixin for WAMP messages with forward_for (Category 3 & 4).

    Category 3: Subscribe, Unsubscribe, Register, Unregister, Cancel, Interrupt
    Category 4: PUBLISH, EVENT, CALL, INVOCATION, YIELD, RESULT, ERROR

    Note on __slots__:
        This mixin has __slots__ = () (empty tuple). This is REQUIRED for multiple
        inheritance with __slots__. DO NOT REMOVE! Empty __slots__ means "I add no
        new slots but allow derived classes to use slots". Without this, the class
        would get a __dict__ and break the slots chain. See docs/wamp/message-design.rst
        for detailed explanation.

    Note on initialization:
        Uses _init_forward_for() method instead of __init__() to avoid complex super()
        chains in multiple inheritance. Concrete classes call this method explicitly.
    """

    __slots__ = ()  # REQUIRED: Empty slots for mixin pattern. DO NOT REMOVE!

    def _init_forward_for(self, forward_for=None):
        """
        Initialize forwarding attributes.

        Note: This is NOT __init__() to avoid super() complexity in multiple inheritance.
        Concrete message classes call this method explicitly after Message.__init__().

        :param forward_for: Forwarding chain metadata (list of dicts)
        """
        self._forward_for = forward_for

    @property
    def forward_for(self):
        """
        Property-based access to WAMP message forward_for attribute.

        Primary purpose: Provides property-based access to the forward_for attribute
        for ALL WAMP serializers (JSON, MessagePack, CBOR, UBJSON, FlatBuffers).

        FlatBuffers detail: For FlatBuffers serialization specifically, this property
        performs lazy deserialization - the forward_for list is only deserialized from
        the underlying FlatBuffers Principal objects when first accessed. For other
        serializers (JSON, CBOR, etc.), the entire WAMP message is deserialized in one
        go during message parsing, so this property simply returns the pre-parsed value.

        :return: List of forwarding chain entries, each a dict with keys:
                 - 'session' (int): WAMP session ID
                 - 'authid' (str or None): Authentication ID
                 - 'authrole' (str): Authentication role
        :rtype: list[dict] or None
        """
        if self._forward_for is None and self._from_fbs:
            # Check if this message type has forward_for in FlatBuffers schema
            # Category 1 messages don't have forward_for
            if hasattr(self._from_fbs, 'ForwardForLength') and self._from_fbs.ForwardForLength():
                forward_for = []
                for j in range(self._from_fbs.ForwardForLength()):
                    principal = self._from_fbs.ForwardFor(j)
                    # Principal is now a table and supports authid/authrole
                    authid = principal.Authid()
                    if authid:
                        authid = (
                            authid.decode("utf-8")
                            if isinstance(authid, bytes)
                            else authid
                        )
                    authrole = principal.Authrole()
                    if authrole:
                        authrole = (
                            authrole.decode("utf-8")
                            if isinstance(authrole, bytes)
                            else authrole
                        )
                    forward_for.append(
                        {
                            "session": principal.Session(),
                            "authid": authid,
                            "authrole": authrole,
                        }
                    )
                self._forward_for = forward_for
        return self._forward_for

    @forward_for.setter
    def forward_for(self, value):
        """
        Set the forward_for attribute.

        :param value: List of forwarding chain entries, each a dict with keys:
                      - 'session' (int): WAMP session ID
                      - 'authid' (str or None): Authentication ID
                      - 'authrole' (str): Authentication role
        :type value: list[dict] or None
        """
        assert value is None or type(value) == list
        if value:
            for ff in value:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str
        self._forward_for = value


class Hello(Message):
    """
    A WAMP ``HELLO`` message.

    Format: ``[HELLO, Realm|uri, Details|dict]``
    """

    MESSAGE_TYPE = 1
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        # string (uri)
        "_realm",
        # ClientRoles (required)
        "_roles",
        # [AuthMethod]
        "_authmethods",
        # string (principal)
        "_authid",
        # string (principal)
        "_authrole",
        # Map
        "_authextra",
        # bool
        "_resumable",
        # uint64
        "_resume_session",
        # string
        "_resume_token",
    )

    def __init__(
        self,
        realm=None,
        roles=None,
        authmethods=None,
        authid=None,
        authrole=None,
        authextra=None,
        resumable=None,
        resume_session=None,
        resume_token=None,
        from_fbs=None,
    ):
        """

        :param realm: The URI of the WAMP realm to join.
        :type realm: str

        :param roles: The WAMP session roles and features to announce.
        :type roles: dict of :class:`autobahn.wamp.role.RoleFeatures`

        :param authmethods: The authentication methods to announce.
        :type authmethods: list of str or None

        :param authid: The authentication ID to announce.
        :type authid: str or None

        :param authrole: The authentication role to announce.
        :type authrole: str or None

        :param authextra: Application-specific "extra data" to be forwarded to the client.
        :type authextra: dict or None

        :param resumable: Whether the client wants this to be a session that can be later resumed.
        :type resumable: bool or None

        :param resume_session: The session the client would like to resume.
        :type resume_session: int or None

        :param resume_token: The secure authorisation token to resume the session.
        :type resume_token: str or None
        """
        assert realm is None or isinstance(realm, str)
        assert roles is None or type(roles) == dict
        if roles is not None and not from_fbs:
            assert len(roles) > 0
            for role in roles:
                assert role in ["subscriber", "publisher", "caller", "callee"]
                assert isinstance(
                    roles[role], autobahn.wamp.role.ROLE_NAME_TO_CLASS[role]
                )
        if authmethods:
            assert type(authmethods) == list
            for authmethod in authmethods:
                assert type(authmethod) == str
        assert authid is None or type(authid) == str
        assert authrole is None or type(authrole) == str
        assert authextra is None or type(authextra) == dict
        assert resumable is None or type(resumable) == bool
        assert resume_session is None or type(resume_session) == int
        assert resume_token is None or type(resume_token) == str

        Message.__init__(self, from_fbs=from_fbs)
        self._realm = realm
        self._roles = roles
        self._authmethods = authmethods
        self._authid = authid
        self._authrole = authrole
        self._authextra = authextra
        self._resumable = resumable
        self._resume_session = resume_session
        self._resume_token = resume_token

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.realm != self.realm:
            return False
        if other.roles != self.roles:
            return False
        if other.authmethods != self.authmethods:
            return False
        if other.authid != self.authid:
            return False
        if other.authrole != self.authrole:
            return False
        if other.authextra != self.authextra:
            return False
        if other.resumable != self.resumable:
            return False
        if other.resume_session != self.resume_session:
            return False
        if other.resume_token != self.resume_token:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def realm(self):
        if self._realm is None and self._from_fbs:
            realm_bytes = self._from_fbs.Realm()
            if realm_bytes:
                self._realm = realm_bytes.decode("utf-8")
        return self._realm

    @realm.setter
    def realm(self, value):
        assert value is None or type(value) == str
        self._realm = value

    @property
    def roles(self):
        if self._roles is None and self._from_fbs:
            # Note: Full deserialization of ClientRoles from FlatBuffers is complex
            # Would require deserializing nested PublisherFeatures, SubscriberFeatures, etc.
            # For now, return empty dict
            self._roles = {}
        return self._roles

    @roles.setter
    def roles(self, value):
        assert value is None or type(value) == dict
        self._roles = value

    @property
    def authmethods(self):
        if self._authmethods is None and self._from_fbs:
            # Note: AuthMethod enum array deserialization deferred
            self._authmethods = []
        return self._authmethods

    @authmethods.setter
    def authmethods(self, value):
        assert value is None or type(value) == list
        self._authmethods = value

    @property
    def authid(self):
        if self._authid is None and self._from_fbs:
            authid_bytes = self._from_fbs.Authid()
            if authid_bytes:
                self._authid = authid_bytes.decode("utf-8")
        return self._authid

    @authid.setter
    def authid(self, value):
        assert value is None or type(value) == str
        self._authid = value

    @property
    def authrole(self):
        if self._authrole is None and self._from_fbs:
            authrole_bytes = self._from_fbs.Authrole()
            if authrole_bytes:
                self._authrole = authrole_bytes.decode("utf-8")
        return self._authrole

    @authrole.setter
    def authrole(self, value):
        assert value is None or type(value) == str
        self._authrole = value

    @property
    def authextra(self):
        if self._authextra is None and self._from_fbs:
            # Note: Map deserialization complex and deferred
            self._authextra = {}
        return self._authextra

    @authextra.setter
    def authextra(self, value):
        assert value is None or type(value) == dict
        self._authextra = value

    @property
    def resumable(self):
        if self._resumable is None and self._from_fbs:
            self._resumable = self._from_fbs.Resumable()
        return self._resumable

    @resumable.setter
    def resumable(self, value):
        assert value is None or type(value) == bool
        self._resumable = value

    @property
    def resume_session(self):
        if self._resume_session is None and self._from_fbs:
            self._resume_session = self._from_fbs.ResumeSession()
        return self._resume_session

    @resume_session.setter
    def resume_session(self, value):
        assert value is None or type(value) == int
        self._resume_session = value

    @property
    def resume_token(self):
        if self._resume_token is None and self._from_fbs:
            resume_token_bytes = self._from_fbs.ResumeToken()
            if resume_token_bytes:
                self._resume_token = resume_token_bytes.decode("utf-8")
        return self._resume_token

    @resume_token.setter
    def resume_token(self, value):
        assert value is None or type(value) == str
        self._resume_token = value

    @staticmethod
    def cast(buf):
        """
        Cast a FlatBuffers buffer to a Hello message.

        :param buf: FlatBuffers buffer
        :type buf: bytes

        :returns: An instance of this class.
        """
        return Hello(from_fbs=message_fbs.Hello.GetRootAsHello(buf, 0))

    def build(self, builder, serializer=None):
        """
        Build FlatBuffers representation of this message.

        :param builder: FlatBuffers builder
        :type builder: flatbuffers.Builder

        :param serializer: Serializer for payload encoding (not used for Hello)
        :type serializer: ISerializer or None

        :returns: FlatBuffers offset
        """
        # Note: Full serialization of ClientRoles to FlatBuffers is complex
        # Would require serializing nested PublisherFeatures, SubscriberFeatures, etc.
        # For now, we only serialize the simple string/int/bool fields

        # Serialize string fields
        realm = self.realm
        if realm:
            realm = builder.CreateString(realm)

        authid = self.authid
        if authid:
            authid = builder.CreateString(authid)

        authrole = self.authrole
        if authrole:
            authrole = builder.CreateString(authrole)

        resume_token = self.resume_token
        if resume_token:
            resume_token = builder.CreateString(resume_token)

        # Start message
        message_fbs.HelloGen.HelloStart(builder)

        # Add fields
        if realm:
            message_fbs.HelloGen.HelloAddRealm(builder, realm)
        if authid:
            message_fbs.HelloGen.HelloAddAuthid(builder, authid)
        if authrole:
            message_fbs.HelloGen.HelloAddAuthrole(builder, authrole)
        if self.resumable is not None:
            message_fbs.HelloGen.HelloAddResumable(builder, self.resumable)
        if self.resume_session:
            message_fbs.HelloGen.HelloAddResumeSession(builder, self.resume_session)
        if resume_token:
            message_fbs.HelloGen.HelloAddResumeToken(builder, resume_token)

        # TODO: Add ClientRoles serialization
        # TODO: Add authmethods array serialization
        # TODO: Add authextra Map serialization

        # End message
        msg = message_fbs.HelloGen.HelloEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.HELLO)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Hello.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for HELLO".format(len(wmsg))
            )

        realm = check_or_raise_uri(wmsg[1], "'realm' in HELLO", allow_none=True)
        details = check_or_raise_extra(wmsg[2], "'details' in HELLO")

        roles = {}

        if "roles" not in details:
            raise ProtocolError("missing mandatory roles attribute in options in HELLO")

        details_roles = check_or_raise_extra(
            details["roles"], "'roles' in 'details' in HELLO"
        )

        if len(details_roles) == 0:
            raise ProtocolError("empty 'roles' in 'details' in HELLO")

        for role in details_roles:
            if role not in ["subscriber", "publisher", "caller", "callee"]:
                raise ProtocolError(
                    "invalid role '{0}' in 'roles' in 'details' in HELLO".format(role)
                )

            role_cls = ROLE_NAME_TO_CLASS[role]

            details_role = check_or_raise_extra(
                details_roles[role],
                "role '{0}' in 'roles' in 'details' in HELLO".format(role),
            )

            if "features" in details_role:
                check_or_raise_extra(
                    details_role["features"],
                    "'features' in role '{0}' in 'roles' in 'details' in HELLO".format(
                        role
                    ),
                )

                role_features = role_cls(**details_role["features"])

            else:
                role_features = role_cls()

            roles[role] = role_features

        authmethods = None
        if "authmethods" in details:
            details_authmethods = details["authmethods"]
            if type(details_authmethods) != list:
                raise ProtocolError(
                    "invalid type {0} for 'authmethods' detail in HELLO".format(
                        type(details_authmethods)
                    )
                )

            for auth_method in details_authmethods:
                if type(auth_method) != str:
                    raise ProtocolError(
                        "invalid type {0} for item in 'authmethods' detail in HELLO".format(
                            type(auth_method)
                        )
                    )

            authmethods = details_authmethods

        authid = None
        if "authid" in details:
            details_authid = details["authid"]
            if type(details_authid) != str:
                raise ProtocolError(
                    "invalid type {0} for 'authid' detail in HELLO".format(
                        type(details_authid)
                    )
                )

            authid = details_authid

        authrole = None
        if "authrole" in details:
            details_authrole = details["authrole"]
            if type(details_authrole) != str:
                raise ProtocolError(
                    "invalid type {0} for 'authrole' detail in HELLO".format(
                        type(details_authrole)
                    )
                )

            authrole = details_authrole

        authextra = None
        if "authextra" in details:
            details_authextra = details["authextra"]
            if type(details_authextra) != dict:
                raise ProtocolError(
                    "invalid type {0} for 'authextra' detail in HELLO".format(
                        type(details_authextra)
                    )
                )

            authextra = details_authextra

        resumable = None
        if "resumable" in details:
            resumable = details["resumable"]
            if type(resumable) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'resumable' detail in HELLO".format(
                        type(resumable)
                    )
                )

        resume_session = None
        if "resume-session" in details:
            resume_session = details["resume-session"]
            if type(resume_session) != int:
                raise ProtocolError(
                    "invalid type {0} for 'resume-session' detail in HELLO".format(
                        type(resume_session)
                    )
                )

        resume_token = None
        if "resume-token" in details:
            resume_token = details["resume-token"]
            if type(resume_token) != str:
                raise ProtocolError(
                    "invalid type {0} for 'resume-token' detail in HELLO".format(
                        type(resume_token)
                    )
                )
        else:
            if resume_session:
                raise ProtocolError(
                    "resume-token must be provided if resume-session is provided in HELLO"
                )

        obj = Hello(
            realm,
            roles,
            authmethods,
            authid,
            authrole,
            authextra,
            resumable,
            resume_session,
            resume_token,
        )

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {"roles": {}}
        for role in self.roles.values():
            details["roles"][role.ROLE] = {}
            for feature in role.__dict__:
                if (
                    not feature.startswith("_")
                    and feature != "ROLE"
                    and getattr(role, feature) is not None
                ):
                    if "features" not in details["roles"][role.ROLE]:
                        details["roles"][role.ROLE] = {"features": {}}
                    details["roles"][role.ROLE]["features"][feature] = getattr(
                        role, feature
                    )

        if self.authmethods is not None:
            details["authmethods"] = self.authmethods

        if self.authid is not None:
            details["authid"] = self.authid

        if self.authrole is not None:
            details["authrole"] = self.authrole

        if self.authextra is not None:
            details["authextra"] = self.authextra

        if self.resumable is not None:
            details["resumable"] = self.resumable

        if self.resume_session is not None:
            details["resume-session"] = self.resume_session

        if self.resume_token is not None:
            details["resume-token"] = self.resume_token

        return [Hello.MESSAGE_TYPE, self.realm, details]


class Welcome(Message):
    """
    A WAMP ``WELCOME`` message.

    Format: ``[WELCOME, Session|id, Details|dict]``
    """

    MESSAGE_TYPE = 2
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        # uint64
        "_session",
        # RouterRoles (required)
        "_roles",
        # string (required, uri)
        "_realm",
        # string (required, principal)
        "_authid",
        # string (required, principal)
        "_authrole",
        # AuthMethod
        "_authmethod",
        # string
        "_authprovider",
        # Map
        "_authextra",
        # bool
        "_resumed",
        # bool
        "_resumable",
        # string
        "_resume_token",
        # dict
        "_custom",
    )

    def __init__(
        self,
        session=None,
        roles=None,
        realm=None,
        authid=None,
        authrole=None,
        authmethod=None,
        authprovider=None,
        authextra=None,
        resumed=None,
        resumable=None,
        resume_token=None,
        custom=None,
        from_fbs=None,
    ):
        """

        :param session: The WAMP session ID the other peer is assigned.
        :type session: int

        :param roles: The WAMP roles to announce.
        :type roles: dict of :class:`autobahn.wamp.role.RoleFeatures`

        :param realm: The effective realm the session is joined on.
        :type realm: str or None

        :param authid: The authentication ID assigned.
        :type authid: str or None

        :param authrole: The authentication role assigned.
        :type authrole: str or None

        :param authmethod: The authentication method in use.
        :type authmethod: str or None

        :param authprovider: The authentication provided in use.
        :type authprovider: str or None

        :param authextra: Application-specific "extra data" to be forwarded to the client.
        :type authextra: arbitrary or None

        :param resumed: Whether the session is a resumed one.
        :type resumed: bool or None

        :param resumable: Whether this session can be resumed later.
        :type resumable: bool or None

        :param resume_token: The secure authorisation token to resume the session.
        :type resume_token: str or None

        :param custom: Implementation-specific "custom attributes" (`x_my_impl_attribute`) to be set.
        :type custom: dict or None
        """
        assert session is None or type(session) == int
        assert roles is None or type(roles) == dict
        if roles is not None and not from_fbs:
            assert len(roles) > 0
            for role in roles:
                assert role in ["broker", "dealer"]
                assert isinstance(
                    roles[role], autobahn.wamp.role.ROLE_NAME_TO_CLASS[role]
                )
        assert realm is None or type(realm) == str
        assert authid is None or type(authid) == str
        assert authrole is None or type(authrole) == str
        assert authmethod is None or type(authmethod) == str
        assert authprovider is None or type(authprovider) == str
        assert authextra is None or type(authextra) == dict
        assert resumed is None or type(resumed) == bool
        assert resumable is None or type(resumable) == bool
        assert resume_token is None or type(resume_token) == str
        assert custom is None or type(custom) == dict
        if custom:
            for k in custom:
                assert _CUSTOM_ATTRIBUTE.match(k)

        Message.__init__(self, from_fbs=from_fbs)
        self._session = session
        self._roles = roles
        self._realm = realm
        self._authid = authid
        self._authrole = authrole
        self._authmethod = authmethod
        self._authprovider = authprovider
        self._authextra = authextra
        self._resumed = resumed
        self._resumable = resumable
        self._resume_token = resume_token
        self._custom = custom or {} if custom is not None or not from_fbs else None

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.session != self.session:
            return False
        if other.roles != self.roles:
            return False
        if other.realm != self.realm:
            return False
        if other.authid != self.authid:
            return False
        if other.authrole != self.authrole:
            return False
        if other.authmethod != self.authmethod:
            return False
        if other.authprovider != self.authprovider:
            return False
        if other.authextra != self.authextra:
            return False
        if other.resumed != self.resumed:
            return False
        if other.resumable != self.resumable:
            return False
        if other.resume_token != self.resume_token:
            return False
        if other.custom != self.custom:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def session(self):
        if self._session is None and self._from_fbs:
            self._session = self._from_fbs.Session()
        return self._session

    @session.setter
    def session(self, value):
        assert value is None or type(value) == int
        self._session = value

    @property
    def roles(self):
        if self._roles is None and self._from_fbs:
            # Note: Full deserialization of RouterRoles from FlatBuffers is complex
            # Would require deserializing nested BrokerFeatures, DealerFeatures, etc.
            # For now, return empty dict
            self._roles = {}
        return self._roles

    @roles.setter
    def roles(self, value):
        assert value is None or type(value) == dict
        self._roles = value

    @property
    def realm(self):
        if self._realm is None and self._from_fbs:
            realm_bytes = self._from_fbs.Realm()
            if realm_bytes:
                self._realm = realm_bytes.decode("utf-8")
        return self._realm

    @realm.setter
    def realm(self, value):
        assert value is None or type(value) == str
        self._realm = value

    @property
    def authid(self):
        if self._authid is None and self._from_fbs:
            authid_bytes = self._from_fbs.Authid()
            if authid_bytes:
                self._authid = authid_bytes.decode("utf-8")
        return self._authid

    @authid.setter
    def authid(self, value):
        assert value is None or type(value) == str
        self._authid = value

    @property
    def authrole(self):
        if self._authrole is None and self._from_fbs:
            authrole_bytes = self._from_fbs.Authrole()
            if authrole_bytes:
                self._authrole = authrole_bytes.decode("utf-8")
        return self._authrole

    @authrole.setter
    def authrole(self, value):
        assert value is None or type(value) == str
        self._authrole = value

    @property
    def authmethod(self):
        if self._authmethod is None and self._from_fbs:
            # Note: AuthMethod enum to string conversion deferred
            method_val = self._from_fbs.Authmethod()
            if method_val:
                self._authmethod = f"authmethod_{method_val}"
        return self._authmethod

    @authmethod.setter
    def authmethod(self, value):
        assert value is None or type(value) == str
        self._authmethod = value

    @property
    def authprovider(self):
        if self._authprovider is None and self._from_fbs:
            authprovider_bytes = self._from_fbs.Authprovider()
            if authprovider_bytes:
                self._authprovider = authprovider_bytes.decode("utf-8")
        return self._authprovider

    @authprovider.setter
    def authprovider(self, value):
        assert value is None or type(value) == str
        self._authprovider = value

    @property
    def authextra(self):
        if self._authextra is None and self._from_fbs:
            # Note: Map deserialization complex and deferred
            self._authextra = {}
        return self._authextra

    @authextra.setter
    def authextra(self, value):
        assert value is None or type(value) == dict
        self._authextra = value

    @property
    def resumed(self):
        if self._resumed is None and self._from_fbs:
            self._resumed = self._from_fbs.Resumed()
        return self._resumed

    @resumed.setter
    def resumed(self, value):
        assert value is None or type(value) == bool
        self._resumed = value

    @property
    def resumable(self):
        if self._resumable is None and self._from_fbs:
            self._resumable = self._from_fbs.Resumable()
        return self._resumable

    @resumable.setter
    def resumable(self, value):
        assert value is None or type(value) == bool
        self._resumable = value

    @property
    def resume_token(self):
        if self._resume_token is None and self._from_fbs:
            resume_token_bytes = self._from_fbs.ResumeToken()
            if resume_token_bytes:
                self._resume_token = resume_token_bytes.decode("utf-8")
        return self._resume_token

    @resume_token.setter
    def resume_token(self, value):
        assert value is None or type(value) == str
        self._resume_token = value

    @property
    def custom(self):
        if self._custom is None and self._from_fbs:
            # Note: custom attributes deserialization deferred
            self._custom = {}
        return self._custom if self._custom is not None else {}

    @custom.setter
    def custom(self, value):
        assert value is None or type(value) == dict
        self._custom = value

    @staticmethod
    def cast(buf):
        """
        Cast a FlatBuffers buffer to a Welcome message.

        :param buf: FlatBuffers buffer
        :type buf: bytes

        :returns: An instance of this class.
        """
        return Welcome(from_fbs=message_fbs.Welcome.GetRootAsWelcome(buf, 0))

    def build(self, builder, serializer=None):
        """
        Build FlatBuffers representation of this message.

        :param builder: FlatBuffers builder
        :type builder: flatbuffers.Builder

        :param serializer: Serializer for payload encoding (not used for Welcome)
        :type serializer: ISerializer or None

        :returns: FlatBuffers offset
        """
        # Note: Full serialization of RouterRoles to FlatBuffers is complex
        # Would require serializing nested BrokerFeatures, DealerFeatures, etc.
        # For now, we only serialize the simple string/int/bool fields

        # Serialize string fields
        realm = self.realm
        if realm:
            realm = builder.CreateString(realm)

        authid = self.authid
        if authid:
            authid = builder.CreateString(authid)

        authrole = self.authrole
        if authrole:
            authrole = builder.CreateString(authrole)

        authprovider = self.authprovider
        if authprovider:
            authprovider = builder.CreateString(authprovider)

        resume_token = self.resume_token
        if resume_token:
            resume_token = builder.CreateString(resume_token)

        # Start message
        message_fbs.WelcomeGen.WelcomeStart(builder)

        # Add fields
        if self.session:
            message_fbs.WelcomeGen.WelcomeAddSession(builder, self.session)
        if realm:
            message_fbs.WelcomeGen.WelcomeAddRealm(builder, realm)
        if authid:
            message_fbs.WelcomeGen.WelcomeAddAuthid(builder, authid)
        if authrole:
            message_fbs.WelcomeGen.WelcomeAddAuthrole(builder, authrole)
        if authprovider:
            message_fbs.WelcomeGen.WelcomeAddAuthprovider(builder, authprovider)
        if self.resumed is not None:
            message_fbs.WelcomeGen.WelcomeAddResumed(builder, self.resumed)
        if self.resumable is not None:
            message_fbs.WelcomeGen.WelcomeAddResumable(builder, self.resumable)
        if resume_token:
            message_fbs.WelcomeGen.WelcomeAddResumeToken(builder, resume_token)

        # TODO: Add RouterRoles serialization
        # TODO: Add authmethod enum serialization
        # TODO: Add authextra Map serialization

        # End message
        msg = message_fbs.WelcomeGen.WelcomeEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.WELCOME)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Welcome.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for WELCOME".format(len(wmsg))
            )

        session = check_or_raise_id(wmsg[1], "'session' in WELCOME")
        details = check_or_raise_extra(wmsg[2], "'details' in WELCOME")

        # FIXME: tigher value checking (types, URIs etc)
        realm = details.get("realm", None)
        authid = details.get("authid", None)
        authrole = details.get("authrole", None)
        authmethod = details.get("authmethod", None)
        authprovider = details.get("authprovider", None)
        authextra = details.get("authextra", None)

        resumed = None
        if "resumed" in details:
            resumed = details["resumed"]
            if not type(resumed) == bool:
                raise ProtocolError(
                    "invalid type {0} for 'resumed' detail in WELCOME".format(
                        type(resumed)
                    )
                )

        resumable = None
        if "resumable" in details:
            resumable = details["resumable"]
            if not type(resumable) == bool:
                raise ProtocolError(
                    "invalid type {0} for 'resumable' detail in WELCOME".format(
                        type(resumable)
                    )
                )

        resume_token = None
        if "resume_token" in details:
            resume_token = details["resume_token"]
            if not type(resume_token) == str:
                raise ProtocolError(
                    "invalid type {0} for 'resume_token' detail in WELCOME".format(
                        type(resume_token)
                    )
                )
        elif resumable:
            raise ProtocolError(
                "resume_token required when resumable is given in WELCOME"
            )

        roles = {}

        if "roles" not in details:
            raise ProtocolError(
                "missing mandatory roles attribute in options in WELCOME"
            )

        details_roles = check_or_raise_extra(
            details["roles"], "'roles' in 'details' in WELCOME"
        )

        if len(details_roles) == 0:
            raise ProtocolError("empty 'roles' in 'details' in WELCOME")

        for role in details_roles:
            if role not in ["broker", "dealer"]:
                raise ProtocolError(
                    "invalid role '{0}' in 'roles' in 'details' in WELCOME".format(role)
                )

            role_cls = ROLE_NAME_TO_CLASS[role]

            details_role = check_or_raise_extra(
                details_roles[role],
                "role '{0}' in 'roles' in 'details' in WELCOME".format(role),
            )

            if "features" in details_role:
                check_or_raise_extra(
                    details_role["features"],
                    "'features' in role '{0}' in 'roles' in 'details' in WELCOME".format(
                        role
                    ),
                )

                role_features = role_cls(**details_roles[role]["features"])

            else:
                role_features = role_cls()

            roles[role] = role_features

        custom = {}
        for k in details:
            if _CUSTOM_ATTRIBUTE.match(k):
                custom[k] = details[k]

        obj = Welcome(
            session,
            roles,
            realm,
            authid,
            authrole,
            authmethod,
            authprovider,
            authextra,
            resumed,
            resumable,
            resume_token,
            custom,
        )

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {}
        details.update(self.custom)

        if self.realm:
            details["realm"] = self.realm

        if self.authid:
            details["authid"] = self.authid

        if self.authrole:
            details["authrole"] = self.authrole

        if self.authrole:
            details["authmethod"] = self.authmethod

        if self.authprovider:
            details["authprovider"] = self.authprovider

        if self.authextra:
            details["authextra"] = self.authextra

        if self.resumed:
            details["resumed"] = self.resumed

        if self.resumable:
            details["resumable"] = self.resumable

        if self.resume_token:
            details["resume_token"] = self.resume_token

        details["roles"] = {}
        for role in self.roles.values():
            details["roles"][role.ROLE] = {}
            for feature in role.__dict__:
                if (
                    not feature.startswith("_")
                    and feature != "ROLE"
                    and getattr(role, feature) is not None
                ):
                    if "features" not in details["roles"][role.ROLE]:
                        details["roles"][role.ROLE] = {"features": {}}
                    details["roles"][role.ROLE]["features"][feature] = getattr(
                        role, feature
                    )

        return [Welcome.MESSAGE_TYPE, self.session, details]


class Abort(Message):
    """
    A WAMP ``ABORT`` message.

    Format: ``[ABORT, Details|dict, Reason|uri]``
    """

    MESSAGE_TYPE = 3
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        # string (required, uri)
        "_reason",
        # string
        "_message",
    )

    def __init__(self, reason=None, message=None, from_fbs=None):
        """

        :param reason: WAMP or application error URI for aborting reason.
        :type reason: str

        :param message: Optional human-readable closing message, e.g. for logging purposes.
        :type message: str or None
        """
        assert reason is None or type(reason) == str
        assert message is None or type(message) == str

        Message.__init__(self, from_fbs=from_fbs)
        self._reason = reason
        self._message = message

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.reason != self.reason:
            return False
        if other.message != self.message:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def reason(self):
        if self._reason is None and self._from_fbs:
            reason_bytes = self._from_fbs.Reason()
            if reason_bytes:
                self._reason = reason_bytes.decode("utf-8")
        return self._reason

    @reason.setter
    def reason(self, value):
        assert value is None or type(value) == str
        self._reason = value

    @property
    def message(self):
        if self._message is None and self._from_fbs:
            message_bytes = self._from_fbs.Message()
            if message_bytes:
                self._message = message_bytes.decode("utf-8")
        return self._message

    @message.setter
    def message(self, value):
        assert value is None or type(value) == str
        self._message = value

    @staticmethod
    def cast(buf):
        """
        Cast a FlatBuffers buffer to an Abort message.

        :param buf: FlatBuffers buffer
        :type buf: bytes

        :returns: An instance of this class.
        """
        return Abort(from_fbs=message_fbs.Abort.GetRootAsAbort(buf, 0))

    def build(self, builder, serializer=None):
        """
        Build FlatBuffers representation of this message.

        :param builder: FlatBuffers builder
        :type builder: flatbuffers.Builder

        :param serializer: Serializer for payload encoding (not used for Abort)
        :type serializer: ISerializer or None

        :returns: FlatBuffers offset
        """
        # Serialize string fields
        reason = self.reason
        if reason:
            reason = builder.CreateString(reason)

        message = self.message
        if message:
            message = builder.CreateString(message)

        # Start message
        message_fbs.AbortGen.AbortStart(builder)

        # Add fields
        session = getattr(self, 'session', None)
        if session:
            message_fbs.AbortGen.AbortAddSession(builder, session)
        if reason:
            message_fbs.AbortGen.AbortAddReason(builder, reason)
        if message:
            message_fbs.AbortGen.AbortAddMessage(builder, message)

        # End and return
        msg = message_fbs.AbortGen.AbortEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.ABORT)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Abort.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for ABORT".format(len(wmsg))
            )

        details = check_or_raise_extra(wmsg[1], "'details' in ABORT")
        reason = check_or_raise_uri(wmsg[2], "'reason' in ABORT")

        message = None

        if "message" in details:
            details_message = details["message"]
            if type(details_message) != str:
                raise ProtocolError(
                    "invalid type {0} for 'message' detail in ABORT".format(
                        type(details_message)
                    )
                )

            message = details_message

        obj = Abort(reason, message)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {}
        if self.message:
            details["message"] = self.message

        return [Abort.MESSAGE_TYPE, details, self.reason]


class Challenge(Message):
    """
    A WAMP ``CHALLENGE`` message.

    Format: ``[CHALLENGE, Method|string, Extra|dict]``
    """

    MESSAGE_TYPE = 4
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        # AuthMethod (enum)
        "_method",
        # Map
        "_extra",
    )

    def __init__(self, method=None, extra=None, from_fbs=None):
        """

        :param method: The authentication method.
        :type method: str

        :param extra: Authentication method specific information.
        :type extra: dict or None
        """
        assert method is None or type(method) == str
        assert extra is None or type(extra) == dict

        Message.__init__(self, from_fbs=from_fbs)
        self._method = method
        self._extra = extra or {} if extra is not None or not from_fbs else None

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.method != self.method:
            return False
        if other.extra != self.extra:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def method(self):
        if self._method is None and self._from_fbs:
            method_val = self._from_fbs.Method()
            # Map AuthMethod enum to string
            # AuthMethod: NULL=0, TICKET=1, CRA=2, SCRAM=3, CRYPTOSIGN=4
            AUTH_METHOD_MAP = {
                0: None,           # NULL/anonymous
                1: "ticket",       # TICKET
                2: "wampcra",      # CRA (Challenge-Response Authentication)
                3: "wamp-scram",   # SCRAM
                4: "cryptosign",   # CRYPTOSIGN
            }
            self._method = AUTH_METHOD_MAP.get(method_val)
        return self._method

    @method.setter
    def method(self, value):
        assert value is None or type(value) == str
        self._method = value

    @property
    def extra(self):
        if self._extra is None and self._from_fbs:
            # Note: FlatBuffers extra uses Map object (key-value pairs)
            # Full deserialization of Map is complex and deferred
            # For now, return empty dict
            self._extra = {}
        return self._extra if self._extra is not None else {}

    @extra.setter
    def extra(self, value):
        assert value is None or type(value) == dict
        self._extra = value

    @staticmethod
    def cast(buf):
        """
        Cast a FlatBuffers buffer to a Challenge message.

        :param buf: FlatBuffers buffer
        :type buf: bytes

        :returns: An instance of this class.
        """
        return Challenge(from_fbs=message_fbs.Challenge.GetRootAsChallenge(buf, 0))

    def build(self, builder, serializer=None):
        """
        Build FlatBuffers representation of this message.

        :param builder: FlatBuffers builder
        :type builder: flatbuffers.Builder

        :param serializer: Serializer for payload encoding (not used for Challenge)
        :type serializer: ISerializer or None

        :returns: FlatBuffers offset
        """
        # Note: FlatBuffers extra field uses Map object
        # Full serialization of arbitrary dict to Map is complex and deferred
        # For now, we only serialize the method field

        # Start message
        message_fbs.ChallengeGen.ChallengeStart(builder)

        # Add fields
        session = getattr(self, 'session', None)
        if session:
            message_fbs.ChallengeGen.ChallengeAddSession(builder, session)

        # Method: Map string to AuthMethod enum
        # AuthMethod: NULL=0, TICKET=1, CRA=2, SCRAM=3, CRYPTOSIGN=4
        if self.method:
            STRING_TO_AUTH_METHOD = {
                "anonymous": 0,     # NULL
                "ticket": 1,        # TICKET
                "wampcra": 2,       # CRA (Challenge-Response Authentication)
                "wamp-scram": 3,    # SCRAM
                "cryptosign": 4,    # CRYPTOSIGN
            }
            method_enum = STRING_TO_AUTH_METHOD.get(self.method, 0)
            message_fbs.ChallengeGen.ChallengeAddMethod(builder, method_enum)

        # TODO: Add proper Map serialization for extra field
        # if self.extra:
        #     extra_map = create_map_from_dict(builder, self.extra)
        #     message_fbs.ChallengeGen.ChallengeAddExtra(builder, extra_map)

        # End and return
        msg = message_fbs.ChallengeGen.ChallengeEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.CHALLENGE)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Challenge.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for CHALLENGE".format(len(wmsg))
            )

        method = wmsg[1]
        if type(method) != str:
            raise ProtocolError(
                "invalid type {0} for 'method' in CHALLENGE".format(type(method))
            )

        extra = check_or_raise_extra(wmsg[2], "'extra' in CHALLENGE")

        obj = Challenge(method, extra)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Challenge.MESSAGE_TYPE, self.method, self.extra]


class Authenticate(Message):
    """
    A WAMP ``AUTHENTICATE`` message.

    Format: ``[AUTHENTICATE, Signature|string, Extra|dict]``
    """

    MESSAGE_TYPE = 5
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        # string (required)
        "_signature",
        # Map
        "_extra",
    )

    def __init__(self, signature=None, extra=None, from_fbs=None):
        """

        :param signature: The signature for the authentication challenge.
        :type signature: str

        :param extra: Authentication method specific information.
        :type extra: dict or None
        """
        assert signature is None or type(signature) == str
        assert extra is None or type(extra) == dict

        Message.__init__(self, from_fbs=from_fbs)
        self._signature = signature
        self._extra = extra or {} if extra is not None or not from_fbs else None

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.signature != self.signature:
            return False
        if other.extra != self.extra:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def signature(self):
        if self._signature is None and self._from_fbs:
            signature_bytes = self._from_fbs.Signature()
            if signature_bytes:
                self._signature = signature_bytes.decode("utf-8")
        return self._signature

    @signature.setter
    def signature(self, value):
        assert value is None or type(value) == str
        self._signature = value

    @property
    def extra(self):
        if self._extra is None and self._from_fbs:
            # Note: FlatBuffers extra uses Map object (key-value pairs)
            # Full deserialization of Map is complex and deferred
            # For now, return empty dict
            self._extra = {}
        return self._extra if self._extra is not None else {}

    @extra.setter
    def extra(self, value):
        assert value is None or type(value) == dict
        self._extra = value

    @staticmethod
    def cast(buf):
        """
        Cast a FlatBuffers buffer to an Authenticate message.

        :param buf: FlatBuffers buffer
        :type buf: bytes

        :returns: An instance of this class.
        """
        return Authenticate(
            from_fbs=message_fbs.Authenticate.GetRootAsAuthenticate(buf, 0)
        )

    def build(self, builder, serializer=None):
        """
        Build FlatBuffers representation of this message.

        :param builder: FlatBuffers builder
        :type builder: flatbuffers.Builder

        :param serializer: Serializer for payload encoding (not used for Authenticate)
        :type serializer: ISerializer or None

        :returns: FlatBuffers offset
        """
        # Note: FlatBuffers extra field uses Map object
        # Full serialization of arbitrary dict to Map is complex and deferred
        # For now, we only serialize the signature field

        # Serialize string fields
        signature = self.signature
        if signature:
            signature = builder.CreateString(signature)

        # Start message
        message_fbs.AuthenticateGen.AuthenticateStart(builder)

        # Add fields
        session = getattr(self, 'session', None)
        if session:
            message_fbs.AuthenticateGen.AuthenticateAddSession(builder, session)
        if signature:
            message_fbs.AuthenticateGen.AuthenticateAddSignature(builder, signature)

        # TODO: Add proper Map serialization for extra field
        # if self.extra:
        #     extra_map = create_map_from_dict(builder, self.extra)
        #     message_fbs.AuthenticateGen.AuthenticateAddExtra(builder, extra_map)

        # End and return
        msg = message_fbs.AuthenticateGen.AuthenticateEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.AUTHENTICATE)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Authenticate.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for AUTHENTICATE".format(len(wmsg))
            )

        signature = wmsg[1]
        if type(signature) != str:
            raise ProtocolError(
                "invalid type {0} for 'signature' in AUTHENTICATE".format(
                    type(signature)
                )
            )

        extra = check_or_raise_extra(wmsg[2], "'extra' in AUTHENTICATE")

        obj = Authenticate(signature, extra)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Authenticate.MESSAGE_TYPE, self.signature, self.extra]


class Goodbye(Message):
    """
    A WAMP ``GOODBYE`` message.

    Format: ``[GOODBYE, Details|dict, Reason|uri]``
    """

    MESSAGE_TYPE = 6
    """
    The WAMP message code for this type of message.
    """

    DEFAULT_REASON = "wamp.close.normal"
    """
    Default WAMP closing reason.
    """

    __slots__ = (
        # string (required, uri)
        "_reason",
        # string
        "_message",
        # bool
        "_resumable",
    )

    def __init__(
        self, reason=DEFAULT_REASON, message=None, resumable=None, from_fbs=None
    ):
        """

        :param reason: Optional WAMP or application error URI for closing reason.
        :type reason: str

        :param message: Optional human-readable closing message, e.g. for logging purposes.
        :type message: str or None

        :param resumable: From the server: Whether the session is able to be resumed (true) or destroyed (false). From the client: Whether it should be resumable (true) or destroyed (false).
        :type resumable: bool or None
        """
        assert reason is None or type(reason) == str
        assert message is None or type(message) == str
        assert resumable is None or type(resumable) == bool

        Message.__init__(self, from_fbs=from_fbs)
        self._reason = reason
        self._message = message
        self._resumable = resumable

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.reason != self.reason:
            return False
        if other.message != self.message:
            return False
        if other.resumable != self.resumable:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def reason(self):
        if self._reason is None and self._from_fbs:
            reason_bytes = self._from_fbs.Reason()
            if reason_bytes:
                self._reason = reason_bytes.decode("utf-8")
        return self._reason

    @reason.setter
    def reason(self, value):
        assert value is None or type(value) == str
        self._reason = value

    @property
    def message(self):
        if self._message is None and self._from_fbs:
            message_bytes = self._from_fbs.Message()
            if message_bytes:
                self._message = message_bytes.decode("utf-8")
        return self._message

    @message.setter
    def message(self, value):
        assert value is None or type(value) == str
        self._message = value

    @property
    def resumable(self):
        if self._resumable is None and self._from_fbs:
            self._resumable = self._from_fbs.Resumable()
        return self._resumable

    @resumable.setter
    def resumable(self, value):
        assert value is None or type(value) == bool
        self._resumable = value

    @staticmethod
    def cast(buf):
        """
        Cast a FlatBuffers buffer to a Goodbye message.

        :param buf: FlatBuffers buffer
        :type buf: bytes

        :returns: An instance of this class.
        """
        return Goodbye(from_fbs=message_fbs.Goodbye.GetRootAsGoodbye(buf, 0))

    def build(self, builder, serializer=None):
        """
        Build FlatBuffers representation of this message.

        :param builder: FlatBuffers builder
        :type builder: flatbuffers.Builder

        :param serializer: Serializer for payload encoding (not used for Goodbye)
        :type serializer: ISerializer or None

        :returns: FlatBuffers offset
        """
        # Serialize string fields
        reason = self.reason
        if reason:
            reason = builder.CreateString(reason)

        message = self.message
        if message:
            message = builder.CreateString(message)

        # Start message
        message_fbs.GoodbyeGen.GoodbyeStart(builder)

        # Add fields
        session = getattr(self, 'session', None)
        if session:
            message_fbs.GoodbyeGen.GoodbyeAddSession(builder, session)
        if reason:
            message_fbs.GoodbyeGen.GoodbyeAddReason(builder, reason)
        if message:
            message_fbs.GoodbyeGen.GoodbyeAddMessage(builder, message)
        if self.resumable is not None:
            message_fbs.GoodbyeGen.GoodbyeAddResumable(builder, self.resumable)

        # End and return
        msg = message_fbs.GoodbyeGen.GoodbyeEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.GOODBYE)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Goodbye.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for GOODBYE".format(len(wmsg))
            )

        details = check_or_raise_extra(wmsg[1], "'details' in GOODBYE")
        reason = check_or_raise_uri(wmsg[2], "'reason' in GOODBYE")

        message = None
        resumable = None

        if "message" in details:
            details_message = details["message"]
            if type(details_message) != str:
                raise ProtocolError(
                    "invalid type {0} for 'message' detail in GOODBYE".format(
                        type(details_message)
                    )
                )

            message = details_message

        if "resumable" in details:
            resumable = details["resumable"]
            if type(resumable) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'resumable' detail in GOODBYE".format(
                        type(resumable)
                    )
                )

        obj = Goodbye(reason=reason, message=message, resumable=resumable)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {}
        if self.message:
            details["message"] = self.message

        if self.resumable:
            details["resumable"] = self.resumable

        return [Goodbye.MESSAGE_TYPE, details, self.reason]


class Error(MessageWithAppPayload, MessageWithForwardFor, Message):
    """
    A WAMP ``ERROR`` message.

    Formats:

    * ``[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri]``
    * ``[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list]``
    * ``[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list, ArgumentsKw|dict]``
    * ``[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri, Payload|binary]``
    """

    MESSAGE_TYPE = 8
    """
    The WAMP message code for this type of message.
    """

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Error-specific slots (FlatBuffers schema types in comments)
        "_request_type",  # uint8 (message type)
        "_request",  # uint64 (key)
        "_error",  # string (required, uri)
        "_callee",  # uint64 (session id)
        "_callee_authid",  # string (principal)
        "_callee_authrole",  # string (principal)
        # From MessageWithAppPayload mixin
        "_args",  # [uint8] - serialized args
        "_kwargs",  # [uint8] - serialized kwargs
        "_payload",  # [uint8] - opaque payload
        "_enc_algo",  # Payload (enum) - encryption algorithm
        "_enc_key",  # [uint8] - encryption key
        "_enc_serializer",  # Serializer (enum) - payload serializer
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal] - forwarding chain
    )

    def __init__(
        self,
        request_type=None,
        request=None,
        error=None,
        args=None,
        kwargs=None,
        payload=None,
        enc_algo=None,
        enc_key=None,
        enc_serializer=None,
        callee=None,
        callee_authid=None,
        callee_authrole=None,
        forward_for=None,
        from_fbs=None,
    ):
        """

        :param request_type: The WAMP message type code for the original request.
        :type request_type: int

        :param request: The WAMP request ID of the original request (`Call`, `Subscribe`, ...) this error occurred for.
        :type request: int

        :param error: The WAMP or application error URI for the error that occurred.
        :type error: str

        :param args: Positional values for application-defined exception.
           Must be serializable using any serializers in use.
        :type args: list or None

        :param kwargs: Keyword values for application-defined exception.
           Must be serializable using any serializers in use.
        :type kwargs: dict or None

        :param payload: Alternative, transparent payload. If given, ``args`` and ``kwargs`` must be left unset.
        :type payload: bytes or None

        :param enc_algo: If using payload transparency, the encoding algorithm that was used to encode the payload.
        :type enc_algo: str or None

        :param enc_key: If using payload transparency with an encryption algorithm, the payload encryption key.
        :type enc_key: str or None

        :param enc_serializer: If using payload transparency, the payload object serializer that was used encoding the payload.
        :type enc_serializer: str or None

        :param callee: The WAMP session ID of the effective callee that responded with the error. Only filled if callee is disclosed.
        :type callee: None or int

        :param callee_authid: The WAMP authid of the responding callee. Only filled if callee is disclosed.
        :type callee_authid: None or unicode

        :param callee_authrole: The WAMP authrole of the responding callee. Only filled if callee is disclosed.
        :type callee_authrole: None or unicode

        :param forward_for: When this Error is forwarded for a client/callee (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert request_type is None or type(request_type) == int
        assert request is None or type(request) == int
        assert error is None or type(error) == str
        assert args is None or type(args) in [list, tuple, str, bytes]
        assert kwargs is None or type(kwargs) in [dict, str, bytes]
        assert payload is None or type(payload) == bytes
        assert payload is None or (
            payload is not None and args is None and kwargs is None
        )

        assert enc_algo is None or is_valid_enc_algo(enc_algo)
        assert (enc_algo is None and enc_key is None and enc_serializer is None) or (
            payload is not None and enc_algo is not None
        )
        assert enc_key is None or type(enc_key) == str
        assert enc_serializer is None or is_valid_enc_serializer(enc_serializer)

        assert callee is None or type(callee) == int
        assert callee_authid is None or type(callee_authid) == str
        assert callee_authrole is None or type(callee_authrole) == str

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_app_payload(
            args=args,
            kwargs=kwargs,
            payload=payload,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
        )
        self._init_forward_for(forward_for=forward_for)

        # Initialize Error-specific attributes
        self._request_type = request_type
        self._request = request
        self._error = error

        # effective callee that responded with the error
        self._callee = callee
        self._callee_authid = callee_authid
        self._callee_authrole = callee_authrole

    @property
    def request_type(self):
        if self._request_type is None and self._from_fbs:
            self._request_type = self._from_fbs.RequestType()
        return self._request_type

    @request_type.setter
    def request_type(self, value):
        assert value is None or type(value) == int
        self._request_type = value

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def error(self):
        if self._error is None and self._from_fbs:
            s = self._from_fbs.Error()
            if s:
                self._error = s.decode("utf8")
        return self._error

    @error.setter
    def error(self, value):
        assert value is None or type(value) == str
        self._error = value

    # NOTE: args, kwargs, payload properties are provided by MessageWithAppPayload mixin

    @property
    def callee(self):
        # Note: Error FlatBuffers schema doesn't include callee fields yet
        return self._callee

    @callee.setter
    def callee(self, value):
        assert value is None or type(value) == int
        self._callee = value

    @property
    def callee_authid(self):
        # Note: Error FlatBuffers schema doesn't include callee fields yet
        return self._callee_authid

    @callee_authid.setter
    def callee_authid(self, value):
        assert value is None or type(value) == str
        self._callee_authid = value

    @property
    def callee_authrole(self):
        # Note: Error FlatBuffers schema doesn't include callee fields yet
        return self._callee_authrole

    @callee_authrole.setter
    def callee_authrole(self, value):
        assert value is None or type(value) == str
        self._callee_authrole = value

    # NOTE: enc_algo, enc_key, enc_serializer properties are provided by MessageWithAppPayload mixin
    # NOTE: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def cast(buf):
        return Error(from_fbs=message_fbs.Error.GetRootAsError(buf, 0))

    def build(self, builder, serializer=None):
        args = self.args
        if args:
            if serializer:
                args = builder.CreateByteVector(serializer.serialize_payload(args))
            else:
                args = builder.CreateByteVector(cbor2.dumps(args))

        kwargs = self.kwargs
        if kwargs:
            if serializer:
                kwargs = builder.CreateByteVector(serializer.serialize_payload(kwargs))
            else:
                kwargs = builder.CreateByteVector(cbor2.dumps(kwargs))

        payload = self.payload
        if payload:
            payload = builder.CreateByteVector(payload)

        error = self.error
        if error:
            error = builder.CreateString(error)

        enc_key = self.enc_key
        if enc_key:
            enc_key = builder.CreateString(enc_key)

        callee_authid = self.callee_authid
        if callee_authid:
            callee_authid = builder.CreateString(callee_authid)

        callee_authrole = self.callee_authrole
        if callee_authrole:
            callee_authrole = builder.CreateString(callee_authrole)

        # forward_for: [Principal]
        forward_for = self.forward_for
        if forward_for:
            from wamp.proto import Principal as PrincipalGen

            _forward_for = []
            for principal in forward_for:
                _session = principal.get("session", 0)
                _authid = principal.get("authid", None)
                _authrole = principal.get("authrole", "")

                if _authid:
                    _authid = builder.CreateString(_authid)
                _authrole = builder.CreateString(_authrole)

                PrincipalGen.Start(builder)
                PrincipalGen.AddSession(builder, _session)
                if _authid:
                    PrincipalGen.AddAuthid(builder, _authid)
                PrincipalGen.AddAuthrole(builder, _authrole)
                _forward_for.append(PrincipalGen.End(builder))

            message_fbs.ErrorGen.ErrorStartForwardForVector(builder, len(_forward_for))
            for principal in reversed(_forward_for):
                builder.PrependUOffsetTRelative(principal)
            forward_for = builder.EndVector()

        # build ErrorGen
        message_fbs.ErrorGen.ErrorStart(builder)

        if self.request_type:
            message_fbs.ErrorGen.ErrorAddRequestType(builder, self.request_type)
        if self.request:
            message_fbs.ErrorGen.ErrorAddRequest(builder, self.request)
        if error:
            message_fbs.ErrorGen.ErrorAddError(builder, error)
        if args:
            message_fbs.ErrorGen.ErrorAddArgs(builder, args)
        if kwargs:
            message_fbs.ErrorGen.ErrorAddKwargs(builder, kwargs)
        if payload:
            message_fbs.ErrorGen.ErrorAddPayload(builder, payload)
        if self.enc_algo:
            # Convert string enc_algo to FlatBuffers enum value
            enc_algo_int = ENC_ALGOS_FROMSTR.get(self.enc_algo, 0)
            message_fbs.ErrorGen.ErrorAddPptScheme(builder, enc_algo_int)
        if self.enc_serializer:
            # Convert string enc_serializer to FlatBuffers enum value
            enc_serializer_int = ENC_SERS_FROMSTR.get(self.enc_serializer, 0)
            message_fbs.ErrorGen.ErrorAddPptSerializer(builder, enc_serializer_int)
        if enc_key:
            message_fbs.ErrorGen.ErrorAddPptKeyid(builder, enc_key)
        if forward_for:
            message_fbs.ErrorGen.ErrorAddForwardFor(builder, forward_for)

        msg = message_fbs.ErrorGen.ErrorEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.ERROR)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Error.MESSAGE_TYPE

        if len(wmsg) not in (5, 6, 7):
            raise ProtocolError(
                "invalid message length {0} for ERROR".format(len(wmsg))
            )

        request_type = wmsg[1]
        if type(request_type) != int:
            raise ProtocolError(
                "invalid type {0} for 'request_type' in ERROR".format(request_type)
            )

        if request_type not in [
            Subscribe.MESSAGE_TYPE,
            Unsubscribe.MESSAGE_TYPE,
            Publish.MESSAGE_TYPE,
            Register.MESSAGE_TYPE,
            Unregister.MESSAGE_TYPE,
            Call.MESSAGE_TYPE,
            Invocation.MESSAGE_TYPE,
        ]:
            raise ProtocolError(
                "invalid value {0} for 'request_type' in ERROR".format(request_type)
            )

        request = check_or_raise_id(wmsg[2], "'request' in ERROR")
        details = check_or_raise_extra(wmsg[3], "'details' in ERROR")
        error = check_or_raise_uri(wmsg[4], "'error' in ERROR")

        args = None
        kwargs = None
        payload = None
        enc_algo = None
        enc_key = None
        enc_serializer = None
        callee = None
        callee_authid = None
        callee_authrole = None
        forward_for = None

        if len(wmsg) == 6 and type(wmsg[5]) == bytes:
            payload = wmsg[5]

            enc_algo = details.get("enc_algo", None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError(
                    "invalid value {0} for 'enc_algo' detail in EVENT".format(enc_algo)
                )

            enc_key = details.get("enc_key", None)
            if enc_key and type(enc_key) != str:
                raise ProtocolError(
                    "invalid type {0} for 'enc_key' detail in EVENT".format(
                        type(enc_key)
                    )
                )

            enc_serializer = details.get("enc_serializer", None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError(
                    "invalid value {0} for 'enc_serializer' detail in EVENT".format(
                        enc_serializer
                    )
                )

        else:
            if len(wmsg) > 5:
                args = wmsg[5]
                if args is not None and type(args) != list:
                    raise ProtocolError(
                        "invalid type {0} for 'args' in ERROR".format(type(args))
                    )

            if len(wmsg) > 6:
                kwargs = wmsg[6]
                if type(kwargs) != dict:
                    raise ProtocolError(
                        "invalid type {0} for 'kwargs' in ERROR".format(type(kwargs))
                    )

        if "callee" in details:
            detail_callee = details["callee"]
            if type(detail_callee) != int:
                raise ProtocolError(
                    "invalid type {0} for 'callee' detail in ERROR".format(
                        type(detail_callee)
                    )
                )

            callee = detail_callee

        if "callee_authid" in details:
            detail_callee_authid = details["callee_authid"]
            if type(detail_callee_authid) != str:
                raise ProtocolError(
                    "invalid type {0} for 'callee_authid' detail in ERROR".format(
                        type(detail_callee_authid)
                    )
                )

            callee_authid = detail_callee_authid

        if "callee_authrole" in details:
            detail_callee_authrole = details["callee_authrole"]
            if type(detail_callee_authrole) != str:
                raise ProtocolError(
                    "invalid type {0} for 'callee_authrole' detail in ERROR".format(
                        type(detail_callee_authrole)
                    )
                )

            callee_authrole = detail_callee_authrole

        if "forward_for" in details:
            forward_for = details["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in ERROR"
                )

        obj = Error(
            request_type,
            request,
            error,
            args=args,
            kwargs=kwargs,
            payload=payload,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
            callee=callee,
            callee_authid=callee_authid,
            callee_authrole=callee_authrole,
            forward_for=forward_for,
        )

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {}

        if self.callee is not None:
            details["callee"] = self.callee
        if self.callee_authid is not None:
            details["callee_authid"] = self.callee_authid
        if self.callee_authrole is not None:
            details["callee_authrole"] = self.callee_authrole
        if self.forward_for is not None:
            details["forward_for"] = self.forward_for

        if self.payload:
            if self.enc_algo is not None:
                details["enc_algo"] = self.enc_algo
            if self.enc_key is not None:
                details["enc_key"] = self.enc_key
            if self.enc_serializer is not None:
                details["enc_serializer"] = self.enc_serializer
            return [
                self.MESSAGE_TYPE,
                self.request_type,
                self.request,
                details,
                self.error,
                self.payload,
            ]
        else:
            if self.kwargs:
                return [
                    self.MESSAGE_TYPE,
                    self.request_type,
                    self.request,
                    details,
                    self.error,
                    self.args,
                    self.kwargs,
                ]
            elif self.args:
                return [
                    self.MESSAGE_TYPE,
                    self.request_type,
                    self.request,
                    details,
                    self.error,
                    self.args,
                ]
            else:
                return [
                    self.MESSAGE_TYPE,
                    self.request_type,
                    self.request,
                    details,
                    self.error,
                ]


class Publish(MessageWithAppPayload, MessageWithForwardFor, Message):
    """
    A WAMP ``PUBLISH`` message.

    Formats:

    * ``[PUBLISH, Request|id, Options|dict, Topic|uri]``
    * ``[PUBLISH, Request|id, Options|dict, Topic|uri, Arguments|list]``
    * ``[PUBLISH, Request|id, Options|dict, Topic|uri, Arguments|list, ArgumentsKw|dict]``
    * ``[PUBLISH, Request|id, Options|dict, Topic|uri, Payload|binary]``
    """

    MESSAGE_TYPE = 16
    """
    The WAMP message code for this type of message.
    """

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Publish-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_topic",  # string (required, uri)
        "_acknowledge",  # bool
        "_exclude_me",  # bool
        "_exclude",  # [uint64]
        "_exclude_authid",  # [string] (principal)
        "_exclude_authrole",  # [string] (principal)
        "_eligible",  # [uint64]
        "_eligible_authid",  # [string] (principal)
        "_eligible_authrole",  # [string] (principal)
        "_retain",  # bool
        "_transaction_hash",  # string
        # From MessageWithAppPayload mixin
        "_args",  # [uint8] - serialized args
        "_kwargs",  # [uint8] - serialized kwargs
        "_payload",  # [uint8] - opaque payload
        "_enc_algo",  # Payload (enum) - encryption algorithm
        "_enc_key",  # [uint8] - encryption key
        "_enc_serializer",  # Serializer (enum) - payload serializer
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal] - forwarding chain
    )

    def __init__(
        self,
        request=None,
        topic=None,
        args=None,
        kwargs=None,
        payload=None,
        acknowledge=None,
        exclude_me=None,
        exclude=None,
        exclude_authid=None,
        exclude_authrole=None,
        eligible=None,
        eligible_authid=None,
        eligible_authrole=None,
        retain=None,
        transaction_hash=None,
        enc_algo=None,
        enc_key=None,
        enc_serializer=None,
        forward_for=None,
        from_fbs=None,
    ):
        """

        :param request: The WAMP request ID of this request.
        :type request: int

        :param topic: The WAMP or application URI of the PubSub topic the event should
           be published to.
        :type topic: str

        :param args: Positional values for application-defined event payload.
           Must be serializable using any serializers in use.
        :type args: list or tuple or None

        :param kwargs: Keyword values for application-defined event payload.
           Must be serializable using any serializers in use.
        :type kwargs: dict or None

        :param payload: Alternative, transparent payload. If given, ``args`` and ``kwargs`` must be left unset.
        :type payload: bytes or None

        :param acknowledge: If True, acknowledge the publication with a success or
           error response.
        :type acknowledge: bool or None

        :param exclude_me: If ``True``, exclude the publisher from receiving the event, even
           if he is subscribed (and eligible).
        :type exclude_me: bool or None

        :param exclude: List of WAMP session IDs to exclude from receiving this event.
        :type exclude: list of int or None

        :param exclude_authid: List of WAMP authids to exclude from receiving this event.
        :type exclude_authid: list of str or None

        :param exclude_authrole: List of WAMP authroles to exclude from receiving this event.
        :type exclude_authrole: list of str or None

        :param eligible: List of WAMP session IDs eligible to receive this event.
        :type eligible: list of int or None

        :param eligible_authid: List of WAMP authids eligible to receive this event.
        :type eligible_authid: list of str or None

        :param eligible_authrole: List of WAMP authroles eligible to receive this event.
        :type eligible_authrole: list of str or None

        :param retain: If ``True``, request the broker retain this event.
        :type retain: bool or None

        :param transaction_hash: An application provided transaction hash for the published event, which may
            be used in the router to throttle or deduplicate the events on the topic. See the discussion
            `here <https://github.com/wamp-proto/wamp-proto/issues/391#issuecomment-998577967>`__.
        :type transaction_hash: str

        :param enc_algo: If using payload transparency, the encoding algorithm that was used to encode the payload.
        :type enc_algo: str or None

        :param enc_key: If using payload transparency with an encryption algorithm, the payload encryption key.
        :type enc_key: str or None

        :param enc_serializer: If using payload transparency, the payload object serializer that was used encoding the payload.
        :type enc_serializer: str or None or None

        :param forward_for: When this Call is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert request is None or type(request) == int
        assert topic is None or type(topic) == str
        assert args is None or type(args) in [list, tuple, str, bytes]
        assert kwargs is None or type(kwargs) in [dict, str, bytes]
        assert payload is None or type(payload) == bytes
        assert payload is None or (
            payload is not None and args is None and kwargs is None
        )
        assert acknowledge is None or type(acknowledge) == bool
        assert retain is None or type(retain) == bool
        assert transaction_hash is None or type(transaction_hash) == str

        # publisher exlusion and black-/whitelisting
        assert exclude_me is None or type(exclude_me) == bool

        assert exclude is None or type(exclude) == list
        if exclude:
            for sessionid in exclude:
                assert type(sessionid) == int

        assert exclude_authid is None or type(exclude_authid) == list
        if exclude_authid:
            for authid in exclude_authid:
                assert type(authid) == str

        assert exclude_authrole is None or type(exclude_authrole) == list
        if exclude_authrole:
            for authrole in exclude_authrole:
                assert type(authrole) == str

        assert eligible is None or type(eligible) == list
        if eligible:
            for sessionid in eligible:
                assert type(sessionid) == int

        assert eligible_authid is None or type(eligible_authid) == list
        if eligible_authid:
            for authid in eligible_authid:
                assert type(authid) == str

        assert eligible_authrole is None or type(eligible_authrole) == list
        if eligible_authrole:
            for authrole in eligible_authrole:
                assert type(authrole) == str

        assert enc_algo is None or is_valid_enc_algo(enc_algo)
        assert (enc_algo is None and enc_key is None and enc_serializer is None) or (
            payload is not None and enc_algo is not None
        )
        assert enc_key is None or type(enc_key) == str
        assert enc_serializer is None or is_valid_enc_serializer(enc_serializer)

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_app_payload(
            args=args,
            kwargs=kwargs,
            payload=payload,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
        )
        self._init_forward_for(forward_for=forward_for)

        # Initialize Publish-specific attributes
        self._request = request
        self._topic = topic
        self._acknowledge = acknowledge

        # publisher exlusion and black-/whitelisting
        self._exclude_me = exclude_me
        self._exclude = exclude
        self._exclude_authid = exclude_authid
        self._exclude_authrole = exclude_authrole
        self._eligible = eligible
        self._eligible_authid = eligible_authid
        self._eligible_authrole = eligible_authrole

        # event retention
        self._retain = retain

        # application provided transaction hash for event
        self._transaction_hash = transaction_hash

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.request != self.request:
            return False
        if other.topic != self.topic:
            return False
        if other.args != self.args:
            return False
        if other.kwargs != self.kwargs:
            return False
        if other.payload != self.payload:
            return False
        if other.acknowledge != self.acknowledge:
            return False
        if other.exclude_me != self.exclude_me:
            return False
        if other.exclude != self.exclude:
            return False
        if other.exclude_authid != self.exclude_authid:
            return False
        if other.exclude_authrole != self.exclude_authrole:
            return False
        if other.eligible != self.eligible:
            return False
        if other.eligible_authid != self.eligible_authid:
            return False
        if other.eligible_authrole != self.eligible_authrole:
            return False
        if other.retain != self.retain:
            return False
        if other.transaction_hash != self.transaction_hash:
            return False
        if other.enc_algo != self.enc_algo:
            return False
        if other.enc_key != self.enc_key:
            return False
        if other.enc_serializer != self.enc_serializer:
            return False
        if other.forward_for != self.forward_for:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def topic(self):
        if self._topic is None and self._from_fbs:
            s = self._from_fbs.Topic()
            if s:
                self._topic = s.decode("utf8")
        return self._topic

    @topic.setter
    def topic(self, value):
        assert value is None or type(value) == str
        self._topic = value

    # NOTE: args, kwargs, payload properties are provided by MessageWithAppPayload mixin

    @property
    def acknowledge(self):
        if self._acknowledge is None and self._from_fbs:
            acknowledge = self._from_fbs.Acknowledge()
            if acknowledge:
                self._acknowledge = acknowledge
        return self._acknowledge

    @acknowledge.setter
    def acknowledge(self, value):
        assert value is None or type(value) == bool
        self._acknowledge = value

    @property
    def exclude_me(self):
        if self._exclude_me is None and self._from_fbs:
            exclude_me = self._from_fbs.ExcludeMe()
            if exclude_me is False:
                self._exclude_me = exclude_me
        return self._exclude_me

    @exclude_me.setter
    def exclude_me(self, value):
        assert value is None or type(value) == bool
        self._exclude_me = value

    @property
    def exclude(self):
        if self._exclude is None and self._from_fbs:
            if self._from_fbs.ExcludeLength():
                exclude = []
                for j in range(self._from_fbs.ExcludeLength()):
                    exclude.append(self._from_fbs.Exclude(j))
                self._exclude = exclude
        return self._exclude

    @exclude.setter
    def exclude(self, value):
        assert value is None or type(value) == list
        if value:
            for x in value:
                assert type(x) == int
        self._exclude = value

    @property
    def exclude_authid(self):
        if self._exclude_authid is None and self._from_fbs:
            if self._from_fbs.ExcludeAuthidLength():
                exclude_authid = []
                for j in range(self._from_fbs.ExcludeAuthidLength()):
                    exclude_authid.append(
                        self._from_fbs.ExcludeAuthid(j).decode("utf8")
                    )
                self._exclude_authid = exclude_authid
        return self._exclude_authid

    @exclude_authid.setter
    def exclude_authid(self, value):
        assert value is None or type(value) == list
        if value:
            for x in value:
                assert type(x) == str
        self._exclude_authid = value

    @property
    def exclude_authrole(self):
        if self._exclude_authrole is None and self._from_fbs:
            if self._from_fbs.ExcludeAuthroleLength():
                exclude_authrole = []
                for j in range(self._from_fbs.ExcludeAuthroleLength()):
                    exclude_authrole.append(
                        self._from_fbs.ExcludeAuthrole(j).decode("utf8")
                    )
                self._exclude_authrole = exclude_authrole
        return self._exclude_authrole

    @exclude_authrole.setter
    def exclude_authrole(self, value):
        assert value is None or type(value) == list
        if value:
            for x in value:
                assert type(x) == str
        self._exclude_authrole = value

    @property
    def eligible(self):
        if self._eligible is None and self._from_fbs:
            if self._from_fbs.EligibleLength():
                eligible = []
                for j in range(self._from_fbs.EligibleLength()):
                    eligible.append(self._from_fbs.Eligible(j))
                self._eligible = eligible
        return self._eligible

    @eligible.setter
    def eligible(self, value):
        assert value is None or type(value) == list
        if value:
            for x in value:
                assert type(x) == int
        self._eligible = value

    @property
    def eligible_authid(self):
        if self._eligible_authid is None and self._from_fbs:
            if self._from_fbs.EligibleAuthidLength():
                eligible_authid = []
                for j in range(self._from_fbs.EligibleAuthidLength()):
                    eligible_authid.append(
                        self._from_fbs.EligibleAuthid(j).decode("utf8")
                    )
                self._eligible_authid = eligible_authid
        return self._eligible_authid

    @eligible_authid.setter
    def eligible_authid(self, value):
        assert value is None or type(value) == list
        if value:
            for x in value:
                assert type(x) == str
        self._eligible_authid = value

    @property
    def eligible_authrole(self):
        if self._eligible_authrole is None and self._from_fbs:
            if self._from_fbs.EligibleAuthroleLength():
                eligible_authrole = []
                for j in range(self._from_fbs.EligibleAuthroleLength()):
                    eligible_authrole.append(
                        self._from_fbs.EligibleAuthrole(j).decode("utf8")
                    )
                self._eligible_authrole = eligible_authrole
        return self._eligible_authrole

    @eligible_authrole.setter
    def eligible_authrole(self, value):
        assert value is None or type(value) == list
        if value:
            for x in value:
                assert type(x) == str
        self._eligible_authrole = value

    @property
    def retain(self):
        if self._retain is None and self._from_fbs:
            retain = self._from_fbs.Retain()
            if retain:
                self._retain = retain
        return self._retain

    @retain.setter
    def retain(self, value):
        assert value is None or type(value) == bool
        self._retain = value

    @property
    def transaction_hash(self):
        if self._transaction_hash is None and self._from_fbs:
            s = self._from_fbs.TransactionHash()
            if s:
                self._transaction_hash = s.decode("utf8")
        return self._transaction_hash

    @transaction_hash.setter
    def transaction_hash(self, value):
        assert value is None or type(value) == str
        self._transaction_hash = value

    # NOTE: enc_algo, enc_key, enc_serializer properties are provided by MessageWithAppPayload mixin
    # NOTE: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def cast(buf):
        return Publish(from_fbs=message_fbs.Publish.GetRootAsPublish(buf, 0))

    def build(self, builder, serializer=None):
        args = self.args
        if args:
            if serializer:
                args = builder.CreateByteVector(serializer.serialize_payload(args))
            else:
                # Fallback for backwards compatibility (shouldn't happen)
                args = builder.CreateByteVector(cbor2.dumps(args))

        kwargs = self.kwargs
        if kwargs:
            if serializer:
                kwargs = builder.CreateByteVector(serializer.serialize_payload(kwargs))
            else:
                # Fallback for backwards compatibility (shouldn't happen)
                kwargs = builder.CreateByteVector(cbor2.dumps(kwargs))

        payload = self.payload
        if payload:
            payload = builder.CreateByteVector(payload)

        topic = self.topic
        if topic:
            topic = builder.CreateString(topic)

        transaction_hash = self.transaction_hash
        if transaction_hash:
            transaction_hash = builder.CreateString(transaction_hash)

        enc_key = self.enc_key
        if enc_key:
            enc_key = builder.CreateString(enc_key)

        # exclude: [int]
        exclude = self.exclude
        if exclude:
            message_fbs.PublishGen.PublishStartExcludeAuthidVector(
                builder, len(exclude)
            )
            for session in reversed(exclude):
                builder.PrependUint64(session)
            exclude = builder.EndVector(len(exclude))

        # exclude_authid: [string]
        exclude_authid = self.exclude_authid
        if exclude_authid:
            _exclude_authid = []
            for authid in exclude_authid:
                _exclude_authid.append(builder.CreateString(authid))
            message_fbs.PublishGen.PublishStartExcludeAuthidVector(
                builder, len(_exclude_authid)
            )
            for o in reversed(_exclude_authid):
                builder.PrependUOffsetTRelative(o)
            exclude_authid = builder.EndVector(len(_exclude_authid))

        # exclude_authrole: [string]
        exclude_authrole = self.exclude_authrole
        if exclude_authid:
            _exclude_authrole = []
            for authrole in exclude_authrole:
                _exclude_authrole.append(builder.CreateString(authrole))
            message_fbs.PublishGen.PublishStartExcludeAuthroleVector(
                builder, len(_exclude_authrole)
            )
            for o in reversed(_exclude_authrole):
                builder.PrependUOffsetTRelative(o)
            exclude_authrole = builder.EndVector(len(_exclude_authrole))

        # eligible: [int]
        eligible = self.eligible
        if eligible:
            message_fbs.PublishGen.PublishStartEligibleAuthidVector(
                builder, len(eligible)
            )
            for session in reversed(eligible):
                builder.PrependUint64(session)
            eligible = builder.EndVector(len(eligible))

        # eligible_authid: [string]
        eligible_authid = self.eligible_authid
        if eligible_authid:
            _eligible_authid = []
            for authid in eligible_authid:
                _eligible_authid.append(builder.CreateString(authid))
            message_fbs.PublishGen.PublishStartEligibleAuthidVector(
                builder, len(_eligible_authid)
            )
            for o in reversed(_eligible_authid):
                builder.PrependUOffsetTRelative(o)
            eligible_authid = builder.EndVector(len(_eligible_authid))

        # eligible_authrole: [string]
        eligible_authrole = self.eligible_authrole
        if eligible_authrole:
            _eligible_authrole = []
            for authrole in eligible_authrole:
                _eligible_authrole.append(builder.CreateString(authrole))
            message_fbs.PublishGen.PublishStartEligibleAuthroleVector(
                builder, len(_eligible_authrole)
            )
            for o in reversed(_eligible_authrole):
                builder.PrependUOffsetTRelative(o)
            eligible_authrole = builder.EndVector(len(_eligible_authrole))

        # forward_for: [Principal]
        forward_for = None
        if self.forward_for:
            from autobahn.wamp.gen.wamp.proto.Principal import (
                PrincipalStart,
                PrincipalAddSession,
                PrincipalAddAuthid,
                PrincipalAddAuthrole,
                PrincipalEnd,
            )

            _forward_for = []
            for ff in self.forward_for:
                # Build Principal table
                authid = (
                    builder.CreateString(ff["authid"]) if ff.get("authid") else None
                )
                authrole = (
                    builder.CreateString(ff["authrole"]) if ff.get("authrole") else None
                )

                PrincipalStart(builder)
                PrincipalAddSession(builder, ff["session"])
                if authid:
                    PrincipalAddAuthid(builder, authid)
                if authrole:
                    PrincipalAddAuthrole(builder, authrole)
                _forward_for.append(PrincipalEnd(builder))

            # Create vector of Principal tables
            message_fbs.PublishGen.PublishStartForwardForVector(
                builder, len(_forward_for)
            )
            for o in reversed(_forward_for):
                builder.PrependUOffsetTRelative(o)
            forward_for = builder.EndVector(len(_forward_for))

        # now start and build a new object ..
        message_fbs.PublishGen.PublishStart(builder)

        if self.request is not None:
            message_fbs.PublishGen.PublishAddRequest(builder, self.request)

        if topic:
            message_fbs.PublishGen.PublishAddTopic(builder, topic)

        if args:
            message_fbs.PublishGen.PublishAddArgs(builder, args)
        if kwargs:
            message_fbs.PublishGen.PublishAddKwargs(builder, kwargs)
        if payload:
            message_fbs.PublishGen.PublishAddPayload(builder, payload)

        if self.enc_algo:
            # Convert string enc_algo to FlatBuffers enum value
            enc_algo_int = ENC_ALGOS_FROMSTR.get(self.enc_algo, 0)
            message_fbs.PublishGen.PublishAddPptScheme(builder, enc_algo_int)
        if self.enc_serializer:
            # Convert string enc_serializer to FlatBuffers enum value
            enc_serializer_int = ENC_SERS_FROMSTR.get(self.enc_serializer, 0)
            message_fbs.PublishGen.PublishAddPptSerializer(builder, enc_serializer_int)
        if enc_key:
            message_fbs.PublishGen.PublishAddPptKeyid(builder, enc_key)

        if self.acknowledge is not None:
            message_fbs.PublishGen.PublishAddAcknowledge(builder, self.acknowledge)
        if self.exclude_me is not None:
            message_fbs.PublishGen.PublishAddExcludeMe(builder, self.exclude_me)

        if exclude:
            message_fbs.PublishGen.PublishAddExclude(builder, exclude)
        if exclude_authid:
            message_fbs.PublishGen.PublishAddExcludeAuthid(builder, exclude_authid)
        if exclude_authrole:
            message_fbs.PublishGen.PublishAddExcludeAuthrole(builder, exclude_authrole)

        if eligible:
            message_fbs.PublishGen.PublishAddEligible(builder, eligible)
        if eligible_authid:
            message_fbs.PublishGen.PublishAddEligibleAuthid(builder, eligible_authid)
        if eligible_authrole:
            message_fbs.PublishGen.PublishAddEligibleAuthrole(
                builder, eligible_authrole
            )

        if self.retain is not None:
            message_fbs.PublishGen.PublishAddRetain(builder, self.retain)
        if transaction_hash is not None:
            message_fbs.PublishGen.PublishAddTransactionHash(builder, transaction_hash)

        if forward_for:
            message_fbs.PublishGen.PublishAddForwardFor(builder, forward_for)

        msg = message_fbs.PublishGen.PublishEnd(builder)

        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.PUBLISH)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Publish.MESSAGE_TYPE

        if len(wmsg) not in (4, 5, 6):
            raise ProtocolError(
                "invalid message length {0} for PUBLISH".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in PUBLISH")
        options = check_or_raise_extra(wmsg[2], "'options' in PUBLISH")
        topic = check_or_raise_uri(wmsg[3], "'topic' in PUBLISH")

        args = None
        kwargs = None
        payload = None

        if len(wmsg) == 5 and type(wmsg[4]) in [str, bytes]:
            payload = wmsg[4]

            enc_algo = options.get("enc_algo", None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError(
                    "invalid value {0} for 'enc_algo' option in PUBLISH".format(
                        enc_algo
                    )
                )

            enc_key = options.get("enc_key", None)
            if enc_key and type(enc_key) != str:
                raise ProtocolError(
                    "invalid type {0} for 'enc_key' option in PUBLISH".format(
                        type(enc_key)
                    )
                )

            enc_serializer = options.get("enc_serializer", None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError(
                    "invalid value {0} for 'enc_serializer' option in PUBLISH".format(
                        enc_serializer
                    )
                )

        else:
            if len(wmsg) > 4:
                args = wmsg[4]
                if type(args) not in [list, str, bytes]:
                    raise ProtocolError(
                        "invalid type {0} for 'args' in PUBLISH".format(type(args))
                    )

            if len(wmsg) > 5:
                kwargs = wmsg[5]
                if type(kwargs) not in [dict, str, bytes]:
                    raise ProtocolError(
                        "invalid type {0} for 'kwargs' in PUBLISH".format(type(kwargs))
                    )

            enc_algo = None
            enc_key = None
            enc_serializer = None

        acknowledge = None
        exclude_me = None
        exclude = None
        exclude_authid = None
        exclude_authrole = None
        eligible = None
        eligible_authid = None
        eligible_authrole = None
        retain = None
        transaction_hash = None
        forward_for = None

        if "acknowledge" in options:
            option_acknowledge = options["acknowledge"]
            if type(option_acknowledge) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'acknowledge' option in PUBLISH".format(
                        type(option_acknowledge)
                    )
                )

            acknowledge = option_acknowledge

        if "exclude_me" in options:
            option_exclude_me = options["exclude_me"]
            if type(option_exclude_me) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'exclude_me' option in PUBLISH".format(
                        type(option_exclude_me)
                    )
                )

            exclude_me = option_exclude_me

        if "exclude" in options:
            option_exclude = options["exclude"]
            if type(option_exclude) != list:
                raise ProtocolError(
                    "invalid type {0} for 'exclude' option in PUBLISH".format(
                        type(option_exclude)
                    )
                )

            for _sessionid in option_exclude:
                if type(_sessionid) != int:
                    raise ProtocolError(
                        "invalid type {0} for value in 'exclude' option in PUBLISH".format(
                            type(_sessionid)
                        )
                    )

            exclude = option_exclude

        if "exclude_authid" in options:
            option_exclude_authid = options["exclude_authid"]
            if type(option_exclude_authid) != list:
                raise ProtocolError(
                    "invalid type {0} for 'exclude_authid' option in PUBLISH".format(
                        type(option_exclude_authid)
                    )
                )

            for _authid in option_exclude_authid:
                if type(_authid) != str:
                    raise ProtocolError(
                        "invalid type {0} for value in 'exclude_authid' option in PUBLISH".format(
                            type(_authid)
                        )
                    )

            exclude_authid = option_exclude_authid

        if "exclude_authrole" in options:
            option_exclude_authrole = options["exclude_authrole"]
            if type(option_exclude_authrole) != list:
                raise ProtocolError(
                    "invalid type {0} for 'exclude_authrole' option in PUBLISH".format(
                        type(option_exclude_authrole)
                    )
                )

            for _authrole in option_exclude_authrole:
                if type(_authrole) != str:
                    raise ProtocolError(
                        "invalid type {0} for value in 'exclude_authrole' option in PUBLISH".format(
                            type(_authrole)
                        )
                    )

            exclude_authrole = option_exclude_authrole

        if "eligible" in options:
            option_eligible = options["eligible"]
            if type(option_eligible) != list:
                raise ProtocolError(
                    "invalid type {0} for 'eligible' option in PUBLISH".format(
                        type(option_eligible)
                    )
                )

            for sessionId in option_eligible:
                if type(sessionId) != int:
                    raise ProtocolError(
                        "invalid type {0} for value in 'eligible' option in PUBLISH".format(
                            type(sessionId)
                        )
                    )

            eligible = option_eligible

        if "eligible_authid" in options:
            option_eligible_authid = options["eligible_authid"]
            if type(option_eligible_authid) != list:
                raise ProtocolError(
                    "invalid type {0} for 'eligible_authid' option in PUBLISH".format(
                        type(option_eligible_authid)
                    )
                )

            for _authid in option_eligible_authid:
                if type(_authid) != str:
                    raise ProtocolError(
                        "invalid type {0} for value in 'eligible_authid' option in PUBLISH".format(
                            type(_authid)
                        )
                    )

            eligible_authid = option_eligible_authid

        if "eligible_authrole" in options:
            option_eligible_authrole = options["eligible_authrole"]
            if type(option_eligible_authrole) != list:
                raise ProtocolError(
                    "invalid type {0} for 'eligible_authrole' option in PUBLISH".format(
                        type(option_eligible_authrole)
                    )
                )

            for _authrole in option_eligible_authrole:
                if type(_authrole) != str:
                    raise ProtocolError(
                        "invalid type {0} for value in 'eligible_authrole' option in PUBLISH".format(
                            type(_authrole)
                        )
                    )

            eligible_authrole = option_eligible_authrole

        if "retain" in options:
            retain = options["retain"]
            if type(retain) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'retain' option in PUBLISH".format(
                        type(retain)
                    )
                )

        if "transaction_hash" in options:
            transaction_hash = options["transaction_hash"]
            if type(transaction_hash) != str:
                raise ProtocolError(
                    "invalid type {0} for 'transaction_hash' option in PUBLISH".format(
                        type(transaction_hash)
                    )
                )

        if "forward_for" in options:
            forward_for = options["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in PUBLISH"
                )

        obj = Publish(
            request,
            topic,
            args=args,
            kwargs=kwargs,
            payload=payload,
            acknowledge=acknowledge,
            exclude_me=exclude_me,
            exclude=exclude,
            exclude_authid=exclude_authid,
            exclude_authrole=exclude_authrole,
            eligible=eligible,
            eligible_authid=eligible_authid,
            eligible_authrole=eligible_authrole,
            retain=retain,
            transaction_hash=transaction_hash,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
            forward_for=forward_for,
        )

        return obj

    def marshal_options(self):
        options = {}

        if self.acknowledge is not None:
            options["acknowledge"] = self.acknowledge

        if self.exclude_me is not None:
            options["exclude_me"] = self.exclude_me
        if self.exclude is not None:
            options["exclude"] = self.exclude
        if self.exclude_authid is not None:
            options["exclude_authid"] = self.exclude_authid
        if self.exclude_authrole is not None:
            options["exclude_authrole"] = self.exclude_authrole
        if self.eligible is not None:
            options["eligible"] = self.eligible
        if self.eligible_authid is not None:
            options["eligible_authid"] = self.eligible_authid
        if self.eligible_authrole is not None:
            options["eligible_authrole"] = self.eligible_authrole
        if self.retain is not None:
            options["retain"] = self.retain
        if self.transaction_hash is not None:
            options["transaction_hash"] = self.transaction_hash

        if self.payload:
            if self.enc_algo is not None:
                options["enc_algo"] = self.enc_algo
            if self.enc_key is not None:
                options["enc_key"] = self.enc_key
            if self.enc_serializer is not None:
                options["enc_serializer"] = self.enc_serializer

        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        return options

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        options = self.marshal_options()

        if self.payload:
            # Convert memoryview to bytes for non-FlatBuffers serializers
            payload = (
                bytes(self.payload)
                if isinstance(self.payload, memoryview)
                else self.payload
            )
            return [
                Publish.MESSAGE_TYPE,
                self.request,
                options,
                self.topic,
                payload,
            ]
        else:
            if self.kwargs:
                return [
                    Publish.MESSAGE_TYPE,
                    self.request,
                    options,
                    self.topic,
                    self.args,
                    self.kwargs,
                ]
            elif self.args:
                return [
                    Publish.MESSAGE_TYPE,
                    self.request,
                    options,
                    self.topic,
                    self.args,
                ]
            else:
                return [Publish.MESSAGE_TYPE, self.request, options, self.topic]


class Published(Message):
    """
    A WAMP ``PUBLISHED`` message.

    Format: ``[PUBLISHED, PUBLISH.Request|id, Publication|id]``
    """

    MESSAGE_TYPE = 17
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        "_request",
        "_publication",
    )

    def __init__(self, request=None, publication=None, from_fbs=None):
        """

        :param request: The request ID of the original `PUBLISH` request.
        :type request: int

        :param publication: The publication ID for the published event.
        :type publication: int
        """
        assert request is None or type(request) == int
        assert publication is None or type(publication) == int

        Message.__init__(self, from_fbs=from_fbs)
        self._request = request
        self._publication = publication

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @property
    def publication(self):
        if self._publication is None and self._from_fbs:
            self._publication = self._from_fbs.Publication()
        return self._publication

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Published.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for PUBLISHED".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in PUBLISHED")
        publication = check_or_raise_id(wmsg[2], "'publication' in PUBLISHED")

        obj = Published(request, publication)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Published.MESSAGE_TYPE, self.request, self.publication]

    @staticmethod
    def cast(buf):
        return Published(from_fbs=message_fbs.Published.GetRootAsPublished(buf, 0))

    def build(self, builder, serializer=None):
        message_fbs.PublishedGen.PublishedStart(builder)

        session = getattr(self, 'session', None)
        if session:
            message_fbs.PublishedGen.PublishedAddSession(builder, session)
        if self.request:
            message_fbs.PublishedGen.PublishedAddRequest(builder, self.request)
        if self.publication:
            message_fbs.PublishedGen.PublishedAddPublication(builder, self.publication)

        msg = message_fbs.PublishedGen.PublishedEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.PUBLISHED)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Subscribe(MessageWithForwardFor, Message):
    """
    A WAMP ``SUBSCRIBE`` message.

    Format: ``[SUBSCRIBE, Request|id, Options|dict, Topic|uri]``
    """

    MESSAGE_TYPE = 32
    """
    The WAMP message code for this type of message.
    """

    MATCH_EXACT = "exact"
    MATCH_PREFIX = "prefix"
    MATCH_WILDCARD = "wildcard"

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Subscribe-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_topic",  # string (required, uri_pattern)
        "_match",  # Match (enum)
        "_get_retained",  # bool
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal]
    )

    def __init__(
        self,
        request=None,
        topic=None,
        match=None,
        get_retained=None,
        forward_for=None,
        from_fbs=None,
    ):
        """

        :param request: The WAMP request ID of this request.
        :type request: int

        :param topic: The WAMP or application URI of the PubSub topic to subscribe to.
        :type topic: str

        :param match: The topic matching method to be used for the subscription.
        :type match: str

        :param get_retained: Whether the client wants the retained message we may have along with the subscription.
        :type get_retained: bool or None

        :param forward_for: When this Subscribe is forwarded over a router-to-router link,
            or via an intermediary router.
        :type forward_for: list[dict]
        """
        assert request is None or type(request) == int
        assert topic is None or type(topic) == str
        assert match is None or type(match) == str
        assert match is None or match in [
            Subscribe.MATCH_EXACT,
            Subscribe.MATCH_PREFIX,
            Subscribe.MATCH_WILDCARD,
        ]
        assert get_retained is None or type(get_retained) is bool
        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_forward_for(forward_for=forward_for)

        # Initialize Subscribe-specific attributes
        self._request = request
        self._topic = topic
        self._match = match or Subscribe.MATCH_EXACT
        self._get_retained = get_retained

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.request != self.request:
            return False
        if other.topic != self.topic:
            return False
        if other.match != self.match:
            return False
        if other.get_retained != self.get_retained:
            return False
        if other.forward_for != self.forward_for:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def topic(self):
        if self._topic is None and self._from_fbs:
            topic_bytes = self._from_fbs.Topic()
            if topic_bytes:
                self._topic = topic_bytes.decode("utf-8")
        return self._topic

    @topic.setter
    def topic(self, value):
        assert value is None or type(value) == str
        self._topic = value

    @property
    def match(self):
        if self._match is None and self._from_fbs:
            # Match is stored as enum in FlatBuffers, need to convert to string
            match_val = self._from_fbs.Match()
            # Map FlatBuffers enum values to string constants
            if match_val == 1:  # MATCH_PREFIX
                self._match = Subscribe.MATCH_PREFIX
            elif match_val == 2:  # MATCH_WILDCARD
                self._match = Subscribe.MATCH_WILDCARD
            else:  # MATCH_EXACT (0 or default)
                self._match = Subscribe.MATCH_EXACT
        return self._match

    @match.setter
    def match(self, value):
        assert value is None or type(value) == str
        self._match = value

    @property
    def get_retained(self):
        if self._get_retained is None and self._from_fbs:
            self._get_retained = self._from_fbs.GetRetained()
        return self._get_retained

    @get_retained.setter
    def get_retained(self, value):
        assert value is None or type(value) == bool
        self._get_retained = value

    # Note: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Subscribe.MESSAGE_TYPE

        if len(wmsg) != 4:
            raise ProtocolError(
                "invalid message length {0} for SUBSCRIBE".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in SUBSCRIBE")
        options = check_or_raise_extra(wmsg[2], "'options' in SUBSCRIBE")
        topic = check_or_raise_uri(
            wmsg[3], "'topic' in SUBSCRIBE", allow_empty_components=True
        )

        match = Subscribe.MATCH_EXACT
        get_retained = None
        forward_for = None

        if "match" in options:
            option_match = options["match"]
            if type(option_match) != str:
                raise ProtocolError(
                    "invalid type {0} for 'match' option in SUBSCRIBE".format(
                        type(option_match)
                    )
                )

            if option_match not in [
                Subscribe.MATCH_EXACT,
                Subscribe.MATCH_PREFIX,
                Subscribe.MATCH_WILDCARD,
            ]:
                raise ProtocolError(
                    "invalid value {0} for 'match' option in SUBSCRIBE".format(
                        option_match
                    )
                )

            match = option_match

        if "get_retained" in options:
            get_retained = options["get_retained"]

            if type(get_retained) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'get_retained' option in SUBSCRIBE".format(
                        type(get_retained)
                    )
                )

        if "forward_for" in options:
            forward_for = options["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in SUBSCRIBE"
                )

        obj = Subscribe(
            request,
            topic,
            match=match,
            get_retained=get_retained,
            forward_for=forward_for,
        )

        return obj

    def marshal_options(self):
        options = {}

        if self.match and self.match != Subscribe.MATCH_EXACT:
            options["match"] = self.match

        if self.get_retained is not None:
            options["get_retained"] = self.get_retained

        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        return options

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [
            Subscribe.MESSAGE_TYPE,
            self.request,
            self.marshal_options(),
            self.topic,
        ]

    @staticmethod
    def cast(buf):
        return Subscribe(from_fbs=message_fbs.Subscribe.GetRootAsSubscribe(buf, 0))

    def build(self, builder, serializer=None):
        # Serialize topic string
        topic = self.topic
        if topic:
            topic = builder.CreateString(topic)

        # Start message
        message_fbs.SubscribeGen.SubscribeStart(builder)

        # Add fields
        session = getattr(self, 'session', None)
        if session:
            message_fbs.SubscribeGen.SubscribeAddSession(builder, session)
        if self.request:
            message_fbs.SubscribeGen.SubscribeAddRequest(builder, self.request)
        if topic:
            message_fbs.SubscribeGen.SubscribeAddTopic(builder, topic)

        # Convert match string to enum value
        if self.match:
            if self.match == Subscribe.MATCH_PREFIX:
                match_val = message_fbs.Match.PREFIX
            elif self.match == Subscribe.MATCH_WILDCARD:
                match_val = message_fbs.Match.WILDCARD
            else:  # MATCH_EXACT
                match_val = message_fbs.Match.EXACT
            message_fbs.SubscribeGen.SubscribeAddMatch(builder, match_val)

        if self.get_retained is not None:
            message_fbs.SubscribeGen.SubscribeAddGetRetained(builder, self.get_retained)

        # End and return
        msg = message_fbs.SubscribeGen.SubscribeEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.SUBSCRIBE)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Subscribed(Message):
    """
    A WAMP ``SUBSCRIBED`` message.

    Format: ``[SUBSCRIBED, SUBSCRIBE.Request|id, Subscription|id]``
    """

    MESSAGE_TYPE = 33
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        "_request",
        "_subscription",
    )

    def __init__(self, request=None, subscription=None, from_fbs=None):
        """

        :param request: The request ID of the original ``SUBSCRIBE`` request.
        :type request: int

        :param subscription: The subscription ID for the subscribed topic (or topic pattern).
        :type subscription: int
        """
        assert request is None or type(request) == int
        assert subscription is None or type(subscription) == int

        Message.__init__(self, from_fbs=from_fbs)
        self._request = request
        self._subscription = subscription

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @property
    def subscription(self):
        if self._subscription is None and self._from_fbs:
            self._subscription = self._from_fbs.Subscription()
        return self._subscription

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Subscribed.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for SUBSCRIBED".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in SUBSCRIBED")
        subscription = check_or_raise_id(wmsg[2], "'subscription' in SUBSCRIBED")

        obj = Subscribed(request, subscription)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Subscribed.MESSAGE_TYPE, self.request, self.subscription]

    @staticmethod
    def cast(buf):
        return Subscribed(from_fbs=message_fbs.Subscribed.GetRootAsSubscribed(buf, 0))

    def build(self, builder, serializer=None):
        message_fbs.SubscribedGen.SubscribedStart(builder)

        session = getattr(self, 'session', None)
        if session:
            message_fbs.SubscribedGen.SubscribedAddSession(builder, session)
        if self.request:
            message_fbs.SubscribedGen.SubscribedAddRequest(builder, self.request)
        if self.subscription:
            message_fbs.SubscribedGen.SubscribedAddSubscription(
                builder, self.subscription
            )

        msg = message_fbs.SubscribedGen.SubscribedEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.SUBSCRIBED)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Unsubscribe(MessageWithForwardFor, Message):
    """
    A WAMP ``UNSUBSCRIBE`` message.

    Formats:

    * ``[UNSUBSCRIBE, Request|id, SUBSCRIBED.Subscription|id]``
    * ``[UNSUBSCRIBE, Request|id, SUBSCRIBED.Subscription|id, Options|dict]``
    """

    MESSAGE_TYPE = 34
    """
    The WAMP message code for this type of message.
    """

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Unsubscribe-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_subscription",  # uint64
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal]
    )

    def __init__(
        self, request=None, subscription=None, forward_for=None, from_fbs=None
    ):
        """

        :param request: The WAMP request ID of this request.
        :type request: int

        :param subscription: The subscription ID for the subscription to unsubscribe from.
        :type subscription: int

        :param forward_for: When this Unsubscribe is forwarded over a router-to-router link,
            or via an intermediary router.
        :type forward_for: list[dict]
        """
        assert request is None or type(request) == int
        assert subscription is None or type(subscription) == int
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_forward_for(forward_for=forward_for)

        # Initialize Unsubscribe-specific attributes
        self._request = request
        self._subscription = subscription

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.request != self.request:
            return False
        if other.subscription != self.subscription:
            return False
        if other.forward_for != self.forward_for:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def subscription(self):
        if self._subscription is None and self._from_fbs:
            self._subscription = self._from_fbs.Subscription()
        return self._subscription

    @subscription.setter
    def subscription(self, value):
        assert value is None or type(value) == int
        self._subscription = value

    # Note: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Unsubscribe.MESSAGE_TYPE

        if len(wmsg) not in [3, 4]:
            raise ProtocolError(
                "invalid message length {0} for WAMP UNSUBSCRIBE".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in UNSUBSCRIBE")
        subscription = check_or_raise_id(wmsg[2], "'subscription' in UNSUBSCRIBE")

        options = None
        if len(wmsg) > 3:
            options = check_or_raise_extra(wmsg[3], "'options' in UNSUBSCRIBE")

        forward_for = None
        if options and "forward_for" in options:
            forward_for = options["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in UNSUBSCRIBE"
                )

        obj = Unsubscribe(request, subscription, forward_for=forward_for)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        if self.forward_for:
            options = {
                "forward_for": self.forward_for,
            }
            return [Unsubscribe.MESSAGE_TYPE, self.request, self.subscription, options]
        else:
            return [Unsubscribe.MESSAGE_TYPE, self.request, self.subscription]

    @staticmethod
    def cast(buf):
        return Unsubscribe(
            from_fbs=message_fbs.Unsubscribe.GetRootAsUnsubscribe(buf, 0)
        )

    def build(self, builder, serializer=None):
        message_fbs.UnsubscribeGen.UnsubscribeStart(builder)

        session = getattr(self, 'session', None)
        if session:
            message_fbs.UnsubscribeGen.UnsubscribeAddSession(builder, session)
        if self.request:
            message_fbs.UnsubscribeGen.UnsubscribeAddRequest(builder, self.request)
        if self.subscription:
            message_fbs.UnsubscribeGen.UnsubscribeAddSubscription(
                builder, self.subscription
            )

        msg = message_fbs.UnsubscribeGen.UnsubscribeEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.UNSUBSCRIBE)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Unsubscribed(Message):
    """
    A WAMP ``UNSUBSCRIBED`` message.

    Formats:

    * ``[UNSUBSCRIBED, UNSUBSCRIBE.Request|id]``
    * ``[UNSUBSCRIBED, UNSUBSCRIBE.Request|id, Details|dict]``
    """

    MESSAGE_TYPE = 35
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        # uint64 (key)
        "_request",
        # uint64
        "_subscription",
        # string (uri)
        "_reason",
    )

    def __init__(self, request=None, subscription=None, reason=None, from_fbs=None):
        """

        :param request: The request ID of the original ``UNSUBSCRIBE`` request or
            ``0`` is router triggered unsubscribe ("router revocation signaling").
        :type request: int

        :param subscription: If unsubscribe was actively triggered by router, the ID
            of the subscription revoked.
        :type subscription: int or None

        :param reason: The reason (an URI) for an active (router initiated) revocation.
        :type reason: str or None.
        """
        assert request is None or type(request) == int
        assert subscription is None or type(subscription) == int
        assert reason is None or type(reason) == str
        if request is not None and subscription is not None:
            assert (request != 0 and subscription is None) or (
                request == 0 and subscription != 0
            )

        Message.__init__(self, from_fbs=from_fbs)
        self._request = request
        self._subscription = subscription
        self._reason = reason

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.request != self.request:
            return False
        if other.subscription != self.subscription:
            return False
        if other.reason != self.reason:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def subscription(self):
        if self._subscription is None and self._from_fbs:
            self._subscription = self._from_fbs.Subscription()
        return self._subscription

    @subscription.setter
    def subscription(self, value):
        assert value is None or type(value) == int
        self._subscription = value

    @property
    def reason(self):
        if self._reason is None and self._from_fbs:
            reason_bytes = self._from_fbs.Reason()
            if reason_bytes:
                self._reason = reason_bytes.decode("utf-8")
        return self._reason

    @reason.setter
    def reason(self, value):
        assert value is None or type(value) == str
        self._reason = value

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Unsubscribed.MESSAGE_TYPE

        if len(wmsg) not in [2, 3]:
            raise ProtocolError(
                "invalid message length {0} for UNSUBSCRIBED".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in UNSUBSCRIBED")

        subscription = None
        reason = None

        if len(wmsg) > 2:
            details = check_or_raise_extra(wmsg[2], "'details' in UNSUBSCRIBED")

            if "subscription" in details:
                details_subscription = details["subscription"]
                if type(details_subscription) != int:
                    raise ProtocolError(
                        "invalid type {0} for 'subscription' detail in UNSUBSCRIBED".format(
                            type(details_subscription)
                        )
                    )
                subscription = details_subscription

            if "reason" in details:
                reason = check_or_raise_uri(
                    details["reason"], "'reason' in UNSUBSCRIBED"
                )

        obj = Unsubscribed(request, subscription, reason)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        if self.reason is not None or self.subscription is not None:
            details = {}
            if self.reason is not None:
                details["reason"] = self.reason
            if self.subscription is not None:
                details["subscription"] = self.subscription
            return [Unsubscribed.MESSAGE_TYPE, self.request, details]
        else:
            return [Unsubscribed.MESSAGE_TYPE, self.request]

    @staticmethod
    def cast(buf):
        return Unsubscribed(
            from_fbs=message_fbs.Unsubscribed.GetRootAsUnsubscribed(buf, 0)
        )

    def build(self, builder, serializer=None):
        # Serialize reason string if present
        reason = self.reason
        if reason:
            reason = builder.CreateString(reason)

        # Start message
        message_fbs.UnsubscribedGen.UnsubscribedStart(builder)

        # Add fields
        session = getattr(self, 'session', None)
        if session:
            message_fbs.UnsubscribedGen.UnsubscribedAddSession(builder, session)
        if self.request:
            message_fbs.UnsubscribedGen.UnsubscribedAddRequest(builder, self.request)
        if self.subscription:
            message_fbs.UnsubscribedGen.UnsubscribedAddSubscription(
                builder, self.subscription
            )
        if reason:
            message_fbs.UnsubscribedGen.UnsubscribedAddReason(builder, reason)

        # End and return
        msg = message_fbs.UnsubscribedGen.UnsubscribedEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.UNSUBSCRIBED)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Event(MessageWithAppPayload, MessageWithForwardFor, Message):
    """
    A WAMP ``EVENT`` message.

    Formats:

    * ``[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict]``
    * ``[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list]``
    * ``[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list, PUBLISH.ArgumentsKw|dict]``
    * ``[EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Payload|binary]``
    """

    MESSAGE_TYPE = 36
    """
    The WAMP message code for this type of message.
    """

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Event-specific slots (FlatBuffers schema types in comments)
        "_subscription",  # uint64
        "_publication",  # uint64
        "_publisher",  # uint64
        "_publisher_authid",  # string (principal)
        "_publisher_authrole",  # string (principal)
        "_topic",  # string (uri)
        "_retained",  # bool
        "_transaction_hash",  # string
        "_x_acknowledged_delivery",  # bool - FIXME: rename to "acknowledge"
        # From MessageWithAppPayload mixin
        "_args",  # [uint8] - serialized args
        "_kwargs",  # [uint8] - serialized kwargs
        "_payload",  # [uint8] - opaque payload
        "_enc_algo",  # Payload (enum) - encryption algorithm
        "_enc_key",  # [uint8] - encryption key
        "_enc_serializer",  # Serializer (enum) - payload serializer
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal] - forwarding chain
    )

    def __init__(
        self,
        subscription=None,
        publication=None,
        args=None,
        kwargs=None,
        payload=None,
        publisher=None,
        publisher_authid=None,
        publisher_authrole=None,
        topic=None,
        retained=None,
        transaction_hash=None,
        x_acknowledged_delivery=None,
        enc_algo=None,
        enc_key=None,
        enc_serializer=None,
        forward_for=None,
        from_fbs=None,
    ):
        """

        :param subscription: The subscription ID this event is dispatched under.
        :type subscription: int

        :param publication: The publication ID of the dispatched event.
        :type publication: int

        :param args: Positional values for application-defined exception.
           Must be serializable using any serializers in use.
        :type args: list or tuple or None

        :param kwargs: Keyword values for application-defined exception.
           Must be serializable using any serializers in use.
        :type kwargs: dict or None

        :param payload: Alternative, transparent payload. If given, ``args`` and ``kwargs`` must be left unset.
        :type payload: bytes or None

        :param publisher: The WAMP session ID of the publisher. Only filled if publisher is disclosed.
        :type publisher: None or int

        :param publisher_authid: The WAMP authid of the publisher. Only filled if publisher is disclosed.
        :type publisher_authid: None or unicode

        :param publisher_authrole: The WAMP authrole of the publisher. Only filled if publisher is disclosed.
        :type publisher_authrole: None or unicode

        :param topic: For pattern-based subscriptions, the event MUST contain the actual topic published to.
        :type topic: str or None

        :param retained: Whether the message was retained by the broker on the topic, rather than just published.
        :type retained: bool or None

        :param transaction_hash: An application provided transaction hash for the originating call, which may
            be used in the router to throttle or deduplicate the calls on the procedure. See the discussion
            `here <https://github.com/wamp-proto/wamp-proto/issues/391#issuecomment-998577967>`__.
        :type transaction_hash: str

        :param x_acknowledged_delivery: Whether this Event should be acknowledged.
        :type x_acknowledged_delivery: bool or None

        :param enc_algo: If using payload transparency, the encoding algorithm that was used to encode the payload.
        :type enc_algo: str or None

        :param enc_key: If using payload transparency with an encryption algorithm, the payload encryption key.
        :type enc_key: str or None

        :param enc_serializer: If using payload transparency, the payload object serializer that was used encoding the payload.
        :type enc_serializer: str or None

        :param forward_for: When this Event is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert subscription is None or type(subscription) == int
        assert publication is None or type(publication) == int
        assert args is None or type(args) in [list, tuple]
        assert kwargs is None or type(kwargs) == dict
        assert payload is None or type(payload) == bytes
        assert payload is None or (
            payload is not None and args is None and kwargs is None
        )
        assert publisher is None or type(publisher) == int
        assert publisher_authid is None or type(publisher_authid) == str
        assert publisher_authrole is None or type(publisher_authrole) == str
        assert topic is None or type(topic) == str
        assert retained is None or type(retained) == bool
        assert transaction_hash is None or type(transaction_hash) == str
        assert x_acknowledged_delivery is None or type(x_acknowledged_delivery) == bool
        assert enc_algo is None or is_valid_enc_algo(enc_algo)
        assert (enc_algo is None and enc_key is None and enc_serializer is None) or (
            payload is not None and enc_algo is not None
        )
        assert enc_key is None or type(enc_key) == str
        assert enc_serializer is None or is_valid_enc_serializer(enc_serializer)

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_app_payload(
            args=args,
            kwargs=kwargs,
            payload=payload,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
        )
        self._init_forward_for(forward_for=forward_for)

        # Initialize Event-specific attributes
        self._subscription = subscription
        self._publication = publication
        self._publisher = publisher
        self._publisher_authid = publisher_authid
        self._publisher_authrole = publisher_authrole
        self._topic = topic
        self._retained = retained
        self._transaction_hash = transaction_hash
        self._x_acknowledged_delivery = x_acknowledged_delivery

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.subscription != self.subscription:
            return False
        if other.publication != self.publication:
            return False
        if other.args != self.args:
            return False
        if other.kwargs != self.kwargs:
            return False
        if other.payload != self.payload:
            return False
        if other.publisher != self.publisher:
            return False
        if other.publisher_authid != self.publisher_authid:
            return False
        if other.publisher_authrole != self.publisher_authrole:
            return False
        if other.topic != self.topic:
            return False
        if other.retained != self.retained:
            return False
        if other.transaction_hash != self.transaction_hash:
            return False
        if other.x_acknowledged_delivery != self.x_acknowledged_delivery:
            return False
        if other.enc_algo != self.enc_algo:
            return False
        if other.enc_key != self.enc_key:
            return False
        if other.enc_serializer != self.enc_serializer:
            return False
        if other.forward_for != self.forward_for:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def subscription(self):
        if self._subscription is None and self._from_fbs:
            self._subscription = self._from_fbs.Subscription()
        return self._subscription

    @subscription.setter
    def subscription(self, value):
        assert value is None or type(value) == int
        self._subscription = value

    @property
    def publication(self):
        if self._publication is None and self._from_fbs:
            self._publication = self._from_fbs.Publication()
        return self._publication

    @publication.setter
    def publication(self, value):
        assert value is None or type(value) == int
        self._publication = value

    # Note: args, kwargs, payload properties are provided by MessageWithAppPayload mixin

    @property
    def publisher(self):
        if self._publisher is None and self._from_fbs:
            publisher = self._from_fbs.Publisher()
            if publisher:
                self._publisher = publisher
        return self._publisher

    @publisher.setter
    def publisher(self, value):
        assert value is None or type(value) == int
        self._publisher = value

    @property
    def publisher_authid(self):
        if self._publisher_authid is None and self._from_fbs:
            s = self._from_fbs.PublisherAuthid()
            if s:
                self._publisher_authid = s.decode("utf8")
        return self._publisher_authid

    @publisher_authid.setter
    def publisher_authid(self, value):
        assert value is None or type(value) == str
        self._publisher_authid = value

    @property
    def publisher_authrole(self):
        if self._publisher_authrole is None and self._from_fbs:
            s = self._from_fbs.PublisherAuthrole()
            if s:
                self._publisher_authrole = s.decode("utf8")
        return self._publisher_authrole

    @publisher_authrole.setter
    def publisher_authrole(self, value):
        assert value is None or type(value) == str
        self._publisher_authrole = value

    @property
    def topic(self):
        if self._topic is None and self._from_fbs:
            s = self._from_fbs.Topic()
            if s:
                self._topic = s.decode("utf8")
        return self._topic

    @topic.setter
    def topic(self, value):
        assert value is None or type(value) == str
        self._topic = value

    @property
    def retained(self):
        if self._retained is None and self._from_fbs:
            # Only set if non-default (True). FlatBuffers returns False for unset booleans.
            val = self._from_fbs.Retained()
            if val:  # Only set if True (non-default)
                self._retained = val
        return self._retained

    @retained.setter
    def retained(self, value):
        assert value is None or type(value) == bool
        self._retained = value

    @property
    def transaction_hash(self):
        if self._transaction_hash is None and self._from_fbs:
            s = self._from_fbs.TransactionHash()
            if s:
                self._transaction_hash = s.decode("utf8")
        return self._transaction_hash

    @transaction_hash.setter
    def transaction_hash(self, value):
        assert value is None or type(value) == str
        self._transaction_hash = value

    @property
    def x_acknowledged_delivery(self):
        if self._x_acknowledged_delivery is None and self._from_fbs:
            x_acknowledged_delivery = self._from_fbs.Acknowledge()
            if x_acknowledged_delivery:
                self._x_acknowledged_delivery = x_acknowledged_delivery
        return self._x_acknowledged_delivery

    @x_acknowledged_delivery.setter
    def x_acknowledged_delivery(self, value):
        assert value is None or type(value) == bool
        self._x_acknowledged_delivery = value

    # Note: enc_algo, enc_key, enc_serializer, forward_for properties are provided by mixins

    @staticmethod
    def cast(buf):
        return Event(from_fbs=message_fbs.Event.GetRootAsEvent(buf, 0))

    def build(self, builder, serializer=None):
        args = self.args
        if args:
            if serializer:
                args = builder.CreateByteVector(serializer.serialize_payload(args))
            else:
                # Fallback for backwards compatibility (shouldn't happen)
                args = builder.CreateByteVector(cbor2.dumps(args))

        kwargs = self.kwargs
        if kwargs:
            if serializer:
                kwargs = builder.CreateByteVector(serializer.serialize_payload(kwargs))
            else:
                # Fallback for backwards compatibility (shouldn't happen)
                kwargs = builder.CreateByteVector(cbor2.dumps(kwargs))

        payload = self.payload
        if payload:
            payload = builder.CreateByteVector(payload)

        publisher_authid = self.publisher_authid
        if publisher_authid:
            publisher_authid = builder.CreateString(publisher_authid)

        publisher_authrole = self.publisher_authrole
        if publisher_authrole:
            publisher_authrole = builder.CreateString(publisher_authrole)

        topic = self.topic
        if topic:
            topic = builder.CreateString(topic)

        transaction_hash = self.transaction_hash
        if transaction_hash:
            transaction_hash = builder.CreateString(transaction_hash)

        enc_key = self.enc_key
        if enc_key:
            enc_key = builder.CreateString(enc_key)

        # forward_for: [Principal]
        forward_for = None
        if self.forward_for:
            from autobahn.wamp.gen.wamp.proto.Principal import (
                PrincipalStart,
                PrincipalAddSession,
                PrincipalAddAuthid,
                PrincipalAddAuthrole,
                PrincipalEnd,
            )

            _forward_for = []
            for ff in self.forward_for:
                # Build Principal table
                authid = (
                    builder.CreateString(ff["authid"]) if ff.get("authid") else None
                )
                authrole = (
                    builder.CreateString(ff["authrole"]) if ff.get("authrole") else None
                )

                PrincipalStart(builder)
                PrincipalAddSession(builder, ff["session"])
                if authid:
                    PrincipalAddAuthid(builder, authid)
                if authrole:
                    PrincipalAddAuthrole(builder, authrole)
                _forward_for.append(PrincipalEnd(builder))

            # Create vector of Principal tables
            message_fbs.EventGen.EventStartForwardForVector(builder, len(_forward_for))
            for o in reversed(_forward_for):
                builder.PrependUOffsetTRelative(o)
            forward_for = builder.EndVector(len(_forward_for))

        message_fbs.EventGen.EventStart(builder)

        if self.subscription:
            message_fbs.EventGen.EventAddSubscription(builder, self.subscription)
        if self.publication:
            message_fbs.EventGen.EventAddPublication(builder, self.publication)

        if args:
            message_fbs.EventGen.EventAddArgs(builder, args)
        if kwargs:
            message_fbs.EventGen.EventAddKwargs(builder, kwargs)
        if payload:
            message_fbs.EventGen.EventAddPayload(builder, payload)

        if self.publisher:
            message_fbs.EventGen.EventAddPublisher(builder, self.publisher)
        if publisher_authid:
            message_fbs.EventGen.EventAddPublisherAuthid(builder, publisher_authid)
        if publisher_authrole:
            message_fbs.EventGen.EventAddPublisherAuthrole(builder, publisher_authrole)

        if topic:
            message_fbs.EventGen.EventAddTopic(builder, topic)
        if self.retained is not None:
            message_fbs.EventGen.EventAddRetained(builder, self.retained)
        if transaction_hash is not None:
            message_fbs.EventGen.EventAddTransactionHash(builder, transaction_hash)
        if self.x_acknowledged_delivery is not None:
            message_fbs.EventGen.EventAddAcknowledge(
                builder, self.x_acknowledged_delivery
            )

        if self.enc_algo:
            # Convert string enc_algo to FlatBuffers enum value
            enc_algo_int = ENC_ALGOS_FROMSTR.get(self.enc_algo, 0)
            message_fbs.EventGen.EventAddPptScheme(builder, enc_algo_int)
        if enc_key:
            message_fbs.EventGen.EventAddPptKeyid(builder, enc_key)
        if self.enc_serializer:
            # Convert string enc_serializer to FlatBuffers enum value
            enc_serializer_int = ENC_SERS_FROMSTR.get(self.enc_serializer, 0)
            message_fbs.EventGen.EventAddPptSerializer(builder, enc_serializer_int)

        if forward_for:
            message_fbs.EventGen.EventAddForwardFor(builder, forward_for)

        msg = message_fbs.EventGen.EventEnd(builder)

        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.EVENT)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Event.MESSAGE_TYPE

        if len(wmsg) not in (4, 5, 6):
            raise ProtocolError(
                "invalid message length {0} for EVENT".format(len(wmsg))
            )

        subscription = check_or_raise_id(wmsg[1], "'subscription' in EVENT")
        publication = check_or_raise_id(wmsg[2], "'publication' in EVENT")
        details = check_or_raise_extra(wmsg[3], "'details' in EVENT")

        args = None
        kwargs = None
        payload = None
        enc_algo = None
        enc_key = None
        enc_serializer = None

        if len(wmsg) == 5 and type(wmsg[4]) == bytes:
            payload = wmsg[4]

            enc_algo = details.get("enc_algo", None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError(
                    "invalid value {0} for 'enc_algo' detail in EVENT".format(enc_algo)
                )

            enc_key = details.get("enc_key", None)
            if enc_key and type(enc_key) != str:
                raise ProtocolError(
                    "invalid type {0} for 'enc_key' detail in EVENT".format(
                        type(enc_key)
                    )
                )

            enc_serializer = details.get("enc_serializer", None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError(
                    "invalid value {0} for 'enc_serializer' detail in EVENT".format(
                        enc_serializer
                    )
                )

        else:
            if len(wmsg) > 4:
                args = wmsg[4]
                if args is not None and type(args) != list:
                    raise ProtocolError(
                        "invalid type {0} for 'args' in EVENT".format(type(args))
                    )
            if len(wmsg) > 5:
                kwargs = wmsg[5]
                if type(kwargs) != dict:
                    raise ProtocolError(
                        "invalid type {0} for 'kwargs' in EVENT".format(type(kwargs))
                    )

        publisher = None
        publisher_authid = None
        publisher_authrole = None
        topic = None
        retained = None
        transaction_hash = None
        forward_for = None
        x_acknowledged_delivery = None

        if "publisher" in details:
            detail_publisher = details["publisher"]
            if type(detail_publisher) != int:
                raise ProtocolError(
                    "invalid type {0} for 'publisher' detail in EVENT".format(
                        type(detail_publisher)
                    )
                )

            publisher = detail_publisher

        if "publisher_authid" in details:
            detail_publisher_authid = details["publisher_authid"]
            if type(detail_publisher_authid) != str:
                raise ProtocolError(
                    "invalid type {0} for 'publisher_authid' detail in EVENT".format(
                        type(detail_publisher_authid)
                    )
                )

            publisher_authid = detail_publisher_authid

        if "publisher_authrole" in details:
            detail_publisher_authrole = details["publisher_authrole"]
            if type(detail_publisher_authrole) != str:
                raise ProtocolError(
                    "invalid type {0} for 'publisher_authrole' detail in EVENT".format(
                        type(detail_publisher_authrole)
                    )
                )

            publisher_authrole = detail_publisher_authrole

        if "topic" in details:
            detail_topic = details["topic"]
            if type(detail_topic) != str:
                raise ProtocolError(
                    "invalid type {0} for 'topic' detail in EVENT".format(
                        type(detail_topic)
                    )
                )

            topic = detail_topic

        if "retained" in details:
            retained = details["retained"]
            if type(retained) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'retained' detail in EVENT".format(
                        type(retained)
                    )
                )

        if "transaction_hash" in details:
            detail_transaction_hash = details["transaction_hash"]
            if type(detail_transaction_hash) != str:
                raise ProtocolError(
                    "invalid type {0} for 'transaction_hash' detail in EVENT".format(
                        type(detail_transaction_hash)
                    )
                )

            transaction_hash = detail_transaction_hash

        if "x_acknowledged_delivery" in details:
            x_acknowledged_delivery = details["x_acknowledged_delivery"]
            if type(x_acknowledged_delivery) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'x_acknowledged_delivery' detail in EVENT".format(
                        type(x_acknowledged_delivery)
                    )
                )

        if "forward_for" in details:
            forward_for = details["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in EVENT"
                )

        obj = Event(
            subscription,
            publication,
            args=args,
            kwargs=kwargs,
            payload=payload,
            publisher=publisher,
            publisher_authid=publisher_authid,
            publisher_authrole=publisher_authrole,
            topic=topic,
            retained=retained,
            transaction_hash=transaction_hash,
            x_acknowledged_delivery=x_acknowledged_delivery,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
            forward_for=forward_for,
        )

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {}

        if self.publisher is not None:
            details["publisher"] = self.publisher

        if self.publisher_authid is not None:
            details["publisher_authid"] = self.publisher_authid

        if self.publisher_authrole is not None:
            details["publisher_authrole"] = self.publisher_authrole

        if self.topic is not None:
            details["topic"] = self.topic

        if self.retained is not None:
            details["retained"] = self.retained

        if self.transaction_hash is not None:
            details["transaction_hash"] = self.transaction_hash

        if self.x_acknowledged_delivery is not None:
            details["x_acknowledged_delivery"] = self.x_acknowledged_delivery

        if self.forward_for is not None:
            details["forward_for"] = self.forward_for

        if self.payload:
            if self.enc_algo is not None:
                details["enc_algo"] = self.enc_algo
            if self.enc_key is not None:
                details["enc_key"] = self.enc_key
            if self.enc_serializer is not None:
                details["enc_serializer"] = self.enc_serializer
            # Convert memoryview to bytes for non-FlatBuffers serializers
            payload = (
                bytes(self.payload)
                if isinstance(self.payload, memoryview)
                else self.payload
            )
            return [
                Event.MESSAGE_TYPE,
                self.subscription,
                self.publication,
                details,
                payload,
            ]
        else:
            if self.kwargs:
                return [
                    Event.MESSAGE_TYPE,
                    self.subscription,
                    self.publication,
                    details,
                    self.args,
                    self.kwargs,
                ]
            elif self.args:
                return [
                    Event.MESSAGE_TYPE,
                    self.subscription,
                    self.publication,
                    details,
                    self.args,
                ]
            else:
                return [
                    Event.MESSAGE_TYPE,
                    self.subscription,
                    self.publication,
                    details,
                ]


class EventReceived(Message):
    """
    A WAMP ``EVENT_RECEIVED`` message.

    Format: ``[EVENT_RECEIVED, EVENT.Publication|id]``
    """

    # NOTE: Implementation-specific message! Should be 37 on ratification.
    MESSAGE_TYPE = 337
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        # uint64
        "_publication",
    )

    def __init__(self, publication=None, from_fbs=None):
        """

        :param publication: The publication ID for the sent event.
        :type publication: int
        """
        assert publication is None or type(publication) == int

        Message.__init__(self, from_fbs=from_fbs)
        self._publication = publication

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.publication != self.publication:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def publication(self):
        if self._publication is None and self._from_fbs:
            self._publication = self._from_fbs.Publication()
        return self._publication

    @publication.setter
    def publication(self, value):
        assert value is None or type(value) == int
        self._publication = value

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == EventReceived.MESSAGE_TYPE

        if len(wmsg) != 2:
            raise ProtocolError(
                "invalid message length {0} for EVENT_RECEIVED".format(len(wmsg))
            )

        publication = check_or_raise_id(wmsg[1], "'publication' in EVENT_RECEIVED")

        obj = EventReceived(publication)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [EventReceived.MESSAGE_TYPE, self.publication]

    @staticmethod
    def cast(buf):
        return EventReceived(
            from_fbs=message_fbs.EventReceived.GetRootAsEventReceived(buf, 0)
        )

    def build(self, builder, serializer=None):
        message_fbs.EventReceivedGen.EventReceivedStart(builder)

        if self.publication:
            message_fbs.EventReceivedGen.EventReceivedAddPublication(
                builder, self.publication
            )

        msg = message_fbs.EventReceivedGen.EventReceivedEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(
            builder, message_fbs.MessageType.EVENT_RECEIVED
        )
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Call(MessageWithAppPayload, MessageWithForwardFor, Message):
    """
    A WAMP ``CALL`` message.

    Formats:

    * ``[CALL, Request|id, Options|dict, Procedure|uri]``
    * ``[CALL, Request|id, Options|dict, Procedure|uri, Arguments|list]``
    * ``[CALL, Request|id, Options|dict, Procedure|uri, Arguments|list, ArgumentsKw|dict]``
    * ``[CALL, Request|id, Options|dict, Procedure|uri, Payload|binary]``
    """

    MESSAGE_TYPE = 48
    """
    The WAMP message code for this type of message.
    """

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Call-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_procedure",  # string (required, uri)
        "_timeout",  # uint32
        "_receive_progress",  # bool
        "_transaction_hash",  # string
        "_caller",  # uint64
        "_caller_authid",  # string (principal)
        "_caller_authrole",  # string (principal)
        # From MessageWithAppPayload mixin
        "_args",  # [uint8] - serialized args
        "_kwargs",  # [uint8] - serialized kwargs
        "_payload",  # [uint8] - opaque payload
        "_enc_algo",  # Payload (enum) - encryption algorithm
        "_enc_key",  # [uint8] - encryption key
        "_enc_serializer",  # Serializer (enum) - payload serializer
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal] - forwarding chain
    )

    def __init__(
        self,
        request=None,
        procedure=None,
        args=None,
        kwargs=None,
        payload=None,
        timeout=None,
        receive_progress=None,
        transaction_hash=None,
        enc_algo=None,
        enc_key=None,
        enc_serializer=None,
        caller=None,
        caller_authid=None,
        caller_authrole=None,
        forward_for=None,
        from_fbs=None,
    ):
        """

        :param request: The WAMP request ID of this request.
        :type request: int

        :param procedure: The WAMP or application URI of the procedure which should be called.
        :type procedure: str

        :param args: Positional values for application-defined call arguments.
           Must be serializable using any serializers in use.
        :type args: list or tuple or None

        :param kwargs: Keyword values for application-defined call arguments.
           Must be serializable using any serializers in use.
        :type kwargs: dict or None

        :param payload: Alternative, transparent payload. If given, ``args`` and ``kwargs`` must be left unset.
        :type payload: bytes or None

        :param timeout: If present, let the callee automatically cancel
           the call after this ms.
        :type timeout: int or None

        :param receive_progress: If ``True``, indicates that the caller wants to receive
           progressive call results.
        :type receive_progress: bool or None

        :param transaction_hash: An application provided transaction hash for the originating call, which may
            be used in the router to throttle or deduplicate the calls on the procedure. See the discussion
            `here <https://github.com/wamp-proto/wamp-proto/issues/391#issuecomment-998577967>`__.
        :type transaction_hash: str

        :param enc_algo: If using payload transparency, the encoding algorithm that was used to encode the payload.
        :type enc_algo: str or None

        :param enc_key: If using payload transparency with an encryption algorithm, the payload encryption key.
        :type enc_key: str or None

        :param enc_serializer: If using payload transparency, the payload object serializer that was used encoding the payload.
        :type enc_serializer: str or None

        :param caller: The WAMP session ID of the caller. Only filled if caller is disclosed.
        :type caller: None or int

        :param caller_authid: The WAMP authid of the caller. Only filled if caller is disclosed.
        :type caller_authid: None or unicode

        :param caller_authrole: The WAMP authrole of the caller. Only filled if caller is disclosed.
        :type caller_authrole: None or unicode

        :param forward_for: When this Publish is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        if from_fbs is None:
            assert type(request) == int
            assert type(procedure) == str
        assert args is None or type(args) in [list, tuple]
        assert kwargs is None or type(kwargs) == dict
        assert payload is None or type(payload) == bytes
        assert payload is None or (
            payload is not None and args is None and kwargs is None
        )
        assert timeout is None or type(timeout) == int
        assert receive_progress is None or type(receive_progress) == bool
        assert transaction_hash is None or type(transaction_hash) == str

        # payload transparency related knobs
        assert enc_algo is None or is_valid_enc_algo(enc_algo)
        assert enc_key is None or type(enc_key) == str
        assert enc_serializer is None or is_valid_enc_serializer(enc_serializer)
        assert (enc_algo is None and enc_key is None and enc_serializer is None) or (
            payload is not None and enc_algo is not None
        )

        assert caller is None or type(caller) == int
        assert caller_authid is None or type(caller_authid) == str
        assert caller_authrole is None or type(caller_authrole) == str

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_app_payload(
            args=args,
            kwargs=kwargs,
            payload=payload,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
        )
        self._init_forward_for(forward_for=forward_for)

        # Initialize Call-specific attributes
        self._request = request
        self._procedure = procedure
        self._timeout = timeout
        self._receive_progress = receive_progress
        self._transaction_hash = transaction_hash
        self._caller = caller
        self._caller_authid = caller_authid
        self._caller_authrole = caller_authrole

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.request != self.request:
            return False
        if other.procedure != self.procedure:
            return False
        if other.args != self.args:
            return False
        if other.kwargs != self.kwargs:
            return False
        if other.payload != self.payload:
            return False
        if other.timeout != self.timeout:
            return False
        if other.receive_progress != self.receive_progress:
            return False
        if other.transaction_hash != self.transaction_hash:
            return False
        if other.enc_algo != self.enc_algo:
            return False
        if other.enc_key != self.enc_key:
            return False
        if other.enc_serializer != self.enc_serializer:
            return False
        if other.caller != self.caller:
            return False
        if other.caller_authid != self.caller_authid:
            return False
        if other.caller_authrole != self.caller_authrole:
            return False
        if other.forward_for != self.forward_for:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def procedure(self):
        if self._procedure is None and self._from_fbs:
            s = self._from_fbs.Procedure()
            if s:
                self._procedure = s.decode("utf8")
        return self._procedure

    @procedure.setter
    def procedure(self, value):
        assert value is None or type(value) == str
        self._procedure = value

    # Note: args, kwargs, payload properties are provided by MessageWithAppPayload mixin

    @property
    def timeout(self):
        if self._timeout is None and self._from_fbs:
            timeout = self._from_fbs.Timeout()
            if timeout:
                self._timeout = timeout
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        assert value is None or type(value) == int
        self._timeout = value

    @property
    def receive_progress(self):
        if self._receive_progress is None and self._from_fbs:
            receive_progress = self._from_fbs.ReceiveProgress()
            if receive_progress:
                self._receive_progress = receive_progress
        return self._receive_progress

    @receive_progress.setter
    def receive_progress(self, value):
        assert value is None or type(value) == bool
        self._receive_progress = value

    @property
    def transaction_hash(self):
        if self._transaction_hash is None and self._from_fbs:
            s = self._from_fbs.TransactionHash()
            if s:
                self._transaction_hash = s.decode("utf8")
        return self._transaction_hash

    @transaction_hash.setter
    def transaction_hash(self, value):
        assert value is None or type(value) == str
        self._transaction_hash = value

    # Note: enc_algo, enc_key, enc_serializer properties are provided by MessageWithAppPayload mixin

    @property
    def caller(self):
        if self._caller is None and self._from_fbs:
            caller = self._from_fbs.Caller()
            if caller:
                self._caller = caller
        return self._caller

    @caller.setter
    def caller(self, value):
        assert value is None or type(value) == int
        self._caller = value

    @property
    def caller_authid(self):
        if self._caller_authid is None and self._from_fbs:
            s = self._from_fbs.CallerAuthid()
            if s:
                self._caller_authid = s.decode("utf8")
        return self._caller_authid

    @caller_authid.setter
    def caller_authid(self, value):
        assert value is None or type(value) == str
        self._caller_authid = value

    @property
    def caller_authrole(self):
        if self._caller_authrole is None and self._from_fbs:
            s = self._from_fbs.CallerAuthrole()
            if s:
                self._caller_authrole = s.decode("utf8")
        return self._caller_authrole

    @caller_authrole.setter
    def caller_authrole(self, value):
        assert value is None or type(value) == str
        self._caller_authrole = value

    # Note: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def cast(buf):
        return Call(from_fbs=message_fbs.Call.GetRootAsCall(buf, 0))

    def build(self, builder, serializer=None):
        args = self.args
        if args:
            if serializer:
                args = builder.CreateByteVector(serializer.serialize_payload(args))
            else:
                # Fallback for backwards compatibility (shouldn't happen)
                args = builder.CreateByteVector(cbor2.dumps(args))

        kwargs = self.kwargs
        if kwargs:
            if serializer:
                kwargs = builder.CreateByteVector(serializer.serialize_payload(kwargs))
            else:
                # Fallback for backwards compatibility (shouldn't happen)
                kwargs = builder.CreateByteVector(cbor2.dumps(kwargs))

        payload = self.payload
        if payload:
            payload = builder.CreateByteVector(payload)

        procedure = self.procedure
        if procedure:
            procedure = builder.CreateString(procedure)

        transaction_hash = self.transaction_hash
        if transaction_hash:
            transaction_hash = builder.CreateString(transaction_hash)

        caller_authid = self.caller_authid
        if caller_authid:
            caller_authid = builder.CreateString(caller_authid)

        caller_authrole = self.caller_authrole
        if caller_authrole:
            caller_authrole = builder.CreateString(caller_authrole)

        enc_key = self.enc_key
        if enc_key:
            enc_key = builder.CreateString(enc_key)

        # forward_for: [Principal]
        forward_for = self.forward_for
        if forward_for:
            from wamp.proto import Principal as PrincipalGen

            _forward_for = []
            for principal in forward_for:
                _session = principal.get("session", 0)
                _authid = principal.get("authid", None)
                _authrole = principal.get("authrole", "")

                if _authid:
                    _authid = builder.CreateString(_authid)
                _authrole = builder.CreateString(_authrole)

                PrincipalGen.Start(builder)
                PrincipalGen.AddSession(builder, _session)
                if _authid:
                    PrincipalGen.AddAuthid(builder, _authid)
                PrincipalGen.AddAuthrole(builder, _authrole)
                _forward_for.append(PrincipalGen.End(builder))

            message_fbs.CallGen.CallStartForwardForVector(builder, len(_forward_for))
            for principal in reversed(_forward_for):
                builder.PrependUOffsetTRelative(principal)
            forward_for = builder.EndVector()

        # build CallGen
        message_fbs.CallGen.CallStart(builder)

        if self.request:
            message_fbs.CallGen.CallAddRequest(builder, self.request)
        if procedure:
            message_fbs.CallGen.CallAddProcedure(builder, procedure)
        if args:
            message_fbs.CallGen.CallAddArgs(builder, args)
        if kwargs:
            message_fbs.CallGen.CallAddKwargs(builder, kwargs)
        if payload:
            message_fbs.CallGen.CallAddPayload(builder, payload)
        if self.enc_algo:
            # Convert string enc_algo to FlatBuffers enum value
            enc_algo_int = ENC_ALGOS_FROMSTR.get(self.enc_algo, 0)
            message_fbs.CallGen.CallAddPptScheme(builder, enc_algo_int)
        if self.enc_serializer:
            # Convert string enc_serializer to FlatBuffers enum value
            enc_serializer_int = ENC_SERS_FROMSTR.get(self.enc_serializer, 0)
            message_fbs.CallGen.CallAddPptSerializer(builder, enc_serializer_int)
        if enc_key:
            message_fbs.CallGen.CallAddPptKeyid(builder, enc_key)
        if self.timeout:
            message_fbs.CallGen.CallAddTimeout(builder, self.timeout)
        if self.receive_progress:
            message_fbs.CallGen.CallAddReceiveProgress(builder, self.receive_progress)
        if transaction_hash:
            message_fbs.CallGen.CallAddTransactionHash(builder, transaction_hash)
        if self.caller:
            message_fbs.CallGen.CallAddCaller(builder, self.caller)
        if caller_authid:
            message_fbs.CallGen.CallAddCallerAuthid(builder, caller_authid)
        if caller_authrole:
            message_fbs.CallGen.CallAddCallerAuthrole(builder, caller_authrole)
        if forward_for:
            message_fbs.CallGen.CallAddForwardFor(builder, forward_for)

        msg = message_fbs.CallGen.CallEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.CALL)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Call.MESSAGE_TYPE

        if len(wmsg) not in (4, 5, 6):
            raise ProtocolError("invalid message length {0} for CALL".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], "'request' in CALL")
        options = check_or_raise_extra(wmsg[2], "'options' in CALL")
        procedure = check_or_raise_uri(wmsg[3], "'procedure' in CALL")

        args = None
        kwargs = None
        payload = None
        enc_algo = None
        enc_key = None
        enc_serializer = None

        if len(wmsg) == 5 and type(wmsg[4]) in [str, bytes]:
            payload = wmsg[4]

            enc_algo = options.get("enc_algo", None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError(
                    "invalid value {0} for 'enc_algo' detail in CALL".format(enc_algo)
                )

            enc_key = options.get("enc_key", None)
            if enc_key and type(enc_key) != str:
                raise ProtocolError(
                    "invalid type {0} for 'enc_key' detail in CALL".format(
                        type(enc_key)
                    )
                )

            enc_serializer = options.get("enc_serializer", None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError(
                    "invalid value {0} for 'enc_serializer' detail in CALL".format(
                        enc_serializer
                    )
                )

        else:
            if len(wmsg) > 4:
                args = wmsg[4]
                if args is not None and type(args) != list:
                    raise ProtocolError(
                        "invalid type {0} for 'args' in CALL".format(type(args))
                    )

            if len(wmsg) > 5:
                kwargs = wmsg[5]
                if type(kwargs) != dict:
                    raise ProtocolError(
                        "invalid type {0} for 'kwargs' in CALL".format(type(kwargs))
                    )

        timeout = None
        receive_progress = None
        transaction_hash = None
        caller = None
        caller_authid = None
        caller_authrole = None
        forward_for = None

        if "timeout" in options:
            option_timeout = options["timeout"]
            if type(option_timeout) != int:
                raise ProtocolError(
                    "invalid type {0} for 'timeout' option in CALL".format(
                        type(option_timeout)
                    )
                )

            if option_timeout < 0:
                raise ProtocolError(
                    "invalid value {0} for 'timeout' option in CALL".format(
                        option_timeout
                    )
                )

            timeout = option_timeout

        if "receive_progress" in options:
            option_receive_progress = options["receive_progress"]
            if type(option_receive_progress) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'receive_progress' option in CALL".format(
                        type(option_receive_progress)
                    )
                )

            receive_progress = option_receive_progress

        if "transaction_hash" in options:
            option_transaction_hash = options["transaction_hash"]
            if type(option_transaction_hash) != str:
                raise ProtocolError(
                    "invalid type {0} for 'transaction_hash' detail in CALL".format(
                        type(option_transaction_hash)
                    )
                )

            transaction_hash = option_transaction_hash

        if "caller" in options:
            option_caller = options["caller"]
            if type(option_caller) != int:
                raise ProtocolError(
                    "invalid type {0} for 'caller' detail in CALL".format(
                        type(option_caller)
                    )
                )

            caller = option_caller

        if "caller_authid" in options:
            option_caller_authid = options["caller_authid"]
            if type(option_caller_authid) != str:
                raise ProtocolError(
                    "invalid type {0} for 'caller_authid' detail in CALL".format(
                        type(option_caller_authid)
                    )
                )

            caller_authid = option_caller_authid

        if "caller_authrole" in options:
            option_caller_authrole = options["caller_authrole"]
            if type(option_caller_authrole) != str:
                raise ProtocolError(
                    "invalid type {0} for 'caller_authrole' detail in CALL".format(
                        type(option_caller_authrole)
                    )
                )

            caller_authrole = option_caller_authrole

        if "forward_for" in options:
            forward_for = options["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in CALL"
                )

        obj = Call(
            request,
            procedure,
            args=args,
            kwargs=kwargs,
            payload=payload,
            timeout=timeout,
            receive_progress=receive_progress,
            transaction_hash=transaction_hash,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
            caller=caller,
            caller_authid=caller_authid,
            caller_authrole=caller_authrole,
            forward_for=forward_for,
        )

        return obj

    def marshal_options(self):
        options = {}

        if self.timeout is not None:
            options["timeout"] = self.timeout

        if self.receive_progress is not None:
            options["receive_progress"] = self.receive_progress

        if self.transaction_hash is not None:
            options["transaction_hash"] = self.transaction_hash

        if self.payload:
            if self.enc_algo is not None:
                options["enc_algo"] = self.enc_algo
            if self.enc_key is not None:
                options["enc_key"] = self.enc_key
            if self.enc_serializer is not None:
                options["enc_serializer"] = self.enc_serializer

        if self.caller is not None:
            options["caller"] = self.caller
        if self.caller_authid is not None:
            options["caller_authid"] = self.caller_authid
        if self.caller_authrole is not None:
            options["caller_authrole"] = self.caller_authrole

        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        return options

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        options = self.marshal_options()

        if self.payload:
            return [
                Call.MESSAGE_TYPE,
                self.request,
                options,
                self.procedure,
                self.payload,
            ]
        else:
            if self.kwargs:
                return [
                    Call.MESSAGE_TYPE,
                    self.request,
                    options,
                    self.procedure,
                    self.args,
                    self.kwargs,
                ]
            elif self.args:
                return [
                    Call.MESSAGE_TYPE,
                    self.request,
                    options,
                    self.procedure,
                    self.args,
                ]
            else:
                return [Call.MESSAGE_TYPE, self.request, options, self.procedure]


class Cancel(MessageWithForwardFor, Message):
    """
    A WAMP ``CANCEL`` message.

    Format: ``[CANCEL, CALL.Request|id, Options|dict]``

    See: https://wamp-proto.org/static/rfc/draft-oberstet-hybi-crossbar-wamp.html#rfc.section.14.3.4
    """

    MESSAGE_TYPE = 49
    """
    The WAMP message code for this type of message.
    """

    SKIP = "skip"
    KILL = "kill"
    KILLNOWAIT = "killnowait"

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Cancel-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_mode",  # CancelMode (enum)
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal]
    )

    def __init__(self, request=None, mode=None, forward_for=None, from_fbs=None):
        """

        :param request: The WAMP request ID of the original `CALL` to cancel.
        :type request: int

        :param mode: Specifies how to cancel the call (``"skip"``, ``"killnowait"`` or ``"kill"``).
        :type mode: str or None

        :param forward_for: When this Cancel is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert request is None or type(request) == int
        assert mode is None or type(mode) == str
        assert mode in [None, self.SKIP, self.KILLNOWAIT, self.KILL]
        assert forward_for is None or type(forward_for) == list

        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_forward_for(forward_for=forward_for)

        # Initialize Cancel-specific attributes
        self._request = request
        self._mode = mode

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.request != self.request:
            return False
        if other.mode != self.mode:
            return False
        if other.forward_for != self.forward_for:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def mode(self):
        if self._mode is None and self._from_fbs:
            mode_val = self._from_fbs.Mode()
            if mode_val == 0:
                self._mode = Cancel.SKIP
            elif mode_val == 2:
                self._mode = Cancel.KILL
            # Note: KILLNOWAIT and ABORT not in FlatBuffers enum mapping
        return self._mode

    @mode.setter
    def mode(self, value):
        assert value is None or type(value) == str
        self._mode = value

    # Note: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Cancel.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for CANCEL".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in CANCEL")
        options = check_or_raise_extra(wmsg[2], "'options' in CANCEL")

        # options
        #
        mode = None
        forward_for = None

        if "mode" in options:
            option_mode = options["mode"]
            if type(option_mode) != str:
                raise ProtocolError(
                    "invalid type {0} for 'mode' option in CANCEL".format(
                        type(option_mode)
                    )
                )

            if option_mode not in [Cancel.SKIP, Cancel.KILLNOWAIT, Cancel.KILL]:
                raise ProtocolError(
                    "invalid value '{0}' for 'mode' option in CANCEL".format(
                        option_mode
                    )
                )

            mode = option_mode

        if "forward_for" in options:
            forward_for = options["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in CANCEL"
                )

        obj = Cancel(request, mode=mode, forward_for=forward_for)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        options = {}

        if self.mode is not None:
            options["mode"] = self.mode
        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        return [Cancel.MESSAGE_TYPE, self.request, options]

    @staticmethod
    def cast(buf):
        return Cancel(from_fbs=message_fbs.Cancel.GetRootAsCancel(buf, 0))

    def build(self, builder, serializer=None):
        # Handle forward_for: [Principal]
        forward_for = self.forward_for
        if forward_for:
            from autobahn.wamp.gen.wamp.proto import Principal as PrincipalGen

            _forward_for = []
            for principal in forward_for:
                _session = principal.get("session", 0)
                _authid = principal.get("authid", None)
                _authrole = principal.get("authrole", "")

                if _authid:
                    _authid = builder.CreateString(_authid)
                _authrole = builder.CreateString(_authrole)

                PrincipalGen.Start(builder)
                PrincipalGen.AddSession(builder, _session)
                if _authid:
                    PrincipalGen.AddAuthid(builder, _authid)
                PrincipalGen.AddAuthrole(builder, _authrole)
                _forward_for.append(PrincipalGen.End(builder))

            message_fbs.CancelGen.CancelStartForwardForVector(builder, len(_forward_for))
            for principal in reversed(_forward_for):
                builder.PrependUOffsetTRelative(principal)
            forward_for = builder.EndVector()

        # Start Cancel message
        message_fbs.CancelGen.CancelStart(builder)

        if self.request:
            message_fbs.CancelGen.CancelAddRequest(builder, self.request)

        # Convert mode string to enum value
        if self.mode:
            if self.mode == Cancel.SKIP:
                mode_val = message_fbs.CancelMode.SKIP
            elif self.mode == Cancel.KILL:
                mode_val = message_fbs.CancelMode.KILL
            # Note: KILLNOWAIT not in FlatBuffers CancelMode enum
            else:
                mode_val = message_fbs.CancelMode.SKIP  # default
            message_fbs.CancelGen.CancelAddMode(builder, mode_val)

        if forward_for:
            message_fbs.CancelGen.CancelAddForwardFor(builder, forward_for)

        msg = message_fbs.CancelGen.CancelEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.CANCEL)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Result(MessageWithAppPayload, MessageWithForwardFor, Message):
    """
    A WAMP ``RESULT`` message.

    Formats:

    * ``[RESULT, CALL.Request|id, Details|dict]``
    * ``[RESULT, CALL.Request|id, Details|dict, YIELD.Arguments|list]``
    * ``[RESULT, CALL.Request|id, Details|dict, YIELD.Arguments|list, YIELD.ArgumentsKw|dict]``
    * ``[RESULT, CALL.Request|id, Details|dict, Payload|binary]``
    """

    MESSAGE_TYPE = 50
    """
    The WAMP message code for this type of message.
    """

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Result-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_progress",  # bool
        "_callee",  # uint64 (session id)
        "_callee_authid",  # string (principal)
        "_callee_authrole",  # string (principal)
        # From MessageWithAppPayload mixin
        "_args",  # [uint8] - serialized args
        "_kwargs",  # [uint8] - serialized kwargs
        "_payload",  # [uint8] - opaque payload
        "_enc_algo",  # Payload (enum) - encryption algorithm
        "_enc_key",  # [uint8] - encryption key
        "_enc_serializer",  # Serializer (enum) - payload serializer
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal] - forwarding chain
    )

    def __init__(
        self,
        request=None,
        args=None,
        kwargs=None,
        payload=None,
        progress=None,
        enc_algo=None,
        enc_key=None,
        enc_serializer=None,
        callee=None,
        callee_authid=None,
        callee_authrole=None,
        forward_for=None,
        from_fbs=None,
    ):
        """

        :param request: The request ID of the original `CALL` request.
        :type request: int

        :param args: Positional values for application-defined event payload.
           Must be serializable using any serializers in use.
        :type args: list or tuple or None

        :param kwargs: Keyword values for application-defined event payload.
           Must be serializable using any serializers in use.
        :type kwargs: dict or None

        :param payload: Alternative, transparent payload. If given, ``args`` and ``kwargs`` must be left unset.
        :type payload: bytes or None

        :param progress: If ``True``, this result is a progressive call result, and subsequent
           results (or a final error) will follow.
        :type progress: bool or None

        :param enc_algo: If using payload transparency, the encoding algorithm that was used to encode the payload.
        :type enc_algo: str or None

        :param enc_key: If using payload transparency with an encryption algorithm, the payload encryption key.
        :type enc_key: str or None

        :param enc_serializer: If using payload transparency, the payload object serializer that was used encoding the payload.
        :type enc_serializer: str or None

        :param callee: The WAMP session ID of the effective callee that responded with the result. Only filled if callee is disclosed.
        :type callee: None or int

        :param callee_authid: The WAMP authid of the responding callee. Only filled if callee is disclosed.
        :type callee_authid: None or unicode

        :param callee_authrole: The WAMP authrole of the responding callee. Only filled if callee is disclosed.
        :type callee_authrole: None or unicode

        :param forward_for: When this Result is forwarded for a client/callee (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert request is None or type(request) == int
        assert args is None or type(args) in [list, tuple, str, bytes]
        assert kwargs is None or type(kwargs) in [dict, str, bytes]
        assert payload is None or type(payload) == bytes
        assert payload is None or (
            payload is not None and args is None and kwargs is None
        )
        assert progress is None or type(progress) == bool

        assert enc_algo is None or is_valid_enc_algo(enc_algo)
        assert enc_key is None or type(enc_key) == str
        assert enc_serializer is None or is_valid_enc_serializer(enc_serializer)
        assert (enc_algo is None and enc_key is None and enc_serializer is None) or (
            payload is not None and enc_algo is not None
        )

        assert callee is None or type(callee) == int
        assert callee_authid is None or type(callee_authid) == str
        assert callee_authrole is None or type(callee_authrole) == str

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_app_payload(
            args=args,
            kwargs=kwargs,
            payload=payload,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
        )
        self._init_forward_for(forward_for=forward_for)

        # Initialize Result-specific attributes
        self._request = request
        self._progress = progress

        # effective callee that responded with the result
        self._callee = callee
        self._callee_authid = callee_authid
        self._callee_authrole = callee_authrole

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    # NOTE: args, kwargs, payload properties are provided by MessageWithAppPayload mixin

    @property
    def progress(self):
        if self._progress is None and self._from_fbs:
            progress = self._from_fbs.Progress()
            if progress:
                self._progress = progress
        return self._progress

    @progress.setter
    def progress(self, value):
        assert value is None or type(value) == bool
        self._progress = value

    @property
    def callee(self):
        if self._callee is None and self._from_fbs:
            callee = self._from_fbs.Callee()
            if callee:
                self._callee = callee
        return self._callee

    @callee.setter
    def callee(self, value):
        assert value is None or type(value) == int
        self._callee = value

    @property
    def callee_authid(self):
        if self._callee_authid is None and self._from_fbs:
            s = self._from_fbs.CalleeAuthid()
            if s:
                self._callee_authid = s.decode("utf8")
        return self._callee_authid

    @callee_authid.setter
    def callee_authid(self, value):
        assert value is None or type(value) == str
        self._callee_authid = value

    @property
    def callee_authrole(self):
        if self._callee_authrole is None and self._from_fbs:
            s = self._from_fbs.CalleeAuthrole()
            if s:
                self._callee_authrole = s.decode("utf8")
        return self._callee_authrole

    @callee_authrole.setter
    def callee_authrole(self, value):
        assert value is None or type(value) == str
        self._callee_authrole = value

    # NOTE: enc_algo, enc_key, enc_serializer properties are provided by MessageWithAppPayload mixin
    # NOTE: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def cast(buf):
        return Result(from_fbs=message_fbs.Result.GetRootAsResult(buf, 0))

    def build(self, builder, serializer=None):
        args = self.args
        if args:
            if serializer:
                args = builder.CreateByteVector(serializer.serialize_payload(args))
            else:
                args = builder.CreateByteVector(cbor2.dumps(args))

        kwargs = self.kwargs
        if kwargs:
            if serializer:
                kwargs = builder.CreateByteVector(serializer.serialize_payload(kwargs))
            else:
                kwargs = builder.CreateByteVector(cbor2.dumps(kwargs))

        payload = self.payload
        if payload:
            payload = builder.CreateByteVector(payload)

        enc_key = self.enc_key
        if enc_key:
            enc_key = builder.CreateString(enc_key)

        callee_authid = self.callee_authid
        if callee_authid:
            callee_authid = builder.CreateString(callee_authid)

        callee_authrole = self.callee_authrole
        if callee_authrole:
            callee_authrole = builder.CreateString(callee_authrole)

        # forward_for: [Principal]
        forward_for = self.forward_for
        if forward_for:
            from wamp.proto import Principal as PrincipalGen

            _forward_for = []
            for principal in forward_for:
                _session = principal.get("session", 0)
                _authid = principal.get("authid", None)
                _authrole = principal.get("authrole", "")

                if _authid:
                    _authid = builder.CreateString(_authid)
                _authrole = builder.CreateString(_authrole)

                PrincipalGen.Start(builder)
                PrincipalGen.AddSession(builder, _session)
                if _authid:
                    PrincipalGen.AddAuthid(builder, _authid)
                PrincipalGen.AddAuthrole(builder, _authrole)
                _forward_for.append(PrincipalGen.End(builder))

            message_fbs.ResultGen.ResultStartForwardForVector(
                builder, len(_forward_for)
            )
            for principal in reversed(_forward_for):
                builder.PrependUOffsetTRelative(principal)
            forward_for = builder.EndVector()

        # build ResultGen
        message_fbs.ResultGen.ResultStart(builder)

        if self.request:
            message_fbs.ResultGen.ResultAddRequest(builder, self.request)
        if args:
            message_fbs.ResultGen.ResultAddArgs(builder, args)
        if kwargs:
            message_fbs.ResultGen.ResultAddKwargs(builder, kwargs)
        if payload:
            message_fbs.ResultGen.ResultAddPayload(builder, payload)
        if self.enc_algo:
            # Convert string enc_algo to FlatBuffers enum value
            enc_algo_int = ENC_ALGOS_FROMSTR.get(self.enc_algo, 0)
            message_fbs.ResultGen.ResultAddPptScheme(builder, enc_algo_int)
        if self.enc_serializer:
            # Convert string enc_serializer to FlatBuffers enum value
            enc_serializer_int = ENC_SERS_FROMSTR.get(self.enc_serializer, 0)
            message_fbs.ResultGen.ResultAddPptSerializer(builder, enc_serializer_int)
        if enc_key:
            message_fbs.ResultGen.ResultAddPptKeyid(builder, enc_key)
        if self.progress:
            message_fbs.ResultGen.ResultAddProgress(builder, self.progress)
        if self.callee:
            message_fbs.ResultGen.ResultAddCallee(builder, self.callee)
        if callee_authid:
            message_fbs.ResultGen.ResultAddCalleeAuthid(builder, callee_authid)
        if callee_authrole:
            message_fbs.ResultGen.ResultAddCalleeAuthrole(builder, callee_authrole)
        if forward_for:
            message_fbs.ResultGen.ResultAddForwardFor(builder, forward_for)

        msg = message_fbs.ResultGen.ResultEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.RESULT)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Result.MESSAGE_TYPE

        if len(wmsg) not in (3, 4, 5):
            raise ProtocolError(
                "invalid message length {0} for RESULT".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in RESULT")
        details = check_or_raise_extra(wmsg[2], "'details' in RESULT")

        args = None
        kwargs = None
        payload = None
        progress = None
        enc_algo = None
        enc_key = None
        enc_serializer = None
        callee = None
        callee_authid = None
        callee_authrole = None
        forward_for = None

        if len(wmsg) == 4 and type(wmsg[3]) in [str, bytes]:
            payload = wmsg[3]

            enc_algo = details.get("enc_algo", None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError(
                    "invalid value {0} for 'enc_algo' detail in RESULT".format(enc_algo)
                )

            enc_key = details.get("enc_key", None)
            if enc_key and type(enc_key) != str:
                raise ProtocolError(
                    "invalid type {0} for 'enc_key' detail in RESULT".format(
                        type(enc_key)
                    )
                )

            enc_serializer = details.get("enc_serializer", None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError(
                    "invalid value {0} for 'enc_serializer' detail in RESULT".format(
                        enc_serializer
                    )
                )

        else:
            if len(wmsg) > 3:
                args = wmsg[3]
                if args is not None and type(args) != list:
                    raise ProtocolError(
                        "invalid type {0} for 'args' in RESULT".format(type(args))
                    )

            if len(wmsg) > 4:
                kwargs = wmsg[4]
                if type(kwargs) != dict:
                    raise ProtocolError(
                        "invalid type {0} for 'kwargs' in RESULT".format(type(kwargs))
                    )

        if "progress" in details:
            detail_progress = details["progress"]
            if type(detail_progress) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'progress' option in RESULT".format(
                        type(detail_progress)
                    )
                )

            progress = detail_progress

        if "callee" in details:
            detail_callee = details["callee"]
            if type(detail_callee) != int:
                raise ProtocolError(
                    "invalid type {0} for 'callee' detail in RESULT".format(
                        type(detail_callee)
                    )
                )

            callee = detail_callee

        if "callee_authid" in details:
            detail_callee_authid = details["callee_authid"]
            if type(detail_callee_authid) != str:
                raise ProtocolError(
                    "invalid type {0} for 'callee_authid' detail in RESULT".format(
                        type(detail_callee_authid)
                    )
                )

            callee_authid = detail_callee_authid

        if "callee_authrole" in details:
            detail_callee_authrole = details["callee_authrole"]
            if type(detail_callee_authrole) != str:
                raise ProtocolError(
                    "invalid type {0} for 'callee_authrole' detail in RESULT".format(
                        type(detail_callee_authrole)
                    )
                )

            callee_authrole = detail_callee_authrole

        if "forward_for" in details:
            forward_for = details["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in RESULT"
                )

        obj = Result(
            request,
            args=args,
            kwargs=kwargs,
            payload=payload,
            progress=progress,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
            callee=callee,
            callee_authid=callee_authid,
            callee_authrole=callee_authrole,
            forward_for=forward_for,
        )

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {}

        if self.progress is not None:
            details["progress"] = self.progress

        if self.callee is not None:
            details["callee"] = self.callee
        if self.callee_authid is not None:
            details["callee_authid"] = self.callee_authid
        if self.callee_authrole is not None:
            details["callee_authrole"] = self.callee_authrole
        if self.forward_for is not None:
            details["forward_for"] = self.forward_for

        if self.payload:
            if self.enc_algo is not None:
                details["enc_algo"] = self.enc_algo
            if self.enc_key is not None:
                details["enc_key"] = self.enc_key
            if self.enc_serializer is not None:
                details["enc_serializer"] = self.enc_serializer
            return [Result.MESSAGE_TYPE, self.request, details, self.payload]
        else:
            if self.kwargs:
                return [
                    Result.MESSAGE_TYPE,
                    self.request,
                    details,
                    self.args,
                    self.kwargs,
                ]
            elif self.args:
                return [Result.MESSAGE_TYPE, self.request, details, self.args]
            else:
                return [Result.MESSAGE_TYPE, self.request, details]


class Register(MessageWithForwardFor, Message):
    """
    A WAMP ``REGISTER`` message.

    Format: ``[REGISTER, Request|id, Options|dict, Procedure|uri]``
    """

    MESSAGE_TYPE = 64
    """
    The WAMP message code for this type of message.
    """

    MATCH_EXACT = "exact"
    MATCH_PREFIX = "prefix"
    MATCH_WILDCARD = "wildcard"

    INVOKE_SINGLE = "single"
    INVOKE_FIRST = "first"
    INVOKE_LAST = "last"
    INVOKE_ROUNDROBIN = "roundrobin"
    INVOKE_RANDOM = "random"

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Register-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_procedure",  # string (required, uri_pattern)
        "_match",  # Match (enum)
        "_invoke",  # InvocationPolicy (enum)
        "_concurrency",  # uint16
        "_force_reregister",  # bool
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal]
    )

    def __init__(
        self,
        request=None,
        procedure=None,
        match=None,
        invoke=None,
        concurrency=None,
        force_reregister=None,
        forward_for=None,
        from_fbs=None,
    ):
        """

        :param request: The WAMP request ID of this request.
        :type request: int

        :param procedure: The WAMP or application URI of the RPC endpoint provided.
        :type procedure: str

        :param match: The procedure matching policy to be used for the registration.
        :type match: str

        :param invoke: The procedure invocation policy to be used for the registration.
        :type invoke: str

        :param concurrency: The (maximum) concurrency to be used for the registration.
        :type concurrency: int

        :param forward_for: When this Register is forwarded over a router-to-router link,
            or via an intermediary router.
        :type forward_for: list[dict]
        """
        assert request is None or type(request) == int
        assert procedure is None or type(procedure) == str
        assert match is None or type(match) == str
        assert match is None or match in [
            Register.MATCH_EXACT,
            Register.MATCH_PREFIX,
            Register.MATCH_WILDCARD,
        ]
        assert invoke is None or type(invoke) == str
        assert invoke is None or invoke in [
            Register.INVOKE_SINGLE,
            Register.INVOKE_FIRST,
            Register.INVOKE_LAST,
            Register.INVOKE_ROUNDROBIN,
            Register.INVOKE_RANDOM,
        ]
        assert concurrency is None or (type(concurrency) == int and concurrency > 0)
        assert force_reregister in [None, True, False]
        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_forward_for(forward_for=forward_for)

        # Initialize Register-specific attributes
        self._request = request
        self._procedure = procedure
        self._match = match or Register.MATCH_EXACT
        self._invoke = invoke or Register.INVOKE_SINGLE
        self._concurrency = concurrency
        self._force_reregister = force_reregister

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.request != self.request:
            return False
        if other.procedure != self.procedure:
            return False
        if other.match != self.match:
            return False
        if other.invoke != self.invoke:
            return False
        if other.concurrency != self.concurrency:
            return False
        if other.force_reregister != self.force_reregister:
            return False
        if other.forward_for != self.forward_for:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def procedure(self):
        if self._procedure is None and self._from_fbs:
            procedure_bytes = self._from_fbs.Procedure()
            if procedure_bytes:
                self._procedure = procedure_bytes.decode("utf-8")
        return self._procedure

    @procedure.setter
    def procedure(self, value):
        assert value is None or type(value) == str
        self._procedure = value

    @property
    def match(self):
        if self._match is None and self._from_fbs:
            match_val = self._from_fbs.Match()
            if match_val == 1:
                self._match = Register.MATCH_PREFIX
            elif match_val == 2:
                self._match = Register.MATCH_WILDCARD
            else:
                self._match = Register.MATCH_EXACT
        return self._match

    @match.setter
    def match(self, value):
        assert value is None or type(value) == str
        self._match = value

    @property
    def invoke(self):
        if self._invoke is None and self._from_fbs:
            invoke_val = self._from_fbs.Invoke()
            if invoke_val == 1:
                self._invoke = Register.INVOKE_FIRST
            elif invoke_val == 2:
                self._invoke = Register.INVOKE_LAST
            elif invoke_val == 3:
                self._invoke = Register.INVOKE_ROUNDROBIN
            elif invoke_val == 4:
                self._invoke = Register.INVOKE_RANDOM
            else:
                self._invoke = Register.INVOKE_SINGLE
        return self._invoke

    @invoke.setter
    def invoke(self, value):
        assert value is None or type(value) == str
        self._invoke = value

    @property
    def concurrency(self):
        if self._concurrency is None and self._from_fbs:
            self._concurrency = self._from_fbs.Concurrency()
        return self._concurrency

    @concurrency.setter
    def concurrency(self, value):
        assert value is None or type(value) == int
        self._concurrency = value

    @property
    def force_reregister(self):
        if self._force_reregister is None and self._from_fbs:
            self._force_reregister = self._from_fbs.ForceReregister()
        return self._force_reregister

    @force_reregister.setter
    def force_reregister(self, value):
        assert value is None or type(value) == bool
        self._force_reregister = value

    # Note: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Register.MESSAGE_TYPE

        if len(wmsg) != 4:
            raise ProtocolError(
                "invalid message length {0} for REGISTER".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in REGISTER")
        options = check_or_raise_extra(wmsg[2], "'options' in REGISTER")

        match = Register.MATCH_EXACT
        invoke = Register.INVOKE_SINGLE
        concurrency = None
        force_reregister = None
        forward_for = None

        if "match" in options:
            option_match = options["match"]
            if type(option_match) != str:
                raise ProtocolError(
                    "invalid type {0} for 'match' option in REGISTER".format(
                        type(option_match)
                    )
                )

            if option_match not in [
                Register.MATCH_EXACT,
                Register.MATCH_PREFIX,
                Register.MATCH_WILDCARD,
            ]:
                raise ProtocolError(
                    "invalid value {0} for 'match' option in REGISTER".format(
                        option_match
                    )
                )

            match = option_match

        if match == Register.MATCH_EXACT:
            allow_empty_components = False
            allow_last_empty = False

        elif match == Register.MATCH_PREFIX:
            allow_empty_components = False
            allow_last_empty = True

        elif match == Register.MATCH_WILDCARD:
            allow_empty_components = True
            allow_last_empty = False

        else:
            raise Exception("logic error")

        procedure = check_or_raise_uri(
            wmsg[3],
            "'procedure' in REGISTER",
            allow_empty_components=allow_empty_components,
            allow_last_empty=allow_last_empty,
        )

        if "invoke" in options:
            option_invoke = options["invoke"]
            if type(option_invoke) != str:
                raise ProtocolError(
                    "invalid type {0} for 'invoke' option in REGISTER".format(
                        type(option_invoke)
                    )
                )

            if option_invoke not in [
                Register.INVOKE_SINGLE,
                Register.INVOKE_FIRST,
                Register.INVOKE_LAST,
                Register.INVOKE_ROUNDROBIN,
                Register.INVOKE_RANDOM,
            ]:
                raise ProtocolError(
                    "invalid value {0} for 'invoke' option in REGISTER".format(
                        option_invoke
                    )
                )

            invoke = option_invoke

        if "concurrency" in options:
            options_concurrency = options["concurrency"]
            if type(options_concurrency) != int:
                raise ProtocolError(
                    "invalid type {0} for 'concurrency' option in REGISTER".format(
                        type(options_concurrency)
                    )
                )

            if options_concurrency < 1:
                raise ProtocolError(
                    "invalid value {0} for 'concurrency' option in REGISTER".format(
                        options_concurrency
                    )
                )

            concurrency = options_concurrency

        options_reregister = options.get("force_reregister", None)
        if options_reregister not in [True, False, None]:
            raise ProtocolError(
                "invalid type {0} for 'force_reregister option in REGISTER".format(
                    type(options_reregister)
                )
            )
        if options_reregister is not None:
            force_reregister = options_reregister

        if "forward_for" in options:
            forward_for = options["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in REGISTER"
                )

        obj = Register(
            request,
            procedure,
            match=match,
            invoke=invoke,
            concurrency=concurrency,
            force_reregister=force_reregister,
            forward_for=forward_for,
        )

        return obj

    def marshal_options(self):
        options = {}

        if self.match and self.match != Register.MATCH_EXACT:
            options["match"] = self.match

        if self.invoke and self.invoke != Register.INVOKE_SINGLE:
            options["invoke"] = self.invoke

        if self.concurrency:
            options["concurrency"] = self.concurrency

        if self.force_reregister is not None:
            options["force_reregister"] = self.force_reregister

        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        return options

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [
            Register.MESSAGE_TYPE,
            self.request,
            self.marshal_options(),
            self.procedure,
        ]

    @staticmethod
    def cast(buf):
        return Register(from_fbs=message_fbs.Register.GetRootAsRegister(buf, 0))

    def build(self, builder, serializer=None):
        # Serialize procedure string
        procedure = self.procedure
        if procedure:
            procedure = builder.CreateString(procedure)

        # Start message
        message_fbs.RegisterGen.RegisterStart(builder)

        # Add fields
        session = getattr(self, 'session', None)
        if session:
            message_fbs.RegisterGen.RegisterAddSession(builder, session)
        if self.request:
            message_fbs.RegisterGen.RegisterAddRequest(builder, self.request)
        if procedure:
            message_fbs.RegisterGen.RegisterAddProcedure(builder, procedure)

        # Convert match string to enum value
        if self.match:
            if self.match == Register.MATCH_PREFIX:
                match_val = message_fbs.Match.PREFIX
            elif self.match == Register.MATCH_WILDCARD:
                match_val = message_fbs.Match.WILDCARD
            else:
                match_val = message_fbs.Match.EXACT
            message_fbs.RegisterGen.RegisterAddMatch(builder, match_val)

        # Convert invoke string to enum value
        if self.invoke:
            if self.invoke == Register.INVOKE_FIRST:
                invoke_val = message_fbs.InvocationPolicy.FIRST
            elif self.invoke == Register.INVOKE_LAST:
                invoke_val = message_fbs.InvocationPolicy.LAST
            elif self.invoke == Register.INVOKE_ROUNDROBIN:
                invoke_val = message_fbs.InvocationPolicy.ROUNDROBIN
            elif self.invoke == Register.INVOKE_RANDOM:
                invoke_val = message_fbs.InvocationPolicy.RANDOM
            else:
                invoke_val = message_fbs.InvocationPolicy.SINGLE
            message_fbs.RegisterGen.RegisterAddInvoke(builder, invoke_val)

        if self.concurrency is not None and self.concurrency > 0:
            message_fbs.RegisterGen.RegisterAddConcurrency(builder, self.concurrency)

        if self.force_reregister is not None:
            message_fbs.RegisterGen.RegisterAddForceReregister(
                builder, self.force_reregister
            )

        # End and return
        msg = message_fbs.RegisterGen.RegisterEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.REGISTER)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Registered(Message):
    """
    A WAMP ``REGISTERED`` message.

    Format: ``[REGISTERED, REGISTER.Request|id, Registration|id]``
    """

    MESSAGE_TYPE = 65
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        # uint64 (key)
        "_request",
        # uint64
        "_registration",
    )

    def __init__(self, request=None, registration=None, from_fbs=None):
        """

        :param request: The request ID of the original ``REGISTER`` request.
        :type request: int

        :param registration: The registration ID for the registered procedure (or procedure pattern).
        :type registration: int
        """
        assert request is None or type(request) == int
        assert registration is None or type(registration) == int

        Message.__init__(self, from_fbs=from_fbs)
        self._request = request
        self._registration = registration

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.request != self.request:
            return False
        if other.registration != self.registration:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def registration(self):
        if self._registration is None and self._from_fbs:
            self._registration = self._from_fbs.Registration()
        return self._registration

    @registration.setter
    def registration(self, value):
        assert value is None or type(value) == int
        self._registration = value

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Registered.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for REGISTERED".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in REGISTERED")
        registration = check_or_raise_id(wmsg[2], "'registration' in REGISTERED")

        obj = Registered(request, registration)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Registered.MESSAGE_TYPE, self.request, self.registration]

    @staticmethod
    def cast(buf):
        return Registered(from_fbs=message_fbs.Registered.GetRootAsRegistered(buf, 0))

    def build(self, builder, serializer=None):
        message_fbs.RegisteredGen.RegisteredStart(builder)

        session = getattr(self, 'session', None)
        if session:
            message_fbs.RegisteredGen.RegisteredAddSession(builder, session)
        if self.request:
            message_fbs.RegisteredGen.RegisteredAddRequest(builder, self.request)
        if self.registration:
            message_fbs.RegisteredGen.RegisteredAddRegistration(
                builder, self.registration
            )

        msg = message_fbs.RegisteredGen.RegisteredEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.REGISTERED)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Unregister(MessageWithForwardFor, Message):
    """
    A WAMP `UNREGISTER` message.

    Formats:

    * ``[UNREGISTER, Request|id, REGISTERED.Registration|id]``
    * ``[UNREGISTER, Request|id, REGISTERED.Registration|id, Options|dict]``
    """

    MESSAGE_TYPE = 66
    """
    The WAMP message code for this type of message.
    """

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Unregister-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_registration",  # uint64
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal]
    )

    def __init__(
        self, request=None, registration=None, forward_for=None, from_fbs=None
    ):
        """

        :param request: The WAMP request ID of this request.
        :type request: int

        :param registration: The registration ID for the registration to unregister.
        :type registration: int

        :param forward_for: When this Unregister is forwarded over a router-to-router link,
            or via an intermediary router.
        :type forward_for: list[dict]
        """
        assert request is None or type(request) == int
        assert registration is None or type(registration) == int

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_forward_for(forward_for=forward_for)

        # Initialize Unregister-specific attributes
        self._request = request
        self._registration = registration

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def registration(self):
        if self._registration is None and self._from_fbs:
            self._registration = self._from_fbs.Registration()
        return self._registration

    @registration.setter
    def registration(self, value):
        assert value is None or type(value) == int
        self._registration = value

    # Note: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Unregister.MESSAGE_TYPE

        if len(wmsg) not in [3, 4]:
            raise ProtocolError(
                "invalid message length {0} for WAMP UNREGISTER".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in UNREGISTER")
        registration = check_or_raise_id(wmsg[2], "'registration' in UNREGISTER")

        options = None
        if len(wmsg) > 3:
            options = check_or_raise_extra(wmsg[3], "'options' in UNREGISTER")

        forward_for = None
        if options and "forward_for" in options:
            forward_for = options["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in UNREGISTER"
                )

        obj = Unregister(request, registration, forward_for=forward_for)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        if self.forward_for:
            options = {
                "forward_for": self.forward_for,
            }
            return [Unregister.MESSAGE_TYPE, self.request, self.registration, options]
        else:
            return [Unregister.MESSAGE_TYPE, self.request, self.registration]

    @staticmethod
    def cast(buf):
        return Unregister(from_fbs=message_fbs.Unregister.GetRootAsUnregister(buf, 0))

    def build(self, builder, serializer=None):
        # Start Unregister message
        message_fbs.UnregisterGen.UnregisterStart(builder)

        if self.request:
            message_fbs.UnregisterGen.UnregisterAddRequest(builder, self.request)
        if self.registration:
            message_fbs.UnregisterGen.UnregisterAddRegistration(
                builder, self.registration
            )

        # Note: forward_for not supported in current FlatBuffers schema

        msg = message_fbs.UnregisterGen.UnregisterEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(
            builder, message_fbs.MessageType.UNREGISTER
        )
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Unregistered(Message):
    """
    A WAMP ``UNREGISTERED`` message.

    Formats:

    * ``[UNREGISTERED, UNREGISTER.Request|id]``
    * ``[UNREGISTERED, UNREGISTER.Request|id, Details|dict]``
    """

    MESSAGE_TYPE = 67
    """
    The WAMP message code for this type of message.
    """

    __slots__ = (
        # uint64 (key)
        "_request",
        # uint64
        "_registration",
        # string (uri)
        "_reason",
    )

    def __init__(self, request=None, registration=None, reason=None, from_fbs=None):
        """

        :param request: The request ID of the original ``UNREGISTER`` request.
        :type request: int

        :param registration: If unregister was actively triggered by router, the ID
            of the registration revoked.
        :type registration: int or None

        :param reason: The reason (an URI) for revocation.
        :type reason: str or None.
        """
        assert request is None or type(request) == int
        assert registration is None or type(registration) == int
        assert reason is None or type(reason) == str
        if request is not None and registration is not None:
            assert (request != 0 and registration is None) or (
                request == 0 and registration != 0
            )

        Message.__init__(self, from_fbs=from_fbs)
        self._request = request
        self._registration = registration
        self._reason = reason

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.request != self.request:
            return False
        if other.registration != self.registration:
            return False
        if other.reason != self.reason:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def registration(self):
        if self._registration is None and self._from_fbs:
            self._registration = self._from_fbs.Registration()
        return self._registration

    @registration.setter
    def registration(self, value):
        assert value is None or type(value) == int
        self._registration = value

    @property
    def reason(self):
        if self._reason is None and self._from_fbs:
            reason_bytes = self._from_fbs.Reason()
            if reason_bytes:
                self._reason = reason_bytes.decode("utf-8")
        return self._reason

    @reason.setter
    def reason(self, value):
        assert value is None or type(value) == str
        self._reason = value

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Unregistered.MESSAGE_TYPE

        if len(wmsg) not in [2, 3]:
            raise ProtocolError(
                "invalid message length {0} for UNREGISTERED".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in UNREGISTERED")

        registration = None
        reason = None

        if len(wmsg) > 2:
            details = check_or_raise_extra(wmsg[2], "'details' in UNREGISTERED")

            if "registration" in details:
                details_registration = details["registration"]
                if type(details_registration) != int:
                    raise ProtocolError(
                        "invalid type {0} for 'registration' detail in UNREGISTERED".format(
                            type(details_registration)
                        )
                    )
                registration = details_registration

            if "reason" in details:
                reason = check_or_raise_uri(
                    details["reason"], "'reason' in UNREGISTERED"
                )

        obj = Unregistered(request, registration, reason)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        if self.reason is not None or self.registration is not None:
            details = {}
            if self.reason is not None:
                details["reason"] = self.reason
            if self.registration is not None:
                details["registration"] = self.registration
            return [Unregistered.MESSAGE_TYPE, self.request, details]
        else:
            return [Unregistered.MESSAGE_TYPE, self.request]

    @staticmethod
    def cast(buf):
        return Unregistered(
            from_fbs=message_fbs.Unregistered.GetRootAsUnregistered(buf, 0)
        )

    def build(self, builder, serializer=None):
        # Serialize reason string if present
        reason = self.reason
        if reason:
            reason = builder.CreateString(reason)

        # Start message
        message_fbs.UnregisteredGen.UnregisteredStart(builder)

        # Add fields
        session = getattr(self, 'session', None)
        if session:
            message_fbs.UnregisteredGen.UnregisteredAddSession(builder, session)
        if self.request:
            message_fbs.UnregisteredGen.UnregisteredAddRequest(builder, self.request)
        if self.registration:
            message_fbs.UnregisteredGen.UnregisteredAddRegistration(
                builder, self.registration
            )
        if reason:
            message_fbs.UnregisteredGen.UnregisteredAddReason(builder, reason)

        # End and return
        msg = message_fbs.UnregisteredGen.UnregisteredEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.UNREGISTERED)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Invocation(MessageWithAppPayload, MessageWithForwardFor, Message):
    """
    A WAMP ``INVOCATION`` message.

    Formats:

    * ``[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict]``
    * ``[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, CALL.Arguments|list]``
    * ``[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, CALL.Arguments|list, CALL.ArgumentsKw|dict]``
    * ``[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, Payload|binary]``
    """

    MESSAGE_TYPE = 68
    """
    The WAMP message code for this type of message.
    """

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Invocation-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_registration",  # uint64 (key)
        "_timeout",  # uint32
        "_receive_progress",  # bool
        "_caller",  # uint64 (session id)
        "_caller_authid",  # string (principal)
        "_caller_authrole",  # string (principal)
        "_procedure",  # string (uri)
        "_transaction_hash",  # string
        # From MessageWithAppPayload mixin
        "_args",  # [uint8] - serialized args
        "_kwargs",  # [uint8] - serialized kwargs
        "_payload",  # [uint8] - opaque payload
        "_enc_algo",  # Payload (enum) - encryption algorithm
        "_enc_key",  # [uint8] - encryption key
        "_enc_serializer",  # Serializer (enum) - payload serializer
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal] - forwarding chain
    )

    def __init__(
        self,
        request=None,
        registration=None,
        args=None,
        kwargs=None,
        payload=None,
        timeout=None,
        receive_progress=None,
        caller=None,
        caller_authid=None,
        caller_authrole=None,
        procedure=None,
        transaction_hash=None,
        enc_algo=None,
        enc_key=None,
        enc_serializer=None,
        forward_for=None,
        from_fbs=None,
    ):
        """

        :param request: The WAMP request ID of this request.
        :type request: int

        :param registration: The registration ID of the endpoint to be invoked.
        :type registration: int

        :param args: Positional values for application-defined event payload.
           Must be serializable using any serializers in use.
        :type args: list or tuple or None

        :param kwargs: Keyword values for application-defined event payload.
           Must be serializable using any serializers in use.
        :type kwargs: dict or None

        :param payload: Alternative, transparent payload. If given, ``args`` and ``kwargs`` must be left unset.
        :type payload: bytes or None

        :param timeout: If present, let the callee automatically cancels
           the invocation after this ms.
        :type timeout: int or None

        :param receive_progress: Indicates if the callee should produce progressive results.
        :type receive_progress: bool or None

        :param caller: The WAMP session ID of the caller. Only filled if caller is disclosed.
        :type caller: None or int

        :param caller_authid: The WAMP authid of the caller. Only filled if caller is disclosed.
        :type caller_authid: None or unicode

        :param caller_authrole: The WAMP authrole of the caller. Only filled if caller is disclosed.
        :type caller_authrole: None or unicode

        :param procedure: For pattern-based registrations, the invocation MUST include the actual procedure being called.
        :type procedure: str or None

        :param transaction_hash: An application provided transaction hash for the originating call, which may
            be used in the router to throttle or deduplicate the calls on the procedure. See the discussion
            `here <https://github.com/wamp-proto/wamp-proto/issues/391#issuecomment-998577967>`__.
        :type transaction_hash: str

        :param enc_algo: If using payload transparency, the encoding algorithm that was used to encode the payload.
        :type enc_algo: str or None

        :param enc_key: If using payload transparency with an encryption algorithm, the payload encryption key.
        :type enc_key: str or None

        :param enc_serializer: If using payload transparency, the payload object serializer that was used encoding the payload.
        :type enc_serializer: str or None

        :param forward_for: When this Call is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert request is None or type(request) == int
        assert registration is None or type(registration) == int
        assert args is None or type(args) in [list, tuple, str, bytes]
        assert kwargs is None or type(kwargs) in [dict, str, bytes]
        assert payload is None or type(payload) == bytes
        assert payload is None or (
            payload is not None and args is None and kwargs is None
        )
        assert timeout is None or type(timeout) == int
        assert receive_progress is None or type(receive_progress) == bool
        assert caller is None or type(caller) == int
        assert caller_authid is None or type(caller_authid) == str
        assert caller_authrole is None or type(caller_authrole) == str
        assert procedure is None or type(procedure) == str
        assert transaction_hash is None or type(transaction_hash) == str
        assert enc_algo is None or is_valid_enc_algo(enc_algo)
        assert enc_key is None or type(enc_key) == str
        assert enc_serializer is None or is_valid_enc_serializer(enc_serializer)
        assert (enc_algo is None and enc_key is None and enc_serializer is None) or (
            payload is not None and enc_algo is not None
        )

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_app_payload(
            args=args,
            kwargs=kwargs,
            payload=payload,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
        )
        self._init_forward_for(forward_for=forward_for)

        # Initialize Invocation-specific attributes
        self._request = request
        self._registration = registration
        self._timeout = timeout
        self._receive_progress = receive_progress
        self._caller = caller
        self._caller_authid = caller_authid
        self._caller_authrole = caller_authrole
        self._procedure = procedure
        self._transaction_hash = transaction_hash

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def registration(self):
        if self._registration is None and self._from_fbs:
            self._registration = self._from_fbs.Registration()
        return self._registration

    @registration.setter
    def registration(self, value):
        assert value is None or type(value) == int
        self._registration = value

    # NOTE: args, kwargs, payload properties are provided by MessageWithAppPayload mixin

    @property
    def timeout(self):
        if self._timeout is None and self._from_fbs:
            timeout = self._from_fbs.Timeout()
            if timeout:
                self._timeout = timeout
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        assert value is None or type(value) == int
        self._timeout = value

    @property
    def receive_progress(self):
        if self._receive_progress is None and self._from_fbs:
            receive_progress = self._from_fbs.ReceiveProgress()
            if receive_progress:
                self._receive_progress = receive_progress
        return self._receive_progress

    @receive_progress.setter
    def receive_progress(self, value):
        assert value is None or type(value) == bool
        self._receive_progress = value

    @property
    def caller(self):
        if self._caller is None and self._from_fbs:
            caller = self._from_fbs.Caller()
            if caller:
                self._caller = caller
        return self._caller

    @caller.setter
    def caller(self, value):
        assert value is None or type(value) == int
        self._caller = value

    @property
    def caller_authid(self):
        if self._caller_authid is None and self._from_fbs:
            s = self._from_fbs.CallerAuthid()
            if s:
                self._caller_authid = s.decode("utf8")
        return self._caller_authid

    @caller_authid.setter
    def caller_authid(self, value):
        assert value is None or type(value) == str
        self._caller_authid = value

    @property
    def caller_authrole(self):
        if self._caller_authrole is None and self._from_fbs:
            s = self._from_fbs.CallerAuthrole()
            if s:
                self._caller_authrole = s.decode("utf8")
        return self._caller_authrole

    @caller_authrole.setter
    def caller_authrole(self, value):
        assert value is None or type(value) == str
        self._caller_authrole = value

    @property
    def procedure(self):
        if self._procedure is None and self._from_fbs:
            s = self._from_fbs.Procedure()
            if s:
                self._procedure = s.decode("utf8")
        return self._procedure

    @procedure.setter
    def procedure(self, value):
        assert value is None or type(value) == str
        self._procedure = value

    @property
    def transaction_hash(self):
        if self._transaction_hash is None and self._from_fbs:
            s = self._from_fbs.TransactionHash()
            if s:
                self._transaction_hash = s.decode("utf8")
        return self._transaction_hash

    @transaction_hash.setter
    def transaction_hash(self, value):
        assert value is None or type(value) == str
        self._transaction_hash = value

    # NOTE: enc_algo, enc_key, enc_serializer properties are provided by MessageWithAppPayload mixin
    # NOTE: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def cast(buf):
        return Invocation(from_fbs=message_fbs.Invocation.GetRootAsInvocation(buf, 0))

    def build(self, builder, serializer=None):
        args = self.args
        if args:
            if serializer:
                args = builder.CreateByteVector(serializer.serialize_payload(args))
            else:
                args = builder.CreateByteVector(cbor2.dumps(args))

        kwargs = self.kwargs
        if kwargs:
            if serializer:
                kwargs = builder.CreateByteVector(serializer.serialize_payload(kwargs))
            else:
                kwargs = builder.CreateByteVector(cbor2.dumps(kwargs))

        payload = self.payload
        if payload:
            payload = builder.CreateByteVector(payload)

        procedure = self.procedure
        if procedure:
            procedure = builder.CreateString(procedure)

        transaction_hash = self.transaction_hash
        if transaction_hash:
            transaction_hash = builder.CreateString(transaction_hash)

        caller_authid = self.caller_authid
        if caller_authid:
            caller_authid = builder.CreateString(caller_authid)

        caller_authrole = self.caller_authrole
        if caller_authrole:
            caller_authrole = builder.CreateString(caller_authrole)

        enc_key = self.enc_key
        if enc_key:
            enc_key = builder.CreateString(enc_key)

        # forward_for: [Principal]
        forward_for = self.forward_for
        if forward_for:
            from wamp.proto import Principal as PrincipalGen

            _forward_for = []
            for principal in forward_for:
                _session = principal.get("session", 0)
                _authid = principal.get("authid", None)
                _authrole = principal.get("authrole", "")

                if _authid:
                    _authid = builder.CreateString(_authid)
                _authrole = builder.CreateString(_authrole)

                PrincipalGen.Start(builder)
                PrincipalGen.AddSession(builder, _session)
                if _authid:
                    PrincipalGen.AddAuthid(builder, _authid)
                PrincipalGen.AddAuthrole(builder, _authrole)
                _forward_for.append(PrincipalGen.End(builder))

            message_fbs.InvocationGen.InvocationStartForwardForVector(
                builder, len(_forward_for)
            )
            for principal in reversed(_forward_for):
                builder.PrependUOffsetTRelative(principal)
            forward_for = builder.EndVector()

        # build InvocationGen
        message_fbs.InvocationGen.InvocationStart(builder)

        if self.request:
            message_fbs.InvocationGen.InvocationAddRequest(builder, self.request)
        if self.registration:
            message_fbs.InvocationGen.InvocationAddRegistration(
                builder, self.registration
            )
        if args:
            message_fbs.InvocationGen.InvocationAddArgs(builder, args)
        if kwargs:
            message_fbs.InvocationGen.InvocationAddKwargs(builder, kwargs)
        if payload:
            message_fbs.InvocationGen.InvocationAddPayload(builder, payload)
        if self.timeout:
            message_fbs.InvocationGen.InvocationAddTimeout(builder, self.timeout)
        if self.receive_progress:
            message_fbs.InvocationGen.InvocationAddReceiveProgress(
                builder, self.receive_progress
            )
        if self.caller:
            message_fbs.InvocationGen.InvocationAddCaller(builder, self.caller)
        if caller_authid:
            message_fbs.InvocationGen.InvocationAddCallerAuthid(builder, caller_authid)
        if caller_authrole:
            message_fbs.InvocationGen.InvocationAddCallerAuthrole(
                builder, caller_authrole
            )
        if procedure:
            message_fbs.InvocationGen.InvocationAddProcedure(builder, procedure)
        if self.enc_algo:
            # Convert string enc_algo to FlatBuffers enum value
            enc_algo_int = ENC_ALGOS_FROMSTR.get(self.enc_algo, 0)
            message_fbs.InvocationGen.InvocationAddPptScheme(builder, enc_algo_int)
        if self.enc_serializer:
            # Convert string enc_serializer to FlatBuffers enum value
            enc_serializer_int = ENC_SERS_FROMSTR.get(self.enc_serializer, 0)
            message_fbs.InvocationGen.InvocationAddPptSerializer(
                builder, enc_serializer_int
            )
        if enc_key:
            message_fbs.InvocationGen.InvocationAddPptKeyid(builder, enc_key)
        if transaction_hash:
            message_fbs.InvocationGen.InvocationAddTransactionHash(
                builder, transaction_hash
            )
        if forward_for:
            message_fbs.InvocationGen.InvocationAddForwardFor(builder, forward_for)

        msg = message_fbs.InvocationGen.InvocationEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.INVOCATION)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Invocation.MESSAGE_TYPE

        if len(wmsg) not in (4, 5, 6):
            raise ProtocolError(
                "invalid message length {0} for INVOCATION".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in INVOCATION")
        registration = check_or_raise_id(wmsg[2], "'registration' in INVOCATION")
        details = check_or_raise_extra(wmsg[3], "'details' in INVOCATION")

        args = None
        kwargs = None
        payload = None
        enc_algo = None
        enc_key = None
        enc_serializer = None

        if len(wmsg) == 5 and type(wmsg[4]) == bytes:
            payload = wmsg[4]

            enc_algo = details.get("enc_algo", None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError(
                    "invalid value {0} for 'enc_algo' detail in INVOCATION".format(
                        enc_algo
                    )
                )

            enc_key = details.get("enc_key", None)
            if enc_key and type(enc_key) != str:
                raise ProtocolError(
                    "invalid type {0} for 'enc_key' detail in INVOCATION".format(
                        type(enc_key)
                    )
                )

            enc_serializer = details.get("enc_serializer", None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError(
                    "invalid value {0} for 'enc_serializer' detail in INVOCATION".format(
                        enc_serializer
                    )
                )

        else:
            if len(wmsg) > 4:
                args = wmsg[4]
                if args is not None and type(args) != list:
                    raise ProtocolError(
                        "invalid type {0} for 'args' in INVOCATION".format(type(args))
                    )

            if len(wmsg) > 5:
                kwargs = wmsg[5]
                if type(kwargs) != dict:
                    raise ProtocolError(
                        "invalid type {0} for 'kwargs' in INVOCATION".format(
                            type(kwargs)
                        )
                    )

        timeout = None
        receive_progress = None
        caller = None
        caller_authid = None
        caller_authrole = None
        procedure = None
        transaction_hash = None
        forward_for = None

        if "timeout" in details:
            detail_timeout = details["timeout"]
            if type(detail_timeout) != int:
                raise ProtocolError(
                    "invalid type {0} for 'timeout' detail in INVOCATION".format(
                        type(detail_timeout)
                    )
                )

            if detail_timeout < 0:
                raise ProtocolError(
                    "invalid value {0} for 'timeout' detail in INVOCATION".format(
                        detail_timeout
                    )
                )

            timeout = detail_timeout

        if "receive_progress" in details:
            detail_receive_progress = details["receive_progress"]
            if type(detail_receive_progress) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'receive_progress' detail in INVOCATION".format(
                        type(detail_receive_progress)
                    )
                )

            receive_progress = detail_receive_progress

        if "caller" in details:
            detail_caller = details["caller"]
            if type(detail_caller) != int:
                raise ProtocolError(
                    "invalid type {0} for 'caller' detail in INVOCATION".format(
                        type(detail_caller)
                    )
                )

            caller = detail_caller

        if "caller_authid" in details:
            detail_caller_authid = details["caller_authid"]
            if type(detail_caller_authid) != str:
                raise ProtocolError(
                    "invalid type {0} for 'caller_authid' detail in INVOCATION".format(
                        type(detail_caller_authid)
                    )
                )

            caller_authid = detail_caller_authid

        if "caller_authrole" in details:
            detail_caller_authrole = details["caller_authrole"]
            if type(detail_caller_authrole) != str:
                raise ProtocolError(
                    "invalid type {0} for 'caller_authrole' detail in INVOCATION".format(
                        type(detail_caller_authrole)
                    )
                )

            caller_authrole = detail_caller_authrole

        if "procedure" in details:
            detail_procedure = details["procedure"]
            if type(detail_procedure) != str:
                raise ProtocolError(
                    "invalid type {0} for 'procedure' detail in INVOCATION".format(
                        type(detail_procedure)
                    )
                )

            procedure = detail_procedure

        if "transaction_hash" in details:
            detail_transaction_hash = details["transaction_hash"]
            if type(detail_transaction_hash) != str:
                raise ProtocolError(
                    "invalid type {0} for 'transaction_hash' detail in EVENT".format(
                        type(detail_transaction_hash)
                    )
                )

            transaction_hash = detail_transaction_hash

        if "forward_for" in details:
            forward_for = details["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in INVOCATION"
                )

        obj = Invocation(
            request,
            registration,
            args=args,
            kwargs=kwargs,
            payload=payload,
            timeout=timeout,
            receive_progress=receive_progress,
            caller=caller,
            caller_authid=caller_authid,
            caller_authrole=caller_authrole,
            procedure=procedure,
            transaction_hash=transaction_hash,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
            forward_for=forward_for,
        )

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        options = {}

        if self.timeout is not None:
            options["timeout"] = self.timeout

        if self.receive_progress is not None:
            options["receive_progress"] = self.receive_progress

        if self.caller is not None:
            options["caller"] = self.caller

        if self.caller_authid is not None:
            options["caller_authid"] = self.caller_authid

        if self.caller_authrole is not None:
            options["caller_authrole"] = self.caller_authrole

        if self.procedure is not None:
            options["procedure"] = self.procedure

        if self.transaction_hash is not None:
            options["transaction_hash"] = self.transaction_hash

        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        if self.payload:
            if self.enc_algo is not None:
                options["enc_algo"] = self.enc_algo
            if self.enc_key is not None:
                options["enc_key"] = self.enc_key
            if self.enc_serializer is not None:
                options["enc_serializer"] = self.enc_serializer
            return [
                Invocation.MESSAGE_TYPE,
                self.request,
                self.registration,
                options,
                self.payload,
            ]
        else:
            if self.kwargs:
                return [
                    Invocation.MESSAGE_TYPE,
                    self.request,
                    self.registration,
                    options,
                    self.args,
                    self.kwargs,
                ]
            elif self.args:
                return [
                    Invocation.MESSAGE_TYPE,
                    self.request,
                    self.registration,
                    options,
                    self.args,
                ]
            else:
                return [
                    Invocation.MESSAGE_TYPE,
                    self.request,
                    self.registration,
                    options,
                ]


class Interrupt(MessageWithForwardFor, Message):
    """
    A WAMP ``INTERRUPT`` message.

    Format: ``[INTERRUPT, INVOCATION.Request|id, Options|dict]``

    See: https://wamp-proto.org/static/rfc/draft-oberstet-hybi-crossbar-wamp.html#rfc.section.14.3.4
    """

    MESSAGE_TYPE = 69
    """
    The WAMP message code for this type of message.
    """

    KILL = "kill"
    KILLNOWAIT = "killnowait"

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Interrupt-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_mode",  # CancelMode (enum)
        "_reason",  # string (uri)
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal]
    )

    def __init__(
        self, request=None, mode=None, reason=None, forward_for=None, from_fbs=None
    ):
        """

        :param request: The WAMP request ID of the original ``INVOCATION`` to interrupt.
        :type request: int

        :param mode: Specifies how to interrupt the invocation (``"killnowait"`` or ``"kill"``).
            With ``"kill"``, the router will wait for the callee to return an ERROR before
            proceeding (sending back an ERROR to the original caller). With ``"killnowait"`` the
            router will immediately proceed (on the caller side returning an ERROR) - but still
            expects the callee to send an ERROR to conclude the message exchange for the inflight
            call.
        :type mode: str or None

        :param reason: The reason (an URI) for the invocation interrupt, eg actively
            triggered by the caller (``"wamp.error.canceled"`` - ApplicationError.CANCELED) or
            passively because of timeout (``"wamp.error.timeout"`` - ApplicationError.TIMEOUT).
        :type reason: str or None.

        :param forward_for: When this Call is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert request is None or type(request) == int
        assert mode is None or type(mode) == str
        assert mode is None or mode in [self.KILL, self.KILLNOWAIT]
        assert reason is None or type(reason) == str

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_forward_for(forward_for=forward_for)

        # Initialize Interrupt-specific attributes
        self._request = request
        self._mode = mode
        self._reason = reason

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if not Message.__eq__(self, other):
            return False
        if other.request != self.request:
            return False
        if other.mode != self.mode:
            return False
        if other.reason != self.reason:
            return False
        if other.forward_for != self.forward_for:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    @property
    def mode(self):
        if self._mode is None and self._from_fbs:
            mode_val = self._from_fbs.Mode()
            # Mode enum: 0=SKIP, 1=ABORT, 2=KILL (but Interrupt only uses KILL/KILLNOWAIT)
            if mode_val == 2:
                self._mode = Interrupt.KILL
            # Note: KILLNOWAIT not in FlatBuffers enum
        return self._mode

    @mode.setter
    def mode(self, value):
        assert value is None or type(value) == str
        self._mode = value

    @property
    def reason(self):
        if self._reason is None and self._from_fbs:
            reason_bytes = self._from_fbs.Reason()
            if reason_bytes:
                self._reason = reason_bytes.decode("utf-8")
        return self._reason

    @reason.setter
    def reason(self, value):
        assert value is None or type(value) == str
        self._reason = value

    # Note: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Interrupt.MESSAGE_TYPE

        if len(wmsg) != 3:
            raise ProtocolError(
                "invalid message length {0} for INTERRUPT".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in INTERRUPT")
        options = check_or_raise_extra(wmsg[2], "'options' in INTERRUPT")

        # options
        #
        mode = None
        reason = None
        forward_for = None

        if "mode" in options:
            option_mode = options["mode"]
            if type(option_mode) != str:
                raise ProtocolError(
                    "invalid type {0} for 'mode' option in INTERRUPT".format(
                        type(option_mode)
                    )
                )

            if option_mode not in [Interrupt.KILL, Interrupt.KILLNOWAIT]:
                raise ProtocolError(
                    "invalid value '{0}' for 'mode' option in INTERRUPT".format(
                        option_mode
                    )
                )

            mode = option_mode

        if "reason" in options:
            reason = check_or_raise_uri(options["reason"], '"reason" in INTERRUPT')

        if "forward_for" in options:
            forward_for = options["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in INTERRUPT"
                )

        obj = Interrupt(request, mode=mode, reason=reason, forward_for=forward_for)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        options = {}

        if self.mode is not None:
            options["mode"] = self.mode

        if self.reason is not None:
            options["reason"] = self.reason

        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        return [Interrupt.MESSAGE_TYPE, self.request, options]

    @staticmethod
    def cast(buf):
        return Interrupt(from_fbs=message_fbs.Interrupt.GetRootAsInterrupt(buf, 0))

    def build(self, builder, serializer=None):
        # Serialize reason string if present
        reason = self.reason
        if reason:
            reason = builder.CreateString(reason)

        # Handle forward_for: [Principal]
        forward_for = self.forward_for
        if forward_for:
            from autobahn.wamp.gen.wamp.proto import Principal as PrincipalGen

            _forward_for = []
            for principal in forward_for:
                _session = principal.get("session", 0)
                _authid = principal.get("authid", None)
                _authrole = principal.get("authrole", "")

                if _authid:
                    _authid = builder.CreateString(_authid)
                _authrole = builder.CreateString(_authrole)

                PrincipalGen.Start(builder)
                PrincipalGen.AddSession(builder, _session)
                if _authid:
                    PrincipalGen.AddAuthid(builder, _authid)
                PrincipalGen.AddAuthrole(builder, _authrole)
                _forward_for.append(PrincipalGen.End(builder))

            message_fbs.InterruptGen.InterruptStartForwardForVector(
                builder, len(_forward_for)
            )
            for principal in reversed(_forward_for):
                builder.PrependUOffsetTRelative(principal)
            forward_for = builder.EndVector()

        # Start message
        message_fbs.InterruptGen.InterruptStart(builder)

        # Add fields
        if self.request:
            message_fbs.InterruptGen.InterruptAddRequest(builder, self.request)

        # Convert mode string to enum value
        if self.mode:
            if self.mode == Interrupt.KILL:
                mode_val = message_fbs.CancelMode.KILL  # Same enum as Cancel
            # Note: KILLNOWAIT not in FlatBuffers CancelMode enum
            else:
                mode_val = message_fbs.CancelMode.KILL  # default to KILL
            message_fbs.InterruptGen.InterruptAddMode(builder, mode_val)

        if reason:
            message_fbs.InterruptGen.InterruptAddReason(builder, reason)

        if forward_for:
            message_fbs.InterruptGen.InterruptAddForwardFor(builder, forward_for)

        msg = message_fbs.InterruptGen.InterruptEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.INTERRUPT)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg


class Yield(MessageWithAppPayload, MessageWithForwardFor, Message):
    """
    A WAMP ``YIELD`` message.

    Formats:

    * ``[YIELD, INVOCATION.Request|id, Options|dict]``
    * ``[YIELD, INVOCATION.Request|id, Options|dict, Arguments|list]``
    * ``[YIELD, INVOCATION.Request|id, Options|dict, Arguments|list, ArgumentsKw|dict]``
    * ``[YIELD, INVOCATION.Request|id, Options|dict, Payload|binary]``
    """

    MESSAGE_TYPE = 70
    """
    The WAMP message code for this type of message.
    """

    # Note: Slots from Message base class (_from_fbs) are inherited, not redefined here
    __slots__ = (
        # Yield-specific slots (FlatBuffers schema types in comments)
        "_request",  # uint64 (key)
        "_progress",  # bool
        "_callee",  # uint64 (session id)
        "_callee_authid",  # string (principal)
        "_callee_authrole",  # string (principal)
        # From MessageWithAppPayload mixin
        "_args",  # [uint8] - serialized args
        "_kwargs",  # [uint8] - serialized kwargs
        "_payload",  # [uint8] - opaque payload
        "_enc_algo",  # Payload (enum) - encryption algorithm
        "_enc_key",  # [uint8] - encryption key
        "_enc_serializer",  # Serializer (enum) - payload serializer
        # From MessageWithForwardFor mixin
        "_forward_for",  # [Principal] - forwarding chain
    )

    def __init__(
        self,
        request=None,
        args=None,
        kwargs=None,
        payload=None,
        progress=None,
        enc_algo=None,
        enc_key=None,
        enc_serializer=None,
        callee=None,
        callee_authid=None,
        callee_authrole=None,
        forward_for=None,
        from_fbs=None,
    ):
        """

        :param request: The WAMP request ID of the original call.
        :type request: int

        :param args: Positional values for application-defined event payload.
           Must be serializable using any serializers in use.
        :type args: list or tuple or None

        :param kwargs: Keyword values for application-defined event payload.
           Must be serializable using any serializers in use.
        :type kwargs: dict or None

        :param payload: Alternative, transparent payload. If given, ``args`` and ``kwargs`` must be left unset.
        :type payload: bytes or None

        :param progress: If ``True``, this result is a progressive invocation result, and subsequent
           results (or a final error) will follow.
        :type progress: bool or None

        :param enc_algo: If using payload transparency, the encoding algorithm that was used to encode the payload.
        :type enc_algo: str or None

        :param enc_key: If using payload transparency with an encryption algorithm, the payload encryption key.
        :type enc_key: str or None

        :param enc_serializer: If using payload transparency, the payload object serializer that was used encoding the payload.
        :type enc_serializer: str or None

        :param callee: The WAMP session ID of the effective callee that responded with the error. Only filled if callee is disclosed.
        :type callee: None or int

        :param callee_authid: The WAMP authid of the responding callee. Only filled if callee is disclosed.
        :type callee_authid: None or unicode

        :param callee_authrole: The WAMP authrole of the responding callee. Only filled if callee is disclosed.
        :type callee_authrole: None or unicode

        :param forward_for: When this Call is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert request is None or type(request) == int
        assert args is None or type(args) in [list, tuple, str, bytes]
        assert kwargs is None or type(kwargs) in [dict, str, bytes]
        assert payload is None or type(payload) == bytes
        assert payload is None or (
            payload is not None and args is None and kwargs is None
        )
        assert progress is None or type(progress) == bool
        assert enc_algo is None or is_valid_enc_algo(enc_algo)
        assert (enc_algo is None and enc_key is None and enc_serializer is None) or (
            payload is not None and enc_algo is not None
        )
        assert enc_key is None or type(enc_key) == str
        assert enc_serializer is None or is_valid_enc_serializer(enc_serializer)

        assert callee is None or type(callee) == int
        assert callee_authid is None or type(callee_authid) == str
        assert callee_authrole is None or type(callee_authrole) == str

        assert forward_for is None or type(forward_for) == list
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert "session" in ff and type(ff["session"]) == int
                assert "authid" in ff and (
                    ff["authid"] is None or type(ff["authid"]) == str
                )
                assert "authrole" in ff and type(ff["authrole"]) == str

        # Initialize Message base class
        Message.__init__(self, from_fbs=from_fbs)

        # Initialize mixin attributes
        self._init_app_payload(
            args=args,
            kwargs=kwargs,
            payload=payload,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
        )
        self._init_forward_for(forward_for=forward_for)

        # Initialize Yield-specific attributes
        self._request = request
        self._progress = progress

        # effective callee that responded with the result
        self._callee = callee
        self._callee_authid = callee_authid
        self._callee_authrole = callee_authrole

    @property
    def request(self):
        if self._request is None and self._from_fbs:
            self._request = self._from_fbs.Request()
        return self._request

    @request.setter
    def request(self, value):
        assert value is None or type(value) == int
        self._request = value

    # NOTE: args, kwargs, payload properties are provided by MessageWithAppPayload mixin

    @property
    def progress(self):
        if self._progress is None and self._from_fbs:
            progress = self._from_fbs.Progress()
            if progress:
                self._progress = progress
        return self._progress

    @progress.setter
    def progress(self, value):
        assert value is None or type(value) == bool
        self._progress = value

    @property
    def callee(self):
        if self._callee is None and self._from_fbs:
            callee = self._from_fbs.Callee()
            if callee:
                self._callee = callee
        return self._callee

    @callee.setter
    def callee(self, value):
        assert value is None or type(value) == int
        self._callee = value

    @property
    def callee_authid(self):
        if self._callee_authid is None and self._from_fbs:
            s = self._from_fbs.CalleeAuthid()
            if s:
                self._callee_authid = s.decode("utf8")
        return self._callee_authid

    @callee_authid.setter
    def callee_authid(self, value):
        assert value is None or type(value) == str
        self._callee_authid = value

    @property
    def callee_authrole(self):
        if self._callee_authrole is None and self._from_fbs:
            s = self._from_fbs.CalleeAuthrole()
            if s:
                self._callee_authrole = s.decode("utf8")
        return self._callee_authrole

    @callee_authrole.setter
    def callee_authrole(self, value):
        assert value is None or type(value) == str
        self._callee_authrole = value

    # NOTE: enc_algo, enc_key, enc_serializer properties are provided by MessageWithAppPayload mixin
    # NOTE: forward_for property is provided by MessageWithForwardFor mixin

    @staticmethod
    def cast(buf):
        return Yield(from_fbs=message_fbs.Yield.GetRootAsYield(buf, 0))

    def build(self, builder, serializer=None):
        args = self.args
        if args:
            if serializer:
                args = builder.CreateByteVector(serializer.serialize_payload(args))
            else:
                args = builder.CreateByteVector(cbor2.dumps(args))

        kwargs = self.kwargs
        if kwargs:
            if serializer:
                kwargs = builder.CreateByteVector(serializer.serialize_payload(kwargs))
            else:
                kwargs = builder.CreateByteVector(cbor2.dumps(kwargs))

        payload = self.payload
        if payload:
            payload = builder.CreateByteVector(payload)

        enc_key = self.enc_key
        if enc_key:
            enc_key = builder.CreateString(enc_key)

        callee_authid = self.callee_authid
        if callee_authid:
            callee_authid = builder.CreateString(callee_authid)

        callee_authrole = self.callee_authrole
        if callee_authrole:
            callee_authrole = builder.CreateString(callee_authrole)

        # forward_for: [Principal]
        forward_for = self.forward_for
        if forward_for:
            from wamp.proto import Principal as PrincipalGen

            _forward_for = []
            for principal in forward_for:
                _session = principal.get("session", 0)
                _authid = principal.get("authid", None)
                _authrole = principal.get("authrole", "")

                if _authid:
                    _authid = builder.CreateString(_authid)
                _authrole = builder.CreateString(_authrole)

                PrincipalGen.Start(builder)
                PrincipalGen.AddSession(builder, _session)
                if _authid:
                    PrincipalGen.AddAuthid(builder, _authid)
                PrincipalGen.AddAuthrole(builder, _authrole)
                _forward_for.append(PrincipalGen.End(builder))

            message_fbs.YieldGen.YieldStartForwardForVector(builder, len(_forward_for))
            for principal in reversed(_forward_for):
                builder.PrependUOffsetTRelative(principal)
            forward_for = builder.EndVector()

        # build YieldGen
        message_fbs.YieldGen.YieldStart(builder)

        if self.request:
            message_fbs.YieldGen.YieldAddRequest(builder, self.request)
        if args:
            message_fbs.YieldGen.YieldAddArgs(builder, args)
        if kwargs:
            message_fbs.YieldGen.YieldAddKwargs(builder, kwargs)
        if payload:
            message_fbs.YieldGen.YieldAddPayload(builder, payload)
        if self.progress:
            message_fbs.YieldGen.YieldAddProgress(builder, self.progress)
        if self.enc_algo:
            # Convert string enc_algo to FlatBuffers enum value
            enc_algo_int = ENC_ALGOS_FROMSTR.get(self.enc_algo, 0)
            message_fbs.YieldGen.YieldAddPptScheme(builder, enc_algo_int)
        if self.enc_serializer:
            # Convert string enc_serializer to FlatBuffers enum value
            enc_serializer_int = ENC_SERS_FROMSTR.get(self.enc_serializer, 0)
            message_fbs.YieldGen.YieldAddPptSerializer(builder, enc_serializer_int)
        if enc_key:
            message_fbs.YieldGen.YieldAddPptKeyid(builder, enc_key)
        if self.callee:
            message_fbs.YieldGen.YieldAddCallee(builder, self.callee)
        if callee_authid:
            message_fbs.YieldGen.YieldAddCalleeAuthid(builder, callee_authid)
        if callee_authrole:
            message_fbs.YieldGen.YieldAddCalleeAuthrole(builder, callee_authrole)
        if forward_for:
            message_fbs.YieldGen.YieldAddForwardFor(builder, forward_for)

        msg = message_fbs.YieldGen.YieldEnd(builder)

        # Wrap in Message union with type
        message_fbs.Message.MessageStart(builder)
        message_fbs.Message.MessageAddMsgType(builder, message_fbs.MessageType.YIELD)
        message_fbs.Message.MessageAddMsg(builder, msg)
        union_msg = message_fbs.Message.MessageEnd(builder)

        return union_msg

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert len(wmsg) > 0 and wmsg[0] == Yield.MESSAGE_TYPE

        if len(wmsg) not in (3, 4, 5):
            raise ProtocolError(
                "invalid message length {0} for YIELD".format(len(wmsg))
            )

        request = check_or_raise_id(wmsg[1], "'request' in YIELD")
        options = check_or_raise_extra(wmsg[2], "'options' in YIELD")

        args = None
        kwargs = None
        payload = None
        enc_algo = None
        enc_key = None
        enc_serializer = None

        if len(wmsg) == 4 and type(wmsg[3]) == bytes:
            payload = wmsg[3]

            enc_algo = options.get("enc_algo", None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError(
                    "invalid value {0} for 'enc_algo' detail in YIELD".format(enc_algo)
                )

            enc_key = options.get("enc_key", None)
            if enc_key and type(enc_key) != str:
                raise ProtocolError(
                    "invalid type {0} for 'enc_key' detail in YIELD".format(
                        type(enc_key)
                    )
                )

            enc_serializer = options.get("enc_serializer", None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError(
                    "invalid value {0} for 'enc_serializer' detail in YIELD".format(
                        enc_serializer
                    )
                )

        else:
            if len(wmsg) > 3:
                args = wmsg[3]
                if args is not None and type(args) != list:
                    raise ProtocolError(
                        "invalid type {0} for 'args' in YIELD".format(type(args))
                    )

            if len(wmsg) > 4:
                kwargs = wmsg[4]
                if type(kwargs) != dict:
                    raise ProtocolError(
                        "invalid type {0} for 'kwargs' in YIELD".format(type(kwargs))
                    )

        progress = None
        callee = None
        callee_authid = None
        callee_authrole = None
        forward_for = None

        if "progress" in options:
            option_progress = options["progress"]
            if type(option_progress) != bool:
                raise ProtocolError(
                    "invalid type {0} for 'progress' option in YIELD".format(
                        type(option_progress)
                    )
                )

            progress = option_progress

        if "callee" in options:
            option_callee = options["callee"]
            if type(option_callee) != int:
                raise ProtocolError(
                    "invalid type {0} for 'callee' detail in YIELD".format(
                        type(option_callee)
                    )
                )

            callee = option_callee

        if "callee_authid" in options:
            option_callee_authid = options["callee_authid"]
            if type(option_callee_authid) != str:
                raise ProtocolError(
                    "invalid type {0} for 'callee_authid' detail in YIELD".format(
                        type(option_callee_authid)
                    )
                )

            callee_authid = option_callee_authid

        if "callee_authrole" in options:
            option_callee_authrole = options["callee_authrole"]
            if type(option_callee_authrole) != str:
                raise ProtocolError(
                    "invalid type {0} for 'callee_authrole' detail in YIELD".format(
                        type(option_callee_authrole)
                    )
                )

            callee_authrole = option_callee_authrole

        if "forward_for" in options:
            forward_for = options["forward_for"]
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if "session" not in ff or type(ff["session"]) != int:
                        break
                    if "authid" not in ff or type(ff["authid"]) != str:
                        break
                    if "authrole" not in ff or type(ff["authrole"]) != str:
                        break
                valid = True

            if not valid:
                raise ProtocolError(
                    "invalid type/value {0} for/within 'forward_for' option in YIELD"
                )

        obj = Yield(
            request,
            args=args,
            kwargs=kwargs,
            payload=payload,
            progress=progress,
            enc_algo=enc_algo,
            enc_key=enc_key,
            enc_serializer=enc_serializer,
            callee=callee,
            callee_authid=callee_authid,
            callee_authrole=callee_authrole,
            forward_for=forward_for,
        )

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        options = {}

        if self.progress is not None:
            options["progress"] = self.progress

        if self.callee is not None:
            options["callee"] = self.callee
        if self.callee_authid is not None:
            options["callee_authid"] = self.callee_authid
        if self.callee_authrole is not None:
            options["callee_authrole"] = self.callee_authrole
        if self.forward_for is not None:
            options["forward_for"] = self.forward_for

        if self.payload:
            if self.enc_algo is not None:
                options["enc_algo"] = self.enc_algo
            if self.enc_key is not None:
                options["enc_key"] = self.enc_key
            if self.enc_serializer is not None:
                options["enc_serializer"] = self.enc_serializer
            return [Yield.MESSAGE_TYPE, self.request, options, self.payload]
        else:
            if self.kwargs:
                return [
                    Yield.MESSAGE_TYPE,
                    self.request,
                    options,
                    self.args,
                    self.kwargs,
                ]
            elif self.args:
                return [Yield.MESSAGE_TYPE, self.request, options, self.args]
            else:
                return [Yield.MESSAGE_TYPE, self.request, options]
