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

from __future__ import absolute_import

import re
import binascii

import six

import autobahn
from autobahn.wamp.exception import ProtocolError, InvalidUriError
from autobahn.wamp.role import ROLE_NAME_TO_CLASS

try:
    import cbor
    import flatbuffers
    from autobahn.wamp import message_fbs
except ImportError:
    _HAS_WAMP_FLATBUFFERS = False
else:
    _HAS_WAMP_FLATBUFFERS = True

__all__ = ('Message',
           'Hello',
           'Welcome',
           'Abort',
           'Challenge',
           'Authenticate',
           'Goodbye',
           'Error',
           'Publish',
           'Published',
           'Subscribe',
           'Subscribed',
           'Unsubscribe',
           'Unsubscribed',
           'Event',
           'Call',
           'Cancel',
           'Result',
           'Register',
           'Registered',
           'Unregister',
           'Unregistered',
           'Invocation',
           'Interrupt',
           'Yield',
           'check_or_raise_uri',
           'check_or_raise_id',
           'is_valid_enc_algo',
           'is_valid_enc_serializer',
           'PAYLOAD_ENC_CRYPTO_BOX',
           'PAYLOAD_ENC_MQTT',
           'PAYLOAD_ENC_STANDARD_IDENTIFIERS')


# strict URI check allowing empty URI components
_URI_PAT_STRICT_EMPTY = re.compile(r"^(([0-9a-z_]+\.)|\.)*([0-9a-z_]+)?$")

# loose URI check allowing empty URI components
_URI_PAT_LOOSE_EMPTY = re.compile(r"^(([^\s\.#]+\.)|\.)*([^\s\.#]+)?$")

# strict URI check disallowing empty URI components
_URI_PAT_STRICT_NON_EMPTY = re.compile(r"^([0-9a-z_]+\.)*([0-9a-z_]+)$")

# loose URI check disallowing empty URI components
_URI_PAT_LOOSE_NON_EMPTY = re.compile(r"^([^\s\.#]+\.)*([^\s\.#]+)$")

# strict URI check disallowing empty URI components in all but the last component
_URI_PAT_STRICT_LAST_EMPTY = re.compile(r"^([0-9a-z_]+\.)*([0-9a-z_]*)$")

# loose URI check disallowing empty URI components in all but the last component
_URI_PAT_LOOSE_LAST_EMPTY = re.compile(r"^([^\s\.#]+\.)*([^\s\.#]*)$")

# custom (=implementation specific) WAMP attributes (used in WAMP message details/options)
_CUSTOM_ATTRIBUTE = re.compile(r"^x_([a-z][0-9a-z_]+)?$")

# Value for algo attribute in end-to-end encrypted messages using cryptobox, which
# is a scheme based on Curve25519, SHA512, Salsa20 and Poly1305.
# See: http://cr.yp.to/highspeed/coolnacl-20120725.pdf
PAYLOAD_ENC_CRYPTO_BOX = u'cryptobox'

# Payload transparency identifier for MQTT payloads (which are arbitrary binary).
PAYLOAD_ENC_MQTT = u'mqtt'

# Payload transparency identifier for XBR payloads
PAYLOAD_ENC_XBR = u'xbr'

# Payload transparency algorithm identifiers from the WAMP spec.
PAYLOAD_ENC_STANDARD_IDENTIFIERS = [PAYLOAD_ENC_CRYPTO_BOX, PAYLOAD_ENC_MQTT, PAYLOAD_ENC_XBR]

# Payload transparency serializer identifiers from the WAMP spec.
PAYLOAD_ENC_STANDARD_SERIALIZERS = [u'json', u'msgpack', u'cbor', u'ubjson', u'flatbuffers']

ENC_ALGO_NONE = 0
ENC_ALGO_CRYPTOBOX = 1
ENC_ALGO_MQTT = 2
ENC_ALGO_XBR = 3

ENC_ALGOS = {
    ENC_ALGO_NONE: u'null',
    ENC_ALGO_CRYPTOBOX: u'cryptobox',
    ENC_ALGO_MQTT: u'mqtt',
    ENC_ALGO_XBR: u'xbr',
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
    ENC_SER_NONE: u'null',
    ENC_SER_JSON: u'json',
    ENC_SER_MSGPACK: u'msgpack',
    ENC_SER_CBOR: u'cbor',
    ENC_SER_UBJSON: u'ubjson',
    ENC_SER_OPAQUE: u'opaque',
    ENC_SER_FLATBUFFERS: u'flatbuffers',
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

    Users can select arbitrary identifiers too, but these MUST start with ``u"x_"``.

    :param enc_algo: The payload transparency algorithm identifier to check.
    :type enc_algo: str

    :returns: Returns ``True`` if and only if the payload transparency
        algorithm identifier is valid.
    :rtype: bool
    """
    return type(enc_algo) == six.text_type and (enc_algo in PAYLOAD_ENC_STANDARD_IDENTIFIERS or _CUSTOM_ATTRIBUTE.match(enc_algo))


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

    Users can select arbitrary identifiers too, but these MUST start with ``u"x_"``.

    :param enc_serializer: The payload transparency serializer identifier to check.
    :type enc_serializer: str

    :returns: Returns ``True`` if and only if the payload transparency
        serializer identifier is valid.
    :rtype: bool
    """
    return type(enc_serializer) == six.text_type and (enc_serializer in PAYLOAD_ENC_STANDARD_SERIALIZERS or _CUSTOM_ATTRIBUTE.match(enc_serializer))


def b2a(data, max_len=40):
    if type(data) == six.text_type:
        s = data
    elif type(data) == six.binary_type:
        s = binascii.b2a_hex(data).decode('ascii')
    elif data is None:
        s = u'-'
    else:
        s = u'{}'.format(data)
    if len(s) > max_len:
        return s[:max_len] + u'..'
    else:
        return s


def check_or_raise_uri(value, message=u"WAMP message invalid", strict=False, allow_empty_components=False, allow_last_empty=False, allow_none=False):
    """
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
    """
    if value is None:
        if allow_none:
            return
        else:
            raise InvalidUriError(u"{0}: URI cannot be null".format(message))

    if type(value) != six.text_type:
        if not (value is None and allow_none):
            raise InvalidUriError(u"{0}: invalid type {1} for URI".format(message, type(value)))

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
        raise InvalidUriError(u'{0}: invalid value "{1}" for URI (did not match pattern "{2}" with options strict={3}, allow_empty_components={4}, allow_last_empty={5}, allow_none={6})'.format(message, value, pat.pattern, strict, allow_empty_components, allow_last_empty, allow_none))
    else:
        return value


def check_or_raise_id(value, message=u"WAMP message invalid"):
    """
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
    """
    if type(value) not in six.integer_types:
        raise ProtocolError(u"{0}: invalid type {1} for ID".format(message, type(value)))
    # the value 0 for WAMP IDs is possible in certain WAMP messages, e.g. UNREGISTERED with
    # router revocation signaling!
    if value < 0 or value > 9007199254740992:  # 2**53
        raise ProtocolError(u"{0}: invalid value {1} for ID".format(message, value))
    return value


def check_or_raise_extra(value, message=u"WAMP message invalid"):
    """
    Check a value for being a valid WAMP extra dictionary.

    If the value is not a valid WAMP extra dictionary, raises :class:`autobahn.wamp.exception.ProtocolError`.
    Otherwise return the value.

    :param value: The value to check.
    :type value: dict

    :param message: Prefix for message in exception raised when value is invalid.
    :type message: str

    :returns: The extra dictionary (if valid).
    :rtype: dict

    :raises: instance of :class:`autobahn.wamp.exception.ProtocolError`
    """
    if type(value) != dict:
        raise ProtocolError(u"{0}: invalid type {1} for WAMP extra".format(message, type(value)))
    for k in value.keys():
        if not isinstance(k, six.text_type):
            raise ProtocolError(u"{0}: invalid type {1} for key in WAMP extra ('{2}')".format(message, type(k), k))
    return value


def _validate_kwargs(kwargs, message=u"WAMP message invalid"):
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
            raise ProtocolError(u"{0}: invalid type {1} for WAMP kwargs".format(message, type(kwargs)))
        for k in kwargs.keys():
            if not isinstance(k, six.text_type):
                raise ProtocolError(u"{0}: invalid type {1} for key in WAMP kwargs ('{2}')".format(message, type(k), k))
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
        '_from_fbs',
        '_serialized',
        '_correlation_id',
        '_correlation_uri',
        '_correlation_is_anchor',
        '_correlation_is_last',
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

    @property
    def correlation_id(self):
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, value):
        assert(value is None or type(value) == six.text_type)
        self._correlation_id = value

    @property
    def correlation_uri(self):
        return self._correlation_uri

    @correlation_uri.setter
    def correlation_uri(self, value):
        assert(value is None or type(value) == six.text_type)
        self._correlation_uri = value

    @property
    def correlation_is_anchor(self):
        return self._correlation_is_anchor

    @correlation_is_anchor.setter
    def correlation_is_anchor(self, value):
        assert(value is None or type(value) == bool)
        self._correlation_is_anchor = value

    @property
    def correlation_is_last(self):
        return self._correlation_is_last

    @correlation_is_last.setter
    def correlation_is_last(self, value):
        assert(value is None or type(value) == bool)
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
            if k not in ['_serialized',
                         '_correlation_id',
                         '_correlation_uri',
                         '_correlation_is_anchor',
                         '_correlation_is_last'] and not k.startswith('_'):
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

    def build(self, builder):
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
            if serializer.NAME == u'flatbuffers':
                # flatbuffers get special treatment ..
                builder = flatbuffers.Builder(1024)

                # this is the core method writing out this message (self) to a (new) flatbuffer
                # FIXME: implement this method for all classes derived from Message
                obj = self.build(builder)

                builder.Finish(obj)
                buf = builder.Output()
                self._serialized[serializer] = bytes(buf)
            else:
                # all other serializers first marshal() the object and then serialize the latter
                self._serialized[serializer] = serializer.serialize(self.marshal())

        # cache is filled now: return serialized, cached bytes
        return self._serialized[serializer]


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
        'realm',
        'roles',
        'authmethods',
        'authid',
        'authrole',
        'authextra',
        'resumable',
        'resume_session',
        'resume_token',
    )

    def __init__(self,
                 realm,
                 roles,
                 authmethods=None,
                 authid=None,
                 authrole=None,
                 authextra=None,
                 resumable=None,
                 resume_session=None,
                 resume_token=None):
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
        assert(realm is None or isinstance(realm, six.text_type))
        assert(type(roles) == dict)
        assert(len(roles) > 0)
        for role in roles:
            assert(role in [u'subscriber', u'publisher', u'caller', u'callee'])
            assert(isinstance(roles[role], autobahn.wamp.role.ROLE_NAME_TO_CLASS[role]))
        if authmethods:
            assert(type(authmethods) == list)
            for authmethod in authmethods:
                assert(type(authmethod) == six.text_type)
        assert(authid is None or type(authid) == six.text_type)
        assert(authrole is None or type(authrole) == six.text_type)
        assert(authextra is None or type(authextra) == dict)
        assert(resumable is None or type(resumable) == bool)
        assert(resume_session is None or type(resume_session) == int)
        assert(resume_token is None or type(resume_token) == six.text_type)

        Message.__init__(self)
        self.realm = realm
        self.roles = roles
        self.authmethods = authmethods
        self.authid = authid
        self.authrole = authrole
        self.authextra = authextra
        self.resumable = resumable
        self.resume_session = resume_session
        self.resume_token = resume_token

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Hello.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for HELLO".format(len(wmsg)))

        realm = check_or_raise_uri(wmsg[1], u"'realm' in HELLO", allow_none=True)
        details = check_or_raise_extra(wmsg[2], u"'details' in HELLO")

        roles = {}

        if u'roles' not in details:
            raise ProtocolError(u"missing mandatory roles attribute in options in HELLO")

        details_roles = check_or_raise_extra(details[u'roles'], u"'roles' in 'details' in HELLO")

        if len(details_roles) == 0:
            raise ProtocolError(u"empty 'roles' in 'details' in HELLO")

        for role in details_roles:
            if role not in [u'subscriber', u'publisher', u'caller', u'callee']:
                raise ProtocolError("invalid role '{0}' in 'roles' in 'details' in HELLO".format(role))

            role_cls = ROLE_NAME_TO_CLASS[role]

            details_role = check_or_raise_extra(details_roles[role], "role '{0}' in 'roles' in 'details' in HELLO".format(role))

            if u'features' in details_role:
                check_or_raise_extra(details_role[u'features'], "'features' in role '{0}' in 'roles' in 'details' in HELLO".format(role))

                role_features = role_cls(**details_role[u'features'])

            else:
                role_features = role_cls()

            roles[role] = role_features

        authmethods = None
        if u'authmethods' in details:
            details_authmethods = details[u'authmethods']
            if type(details_authmethods) != list:
                raise ProtocolError("invalid type {0} for 'authmethods' detail in HELLO".format(type(details_authmethods)))

            for auth_method in details_authmethods:
                if type(auth_method) != six.text_type:
                    raise ProtocolError("invalid type {0} for item in 'authmethods' detail in HELLO".format(type(auth_method)))

            authmethods = details_authmethods

        authid = None
        if u'authid' in details:
            details_authid = details[u'authid']
            if type(details_authid) != six.text_type:
                raise ProtocolError("invalid type {0} for 'authid' detail in HELLO".format(type(details_authid)))

            authid = details_authid

        authrole = None
        if u'authrole' in details:
            details_authrole = details[u'authrole']
            if type(details_authrole) != six.text_type:
                raise ProtocolError("invalid type {0} for 'authrole' detail in HELLO".format(type(details_authrole)))

            authrole = details_authrole

        authextra = None
        if u'authextra' in details:
            details_authextra = details[u'authextra']
            if type(details_authextra) != dict:
                raise ProtocolError("invalid type {0} for 'authextra' detail in HELLO".format(type(details_authextra)))

            authextra = details_authextra

        resumable = None
        if u'resumable' in details:
            resumable = details[u'resumable']
            if type(resumable) != bool:
                raise ProtocolError("invalid type {0} for 'resumable' detail in HELLO".format(type(resumable)))

        resume_session = None
        if u'resume-session' in details:
            resume_session = details[u'resume-session']
            if type(resume_session) != int:
                raise ProtocolError("invalid type {0} for 'resume-session' detail in HELLO".format(type(resume_session)))

        resume_token = None
        if u'resume-token' in details:
            resume_token = details[u'resume-token']
            if type(resume_token) != six.text_type:
                raise ProtocolError("invalid type {0} for 'resume-token' detail in HELLO".format(type(resume_token)))
        else:
            if resume_session:
                raise ProtocolError("resume-token must be provided if resume-session is provided in HELLO")

        obj = Hello(realm, roles, authmethods, authid, authrole, authextra, resumable, resume_session, resume_token)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {u'roles': {}}
        for role in self.roles.values():
            details[u'roles'][role.ROLE] = {}
            for feature in role.__dict__:
                if not feature.startswith('_') and feature != 'ROLE' and getattr(role, feature) is not None:
                    if u'features' not in details[u'roles'][role.ROLE]:
                        details[u'roles'][role.ROLE] = {u'features': {}}
                    details[u'roles'][role.ROLE][u'features'][six.u(feature)] = getattr(role, feature)

        if self.authmethods is not None:
            details[u'authmethods'] = self.authmethods

        if self.authid is not None:
            details[u'authid'] = self.authid

        if self.authrole is not None:
            details[u'authrole'] = self.authrole

        if self.authextra is not None:
            details[u'authextra'] = self.authextra

        if self.resumable is not None:
            details[u'resumable'] = self.resumable

        if self.resume_session is not None:
            details[u'resume-session'] = self.resume_session

        if self.resume_token is not None:
            details[u'resume-token'] = self.resume_token

        return [Hello.MESSAGE_TYPE, self.realm, details]

    def __str__(self):
        """
        Return a string representation of this message.
        """
        return u"Hello(realm={}, roles={}, authmethods={}, authid={}, authrole={}, authextra={}, resumable={}, resume_session={}, resume_token={})".format(self.realm, self.roles, self.authmethods, self.authid, self.authrole, self.authextra, self.resumable, self.resume_session, self.resume_token)


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
        'session',
        'roles',
        'realm',
        'authid',
        'authrole',
        'authmethod',
        'authprovider',
        'authextra',
        'resumed',
        'resumable',
        'resume_token',
        'custom',
    )

    def __init__(self,
                 session,
                 roles,
                 realm=None,
                 authid=None,
                 authrole=None,
                 authmethod=None,
                 authprovider=None,
                 authextra=None,
                 resumed=None,
                 resumable=None,
                 resume_token=None,
                 custom=None):
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
        assert(type(session) in six.integer_types)
        assert(type(roles) == dict)
        assert(len(roles) > 0)
        for role in roles:
            assert(role in [u'broker', u'dealer'])
            assert(isinstance(roles[role], autobahn.wamp.role.ROLE_NAME_TO_CLASS[role]))
        assert(realm is None or type(realm) == six.text_type)
        assert(authid is None or type(authid) == six.text_type)
        assert(authrole is None or type(authrole) == six.text_type)
        assert(authmethod is None or type(authmethod) == six.text_type)
        assert(authprovider is None or type(authprovider) == six.text_type)
        assert(authextra is None or type(authextra) == dict)
        assert(resumed is None or type(resumed) == bool)
        assert(resumable is None or type(resumable) == bool)
        assert(resume_token is None or type(resume_token) == six.text_type)
        assert(custom is None or type(custom) == dict)
        if custom:
            for k in custom:
                assert(_CUSTOM_ATTRIBUTE.match(k))

        Message.__init__(self)
        self.session = session
        self.roles = roles
        self.realm = realm
        self.authid = authid
        self.authrole = authrole
        self.authmethod = authmethod
        self.authprovider = authprovider
        self.authextra = authextra
        self.resumed = resumed
        self.resumable = resumable
        self.resume_token = resume_token
        self.custom = custom or {}

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Welcome.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for WELCOME".format(len(wmsg)))

        session = check_or_raise_id(wmsg[1], u"'session' in WELCOME")
        details = check_or_raise_extra(wmsg[2], u"'details' in WELCOME")

        # FIXME: tigher value checking (types, URIs etc)
        realm = details.get(u'realm', None)
        authid = details.get(u'authid', None)
        authrole = details.get(u'authrole', None)
        authmethod = details.get(u'authmethod', None)
        authprovider = details.get(u'authprovider', None)
        authextra = details.get(u'authextra', None)

        resumed = None
        if u'resumed' in details:
            resumed = details[u'resumed']
            if not type(resumed) == bool:
                raise ProtocolError("invalid type {0} for 'resumed' detail in WELCOME".format(type(resumed)))

        resumable = None
        if u'resumable' in details:
            resumable = details[u'resumable']
            if not type(resumable) == bool:
                raise ProtocolError("invalid type {0} for 'resumable' detail in WELCOME".format(type(resumable)))

        resume_token = None
        if u'resume_token' in details:
            resume_token = details[u'resume_token']
            if not type(resume_token) == six.text_type:
                raise ProtocolError("invalid type {0} for 'resume_token' detail in WELCOME".format(type(resume_token)))
        elif resumable:
            raise ProtocolError("resume_token required when resumable is given in WELCOME")

        roles = {}

        if u'roles' not in details:
            raise ProtocolError(u"missing mandatory roles attribute in options in WELCOME")

        details_roles = check_or_raise_extra(details['roles'], u"'roles' in 'details' in WELCOME")

        if len(details_roles) == 0:
            raise ProtocolError(u"empty 'roles' in 'details' in WELCOME")

        for role in details_roles:
            if role not in [u'broker', u'dealer']:
                raise ProtocolError("invalid role '{0}' in 'roles' in 'details' in WELCOME".format(role))

            role_cls = ROLE_NAME_TO_CLASS[role]

            details_role = check_or_raise_extra(details_roles[role], "role '{0}' in 'roles' in 'details' in WELCOME".format(role))

            if u'features' in details_role:
                check_or_raise_extra(details_role[u'features'], "'features' in role '{0}' in 'roles' in 'details' in WELCOME".format(role))

                role_features = role_cls(**details_roles[role][u'features'])

            else:
                role_features = role_cls()

            roles[role] = role_features

        custom = {}
        for k in details:
            if _CUSTOM_ATTRIBUTE.match(k):
                custom[k] = details[k]

        obj = Welcome(session, roles, realm, authid, authrole, authmethod, authprovider, authextra, resumed, resumable, resume_token, custom)

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
            details[u'realm'] = self.realm

        if self.authid:
            details[u'authid'] = self.authid

        if self.authrole:
            details[u'authrole'] = self.authrole

        if self.authrole:
            details[u'authmethod'] = self.authmethod

        if self.authprovider:
            details[u'authprovider'] = self.authprovider

        if self.authextra:
            details[u'authextra'] = self.authextra

        if self.resumed:
            details[u'resumed'] = self.resumed

        if self.resumable:
            details[u'resumable'] = self.resumable

        if self.resume_token:
            details[u'resume_token'] = self.resume_token

        details[u'roles'] = {}
        for role in self.roles.values():
            details[u'roles'][role.ROLE] = {}
            for feature in role.__dict__:
                if not feature.startswith('_') and feature != 'ROLE' and getattr(role, feature) is not None:
                    if u'features' not in details[u'roles'][role.ROLE]:
                        details[u'roles'][role.ROLE] = {u'features': {}}
                    details[u'roles'][role.ROLE][u'features'][six.u(feature)] = getattr(role, feature)

        return [Welcome.MESSAGE_TYPE, self.session, details]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Welcome(session={}, roles={}, realm={}, authid={}, authrole={}, authmethod={}, authprovider={}, authextra={}, resumed={}, resumable={}, resume_token={})".format(self.session, self.roles, self.realm, self.authid, self.authrole, self.authmethod, self.authprovider, self.authextra, self.resumed, self.resumable, self.resume_token)


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
        'reason',
        'message',
    )

    def __init__(self, reason, message=None):
        """

        :param reason: WAMP or application error URI for aborting reason.
        :type reason: str

        :param message: Optional human-readable closing message, e.g. for logging purposes.
        :type message: str or None
        """
        assert(type(reason) == six.text_type)
        assert(message is None or type(message) == six.text_type)

        Message.__init__(self)
        self.reason = reason
        self.message = message

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Abort.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for ABORT".format(len(wmsg)))

        details = check_or_raise_extra(wmsg[1], u"'details' in ABORT")
        reason = check_or_raise_uri(wmsg[2], u"'reason' in ABORT")

        message = None

        if u'message' in details:

            details_message = details[u'message']
            if type(details_message) != six.text_type:
                raise ProtocolError("invalid type {0} for 'message' detail in ABORT".format(type(details_message)))

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
            details[u'message'] = self.message

        return [Abort.MESSAGE_TYPE, details, self.reason]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Abort(message={0}, reason={1})".format(self.message, self.reason)


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
        'method',
        'extra',
    )

    def __init__(self, method, extra=None):
        """

        :param method: The authentication method.
        :type method: str

        :param extra: Authentication method specific information.
        :type extra: dict or None
        """
        assert(type(method) == six.text_type)
        assert(extra is None or type(extra) == dict)

        Message.__init__(self)
        self.method = method
        self.extra = extra or {}

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Challenge.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for CHALLENGE".format(len(wmsg)))

        method = wmsg[1]
        if type(method) != six.text_type:
            raise ProtocolError("invalid type {0} for 'method' in CHALLENGE".format(type(method)))

        extra = check_or_raise_extra(wmsg[2], u"'extra' in CHALLENGE")

        obj = Challenge(method, extra)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Challenge.MESSAGE_TYPE, self.method, self.extra]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Challenge(method={0}, extra={1})".format(self.method, self.extra)


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
        'signature',
        'extra',
    )

    def __init__(self, signature, extra=None):
        """

        :param signature: The signature for the authentication challenge.
        :type signature: str

        :param extra: Authentication method specific information.
        :type extra: dict or None
        """
        assert(type(signature) == six.text_type)
        assert(extra is None or type(extra) == dict)

        Message.__init__(self)
        self.signature = signature
        self.extra = extra or {}

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Authenticate.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for AUTHENTICATE".format(len(wmsg)))

        signature = wmsg[1]
        if type(signature) != six.text_type:
            raise ProtocolError("invalid type {0} for 'signature' in AUTHENTICATE".format(type(signature)))

        extra = check_or_raise_extra(wmsg[2], u"'extra' in AUTHENTICATE")

        obj = Authenticate(signature, extra)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Authenticate.MESSAGE_TYPE, self.signature, self.extra]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Authenticate(signature={0}, extra={1})".format(self.signature, self.extra)


class Goodbye(Message):
    """
    A WAMP ``GOODBYE`` message.

    Format: ``[GOODBYE, Details|dict, Reason|uri]``
    """

    MESSAGE_TYPE = 6
    """
    The WAMP message code for this type of message.
    """

    DEFAULT_REASON = u"wamp.close.normal"
    """
    Default WAMP closing reason.
    """

    __slots__ = (
        'reason',
        'message',
        'resumable',
    )

    def __init__(self, reason=DEFAULT_REASON, message=None, resumable=None):
        """

        :param reason: Optional WAMP or application error URI for closing reason.
        :type reason: str

        :param message: Optional human-readable closing message, e.g. for logging purposes.
        :type message: str or None

        :param resumable: From the server: Whether the session is able to be resumed (true) or destroyed (false). From the client: Whether it should be resumable (true) or destroyed (false).
        :type resumable: bool or None
        """
        assert(type(reason) == six.text_type)
        assert(message is None or type(message) == six.text_type)
        assert(resumable is None or type(resumable) == bool)

        Message.__init__(self)
        self.reason = reason
        self.message = message
        self.resumable = resumable

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Goodbye.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for GOODBYE".format(len(wmsg)))

        details = check_or_raise_extra(wmsg[1], u"'details' in GOODBYE")
        reason = check_or_raise_uri(wmsg[2], u"'reason' in GOODBYE")

        message = None
        resumable = None

        if u'message' in details:

            details_message = details[u'message']
            if type(details_message) != six.text_type:
                raise ProtocolError("invalid type {0} for 'message' detail in GOODBYE".format(type(details_message)))

            message = details_message

        if u'resumable' in details:
            resumable = details[u'resumable']
            if type(resumable) != bool:
                raise ProtocolError("invalid type {0} for 'resumable' detail in GOODBYE".format(type(resumable)))

        obj = Goodbye(reason=reason,
                      message=message,
                      resumable=resumable)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {}
        if self.message:
            details[u'message'] = self.message

        if self.resumable:
            details[u'resumable'] = self.resumable

        return [Goodbye.MESSAGE_TYPE, details, self.reason]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Goodbye(message={}, reason={}, resumable={})".format(self.message, self.reason, self.resumable)


class Error(Message):
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

    __slots__ = (
        'request_type',
        'request',
        'error',
        'args',
        'kwargs',
        'payload',
        'enc_algo',
        'enc_key',
        'enc_serializer',
        'callee',
        'callee_authid',
        'callee_authrole',
        'forward_for',
    )

    def __init__(self,
                 request_type,
                 request,
                 error,
                 args=None,
                 kwargs=None,
                 payload=None,
                 enc_algo=None,
                 enc_key=None,
                 enc_serializer=None,
                 callee=None,
                 callee_authid=None,
                 callee_authrole=None,
                 forward_for=None):
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
        assert(type(request_type) in six.integer_types)
        assert(type(request) in six.integer_types)
        assert(type(error) == six.text_type)
        assert(args is None or type(args) in [list, tuple])
        assert(kwargs is None or type(kwargs) == dict)
        assert(payload is None or type(payload) == six.binary_type)
        assert(payload is None or (payload is not None and args is None and kwargs is None))

        assert(enc_algo is None or is_valid_enc_algo(enc_algo))
        assert((enc_algo is None and enc_key is None and enc_serializer is None) or (payload is not None and enc_algo is not None))
        assert(enc_key is None or type(enc_key) == six.text_type)
        assert(enc_serializer is None or is_valid_enc_serializer(enc_serializer))

        assert(callee is None or type(callee) in six.integer_types)
        assert(callee_authid is None or type(callee_authid) == six.text_type)
        assert(callee_authrole is None or type(callee_authrole) == six.text_type)

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self)
        self.request_type = request_type
        self.request = request
        self.error = error
        self.args = args
        self.kwargs = _validate_kwargs(kwargs)
        self.payload = payload

        # payload transparency related knobs
        self.enc_algo = enc_algo
        self.enc_key = enc_key
        self.enc_serializer = enc_serializer

        # effective callee that responded with the error
        self.callee = callee
        self.callee_authid = callee_authid
        self.callee_authrole = callee_authrole

        # message forwarding
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Error.MESSAGE_TYPE)

        if len(wmsg) not in (5, 6, 7):
            raise ProtocolError("invalid message length {0} for ERROR".format(len(wmsg)))

        request_type = wmsg[1]
        if type(request_type) not in six.integer_types:
            raise ProtocolError("invalid type {0} for 'request_type' in ERROR".format(request_type))

        if request_type not in [Subscribe.MESSAGE_TYPE,
                                Unsubscribe.MESSAGE_TYPE,
                                Publish.MESSAGE_TYPE,
                                Register.MESSAGE_TYPE,
                                Unregister.MESSAGE_TYPE,
                                Call.MESSAGE_TYPE,
                                Invocation.MESSAGE_TYPE]:
            raise ProtocolError("invalid value {0} for 'request_type' in ERROR".format(request_type))

        request = check_or_raise_id(wmsg[2], u"'request' in ERROR")
        details = check_or_raise_extra(wmsg[3], u"'details' in ERROR")
        error = check_or_raise_uri(wmsg[4], u"'error' in ERROR")

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

        if len(wmsg) == 6 and type(wmsg[5]) == six.binary_type:

            payload = wmsg[5]

            enc_algo = details.get(u'enc_algo', None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError("invalid value {0} for 'enc_algo' detail in EVENT".format(enc_algo))

            enc_key = details.get(u'enc_key', None)
            if enc_key and type(enc_key) != six.text_type:
                raise ProtocolError("invalid type {0} for 'enc_key' detail in EVENT".format(type(enc_key)))

            enc_serializer = details.get(u'enc_serializer', None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError("invalid value {0} for 'enc_serializer' detail in EVENT".format(enc_serializer))

        else:
            if len(wmsg) > 5:
                args = wmsg[5]
                if args is not None and type(args) != list:
                    raise ProtocolError("invalid type {0} for 'args' in ERROR".format(type(args)))

            if len(wmsg) > 6:
                kwargs = wmsg[6]
                if type(kwargs) != dict:
                    raise ProtocolError("invalid type {0} for 'kwargs' in ERROR".format(type(kwargs)))

        if u'callee' in details:

            detail_callee = details[u'callee']
            if type(detail_callee) not in six.integer_types:
                raise ProtocolError("invalid type {0} for 'callee' detail in ERROR".format(type(detail_callee)))

            callee = detail_callee

        if u'callee_authid' in details:

            detail_callee_authid = details[u'callee_authid']
            if type(detail_callee_authid) != six.text_type:
                raise ProtocolError("invalid type {0} for 'callee_authid' detail in ERROR".format(type(detail_callee_authid)))

            callee_authid = detail_callee_authid

        if u'callee_authrole' in details:

            detail_callee_authrole = details[u'callee_authrole']
            if type(detail_callee_authrole) != six.text_type:
                raise ProtocolError("invalid type {0} for 'callee_authrole' detail in ERROR".format(type(detail_callee_authrole)))

            callee_authrole = detail_callee_authrole

        if u'forward_for' in details:
            forward_for = details[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in ERROR")

        obj = Error(request_type,
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
                    forward_for=forward_for)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {}

        if self.callee is not None:
            details[u'callee'] = self.callee
        if self.callee_authid is not None:
            details[u'callee_authid'] = self.callee_authid
        if self.callee_authrole is not None:
            details[u'callee_authrole'] = self.callee_authrole
        if self.forward_for is not None:
            details[u'forward_for'] = self.forward_for

        if self.payload:
            if self.enc_algo is not None:
                details[u'enc_algo'] = self.enc_algo
            if self.enc_key is not None:
                details[u'enc_key'] = self.enc_key
            if self.enc_serializer is not None:
                details[u'enc_serializer'] = self.enc_serializer
            return [self.MESSAGE_TYPE, self.request_type, self.request, details, self.error, self.payload]
        else:
            if self.kwargs:
                return [self.MESSAGE_TYPE, self.request_type, self.request, details, self.error, self.args, self.kwargs]
            elif self.args:
                return [self.MESSAGE_TYPE, self.request_type, self.request, details, self.error, self.args]
            else:
                return [self.MESSAGE_TYPE, self.request_type, self.request, details, self.error]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Error(request_type={0}, request={1}, error={2}, args={3}, kwargs={4}, enc_algo={5}, enc_key={6}, enc_serializer={7}, payload={8}, callee={9}, callee_authid={10}, callee_authrole={11}, forward_for={12})".format(self.request_type, self.request, self.error, self.args, self.kwargs, self.enc_algo, self.enc_key, self.enc_serializer, b2a(self.payload), self.callee, self.callee_authid, self.callee_authrole, self.forward_for)


class Publish(Message):
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

    __slots__ = (
        # uint64 (key)
        '_request',

        # string (required, uri)
        '_topic',

        # [uint8]
        '_args',

        # [uint8]
        '_kwargs',

        # [uint8]
        '_payload',

        # Payload => uint8
        '_enc_algo',

        # Serializer => uint8
        '_enc_serializer',

        # [uint8]
        '_enc_key',

        # bool
        '_acknowledge',

        # bool
        '_exclude_me',

        # [uint64]
        '_exclude',

        # [string] (principal)
        '_exclude_authid',

        # [string] (principal)
        '_exclude_authrole',

        # [uint64]
        '_eligible',

        # [string] (principal)
        '_eligible_authid',

        # [string] (principal)
        '_eligible_authrole',

        # bool
        '_retain',

        # [Principal]
        '_forward_for',
    )

    def __init__(self,
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
                 enc_algo=None,
                 enc_key=None,
                 enc_serializer=None,
                 forward_for=None,
                 from_fbs=None):
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

        :param enc_algo: If using payload transparency, the encoding algorithm that was used to encode the payload.
        :type enc_algo: str or None

        :param enc_key: If using payload transparency with an encryption algorithm, the payload encryption key.
        :type enc_key: str or None

        :param enc_serializer: If using payload transparency, the payload object serializer that was used encoding the payload.
        :type enc_serializer: str or None or None

        :param forward_for: When this Call is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert(request is None or type(request) in six.integer_types)
        assert(topic is None or type(topic) == six.text_type)
        assert(args is None or type(args) in [list, tuple, six.text_type, six.binary_type])
        assert(kwargs is None or type(kwargs) in [dict, six.text_type, six.binary_type])
        assert(payload is None or type(payload) == six.binary_type)
        assert(payload is None or (payload is not None and args is None and kwargs is None))
        assert(acknowledge is None or type(acknowledge) == bool)
        assert(retain is None or type(retain) == bool)

        # publisher exlusion and black-/whitelisting
        assert(exclude_me is None or type(exclude_me) == bool)

        assert(exclude is None or type(exclude) == list)
        if exclude:
            for sessionid in exclude:
                assert(type(sessionid) in six.integer_types)

        assert(exclude_authid is None or type(exclude_authid) == list)
        if exclude_authid:
            for authid in exclude_authid:
                assert(type(authid) == six.text_type)

        assert(exclude_authrole is None or type(exclude_authrole) == list)
        if exclude_authrole:
            for authrole in exclude_authrole:
                assert(type(authrole) == six.text_type)

        assert(eligible is None or type(eligible) == list)
        if eligible:
            for sessionid in eligible:
                assert(type(sessionid) in six.integer_types)

        assert(eligible_authid is None or type(eligible_authid) == list)
        if eligible_authid:
            for authid in eligible_authid:
                assert(type(authid) == six.text_type)

        assert(eligible_authrole is None or type(eligible_authrole) == list)
        if eligible_authrole:
            for authrole in eligible_authrole:
                assert(type(authrole) == six.text_type)

        assert(enc_algo is None or is_valid_enc_algo(enc_algo))
        assert((enc_algo is None and enc_key is None and enc_serializer is None) or (payload is not None and enc_algo is not None))
        assert(enc_key is None or type(enc_key) == six.text_type)
        assert(enc_serializer is None or is_valid_enc_serializer(enc_serializer))

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self, from_fbs=from_fbs)
        self._request = request
        self._topic = topic
        self._args = args
        self._kwargs = _validate_kwargs(kwargs)
        self._payload = payload
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

        # payload transparency related knobs
        self._enc_algo = enc_algo
        self._enc_key = enc_key
        self._enc_serializer = enc_serializer

        # message forwarding
        self._forward_for = forward_for

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
        assert(value is None or type(value) in six.integer_types)
        self._request = value

    @property
    def topic(self):
        if self._topic is None and self._from_fbs:
            s = self._from_fbs.Topic()
            if s:
                self._topic = s.decode('utf8')
        return self._topic

    @topic.setter
    def topic(self, value):
        assert value is None or type(value) == str
        self._topic = value

    @property
    def args(self):
        if self._args is None and self._from_fbs:
            if self._from_fbs.ArgsLength():
                self._args = cbor.loads(bytes(self._from_fbs.ArgsAsBytes()))
        return self._args

    @args.setter
    def args(self, value):
        assert(value is None or type(value) in [list, tuple])
        self._args = value

    @property
    def kwargs(self):
        if self._kwargs is None and self._from_fbs:
            if self._from_fbs.KwargsLength():
                self._kwargs = cbor.loads(bytes(self._from_fbs.KwargsAsBytes()))
        return self._kwargs

    @kwargs.setter
    def kwargs(self, value):
        assert(value is None or type(value) == dict)
        self._kwargs = value

    @property
    def payload(self):
        if self._payload is None and self._from_fbs:
            if self._from_fbs.PayloadLength():
                self._payload = self._from_fbs.PayloadAsBytes()
        return self._payload

    @payload.setter
    def payload(self, value):
        assert value is None or type(value) == bytes
        self._payload = value

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
                    exclude_authid.append(self._from_fbs.ExcludeAuthid(j).decode('utf8'))
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
                    exclude_authrole.append(self._from_fbs.ExcludeAuthrole(j).decode('utf8'))
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
                    eligible_authid.append(self._from_fbs.EligibleAuthid(j).decode('utf8'))
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
                    eligible_authrole.append(self._from_fbs.EligibleAuthrole(j).decode('utf8'))
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
    def enc_algo(self):
        if self._enc_algo is None and self._from_fbs:
            enc_algo = self._from_fbs.EncAlgo()
            if enc_algo:
                self._enc_algo = enc_algo
        return self._enc_algo

    @enc_algo.setter
    def enc_algo(self, value):
        assert value is None or value in [ENC_ALGO_CRYPTOBOX, ENC_ALGO_MQTT, ENC_ALGO_XBR]
        self._enc_algo = value

    @property
    def enc_key(self):
        if self._enc_key is None and self._from_fbs:
            if self._from_fbs.EncKeyLength():
                self._enc_key = self._from_fbs.EncKeyAsBytes()
        return self._enc_key

    @enc_key.setter
    def enc_key(self, value):
        assert value is None or type(value) == bytes
        self._enc_key = value

    @property
    def enc_serializer(self):
        if self._enc_serializer is None and self._from_fbs:
            enc_serializer = self._from_fbs.EncSerializer()
            if enc_serializer:
                self._enc_serializer = enc_serializer
        return self._enc_serializer

    @enc_serializer.setter
    def enc_serializer(self, value):
        assert value is None or value in [ENC_SER_JSON, ENC_SER_MSGPACK, ENC_SER_CBOR, ENC_SER_UBJSON]
        self._enc_serializer = value

    @property
    def forward_for(self):
        # FIXME
        return self._forward_for

    @forward_for.setter
    def forward_for(self, value):
        # FIXME
        self._forward_for = value

    @staticmethod
    def cast(buf):
        return Publish(from_fbs=message_fbs.Publish.GetRootAsPublish(buf, 0))

    def build(self, builder):

        args = self.args
        if args:
            args = builder.CreateByteVector(cbor.dumps(args))

        kwargs = self.kwargs
        if kwargs:
            kwargs = builder.CreateByteVector(cbor.dumps(kwargs))

        payload = self.payload
        if payload:
            payload = builder.CreateByteVector(payload)

        topic = self.topic
        if topic:
            topic = builder.CreateString(topic)

        enc_key = self.enc_key
        if enc_key:
            enc_key = builder.CreateByteVector(enc_key)

        # exclude: [int]
        exclude = self.exclude
        if exclude:
            message_fbs.PublishGen.PublishStartExcludeAuthidVector(builder, len(exclude))
            for session in reversed(exclude):
                builder.PrependUint64(session)
            exclude = builder.EndVector(len(exclude))

        # exclude_authid: [string]
        exclude_authid = self.exclude_authid
        if exclude_authid:
            _exclude_authid = []
            for authid in exclude_authid:
                _exclude_authid.append(builder.CreateString(authid))
            message_fbs.PublishGen.PublishStartExcludeAuthidVector(builder, len(_exclude_authid))
            for o in reversed(_exclude_authid):
                builder.PrependUOffsetTRelative(o)
            exclude_authid = builder.EndVector(len(_exclude_authid))

        # exclude_authrole: [string]
        exclude_authrole = self.exclude_authrole
        if exclude_authid:
            _exclude_authrole = []
            for authrole in exclude_authrole:
                _exclude_authrole.append(builder.CreateString(authrole))
            message_fbs.PublishGen.PublishStartExcludeAuthroleVector(builder, len(_exclude_authrole))
            for o in reversed(_exclude_authrole):
                builder.PrependUOffsetTRelative(o)
            exclude_authrole = builder.EndVector(len(_exclude_authrole))

        # eligible: [int]
        eligible = self.eligible
        if eligible:
            message_fbs.PublishGen.PublishStartEligibleAuthidVector(builder, len(eligible))
            for session in reversed(eligible):
                builder.PrependUint64(session)
            eligible = builder.EndVector(len(eligible))

        # eligible_authid: [string]
        eligible_authid = self.eligible_authid
        if eligible_authid:
            _eligible_authid = []
            for authid in eligible_authid:
                _eligible_authid.append(builder.CreateString(authid))
            message_fbs.PublishGen.PublishStartEligibleAuthidVector(builder, len(_eligible_authid))
            for o in reversed(_eligible_authid):
                builder.PrependUOffsetTRelative(o)
            eligible_authid = builder.EndVector(len(_eligible_authid))

        # eligible_authrole: [string]
        eligible_authrole = self.eligible_authrole
        if eligible_authrole:
            _eligible_authrole = []
            for authrole in eligible_authrole:
                _eligible_authrole.append(builder.CreateString(authrole))
            message_fbs.PublishGen.PublishStartEligibleAuthroleVector(builder, len(_eligible_authrole))
            for o in reversed(_eligible_authrole):
                builder.PrependUOffsetTRelative(o)
            eligible_authrole = builder.EndVector(len(_eligible_authrole))

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

        if self.acknowledge is not None:
            message_fbs.PublishGen.PublishAddAcknowledge(builder, self.acknowledge)
        if self.retain is not None:
            message_fbs.PublishGen.PublishAddRetain(builder, self.retain)
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
            message_fbs.PublishGen.PublishAddEligibleAuthrole(builder, eligible_authrole)

        if self.enc_algo:
            message_fbs.PublishGen.PublishAddEncAlgo(builder, self.enc_algo)
        if enc_key:
            message_fbs.PublishGen.PublishAddEncKey(builder, enc_key)
        if self.enc_serializer:
            message_fbs.PublishGen.PublishAddEncSerializer(builder, self.enc_serializer)

        # FIXME: add forward_for

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
        assert(len(wmsg) > 0 and wmsg[0] == Publish.MESSAGE_TYPE)

        if len(wmsg) not in (4, 5, 6):
            raise ProtocolError("invalid message length {0} for PUBLISH".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in PUBLISH")
        options = check_or_raise_extra(wmsg[2], u"'options' in PUBLISH")
        topic = check_or_raise_uri(wmsg[3], u"'topic' in PUBLISH")

        args = None
        kwargs = None
        payload = None

        if len(wmsg) == 5 and type(wmsg[4]) in [six.text_type, six.binary_type]:

            payload = wmsg[4]

            enc_algo = options.get(u'enc_algo', None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError("invalid value {0} for 'enc_algo' option in PUBLISH".format(enc_algo))

            enc_key = options.get(u'enc_key', None)
            if enc_key and type(enc_key) != six.text_type:
                raise ProtocolError("invalid type {0} for 'enc_key' option in PUBLISH".format(type(enc_key)))

            enc_serializer = options.get(u'enc_serializer', None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError("invalid value {0} for 'enc_serializer' option in PUBLISH".format(enc_serializer))

        else:
            if len(wmsg) > 4:
                args = wmsg[4]
                if type(args) not in [list, six.text_type, six.binary_type]:
                    raise ProtocolError("invalid type {0} for 'args' in PUBLISH".format(type(args)))

            if len(wmsg) > 5:
                kwargs = wmsg[5]
                if type(kwargs) not in [dict, six.text_type, six.binary_type]:
                    raise ProtocolError("invalid type {0} for 'kwargs' in PUBLISH".format(type(kwargs)))

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
        forward_for = None

        if u'acknowledge' in options:

            option_acknowledge = options[u'acknowledge']
            if type(option_acknowledge) != bool:
                raise ProtocolError("invalid type {0} for 'acknowledge' option in PUBLISH".format(type(option_acknowledge)))

            acknowledge = option_acknowledge

        if u'exclude_me' in options:

            option_exclude_me = options[u'exclude_me']
            if type(option_exclude_me) != bool:
                raise ProtocolError("invalid type {0} for 'exclude_me' option in PUBLISH".format(type(option_exclude_me)))

            exclude_me = option_exclude_me

        if u'exclude' in options:

            option_exclude = options[u'exclude']
            if type(option_exclude) != list:
                raise ProtocolError("invalid type {0} for 'exclude' option in PUBLISH".format(type(option_exclude)))

            for _sessionid in option_exclude:
                if type(_sessionid) not in six.integer_types:
                    raise ProtocolError("invalid type {0} for value in 'exclude' option in PUBLISH".format(type(_sessionid)))

            exclude = option_exclude

        if u'exclude_authid' in options:

            option_exclude_authid = options[u'exclude_authid']
            if type(option_exclude_authid) != list:
                raise ProtocolError("invalid type {0} for 'exclude_authid' option in PUBLISH".format(type(option_exclude_authid)))

            for _authid in option_exclude_authid:
                if type(_authid) != six.text_type:
                    raise ProtocolError("invalid type {0} for value in 'exclude_authid' option in PUBLISH".format(type(_authid)))

            exclude_authid = option_exclude_authid

        if u'exclude_authrole' in options:

            option_exclude_authrole = options[u'exclude_authrole']
            if type(option_exclude_authrole) != list:
                raise ProtocolError("invalid type {0} for 'exclude_authrole' option in PUBLISH".format(type(option_exclude_authrole)))

            for _authrole in option_exclude_authrole:
                if type(_authrole) != six.text_type:
                    raise ProtocolError("invalid type {0} for value in 'exclude_authrole' option in PUBLISH".format(type(_authrole)))

            exclude_authrole = option_exclude_authrole

        if u'eligible' in options:

            option_eligible = options[u'eligible']
            if type(option_eligible) != list:
                raise ProtocolError("invalid type {0} for 'eligible' option in PUBLISH".format(type(option_eligible)))

            for sessionId in option_eligible:
                if type(sessionId) not in six.integer_types:
                    raise ProtocolError("invalid type {0} for value in 'eligible' option in PUBLISH".format(type(sessionId)))

            eligible = option_eligible

        if u'eligible_authid' in options:

            option_eligible_authid = options[u'eligible_authid']
            if type(option_eligible_authid) != list:
                raise ProtocolError("invalid type {0} for 'eligible_authid' option in PUBLISH".format(type(option_eligible_authid)))

            for _authid in option_eligible_authid:
                if type(_authid) != six.text_type:
                    raise ProtocolError("invalid type {0} for value in 'eligible_authid' option in PUBLISH".format(type(_authid)))

            eligible_authid = option_eligible_authid

        if u'eligible_authrole' in options:

            option_eligible_authrole = options[u'eligible_authrole']
            if type(option_eligible_authrole) != list:
                raise ProtocolError("invalid type {0} for 'eligible_authrole' option in PUBLISH".format(type(option_eligible_authrole)))

            for _authrole in option_eligible_authrole:
                if type(_authrole) != six.text_type:
                    raise ProtocolError("invalid type {0} for value in 'eligible_authrole' option in PUBLISH".format(type(_authrole)))

            eligible_authrole = option_eligible_authrole

        if u'retain' in options:
            retain = options[u'retain']
            if type(retain) != bool:
                raise ProtocolError("invalid type {0} for 'retain' option in PUBLISH".format(type(retain)))

        if u'forward_for' in options:
            forward_for = options[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in PUBLISH")

        obj = Publish(request,
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
                      enc_algo=enc_algo,
                      enc_key=enc_key,
                      enc_serializer=enc_serializer,
                      forward_for=forward_for)

        return obj

    def marshal_options(self):
        options = {}

        if self.acknowledge is not None:
            options[u'acknowledge'] = self.acknowledge

        if self.exclude_me is not None:
            options[u'exclude_me'] = self.exclude_me
        if self.exclude is not None:
            options[u'exclude'] = self.exclude
        if self.exclude_authid is not None:
            options[u'exclude_authid'] = self.exclude_authid
        if self.exclude_authrole is not None:
            options[u'exclude_authrole'] = self.exclude_authrole
        if self.eligible is not None:
            options[u'eligible'] = self.eligible
        if self.eligible_authid is not None:
            options[u'eligible_authid'] = self.eligible_authid
        if self.eligible_authrole is not None:
            options[u'eligible_authrole'] = self.eligible_authrole
        if self.retain is not None:
            options[u'retain'] = self.retain

        if self.payload:
            if self.enc_algo is not None:
                options[u'enc_algo'] = self.enc_algo
            if self.enc_key is not None:
                options[u'enc_key'] = self.enc_key
            if self.enc_serializer is not None:
                options[u'enc_serializer'] = self.enc_serializer

        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        return options

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        options = self.marshal_options()

        if self.payload:
            return [Publish.MESSAGE_TYPE, self.request, options, self.topic, self.payload]
        else:
            if self.kwargs:
                return [Publish.MESSAGE_TYPE, self.request, options, self.topic, self.args, self.kwargs]
            elif self.args:
                return [Publish.MESSAGE_TYPE, self.request, options, self.topic, self.args]
            else:
                return [Publish.MESSAGE_TYPE, self.request, options, self.topic]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Publish(request={}, topic={}, args={}, kwargs={}, acknowledge={}, exclude_me={}, exclude={}, exclude_authid={}, exclude_authrole={}, eligible={}, eligible_authid={}, eligible_authrole={}, retain={}, enc_algo={}, enc_key={}, enc_serializer={}, payload={}, forward_for={})".format(self.request, self.topic, self.args, self.kwargs, self.acknowledge, self.exclude_me, self.exclude, self.exclude_authid, self.exclude_authrole, self.eligible, self.eligible_authid, self.eligible_authrole, self.retain, self.enc_algo, self.enc_key, self.enc_serializer, b2a(self.payload), self.forward_for)


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
        'request',
        'publication',
    )

    def __init__(self, request, publication):
        """

        :param request: The request ID of the original `PUBLISH` request.
        :type request: int

        :param publication: The publication ID for the published event.
        :type publication: int
        """
        assert(type(request) in six.integer_types)
        assert(type(publication) in six.integer_types)

        Message.__init__(self)
        self.request = request
        self.publication = publication

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Published.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for PUBLISHED".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in PUBLISHED")
        publication = check_or_raise_id(wmsg[2], u"'publication' in PUBLISHED")

        obj = Published(request, publication)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Published.MESSAGE_TYPE, self.request, self.publication]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Published(request={0}, publication={1})".format(self.request, self.publication)


class Subscribe(Message):
    """
    A WAMP ``SUBSCRIBE`` message.

    Format: ``[SUBSCRIBE, Request|id, Options|dict, Topic|uri]``
    """

    MESSAGE_TYPE = 32
    """
    The WAMP message code for this type of message.
    """

    MATCH_EXACT = u'exact'
    MATCH_PREFIX = u'prefix'
    MATCH_WILDCARD = u'wildcard'

    __slots__ = (
        'request',
        'topic',
        'match',
        'get_retained',
        'forward_for',
    )

    def __init__(self,
                 request,
                 topic,
                 match=None,
                 get_retained=None,
                 forward_for=None):
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
        assert(type(request) in six.integer_types)
        assert(type(topic) == six.text_type)
        assert(match is None or type(match) == six.text_type)
        assert(match is None or match in [Subscribe.MATCH_EXACT, Subscribe.MATCH_PREFIX, Subscribe.MATCH_WILDCARD])
        assert(get_retained is None or type(get_retained) is bool)
        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self)
        self.request = request
        self.topic = topic
        self.match = match or Subscribe.MATCH_EXACT
        self.get_retained = get_retained
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Subscribe.MESSAGE_TYPE)

        if len(wmsg) != 4:
            raise ProtocolError("invalid message length {0} for SUBSCRIBE".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in SUBSCRIBE")
        options = check_or_raise_extra(wmsg[2], u"'options' in SUBSCRIBE")
        topic = check_or_raise_uri(wmsg[3], u"'topic' in SUBSCRIBE", allow_empty_components=True)

        match = Subscribe.MATCH_EXACT
        get_retained = None
        forward_for = None

        if u'match' in options:

            option_match = options[u'match']
            if type(option_match) != six.text_type:
                raise ProtocolError("invalid type {0} for 'match' option in SUBSCRIBE".format(type(option_match)))

            if option_match not in [Subscribe.MATCH_EXACT, Subscribe.MATCH_PREFIX, Subscribe.MATCH_WILDCARD]:
                raise ProtocolError("invalid value {0} for 'match' option in SUBSCRIBE".format(option_match))

            match = option_match

        if u'get_retained' in options:
            get_retained = options[u'get_retained']

            if type(get_retained) != bool:
                raise ProtocolError("invalid type {0} for 'get_retained' option in SUBSCRIBE".format(type(get_retained)))

        if u'forward_for' in options:
            forward_for = options[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in SUBSCRIBE")

        obj = Subscribe(request, topic, match=match, get_retained=get_retained, forward_for=forward_for)

        return obj

    def marshal_options(self):
        options = {}

        if self.match and self.match != Subscribe.MATCH_EXACT:
            options[u'match'] = self.match

        if self.get_retained is not None:
            options[u'get_retained'] = self.get_retained

        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        return options

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Subscribe.MESSAGE_TYPE, self.request, self.marshal_options(), self.topic]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Subscribe(request={0}, topic={1}, match={2}, get_retained={3}, forward_for={4})".format(self.request, self.topic, self.match, self.get_retained, self.forward_for)


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
        'request',
        'subscription',
    )

    def __init__(self, request, subscription):
        """

        :param request: The request ID of the original ``SUBSCRIBE`` request.
        :type request: int

        :param subscription: The subscription ID for the subscribed topic (or topic pattern).
        :type subscription: int
        """
        assert(type(request) in six.integer_types)
        assert(type(subscription) in six.integer_types)

        Message.__init__(self)
        self.request = request
        self.subscription = subscription

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Subscribed.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for SUBSCRIBED".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in SUBSCRIBED")
        subscription = check_or_raise_id(wmsg[2], u"'subscription' in SUBSCRIBED")

        obj = Subscribed(request, subscription)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Subscribed.MESSAGE_TYPE, self.request, self.subscription]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Subscribed(request={0}, subscription={1})".format(self.request, self.subscription)


class Unsubscribe(Message):
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

    __slots__ = (
        'request',
        'subscription',
        'forward_for',
    )

    def __init__(self, request, subscription, forward_for=None):
        """

        :param request: The WAMP request ID of this request.
        :type request: int

        :param subscription: The subscription ID for the subscription to unsubscribe from.
        :type subscription: int

        :param forward_for: When this Unsubscribe is forwarded over a router-to-router link,
            or via an intermediary router.
        :type forward_for: list[dict]
        """
        assert(type(request) in six.integer_types)
        assert(type(subscription) in six.integer_types)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self)
        self.request = request
        self.subscription = subscription
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Unsubscribe.MESSAGE_TYPE)

        if len(wmsg) not in [3, 4]:
            raise ProtocolError("invalid message length {0} for WAMP UNSUBSCRIBE".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in UNSUBSCRIBE")
        subscription = check_or_raise_id(wmsg[2], u"'subscription' in UNSUBSCRIBE")

        options = None
        if len(wmsg) > 3:
            options = check_or_raise_extra(wmsg[3], u"'options' in UNSUBSCRIBE")

        forward_for = None
        if options and u'forward_for' in options:
            forward_for = options[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in UNSUBSCRIBE")

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
                u'forward_for': self.forward_for,
            }
            return [Unsubscribe.MESSAGE_TYPE, self.request, self.subscription, options]
        else:
            return [Unsubscribe.MESSAGE_TYPE, self.request, self.subscription]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Unsubscribe(request={0}, subscription={1}, forward_for={2})".format(self.request, self.subscription, self.forward_for)


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
        'request',
        'subscription',
        'reason',
    )

    def __init__(self, request, subscription=None, reason=None):
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
        assert(type(request) in six.integer_types)
        assert(subscription is None or type(subscription) in six.integer_types)
        assert(reason is None or type(reason) == six.text_type)
        assert((request != 0 and subscription is None) or (request == 0 and subscription != 0))

        Message.__init__(self)
        self.request = request
        self.subscription = subscription
        self.reason = reason

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Unsubscribed.MESSAGE_TYPE)

        if len(wmsg) not in [2, 3]:
            raise ProtocolError("invalid message length {0} for UNSUBSCRIBED".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in UNSUBSCRIBED")

        subscription = None
        reason = None

        if len(wmsg) > 2:

            details = check_or_raise_extra(wmsg[2], u"'details' in UNSUBSCRIBED")

            if u"subscription" in details:
                details_subscription = details[u"subscription"]
                if type(details_subscription) not in six.integer_types:
                    raise ProtocolError("invalid type {0} for 'subscription' detail in UNSUBSCRIBED".format(type(details_subscription)))
                subscription = details_subscription

            if u"reason" in details:
                reason = check_or_raise_uri(details[u"reason"], u"'reason' in UNSUBSCRIBED")

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
                details[u"reason"] = self.reason
            if self.subscription is not None:
                details[u"subscription"] = self.subscription
            return [Unsubscribed.MESSAGE_TYPE, self.request, details]
        else:
            return [Unsubscribed.MESSAGE_TYPE, self.request]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Unsubscribed(request={0}, reason={1}, subscription={2})".format(self.request, self.reason, self.subscription)


class Event(Message):
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

    __slots__ = (
        # uint64
        '_subscription',

        # uint64
        '_publication',

        # [uint8]
        '_args',

        # [uint8]
        '_kwargs',

        # [uint8]
        '_payload',

        # Payload => uint8
        '_enc_algo',

        # Serializer => uint8
        '_enc_serializer',

        # [uint8]
        '_enc_key',

        # uint64
        '_publisher',

        # string (principal)
        '_publisher_authid',

        # string (principal)
        '_publisher_authrole',

        # string (uri)
        '_topic',

        # bool
        '_retained',

        # bool - FIXME: rename to "acknowledge"
        '_x_acknowledged_delivery',

        # [Principal]
        '_forward_for',
    )

    def __init__(self, subscription=None, publication=None, args=None, kwargs=None, payload=None,
                 publisher=None, publisher_authid=None, publisher_authrole=None, topic=None,
                 retained=None, x_acknowledged_delivery=None,
                 enc_algo=None, enc_key=None, enc_serializer=None, forward_for=None,
                 from_fbs=None):
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
        assert(subscription is None or type(subscription) in six.integer_types)
        assert(publication is None or type(publication) in six.integer_types)
        assert(args is None or type(args) in [list, tuple])
        assert(kwargs is None or type(kwargs) == dict)
        assert(payload is None or type(payload) == six.binary_type)
        assert(payload is None or (payload is not None and args is None and kwargs is None))
        assert(publisher is None or type(publisher) in six.integer_types)
        assert(publisher_authid is None or type(publisher_authid) == six.text_type)
        assert(publisher_authrole is None or type(publisher_authrole) == six.text_type)
        assert(topic is None or type(topic) == six.text_type)
        assert(retained is None or type(retained) == bool)
        assert(x_acknowledged_delivery is None or type(x_acknowledged_delivery) == bool)
        assert(enc_algo is None or is_valid_enc_algo(enc_algo))
        assert((enc_algo is None and enc_key is None and enc_serializer is None) or (payload is not None and enc_algo is not None))
        assert(enc_key is None or type(enc_key) == six.text_type)
        assert(enc_serializer is None or is_valid_enc_serializer(enc_serializer))

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self, from_fbs=from_fbs)
        self._subscription = subscription
        self._publication = publication
        self._args = args
        self._kwargs = _validate_kwargs(kwargs)
        self._payload = payload
        self._publisher = publisher
        self._publisher_authid = publisher_authid
        self._publisher_authrole = publisher_authrole
        self._topic = topic
        self._retained = retained
        self._x_acknowledged_delivery = x_acknowledged_delivery
        self._enc_algo = enc_algo
        self._enc_key = enc_key
        self._enc_serializer = enc_serializer
        self._forward_for = forward_for

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
        assert(value is None or type(value) in six.integer_types)
        self._subscription = value

    @property
    def publication(self):
        if self._publication is None and self._from_fbs:
            self._publication = self._from_fbs.Publication()
        return self._publication

    @publication.setter
    def publication(self, value):
        assert(value is None or type(value) in six.integer_types)
        self._publication = value

    @property
    def args(self):
        if self._args is None and self._from_fbs:
            if self._from_fbs.ArgsLength():
                self._args = cbor.loads(bytes(self._from_fbs.ArgsAsBytes()))
        return self._args

    @args.setter
    def args(self, value):
        assert(value is None or type(value) in [list, tuple])
        self._args = value

    @property
    def kwargs(self):
        if self._kwargs is None and self._from_fbs:
            if self._from_fbs.KwargsLength():
                self._kwargs = cbor.loads(bytes(self._from_fbs.KwargsAsBytes()))
        return self._kwargs

    @kwargs.setter
    def kwargs(self, value):
        assert(value is None or type(value) == dict)
        self._kwargs = value

    @property
    def payload(self):
        if self._payload is None and self._from_fbs:
            if self._from_fbs.PayloadLength():
                self._payload = self._from_fbs.PayloadAsBytes()
        return self._payload

    @payload.setter
    def payload(self, value):
        assert value is None or type(value) == bytes
        self._payload = value

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
                self._publisher_authid = s.decode('utf8')
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
                self._publisher_authrole = s.decode('utf8')
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
                self._topic = s.decode('utf8')
        return self._topic

    @topic.setter
    def topic(self, value):
        assert value is None or type(value) == str
        self._topic = value

    @property
    def retained(self):
        if self._retained is None and self._from_fbs:
            self._retained = self._from_fbs.Retained()
        return self._retained

    @retained.setter
    def retained(self, value):
        assert value is None or type(value) == bool
        self._retained = value

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

    @property
    def enc_algo(self):
        if self._enc_algo is None and self._from_fbs:
            enc_algo = self._from_fbs.EncAlgo()
            if enc_algo:
                self._enc_algo = enc_algo
        return self._enc_algo

    @enc_algo.setter
    def enc_algo(self, value):
        assert value is None or value in [ENC_ALGO_CRYPTOBOX, ENC_ALGO_MQTT, ENC_ALGO_XBR]
        self._enc_algo = value

    @property
    def enc_key(self):
        if self._enc_key is None and self._from_fbs:
            if self._from_fbs.EncKeyLength():
                self._enc_key = self._from_fbs.EncKeyAsBytes()
        return self._enc_key

    @enc_key.setter
    def enc_key(self, value):
        assert value is None or type(value) == bytes
        self._enc_key = value

    @property
    def enc_serializer(self):
        if self._enc_serializer is None and self._from_fbs:
            enc_serializer = self._from_fbs.EncSerializer()
            if enc_serializer:
                self._enc_serializer = enc_serializer
        return self._enc_serializer

    @enc_serializer.setter
    def enc_serializer(self, value):
        assert value is None or value in [ENC_SER_JSON, ENC_SER_MSGPACK, ENC_SER_CBOR, ENC_SER_UBJSON]
        self._enc_serializer = value

    @property
    def forward_for(self):
        # FIXME
        return self._forward_for

    @forward_for.setter
    def forward_for(self, value):
        # FIXME
        self._forward_for = value

    @staticmethod
    def cast(buf):
        return Event(from_fbs=message_fbs.Event.GetRootAsEvent(buf, 0))

    def build(self, builder):

        args = self.args
        if args:
            args = builder.CreateByteVector(cbor.dumps(args))

        kwargs = self.kwargs
        if kwargs:
            kwargs = builder.CreateByteVector(cbor.dumps(kwargs))

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

        enc_key = self.enc_key
        if enc_key:
            enc_key = builder.CreateByteVector(enc_key)

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
        if self.x_acknowledged_delivery is not None:
            message_fbs.EventGen.EventAddAcknowledge(builder, self.x_acknowledged_delivery)

        if self.enc_algo:
            message_fbs.EventGen.EventAddEncAlgo(builder, self.enc_algo)
        if enc_key:
            message_fbs.EventGen.EventAddEncKey(builder, enc_key)
        if self.enc_serializer:
            message_fbs.EventGen.EventAddEncSerializer(builder, self.enc_serializer)

        # FIXME: add forward_for

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
        assert(len(wmsg) > 0 and wmsg[0] == Event.MESSAGE_TYPE)

        if len(wmsg) not in (4, 5, 6):
            raise ProtocolError("invalid message length {0} for EVENT".format(len(wmsg)))

        subscription = check_or_raise_id(wmsg[1], u"'subscription' in EVENT")
        publication = check_or_raise_id(wmsg[2], u"'publication' in EVENT")
        details = check_or_raise_extra(wmsg[3], u"'details' in EVENT")

        args = None
        kwargs = None
        payload = None
        enc_algo = None
        enc_key = None
        enc_serializer = None

        if len(wmsg) == 5 and type(wmsg[4]) == six.binary_type:

            payload = wmsg[4]

            enc_algo = details.get(u'enc_algo', None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError("invalid value {0} for 'enc_algo' detail in EVENT".format(enc_algo))

            enc_key = details.get(u'enc_key', None)
            if enc_key and type(enc_key) != six.text_type:
                raise ProtocolError("invalid type {0} for 'enc_key' detail in EVENT".format(type(enc_key)))

            enc_serializer = details.get(u'enc_serializer', None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError("invalid value {0} for 'enc_serializer' detail in EVENT".format(enc_serializer))

        else:
            if len(wmsg) > 4:
                args = wmsg[4]
                if args is not None and type(args) != list:
                    raise ProtocolError("invalid type {0} for 'args' in EVENT".format(type(args)))
            if len(wmsg) > 5:
                kwargs = wmsg[5]
                if type(kwargs) != dict:
                    raise ProtocolError("invalid type {0} for 'kwargs' in EVENT".format(type(kwargs)))

        publisher = None
        publisher_authid = None
        publisher_authrole = None
        topic = None
        retained = None
        forward_for = None
        x_acknowledged_delivery = None

        if u'publisher' in details:

            detail_publisher = details[u'publisher']
            if type(detail_publisher) not in six.integer_types:
                raise ProtocolError("invalid type {0} for 'publisher' detail in EVENT".format(type(detail_publisher)))

            publisher = detail_publisher

        if u'publisher_authid' in details:

            detail_publisher_authid = details[u'publisher_authid']
            if type(detail_publisher_authid) != six.text_type:
                raise ProtocolError("invalid type {0} for 'publisher_authid' detail in EVENT".format(type(detail_publisher_authid)))

            publisher_authid = detail_publisher_authid

        if u'publisher_authrole' in details:

            detail_publisher_authrole = details[u'publisher_authrole']
            if type(detail_publisher_authrole) != six.text_type:
                raise ProtocolError("invalid type {0} for 'publisher_authrole' detail in EVENT".format(type(detail_publisher_authrole)))

            publisher_authrole = detail_publisher_authrole

        if u'topic' in details:

            detail_topic = details[u'topic']
            if type(detail_topic) != six.text_type:
                raise ProtocolError("invalid type {0} for 'topic' detail in EVENT".format(type(detail_topic)))

            topic = detail_topic

        if u'retained' in details:
            retained = details[u'retained']
            if type(retained) != bool:
                raise ProtocolError("invalid type {0} for 'retained' detail in EVENT".format(type(retained)))

        if u'x_acknowledged_delivery' in details:
            x_acknowledged_delivery = details[u'x_acknowledged_delivery']
            if type(x_acknowledged_delivery) != bool:
                raise ProtocolError("invalid type {0} for 'x_acknowledged_delivery' detail in EVENT".format(type(x_acknowledged_delivery)))

        if u'forward_for' in details:
            forward_for = details[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in EVENT")

        obj = Event(subscription,
                    publication,
                    args=args,
                    kwargs=kwargs,
                    payload=payload,
                    publisher=publisher,
                    publisher_authid=publisher_authid,
                    publisher_authrole=publisher_authrole,
                    topic=topic,
                    retained=retained,
                    x_acknowledged_delivery=x_acknowledged_delivery,
                    enc_algo=enc_algo,
                    enc_key=enc_key,
                    enc_serializer=enc_serializer,
                    forward_for=forward_for)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {}

        if self.publisher is not None:
            details[u'publisher'] = self.publisher

        if self.publisher_authid is not None:
            details[u'publisher_authid'] = self.publisher_authid

        if self.publisher_authrole is not None:
            details[u'publisher_authrole'] = self.publisher_authrole

        if self.topic is not None:
            details[u'topic'] = self.topic

        if self.retained is not None:
            details[u'retained'] = self.retained

        if self.x_acknowledged_delivery is not None:
            details[u'x_acknowledged_delivery'] = self.x_acknowledged_delivery

        if self.forward_for is not None:
            details[u'forward_for'] = self.forward_for

        if self.payload:
            if self.enc_algo is not None:
                details[u'enc_algo'] = self.enc_algo
            if self.enc_key is not None:
                details[u'enc_key'] = self.enc_key
            if self.enc_serializer is not None:
                details[u'enc_serializer'] = self.enc_serializer
            return [Event.MESSAGE_TYPE, self.subscription, self.publication, details, self.payload]
        else:
            if self.kwargs:
                return [Event.MESSAGE_TYPE, self.subscription, self.publication, details, self.args, self.kwargs]
            elif self.args:
                return [Event.MESSAGE_TYPE, self.subscription, self.publication, details, self.args]
            else:
                return [Event.MESSAGE_TYPE, self.subscription, self.publication, details]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Event(subscription={}, publication={}, args={}, kwargs={}, publisher={}, publisher_authid={}, publisher_authrole={}, topic={}, retained={}, enc_algo={}, enc_key={}, enc_serializer={}, payload={}, forward_for={})".format(self.subscription, self.publication, self.args, self.kwargs, self.publisher, self.publisher_authid, self.publisher_authrole, self.topic, self.retained, self.enc_algo, self.enc_key, self.enc_serializer, b2a(self.payload), self.forward_for)


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
        'publication',
    )

    def __init__(self, publication):
        """

        :param publication: The publication ID for the sent event.
        :type publication: int
        """
        assert(type(publication) in six.integer_types)

        Message.__init__(self)
        self.publication = publication

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == EventReceived.MESSAGE_TYPE)

        if len(wmsg) != 2:
            raise ProtocolError("invalid message length {0} for EVENT_RECEIVED".format(len(wmsg)))

        publication = check_or_raise_id(wmsg[1], u"'publication' in EVENT_RECEIVED")

        obj = EventReceived(publication)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [EventReceived.MESSAGE_TYPE, self.publication]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"EventReceived(publication={})".format(self.publication)


class Call(Message):
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

    __slots__ = (
        'request',
        'procedure',
        'args',
        'kwargs',
        'payload',
        'timeout',
        'receive_progress',
        'enc_algo',
        'enc_key',
        'enc_serializer',
        'caller',
        'caller_authid',
        'caller_authrole',
        'forward_for',
    )

    def __init__(self,
                 request,
                 procedure,
                 args=None,
                 kwargs=None,
                 payload=None,
                 timeout=None,
                 receive_progress=None,
                 enc_algo=None,
                 enc_key=None,
                 enc_serializer=None,
                 caller=None,
                 caller_authid=None,
                 caller_authrole=None,
                 forward_for=None):
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
        assert(type(request) in six.integer_types)
        assert(type(procedure) == six.text_type)
        assert(args is None or type(args) in [list, tuple])
        assert(kwargs is None or type(kwargs) == dict)
        assert(payload is None or type(payload) == six.binary_type)
        assert(payload is None or (payload is not None and args is None and kwargs is None))
        assert(timeout is None or type(timeout) in six.integer_types)
        assert(receive_progress is None or type(receive_progress) == bool)

        # payload transparency related knobs
        assert(enc_algo is None or is_valid_enc_algo(enc_algo))
        assert(enc_key is None or type(enc_key) == six.text_type)
        assert(enc_serializer is None or is_valid_enc_serializer(enc_serializer))
        assert((enc_algo is None and enc_key is None and enc_serializer is None) or (payload is not None and enc_algo is not None))

        assert(caller is None or type(caller) in six.integer_types)
        assert(caller_authid is None or type(caller_authid) == six.text_type)
        assert(caller_authrole is None or type(caller_authrole) == six.text_type)

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self)
        self.request = request
        self.procedure = procedure
        self.args = args
        self.kwargs = _validate_kwargs(kwargs)
        self.payload = payload
        self.timeout = timeout
        self.receive_progress = receive_progress

        # payload transparency related knobs
        self.enc_algo = enc_algo
        self.enc_key = enc_key
        self.enc_serializer = enc_serializer

        # message forwarding
        self.caller = caller
        self.caller_authid = caller_authid
        self.caller_authrole = caller_authrole
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Call.MESSAGE_TYPE)

        if len(wmsg) not in (4, 5, 6):
            raise ProtocolError("invalid message length {0} for CALL".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in CALL")
        options = check_or_raise_extra(wmsg[2], u"'options' in CALL")
        procedure = check_or_raise_uri(wmsg[3], u"'procedure' in CALL")

        args = None
        kwargs = None
        payload = None
        enc_algo = None
        enc_key = None
        enc_serializer = None

        if len(wmsg) == 5 and type(wmsg[4]) in [six.text_type, six.binary_type]:

            payload = wmsg[4]

            enc_algo = options.get(u'enc_algo', None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError("invalid value {0} for 'enc_algo' detail in CALL".format(enc_algo))

            enc_key = options.get(u'enc_key', None)
            if enc_key and type(enc_key) != six.text_type:
                raise ProtocolError("invalid type {0} for 'enc_key' detail in CALL".format(type(enc_key)))

            enc_serializer = options.get(u'enc_serializer', None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError("invalid value {0} for 'enc_serializer' detail in CALL".format(enc_serializer))

        else:
            if len(wmsg) > 4:
                args = wmsg[4]
                if args is not None and type(args) != list:
                    raise ProtocolError("invalid type {0} for 'args' in CALL".format(type(args)))

            if len(wmsg) > 5:
                kwargs = wmsg[5]
                if type(kwargs) != dict:
                    raise ProtocolError("invalid type {0} for 'kwargs' in CALL".format(type(kwargs)))

        timeout = None
        receive_progress = None
        caller = None
        caller_authid = None
        caller_authrole = None
        forward_for = None

        if u'timeout' in options:

            option_timeout = options[u'timeout']
            if type(option_timeout) not in six.integer_types:
                raise ProtocolError("invalid type {0} for 'timeout' option in CALL".format(type(option_timeout)))

            if option_timeout < 0:
                raise ProtocolError("invalid value {0} for 'timeout' option in CALL".format(option_timeout))

            timeout = option_timeout

        if u'receive_progress' in options:

            option_receive_progress = options[u'receive_progress']
            if type(option_receive_progress) != bool:
                raise ProtocolError("invalid type {0} for 'receive_progress' option in CALL".format(type(option_receive_progress)))

            receive_progress = option_receive_progress

        if u'caller' in options:

            option_caller = options[u'caller']
            if type(option_caller) not in six.integer_types:
                raise ProtocolError("invalid type {0} for 'caller' detail in CALL".format(type(option_caller)))

            caller = option_caller

        if u'caller_authid' in options:

            option_caller_authid = options[u'caller_authid']
            if type(option_caller_authid) != six.text_type:
                raise ProtocolError("invalid type {0} for 'caller_authid' detail in CALL".format(type(option_caller_authid)))

            caller_authid = option_caller_authid

        if u'caller_authrole' in options:

            option_caller_authrole = options[u'caller_authrole']
            if type(option_caller_authrole) != six.text_type:
                raise ProtocolError("invalid type {0} for 'caller_authrole' detail in CALL".format(type(option_caller_authrole)))

            caller_authrole = option_caller_authrole

        if u'forward_for' in options:
            forward_for = options[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in CALL")

        obj = Call(request,
                   procedure,
                   args=args,
                   kwargs=kwargs,
                   payload=payload,
                   timeout=timeout,
                   receive_progress=receive_progress,
                   enc_algo=enc_algo,
                   enc_key=enc_key,
                   enc_serializer=enc_serializer,
                   caller=caller,
                   caller_authid=caller_authid,
                   caller_authrole=caller_authrole,
                   forward_for=forward_for)

        return obj

    def marshal_options(self):
        options = {}

        if self.timeout is not None:
            options[u'timeout'] = self.timeout

        if self.receive_progress is not None:
            options[u'receive_progress'] = self.receive_progress

        if self.payload:
            if self.enc_algo is not None:
                options[u'enc_algo'] = self.enc_algo
            if self.enc_key is not None:
                options[u'enc_key'] = self.enc_key
            if self.enc_serializer is not None:
                options[u'enc_serializer'] = self.enc_serializer

        if self.caller is not None:
            options[u'caller'] = self.caller
        if self.caller_authid is not None:
            options[u'caller_authid'] = self.caller_authid
        if self.caller_authrole is not None:
            options[u'caller_authrole'] = self.caller_authrole

        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        return options

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        options = self.marshal_options()

        if self.payload:
            return [Call.MESSAGE_TYPE, self.request, options, self.procedure, self.payload]
        else:
            if self.kwargs:
                return [Call.MESSAGE_TYPE, self.request, options, self.procedure, self.args, self.kwargs]
            elif self.args:
                return [Call.MESSAGE_TYPE, self.request, options, self.procedure, self.args]
            else:
                return [Call.MESSAGE_TYPE, self.request, options, self.procedure]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Call(request={}, procedure={}, args={}, kwargs={}, timeout={}, receive_progress={}, enc_algo={}, enc_key={}, enc_serializer={}, payload={}, caller={}, caller_authid={}, caller_authrole={}, forward_for={})".format(self.request, self.procedure, self.args, self.kwargs, self.timeout, self.receive_progress, self.enc_algo, self.enc_key, self.enc_serializer, b2a(self.payload), self.caller, self.caller_authid, self.caller_authrole, self.forward_for)


class Cancel(Message):
    """
    A WAMP ``CANCEL`` message.

    Format: ``[CANCEL, CALL.Request|id, Options|dict]``

    See: https://wamp-proto.org/static/rfc/draft-oberstet-hybi-crossbar-wamp.html#rfc.section.14.3.4
    """

    MESSAGE_TYPE = 49
    """
    The WAMP message code for this type of message.
    """

    SKIP = u'skip'
    KILL = u'kill'
    KILLNOWAIT = u'killnowait'

    __slots__ = (
        'request',
        'mode',
        'forward_for',
    )

    def __init__(self, request, mode=None, forward_for=None):
        """

        :param request: The WAMP request ID of the original `CALL` to cancel.
        :type request: int

        :param mode: Specifies how to cancel the call (``"skip"``, ``"killnowait"`` or ``"kill"``).
        :type mode: str or None

        :param forward_for: When this Cancel is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert(type(request) in six.integer_types)
        assert(mode is None or type(mode) == six.text_type)
        assert(mode in [None, self.SKIP, self.KILLNOWAIT, self.KILL])
        assert(forward_for is None or type(forward_for) == list)

        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self)
        self.request = request
        self.mode = mode

        # message forwarding
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Cancel.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for CANCEL".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in CANCEL")
        options = check_or_raise_extra(wmsg[2], u"'options' in CANCEL")

        # options
        #
        mode = None
        forward_for = None

        if u'mode' in options:

            option_mode = options[u'mode']
            if type(option_mode) != six.text_type:
                raise ProtocolError("invalid type {0} for 'mode' option in CANCEL".format(type(option_mode)))

            if option_mode not in [Cancel.SKIP, Cancel.KILLNOWAIT, Cancel.KILL]:
                raise ProtocolError("invalid value '{0}' for 'mode' option in CANCEL".format(option_mode))

            mode = option_mode

        if u'forward_for' in options:
            forward_for = options[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in CANCEL")

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
            options[u'mode'] = self.mode
        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        return [Cancel.MESSAGE_TYPE, self.request, options]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Cancel(request={0}, mode={1})".format(self.request, self.mode)


class Result(Message):
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

    __slots__ = (
        'request',
        'args',
        'kwargs',
        'payload',
        'progress',
        'enc_algo',
        'enc_key',
        'enc_serializer',
        'callee',
        'callee_authid',
        'callee_authrole',
        'forward_for',
    )

    def __init__(self,
                 request,
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
                 forward_for=None):
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
        assert(type(request) in six.integer_types)
        assert(args is None or type(args) in [list, tuple])
        assert(kwargs is None or type(kwargs) == dict)
        assert(payload is None or type(payload) == six.binary_type)
        assert(payload is None or (payload is not None and args is None and kwargs is None))
        assert(progress is None or type(progress) == bool)

        assert(enc_algo is None or is_valid_enc_algo(enc_algo))
        assert(enc_key is None or type(enc_key) == six.text_type)
        assert(enc_serializer is None or is_valid_enc_serializer(enc_serializer))
        assert((enc_algo is None and enc_key is None and enc_serializer is None) or (payload is not None and enc_algo is not None))

        assert(callee is None or type(callee) in six.integer_types)
        assert(callee_authid is None or type(callee_authid) == six.text_type)
        assert(callee_authrole is None or type(callee_authrole) == six.text_type)

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self)
        self.request = request
        self.args = args
        self.kwargs = _validate_kwargs(kwargs)
        self.payload = payload
        self.progress = progress

        # payload transparency related knobs
        self.enc_algo = enc_algo
        self.enc_key = enc_key
        self.enc_serializer = enc_serializer

        # effective callee that responded with the result
        self.callee = callee
        self.callee_authid = callee_authid
        self.callee_authrole = callee_authrole

        # message forwarding
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Result.MESSAGE_TYPE)

        if len(wmsg) not in (3, 4, 5):
            raise ProtocolError("invalid message length {0} for RESULT".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in RESULT")
        details = check_or_raise_extra(wmsg[2], u"'details' in RESULT")

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

        if len(wmsg) == 4 and type(wmsg[3]) in [six.text_type, six.binary_type]:

            payload = wmsg[3]

            enc_algo = details.get(u'enc_algo', None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError("invalid value {0} for 'enc_algo' detail in RESULT".format(enc_algo))

            enc_key = details.get(u'enc_key', None)
            if enc_key and type(enc_key) != six.text_type:
                raise ProtocolError("invalid type {0} for 'enc_key' detail in RESULT".format(type(enc_key)))

            enc_serializer = details.get(u'enc_serializer', None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError("invalid value {0} for 'enc_serializer' detail in RESULT".format(enc_serializer))

        else:
            if len(wmsg) > 3:
                args = wmsg[3]
                if args is not None and type(args) != list:
                    raise ProtocolError("invalid type {0} for 'args' in RESULT".format(type(args)))

            if len(wmsg) > 4:
                kwargs = wmsg[4]
                if type(kwargs) != dict:
                    raise ProtocolError("invalid type {0} for 'kwargs' in RESULT".format(type(kwargs)))

        if u'progress' in details:

            detail_progress = details[u'progress']
            if type(detail_progress) != bool:
                raise ProtocolError("invalid type {0} for 'progress' option in RESULT".format(type(detail_progress)))

            progress = detail_progress

        if u'callee' in details:

            detail_callee = details[u'callee']
            if type(detail_callee) not in six.integer_types:
                raise ProtocolError("invalid type {0} for 'callee' detail in RESULT".format(type(detail_callee)))

            callee = detail_callee

        if u'callee_authid' in details:

            detail_callee_authid = details[u'callee_authid']
            if type(detail_callee_authid) != six.text_type:
                raise ProtocolError("invalid type {0} for 'callee_authid' detail in RESULT".format(type(detail_callee_authid)))

            callee_authid = detail_callee_authid

        if u'callee_authrole' in details:

            detail_callee_authrole = details[u'callee_authrole']
            if type(detail_callee_authrole) != six.text_type:
                raise ProtocolError("invalid type {0} for 'callee_authrole' detail in RESULT".format(type(detail_callee_authrole)))

            callee_authrole = detail_callee_authrole

        if u'forward_for' in details:
            forward_for = details[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in RESULT")

        obj = Result(request,
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
                     forward_for=forward_for)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        details = {}

        if self.progress is not None:
            details[u'progress'] = self.progress

        if self.callee is not None:
            details[u'callee'] = self.callee
        if self.callee_authid is not None:
            details[u'callee_authid'] = self.callee_authid
        if self.callee_authrole is not None:
            details[u'callee_authrole'] = self.callee_authrole
        if self.forward_for is not None:
            details[u'forward_for'] = self.forward_for

        if self.payload:
            if self.enc_algo is not None:
                details[u'enc_algo'] = self.enc_algo
            if self.enc_key is not None:
                details[u'enc_key'] = self.enc_key
            if self.enc_serializer is not None:
                details[u'enc_serializer'] = self.enc_serializer
            return [Result.MESSAGE_TYPE, self.request, details, self.payload]
        else:
            if self.kwargs:
                return [Result.MESSAGE_TYPE, self.request, details, self.args, self.kwargs]
            elif self.args:
                return [Result.MESSAGE_TYPE, self.request, details, self.args]
            else:
                return [Result.MESSAGE_TYPE, self.request, details]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Result(request={0}, args={1}, kwargs={2}, progress={3}, enc_algo={4}, enc_key={5}, enc_serializer={6}, payload={7}, callee={8}, callee_authid={9}, callee_authrole={10}, forward_for={11})".format(self.request, self.args, self.kwargs, self.progress, self.enc_algo, self.enc_key, self.enc_serializer, b2a(self.payload), self.callee, self.callee_authid, self.callee_authrole, self.forward_for)


class Register(Message):
    """
    A WAMP ``REGISTER`` message.

    Format: ``[REGISTER, Request|id, Options|dict, Procedure|uri]``
    """

    MESSAGE_TYPE = 64
    """
    The WAMP message code for this type of message.
    """

    MATCH_EXACT = u'exact'
    MATCH_PREFIX = u'prefix'
    MATCH_WILDCARD = u'wildcard'

    INVOKE_SINGLE = u'single'
    INVOKE_FIRST = u'first'
    INVOKE_LAST = u'last'
    INVOKE_ROUNDROBIN = u'roundrobin'
    INVOKE_RANDOM = u'random'
    INVOKE_ALL = u'all'

    __slots__ = (
        'request',
        'procedure',
        'match',
        'invoke',
        'concurrency',
        'force_reregister',
        'forward_for',
    )

    def __init__(self,
                 request,
                 procedure,
                 match=None,
                 invoke=None,
                 concurrency=None,
                 force_reregister=None,
                 forward_for=None):
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
        assert(type(request) in six.integer_types)
        assert(type(procedure) == six.text_type)
        assert(match is None or type(match) == six.text_type)
        assert(match is None or match in [Register.MATCH_EXACT, Register.MATCH_PREFIX, Register.MATCH_WILDCARD])
        assert(invoke is None or type(invoke) == six.text_type)
        assert(invoke is None or invoke in [Register.INVOKE_SINGLE, Register.INVOKE_FIRST, Register.INVOKE_LAST, Register.INVOKE_ROUNDROBIN, Register.INVOKE_RANDOM])
        assert(concurrency is None or (type(concurrency) in six.integer_types and concurrency > 0))
        assert force_reregister in [None, True, False]
        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self)
        self.request = request
        self.procedure = procedure
        self.match = match or Register.MATCH_EXACT
        self.invoke = invoke or Register.INVOKE_SINGLE
        self.concurrency = concurrency
        self.force_reregister = force_reregister
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Register.MESSAGE_TYPE)

        if len(wmsg) != 4:
            raise ProtocolError("invalid message length {0} for REGISTER".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in REGISTER")
        options = check_or_raise_extra(wmsg[2], u"'options' in REGISTER")

        match = Register.MATCH_EXACT
        invoke = Register.INVOKE_SINGLE
        concurrency = None
        force_reregister = None
        forward_for = None

        if u'match' in options:

            option_match = options[u'match']
            if type(option_match) != six.text_type:
                raise ProtocolError("invalid type {0} for 'match' option in REGISTER".format(type(option_match)))

            if option_match not in [Register.MATCH_EXACT, Register.MATCH_PREFIX, Register.MATCH_WILDCARD]:
                raise ProtocolError("invalid value {0} for 'match' option in REGISTER".format(option_match))

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

        procedure = check_or_raise_uri(wmsg[3], u"'procedure' in REGISTER", allow_empty_components=allow_empty_components, allow_last_empty=allow_last_empty)

        if u'invoke' in options:

            option_invoke = options[u'invoke']
            if type(option_invoke) != six.text_type:
                raise ProtocolError("invalid type {0} for 'invoke' option in REGISTER".format(type(option_invoke)))

            if option_invoke not in [Register.INVOKE_SINGLE, Register.INVOKE_FIRST, Register.INVOKE_LAST, Register.INVOKE_ROUNDROBIN, Register.INVOKE_RANDOM]:
                raise ProtocolError("invalid value {0} for 'invoke' option in REGISTER".format(option_invoke))

            invoke = option_invoke

        if u'concurrency' in options:

            options_concurrency = options[u'concurrency']
            if type(options_concurrency) not in six.integer_types:
                raise ProtocolError("invalid type {0} for 'concurrency' option in REGISTER".format(type(options_concurrency)))

            if options_concurrency < 1:
                raise ProtocolError("invalid value {0} for 'concurrency' option in REGISTER".format(options_concurrency))

            concurrency = options_concurrency

        options_reregister = options.get(u'force_reregister', None)
        if options_reregister not in [True, False, None]:
            raise ProtocolError(
                "invalid type {0} for 'force_reregister option in REGISTER".format(
                    type(options_reregister)
                )
            )
        if options_reregister is not None:
            force_reregister = options_reregister

        if u'forward_for' in options:
            forward_for = options[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in REGISTER")

        obj = Register(request, procedure, match=match, invoke=invoke, concurrency=concurrency,
                       force_reregister=force_reregister, forward_for=forward_for)

        return obj

    def marshal_options(self):
        options = {}

        if self.match and self.match != Register.MATCH_EXACT:
            options[u'match'] = self.match

        if self.invoke and self.invoke != Register.INVOKE_SINGLE:
            options[u'invoke'] = self.invoke

        if self.concurrency:
            options[u'concurrency'] = self.concurrency

        if self.force_reregister is not None:
            options[u'force_reregister'] = self.force_reregister

        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        return options

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Register.MESSAGE_TYPE, self.request, self.marshal_options(), self.procedure]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Register(request={0}, procedure={1}, match={2}, invoke={3}, concurrency={4}, force_reregister={5}, forward_for={6})".format(self.request, self.procedure, self.match, self.invoke, self.concurrency, self.force_reregister, self.forward_for)


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
        'request',
        'registration',
    )

    def __init__(self, request, registration):
        """

        :param request: The request ID of the original ``REGISTER`` request.
        :type request: int

        :param registration: The registration ID for the registered procedure (or procedure pattern).
        :type registration: int
        """
        assert(type(request) in six.integer_types)
        assert(type(registration) in six.integer_types)

        Message.__init__(self)
        self.request = request
        self.registration = registration

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Registered.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for REGISTERED".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in REGISTERED")
        registration = check_or_raise_id(wmsg[2], u"'registration' in REGISTERED")

        obj = Registered(request, registration)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        return [Registered.MESSAGE_TYPE, self.request, self.registration]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Registered(request={0}, registration={1})".format(self.request, self.registration)


class Unregister(Message):
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

    __slots__ = (
        'request',
        'registration',
        'forward_for',
    )

    def __init__(self, request, registration, forward_for=None):
        """

        :param request: The WAMP request ID of this request.
        :type request: int

        :param registration: The registration ID for the registration to unregister.
        :type registration: int

        :param forward_for: When this Unregister is forwarded over a router-to-router link,
            or via an intermediary router.
        :type forward_for: list[dict]
        """
        assert(type(request) in six.integer_types)
        assert(type(registration) in six.integer_types)

        Message.__init__(self)
        self.request = request
        self.registration = registration
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Unregister.MESSAGE_TYPE)

        if len(wmsg) not in [3, 4]:
            raise ProtocolError("invalid message length {0} for WAMP UNREGISTER".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in UNREGISTER")
        registration = check_or_raise_id(wmsg[2], u"'registration' in UNREGISTER")

        options = None
        if len(wmsg) > 3:
            options = check_or_raise_extra(wmsg[3], u"'options' in UNREGISTER")

        forward_for = None
        if options and u'forward_for' in options:
            forward_for = options[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in UNREGISTER")

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
                u'forward_for': self.forward_for,
            }
            return [Unregister.MESSAGE_TYPE, self.request, self.registration, options]
        else:
            return [Unregister.MESSAGE_TYPE, self.request, self.registration]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Unregister(request={0}, registration={1})".format(self.request, self.registration)


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
        'request',
        'registration',
        'reason',
    )

    def __init__(self, request, registration=None, reason=None):
        """

        :param request: The request ID of the original ``UNREGISTER`` request.
        :type request: int

        :param registration: If unregister was actively triggered by router, the ID
            of the registration revoked.
        :type registration: int or None

        :param reason: The reason (an URI) for revocation.
        :type reason: str or None.
        """
        assert(type(request) in six.integer_types)
        assert(registration is None or type(registration) in six.integer_types)
        assert(reason is None or type(reason) == six.text_type)
        assert((request != 0 and registration is None) or (request == 0 and registration != 0))

        Message.__init__(self)
        self.request = request
        self.registration = registration
        self.reason = reason

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Unregistered.MESSAGE_TYPE)

        if len(wmsg) not in [2, 3]:
            raise ProtocolError("invalid message length {0} for UNREGISTERED".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in UNREGISTERED")

        registration = None
        reason = None

        if len(wmsg) > 2:

            details = check_or_raise_extra(wmsg[2], u"'details' in UNREGISTERED")

            if u"registration" in details:
                details_registration = details[u"registration"]
                if type(details_registration) not in six.integer_types:
                    raise ProtocolError("invalid type {0} for 'registration' detail in UNREGISTERED".format(type(details_registration)))
                registration = details_registration

            if u"reason" in details:
                reason = check_or_raise_uri(details[u"reason"], u"'reason' in UNREGISTERED")

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
                details[u"reason"] = self.reason
            if self.registration is not None:
                details[u"registration"] = self.registration
            return [Unregistered.MESSAGE_TYPE, self.request, details]
        else:
            return [Unregistered.MESSAGE_TYPE, self.request]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Unregistered(request={0}, reason={1}, registration={2})".format(self.request, self.reason, self.registration)


class Invocation(Message):
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

    __slots__ = (
        'request',
        'registration',
        'args',
        'kwargs',
        'payload',
        'timeout',
        'receive_progress',
        'caller',
        'caller_authid',
        'caller_authrole',
        'procedure',
        'enc_algo',
        'enc_key',
        'enc_serializer',
        'forward_for',
    )

    def __init__(self,
                 request,
                 registration,
                 args=None,
                 kwargs=None,
                 payload=None,
                 timeout=None,
                 receive_progress=None,
                 caller=None,
                 caller_authid=None,
                 caller_authrole=None,
                 procedure=None,
                 enc_algo=None,
                 enc_key=None,
                 enc_serializer=None,
                 forward_for=None):
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

        :param enc_algo: If using payload transparency, the encoding algorithm that was used to encode the payload.
        :type enc_algo: str or None

        :param enc_key: If using payload transparency with an encryption algorithm, the payload encryption key.
        :type enc_key: str or None

        :param enc_serializer: If using payload transparency, the payload object serializer that was used encoding the payload.
        :type enc_serializer: str or None

        :param forward_for: When this Call is forwarded for a client (or from an intermediary router).
        :type forward_for: list[dict]
        """
        assert(type(request) in six.integer_types)
        assert(type(registration) in six.integer_types)
        assert(args is None or type(args) in [list, tuple])
        assert(kwargs is None or type(kwargs) == dict)
        assert(payload is None or type(payload) == six.binary_type)
        assert(payload is None or (payload is not None and args is None and kwargs is None))
        assert(timeout is None or type(timeout) in six.integer_types)
        assert(receive_progress is None or type(receive_progress) == bool)
        assert(caller is None or type(caller) in six.integer_types)
        assert(caller_authid is None or type(caller_authid) == six.text_type)
        assert(caller_authrole is None or type(caller_authrole) == six.text_type)
        assert(procedure is None or type(procedure) == six.text_type)
        assert(enc_algo is None or is_valid_enc_algo(enc_algo))
        assert(enc_key is None or type(enc_key) == six.text_type)
        assert(enc_serializer is None or is_valid_enc_serializer(enc_serializer))
        assert((enc_algo is None and enc_key is None and enc_serializer is None) or (payload is not None and enc_algo is not None))

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self)
        self.request = request
        self.registration = registration
        self.args = args
        self.kwargs = _validate_kwargs(kwargs)
        self.payload = payload
        self.timeout = timeout
        self.receive_progress = receive_progress
        self.caller = caller
        self.caller_authid = caller_authid
        self.caller_authrole = caller_authrole
        self.procedure = procedure
        self.enc_algo = enc_algo
        self.enc_key = enc_key
        self.enc_serializer = enc_serializer

        # message forwarding
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Invocation.MESSAGE_TYPE)

        if len(wmsg) not in (4, 5, 6):
            raise ProtocolError("invalid message length {0} for INVOCATION".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in INVOCATION")
        registration = check_or_raise_id(wmsg[2], u"'registration' in INVOCATION")
        details = check_or_raise_extra(wmsg[3], u"'details' in INVOCATION")

        args = None
        kwargs = None
        payload = None
        enc_algo = None
        enc_key = None
        enc_serializer = None

        if len(wmsg) == 5 and type(wmsg[4]) == six.binary_type:

            payload = wmsg[4]

            enc_algo = details.get(u'enc_algo', None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError("invalid value {0} for 'enc_algo' detail in INVOCATION".format(enc_algo))

            enc_key = details.get(u'enc_key', None)
            if enc_key and type(enc_key) != six.text_type:
                raise ProtocolError("invalid type {0} for 'enc_key' detail in INVOCATION".format(type(enc_key)))

            enc_serializer = details.get(u'enc_serializer', None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError("invalid value {0} for 'enc_serializer' detail in INVOCATION".format(enc_serializer))

        else:
            if len(wmsg) > 4:
                args = wmsg[4]
                if args is not None and type(args) != list:
                    raise ProtocolError("invalid type {0} for 'args' in INVOCATION".format(type(args)))

            if len(wmsg) > 5:
                kwargs = wmsg[5]
                if type(kwargs) != dict:
                    raise ProtocolError("invalid type {0} for 'kwargs' in INVOCATION".format(type(kwargs)))

        timeout = None
        receive_progress = None
        caller = None
        caller_authid = None
        caller_authrole = None
        procedure = None
        forward_for = None

        if u'timeout' in details:

            detail_timeout = details[u'timeout']
            if type(detail_timeout) not in six.integer_types:
                raise ProtocolError("invalid type {0} for 'timeout' detail in INVOCATION".format(type(detail_timeout)))

            if detail_timeout < 0:
                raise ProtocolError("invalid value {0} for 'timeout' detail in INVOCATION".format(detail_timeout))

            timeout = detail_timeout

        if u'receive_progress' in details:

            detail_receive_progress = details[u'receive_progress']
            if type(detail_receive_progress) != bool:
                raise ProtocolError("invalid type {0} for 'receive_progress' detail in INVOCATION".format(type(detail_receive_progress)))

            receive_progress = detail_receive_progress

        if u'caller' in details:

            detail_caller = details[u'caller']
            if type(detail_caller) not in six.integer_types:
                raise ProtocolError("invalid type {0} for 'caller' detail in INVOCATION".format(type(detail_caller)))

            caller = detail_caller

        if u'caller_authid' in details:

            detail_caller_authid = details[u'caller_authid']
            if type(detail_caller_authid) != six.text_type:
                raise ProtocolError("invalid type {0} for 'caller_authid' detail in INVOCATION".format(type(detail_caller_authid)))

            caller_authid = detail_caller_authid

        if u'caller_authrole' in details:

            detail_caller_authrole = details[u'caller_authrole']
            if type(detail_caller_authrole) != six.text_type:
                raise ProtocolError("invalid type {0} for 'caller_authrole' detail in INVOCATION".format(type(detail_caller_authrole)))

            caller_authrole = detail_caller_authrole

        if u'procedure' in details:

            detail_procedure = details[u'procedure']
            if type(detail_procedure) != six.text_type:
                raise ProtocolError("invalid type {0} for 'procedure' detail in INVOCATION".format(type(detail_procedure)))

            procedure = detail_procedure

        if u'forward_for' in details:
            forward_for = details[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in INVOCATION")

        obj = Invocation(request,
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
                         enc_algo=enc_algo,
                         enc_key=enc_key,
                         enc_serializer=enc_serializer,
                         forward_for=forward_for)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        options = {}

        if self.timeout is not None:
            options[u'timeout'] = self.timeout

        if self.receive_progress is not None:
            options[u'receive_progress'] = self.receive_progress

        if self.caller is not None:
            options[u'caller'] = self.caller

        if self.caller_authid is not None:
            options[u'caller_authid'] = self.caller_authid

        if self.caller_authrole is not None:
            options[u'caller_authrole'] = self.caller_authrole

        if self.procedure is not None:
            options[u'procedure'] = self.procedure

        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        if self.payload:
            if self.enc_algo is not None:
                options[u'enc_algo'] = self.enc_algo
            if self.enc_key is not None:
                options[u'enc_key'] = self.enc_key
            if self.enc_serializer is not None:
                options[u'enc_serializer'] = self.enc_serializer
            return [Invocation.MESSAGE_TYPE, self.request, self.registration, options, self.payload]
        else:
            if self.kwargs:
                return [Invocation.MESSAGE_TYPE, self.request, self.registration, options, self.args, self.kwargs]
            elif self.args:
                return [Invocation.MESSAGE_TYPE, self.request, self.registration, options, self.args]
            else:
                return [Invocation.MESSAGE_TYPE, self.request, self.registration, options]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Invocation(request={0}, registration={1}, args={2}, kwargs={3}, timeout={4}, receive_progress={5}, caller={6}, caller_authid={7}, caller_authrole={8}, procedure={9}, enc_algo={10}, enc_key={11}, enc_serializer={12}, payload={13})".format(self.request, self.registration, self.args, self.kwargs, self.timeout, self.receive_progress, self.caller, self.caller_authid, self.caller_authrole, self.procedure, self.enc_algo, self.enc_key, self.enc_serializer, b2a(self.payload))


class Interrupt(Message):
    """
    A WAMP ``INTERRUPT`` message.

    Format: ``[INTERRUPT, INVOCATION.Request|id, Options|dict]``

    See: https://wamp-proto.org/static/rfc/draft-oberstet-hybi-crossbar-wamp.html#rfc.section.14.3.4
    """

    MESSAGE_TYPE = 69
    """
    The WAMP message code for this type of message.
    """

    KILL = u'kill'
    KILLNOWAIT = u'killnowait'

    __slots__ = (
        'request',
        'mode',
        'reason',
        'forward_for',
    )

    def __init__(self, request, mode=None, reason=None, forward_for=None):
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
        assert(type(request) in six.integer_types)
        assert(mode is None or type(mode) == six.text_type)
        assert(mode is None or mode in [self.KILL, self.KILLNOWAIT])
        assert(reason is None or type(reason) == six.text_type)

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self)
        self.request = request
        self.mode = mode
        self.reason = reason

        # message forwarding
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Interrupt.MESSAGE_TYPE)

        if len(wmsg) != 3:
            raise ProtocolError("invalid message length {0} for INTERRUPT".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in INTERRUPT")
        options = check_or_raise_extra(wmsg[2], u"'options' in INTERRUPT")

        # options
        #
        mode = None
        reason = None
        forward_for = None

        if u'mode' in options:

            option_mode = options[u'mode']
            if type(option_mode) != six.text_type:
                raise ProtocolError("invalid type {0} for 'mode' option in INTERRUPT".format(type(option_mode)))

            if option_mode not in [Interrupt.KILL, Interrupt.KILLNOWAIT]:
                raise ProtocolError("invalid value '{0}' for 'mode' option in INTERRUPT".format(option_mode))

            mode = option_mode

        if u'reason' in options:
            reason = check_or_raise_uri(options[u'reason'], u'"reason" in INTERRUPT')

        if u'forward_for' in options:
            forward_for = options[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in INTERRUPT")

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
            options[u'mode'] = self.mode

        if self.reason is not None:
            options[u'reason'] = self.reason

        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        return [Interrupt.MESSAGE_TYPE, self.request, options]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Interrupt(request={0}, mode={1}, reason={2})".format(self.request, self.mode, self.reason)


class Yield(Message):
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

    __slots__ = (
        'request',
        'args',
        'kwargs',
        'payload',
        'progress',
        'enc_algo',
        'enc_key',
        'enc_serializer',
        'callee',
        'callee_authid',
        'callee_authrole',
        'forward_for',
    )

    def __init__(self,
                 request,
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
                 forward_for=None):
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
        assert(type(request) in six.integer_types)
        assert(args is None or type(args) in [list, tuple])
        assert(kwargs is None or type(kwargs) == dict)
        assert(payload is None or type(payload) == six.binary_type)
        assert(payload is None or (payload is not None and args is None and kwargs is None))
        assert(progress is None or type(progress) == bool)
        assert(enc_algo is None or is_valid_enc_algo(enc_algo))
        assert((enc_algo is None and enc_key is None and enc_serializer is None) or (payload is not None and enc_algo is not None))
        assert(enc_key is None or type(enc_key) == six.text_type)
        assert(enc_serializer is None or is_valid_enc_serializer(enc_serializer))

        assert(callee is None or type(callee) in six.integer_types)
        assert(callee_authid is None or type(callee_authid) == six.text_type)
        assert(callee_authrole is None or type(callee_authrole) == six.text_type)

        assert(forward_for is None or type(forward_for) == list)
        if forward_for:
            for ff in forward_for:
                assert type(ff) == dict
                assert 'session' in ff and type(ff['session']) in six.integer_types
                assert 'authid' in ff and (ff['authid'] is None or type(ff['authid']) == six.text_type)
                assert 'authrole' in ff and type(ff['authrole']) == six.text_type

        Message.__init__(self)
        self.request = request
        self.args = args
        self.kwargs = _validate_kwargs(kwargs)
        self.payload = payload
        self.progress = progress
        self.enc_algo = enc_algo
        self.enc_key = enc_key
        self.enc_serializer = enc_serializer

        # effective callee that responded with the result
        self.callee = callee
        self.callee_authid = callee_authid
        self.callee_authrole = callee_authrole

        # message forwarding
        self.forward_for = forward_for

    @staticmethod
    def parse(wmsg):
        """
        Verifies and parses an unserialized raw message into an actual WAMP message instance.

        :param wmsg: The unserialized raw message.
        :type wmsg: list

        :returns: An instance of this class.
        """
        # this should already be verified by WampSerializer.unserialize
        assert(len(wmsg) > 0 and wmsg[0] == Yield.MESSAGE_TYPE)

        if len(wmsg) not in (3, 4, 5):
            raise ProtocolError("invalid message length {0} for YIELD".format(len(wmsg)))

        request = check_or_raise_id(wmsg[1], u"'request' in YIELD")
        options = check_or_raise_extra(wmsg[2], u"'options' in YIELD")

        args = None
        kwargs = None
        payload = None
        enc_algo = None
        enc_key = None
        enc_serializer = None

        if len(wmsg) == 4 and type(wmsg[3]) == six.binary_type:

            payload = wmsg[3]

            enc_algo = options.get(u'enc_algo', None)
            if enc_algo and not is_valid_enc_algo(enc_algo):
                raise ProtocolError("invalid value {0} for 'enc_algo' detail in YIELD".format(enc_algo))

            enc_key = options.get(u'enc_key', None)
            if enc_key and type(enc_key) != six.text_type:
                raise ProtocolError("invalid type {0} for 'enc_key' detail in YIELD".format(type(enc_key)))

            enc_serializer = options.get(u'enc_serializer', None)
            if enc_serializer and not is_valid_enc_serializer(enc_serializer):
                raise ProtocolError("invalid value {0} for 'enc_serializer' detail in YIELD".format(enc_serializer))

        else:
            if len(wmsg) > 3:
                args = wmsg[3]
                if args is not None and type(args) != list:
                    raise ProtocolError("invalid type {0} for 'args' in YIELD".format(type(args)))

            if len(wmsg) > 4:
                kwargs = wmsg[4]
                if type(kwargs) != dict:
                    raise ProtocolError("invalid type {0} for 'kwargs' in YIELD".format(type(kwargs)))

        progress = None
        callee = None
        callee_authid = None
        callee_authrole = None
        forward_for = None

        if u'progress' in options:

            option_progress = options[u'progress']
            if type(option_progress) != bool:
                raise ProtocolError("invalid type {0} for 'progress' option in YIELD".format(type(option_progress)))

            progress = option_progress

        if u'callee' in options:

            option_callee = options[u'callee']
            if type(option_callee) not in six.integer_types:
                raise ProtocolError("invalid type {0} for 'callee' detail in YIELD".format(type(option_callee)))

            callee = option_callee

        if u'callee_authid' in options:

            option_callee_authid = options[u'callee_authid']
            if type(option_callee_authid) != six.text_type:
                raise ProtocolError("invalid type {0} for 'callee_authid' detail in YIELD".format(type(option_callee_authid)))

            callee_authid = option_callee_authid

        if u'callee_authrole' in options:

            option_callee_authrole = options[u'callee_authrole']
            if type(option_callee_authrole) != six.text_type:
                raise ProtocolError("invalid type {0} for 'callee_authrole' detail in YIELD".format(type(option_callee_authrole)))

            callee_authrole = option_callee_authrole

        if u'forward_for' in options:
            forward_for = options[u'forward_for']
            valid = False
            if type(forward_for) == list:
                for ff in forward_for:
                    if type(ff) != dict:
                        break
                    if 'session' not in ff or type(ff['session']) not in six.integer_types:
                        break
                    if 'authid' not in ff or type(ff['authid']) != six.text_type:
                        break
                    if 'authrole' not in ff or type(ff['authrole']) != six.text_type:
                        break
                valid = True

            if not valid:
                raise ProtocolError("invalid type/value {0} for/within 'forward_for' option in YIELD")

        obj = Yield(request,
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
                    forward_for=forward_for)

        return obj

    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: The serialized raw message.
        :rtype: list
        """
        options = {}

        if self.progress is not None:
            options[u'progress'] = self.progress

        if self.callee is not None:
            options[u'callee'] = self.callee
        if self.callee_authid is not None:
            options[u'callee_authid'] = self.callee_authid
        if self.callee_authrole is not None:
            options[u'callee_authrole'] = self.callee_authrole
        if self.forward_for is not None:
            options[u'forward_for'] = self.forward_for

        if self.payload:
            if self.enc_algo is not None:
                options[u'enc_algo'] = self.enc_algo
            if self.enc_key is not None:
                options[u'enc_key'] = self.enc_key
            if self.enc_serializer is not None:
                options[u'enc_serializer'] = self.enc_serializer
            return [Yield.MESSAGE_TYPE, self.request, options, self.payload]
        else:
            if self.kwargs:
                return [Yield.MESSAGE_TYPE, self.request, options, self.args, self.kwargs]
            elif self.args:
                return [Yield.MESSAGE_TYPE, self.request, options, self.args]
            else:
                return [Yield.MESSAGE_TYPE, self.request, options]

    def __str__(self):
        """
        Returns string representation of this message.
        """
        return u"Yield(request={0}, args={1}, kwargs={2}, progress={3}, enc_algo={4}, enc_key={5}, enc_serializer={6}, payload={7}, callee={8}, callee_authid={9}, callee_authrole={10}, forward_for={11})".format(self.request, self.args, self.kwargs, self.progress, self.enc_algo, self.enc_key, self.enc_serializer, b2a(self.payload), self.callee, self.callee_authid, self.callee_authrole, self.forward_for)
