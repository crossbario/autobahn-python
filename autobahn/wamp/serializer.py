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

import os
import six
import struct
import platform

from autobahn.wamp.interfaces import IObjectSerializer, ISerializer
from autobahn.wamp.exception import ProtocolError
from autobahn.wamp import message

# note: __all__ must be a list here, since we dynamically
# extend it depending on availability of more serializers
__all__ = ['Serializer',
           'JsonObjectSerializer',
           'JsonSerializer']


SERID_TO_OBJSER = {}
SERID_TO_SER = {}


class Serializer(object):
    """
    Base class for WAMP serializers. A WAMP serializer is the core glue between
    parsed WAMP message objects and the bytes on wire (the transport).
    """

    # WAMP defines the following 24 message types
    MESSAGE_TYPE_MAP = {
        message.Hello.MESSAGE_TYPE: message.Hello,
        message.Welcome.MESSAGE_TYPE: message.Welcome,
        message.Abort.MESSAGE_TYPE: message.Abort,
        message.Challenge.MESSAGE_TYPE: message.Challenge,
        message.Authenticate.MESSAGE_TYPE: message.Authenticate,
        message.Goodbye.MESSAGE_TYPE: message.Goodbye,
        message.Error.MESSAGE_TYPE: message.Error,
        message.Publish.MESSAGE_TYPE: message.Publish,
        message.Published.MESSAGE_TYPE: message.Published,
        message.Subscribe.MESSAGE_TYPE: message.Subscribe,
        message.Subscribed.MESSAGE_TYPE: message.Subscribed,
        message.Unsubscribe.MESSAGE_TYPE: message.Unsubscribe,
        message.Unsubscribed.MESSAGE_TYPE: message.Unsubscribed,
        message.Event.MESSAGE_TYPE: message.Event,
        message.Call.MESSAGE_TYPE: message.Call,
        message.Cancel.MESSAGE_TYPE: message.Cancel,
        message.Result.MESSAGE_TYPE: message.Result,
        message.Register.MESSAGE_TYPE: message.Register,
        message.Registered.MESSAGE_TYPE: message.Registered,
        message.Unregister.MESSAGE_TYPE: message.Unregister,
        message.Unregistered.MESSAGE_TYPE: message.Unregistered,
        message.Invocation.MESSAGE_TYPE: message.Invocation,
        message.Interrupt.MESSAGE_TYPE: message.Interrupt,
        message.Yield.MESSAGE_TYPE: message.Yield
    }
    """
    Mapping of WAMP message type codes to WAMP message classes.
    """

    def __init__(self, serializer):
        """

        :param serializer: The object serializer to use for WAMP wire-level serialization.
        :type serializer: An object that implements :class:`autobahn.interfaces.IObjectSerializer`.
        """
        self._serializer = serializer

    def serialize(self, msg):
        """
        Implements :func:`autobahn.wamp.interfaces.ISerializer.serialize`
        """
        return msg.serialize(self._serializer), self._serializer.BINARY

    def unserialize(self, payload, isBinary=None):
        """
        Implements :func:`autobahn.wamp.interfaces.ISerializer.unserialize`
        """
        if isBinary is not None:
            if isBinary != self._serializer.BINARY:
                raise ProtocolError(
                    "invalid serialization of WAMP message (binary {0}, but expected {1})".format(isBinary,
                                                                                                  self._serializer.BINARY))
        try:
            raw_msgs = self._serializer.unserialize(payload)
        except Exception as e:
            raise ProtocolError("invalid serialization of WAMP message: {0} {1}".format(type(e).__name__, e))

        if self._serializer.NAME == u'flatbuffers':
            msgs = raw_msgs
        else:
            msgs = []
            for raw_msg in raw_msgs:

                if type(raw_msg) != list:
                    raise ProtocolError("invalid type {0} for WAMP message".format(type(raw_msg)))

                if len(raw_msg) == 0:
                    raise ProtocolError(u"missing message type in WAMP message")

                message_type = raw_msg[0]

                if type(message_type) not in six.integer_types:
                    # CBOR doesn't roundtrip number types
                    # https://bitbucket.org/bodhisnarkva/cbor/issues/6/number-types-dont-roundtrip
                    raise ProtocolError("invalid type {0} for WAMP message type".format(type(message_type)))

                Klass = self.MESSAGE_TYPE_MAP.get(message_type)

                if Klass is None:
                    raise ProtocolError("invalid WAMP message type {0}".format(message_type))

                # this might again raise `ProtocolError` ..
                msg = Klass.parse(raw_msg)

                msgs.append(msg)

        return msgs


# JSON serialization is always supported
_USE_UJSON = 'AUTOBAHN_USE_UJSON' in os.environ
if _USE_UJSON:
    try:
        import ujson
        _USE_UJSON = True
    except ImportError:
        import json
        _USE_UJSON = False
else:
    import json


if _USE_UJSON:
    # ujson doesn't support plugging into the JSON string parsing machinery ..
    print('WARNING: Autobahn is using ujson accelerated JSON module - will run faster,\nbut only on CPython and will loose ability to transport binary payload transparently!')
    _loads = ujson.loads
    _dumps = ujson.dumps
    _json = ujson
else:
    # print('Notice: Autobahn is using json built-in standard library module for JSON serialization')
    import base64

    class _WAMPJsonEncoder(json.JSONEncoder):

        def default(self, obj):
            if isinstance(obj, six.binary_type):
                return u'\x00' + base64.b64encode(obj).decode('ascii')
            else:
                return json.JSONEncoder.default(self, obj)

    #
    # the following is a hack. see http://bugs.python.org/issue29992
    #

    from json import scanner
    from json.decoder import scanstring

    def _parse_string(*args, **kwargs):
        s, idx = scanstring(*args, **kwargs)
        if s and s[0] == u'\x00':
            s = base64.b64decode(s[1:])
        return s, idx

    class _WAMPJsonDecoder(json.JSONDecoder):

        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(self, *args, **kwargs)
            self.parse_string = _parse_string

            # we need to recreate the internal scan function ..
            self.scan_once = scanner.py_make_scanner(self)

            # .. and we have to explicitly use the Py version,
            # not the C version, as the latter won't work
            # self.scan_once = scanner.make_scanner(self)

    def _loads(s):
        return json.loads(s, cls=_WAMPJsonDecoder)

    def _dumps(obj):
        return json.dumps(obj,
                          separators=(',', ':'),
                          ensure_ascii=False,
                          sort_keys=False,
                          cls=_WAMPJsonEncoder)

    _json = json


class JsonObjectSerializer(object):

    JSON_MODULE = _json
    """
    The JSON module used (now only stdlib).
    """

    NAME = u'json'

    BINARY = False

    def __init__(self, batched=False):
        """
        Ctor.

        :param batched: Flag that controls whether serializer operates in batched mode.
        :type batched: bool
        """
        self._batched = batched

    def serialize(self, obj):
        """
        Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.serialize`
        """
        s = _dumps(obj)
        if isinstance(s, six.text_type):
            s = s.encode('utf8')
        if self._batched:
            return s + b'\30'
        else:
            return s

    def unserialize(self, payload):
        """
        Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.unserialize`
        """
        if self._batched:
            chunks = payload.split(b'\30')[:-1]
        else:
            chunks = [payload]
        if len(chunks) == 0:
            raise Exception("batch format error")
        return [_loads(data.decode('utf8')) for data in chunks]


IObjectSerializer.register(JsonObjectSerializer)
SERID_TO_OBJSER[JsonObjectSerializer.NAME] = JsonObjectSerializer


class JsonSerializer(Serializer):

    SERIALIZER_ID = u"json"
    """
    ID used as part of the WebSocket subprotocol name to identify the
    serializer with WAMP-over-WebSocket.
    """

    RAWSOCKET_SERIALIZER_ID = 1
    """
    ID used in lower four bits of second octet in RawSocket opening
    handshake identify the serializer with WAMP-over-RawSocket.
    """

    MIME_TYPE = u"application/json"
    """
    MIME type announced in HTTP request/response headers when running
    WAMP-over-Longpoll HTTP fallback.
    """

    def __init__(self, batched=False):
        """
        Ctor.

        :param batched: Flag to control whether to put this serialized into batched mode.
        :type batched: bool
        """
        Serializer.__init__(self, JsonObjectSerializer(batched=batched))
        if batched:
            self.SERIALIZER_ID = u"json.batched"


ISerializer.register(JsonSerializer)
SERID_TO_SER[JsonSerializer.SERIALIZER_ID] = JsonSerializer


_HAS_MSGPACK = False
_USE_UMSGPACK = platform.python_implementation() == u'PyPy' or 'AUTOBAHN_USE_UMSGPACK' in os.environ

if not _USE_UMSGPACK:
    try:
        # on CPython, use an impl. with native extension:
        # https://pypi.org/project/msgpack/
        # https://github.com/msgpack/msgpack-python
        import msgpack
    except ImportError:
        pass
    else:
        _HAS_MSGPACK = True
        _packb = lambda obj: msgpack.packb(obj, use_bin_type=True)  # noqa
        _unpackb = lambda data: msgpack.unpackb(data, raw=False)  # noqa
        _msgpack = msgpack
        # print('Notice: Autobahn is using msgpack library (with native extension, best on CPython) for MessagePack serialization')
else:
    try:
        # on PyPy in particular, use a pure python impl.:
        # https://pypi.python.org/pypi/u-msgpack-python
        # https://github.com/vsergeev/u-msgpack-python
        import umsgpack
    except ImportError:
        pass
    else:
        _HAS_MSGPACK = True
        _packb = umsgpack.packb
        _unpackb = umsgpack.unpackb
        _msgpack = umsgpack
        # print('Notice: Autobahn is using umsgpack library (pure Python, best on PyPy) for MessagePack serialization')


if _HAS_MSGPACK:

    class MsgPackObjectSerializer(object):

        NAME = u'msgpack'

        MSGPACK_MODULE = _msgpack

        BINARY = True
        """
        Flag that indicates whether this serializer needs a binary clean transport.
        """

        def __init__(self, batched=False):
            """

            :param batched: Flag that controls whether serializer operates in batched mode.
            :type batched: bool
            """
            self._batched = batched

        def serialize(self, obj):
            """
            Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.serialize`
            """
            data = _packb(obj)
            if self._batched:
                return struct.pack("!L", len(data)) + data
            else:
                return data

        def unserialize(self, payload):
            """
            Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.unserialize`
            """

            if self._batched:
                msgs = []
                N = len(payload)
                i = 0
                while i < N:
                    # read message length prefix
                    if i + 4 > N:
                        raise Exception("batch format error [1]")
                    l = struct.unpack("!L", payload[i:i + 4])[0]

                    # read message data
                    if i + 4 + l > N:
                        raise Exception("batch format error [2]")
                    data = payload[i + 4:i + 4 + l]

                    # append parsed raw message
                    msgs.append(_unpackb(data))

                    # advance until everything consumed
                    i = i + 4 + l

                if i != N:
                    raise Exception("batch format error [3]")
                return msgs

            else:
                unpacked = _unpackb(payload)
                return [unpacked]

    IObjectSerializer.register(MsgPackObjectSerializer)

    __all__.append('MsgPackObjectSerializer')
    SERID_TO_OBJSER[MsgPackObjectSerializer.NAME] = MsgPackObjectSerializer

    class MsgPackSerializer(Serializer):

        SERIALIZER_ID = u"msgpack"
        """
        ID used as part of the WebSocket subprotocol name to identify the
        serializer with WAMP-over-WebSocket.
        """

        RAWSOCKET_SERIALIZER_ID = 2
        """
        ID used in lower four bits of second octet in RawSocket opening
        handshake identify the serializer with WAMP-over-RawSocket.
        """

        MIME_TYPE = u"application/x-msgpack"
        """
        MIME type announced in HTTP request/response headers when running
        WAMP-over-Longpoll HTTP fallback.
        """

        def __init__(self, batched=False):
            """
            Ctor.

            :param batched: Flag to control whether to put this serialized into batched mode.
            :type batched: bool
            """
            Serializer.__init__(self, MsgPackObjectSerializer(batched=batched))
            if batched:
                self.SERIALIZER_ID = u"msgpack.batched"

    ISerializer.register(MsgPackSerializer)
    SERID_TO_SER[MsgPackSerializer.SERIALIZER_ID] = MsgPackSerializer

    __all__.append('MsgPackSerializer')


_HAS_CBOR = False
if 'AUTOBAHN_USE_CBOR2' in os.environ:
    try:
        # https://pypi.org/project/cbor2/
        # https://github.com/agronholm/cbor2
        import cbor2
    except ImportError:
        pass
    else:
        _HAS_CBOR = True
        _cbor_loads = cbor2.loads
        _cbor_dumps = cbor2.dumps
        _cbor = cbor2
        # print('Notice: Autobahn is using cbor2 library for CBOR serialization')
else:
    try:
        # https://pypi.python.org/pypi/cbor
        # https://bitbucket.org/bodhisnarkva/cbor
        import cbor
    except ImportError:
        pass
    else:
        _HAS_CBOR = True
        _cbor_loads = cbor.loads
        _cbor_dumps = cbor.dumps
        _cbor = cbor
        # print('Notice: Autobahn is using cbor library for CBOR serialization')


if _HAS_CBOR:

    class CBORObjectSerializer(object):

        NAME = u'cbor'

        CBOR_MODULE = _cbor

        BINARY = True
        """
        Flag that indicates whether this serializer needs a binary clean transport.
        """

        def __init__(self, batched=False):
            """
            Ctor.

            :param batched: Flag that controls whether serializer operates in batched mode.
            :type batched: bool
            """
            self._batched = batched

        def serialize(self, obj):
            """
            Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.serialize`
            """
            data = _cbor_dumps(obj)
            if self._batched:
                return struct.pack("!L", len(data)) + data
            else:
                return data

        def unserialize(self, payload):
            """
            Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.unserialize`
            """

            if self._batched:
                msgs = []
                N = len(payload)
                i = 0
                while i < N:
                    # read message length prefix
                    if i + 4 > N:
                        raise Exception("batch format error [1]")
                    l = struct.unpack("!L", payload[i:i + 4])[0]

                    # read message data
                    if i + 4 + l > N:
                        raise Exception("batch format error [2]")
                    data = payload[i + 4:i + 4 + l]

                    # append parsed raw message
                    msgs.append(_cbor_loads(data))

                    # advance until everything consumed
                    i = i + 4 + l

                if i != N:
                    raise Exception("batch format error [3]")
                return msgs

            else:
                unpacked = _cbor_loads(payload)
                return [unpacked]

    IObjectSerializer.register(CBORObjectSerializer)
    SERID_TO_OBJSER[CBORObjectSerializer.NAME] = CBORObjectSerializer

    __all__.append('CBORObjectSerializer')

    class CBORSerializer(Serializer):

        SERIALIZER_ID = u"cbor"
        """
        ID used as part of the WebSocket subprotocol name to identify the
        serializer with WAMP-over-WebSocket.
        """

        RAWSOCKET_SERIALIZER_ID = 3
        """
        ID used in lower four bits of second octet in RawSocket opening
        handshake identify the serializer with WAMP-over-RawSocket.
        """

        MIME_TYPE = u"application/cbor"
        """
        MIME type announced in HTTP request/response headers when running
        WAMP-over-Longpoll HTTP fallback.
        """

        def __init__(self, batched=False):
            """
            Ctor.

            :param batched: Flag to control whether to put this serialized into batched mode.
            :type batched: bool
            """
            Serializer.__init__(self, CBORObjectSerializer(batched=batched))
            if batched:
                self.SERIALIZER_ID = u"cbor.batched"

    ISerializer.register(CBORSerializer)
    SERID_TO_SER[CBORSerializer.SERIALIZER_ID] = CBORSerializer

    __all__.append('CBORSerializer')


# UBJSON serialization depends on the `py-ubjson` package being available
# https://pypi.python.org/pypi/py-ubjson
# https://github.com/Iotic-Labs/py-ubjson
try:
    import ubjson
except ImportError:
    pass
else:
    # print('Notice: Autobahn is using ubjson module for UBJSON serialization')

    class UBJSONObjectSerializer(object):

        NAME = u'ubjson'

        UBJSON_MODULE = ubjson

        BINARY = True
        """
        Flag that indicates whether this serializer needs a binary clean transport.
        """

        def __init__(self, batched=False):
            """

            :param batched: Flag that controls whether serializer operates in batched mode.
            :type batched: bool
            """
            self._batched = batched

        def serialize(self, obj):
            """
            Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.serialize`
            """
            data = ubjson.dumpb(obj)
            if self._batched:
                return struct.pack("!L", len(data)) + data
            else:
                return data

        def unserialize(self, payload):
            """
            Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.unserialize`
            """

            if self._batched:
                msgs = []
                N = len(payload)
                i = 0
                while i < N:
                    # read message length prefix
                    if i + 4 > N:
                        raise Exception("batch format error [1]")
                    l = struct.unpack("!L", payload[i:i + 4])[0]

                    # read message data
                    if i + 4 + l > N:
                        raise Exception("batch format error [2]")
                    data = payload[i + 4:i + 4 + l]

                    # append parsed raw message
                    msgs.append(ubjson.loadb(data))

                    # advance until everything consumed
                    i = i + 4 + l

                if i != N:
                    raise Exception("batch format error [3]")
                return msgs

            else:
                unpacked = ubjson.loadb(payload)
                return [unpacked]

    IObjectSerializer.register(UBJSONObjectSerializer)
    SERID_TO_OBJSER[UBJSONObjectSerializer.NAME] = UBJSONObjectSerializer

    __all__.append('UBJSONObjectSerializer')

    class UBJSONSerializer(Serializer):

        SERIALIZER_ID = u"ubjson"
        """
        ID used as part of the WebSocket subprotocol name to identify the
        serializer with WAMP-over-WebSocket.
        """

        RAWSOCKET_SERIALIZER_ID = 4
        """
        ID used in lower four bits of second octet in RawSocket opening
        handshake identify the serializer with WAMP-over-RawSocket.
        """

        MIME_TYPE = u"application/ubjson"
        """
        MIME type announced in HTTP request/response headers when running
        WAMP-over-Longpoll HTTP fallback.
        """

        def __init__(self, batched=False):
            """
            Ctor.

            :param batched: Flag to control whether to put this serialized into batched mode.
            :type batched: bool
            """
            Serializer.__init__(self, UBJSONObjectSerializer(batched=batched))
            if batched:
                self.SERIALIZER_ID = u"ubjson.batched"

    ISerializer.register(UBJSONSerializer)
    SERID_TO_SER[UBJSONSerializer.SERIALIZER_ID] = UBJSONSerializer

    __all__.append('UBJSONSerializer')


_HAS_FLATBUFFERS = False
try:
    import flatbuffers  # noqa
    from autobahn.wamp import message_fbs
except ImportError:
    pass
else:
    _HAS_FLATBUFFERS = True


if _HAS_FLATBUFFERS:

    class FlatBuffersObjectSerializer(object):

        NAME = u'flatbuffers'

        FLATBUFFERS_MODULE = flatbuffers

        BINARY = True
        """
        Flag that indicates whether this serializer needs a binary clean transport.
        """

        MESSAGE_TYPE_MAP = {
            message_fbs.MessageType.EVENT: (message_fbs.Event, message.Event),
            message_fbs.MessageType.PUBLISH: (message_fbs.Publish, message.Publish),
        }

        def __init__(self, batched=False):
            """

            :param batched: Flag that controls whether serializer operates in batched mode.
            :type batched: bool
            """
            assert not batched, 'WAMP-FlatBuffers serialization does not support message batching currently'
            self._batched = batched

        def serialize(self, obj):
            """
            Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.serialize`
            """
            raise NotImplementedError()

        def unserialize(self, payload):
            """
            Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.unserialize`
            """
            union_msg = message_fbs.Message.Message.GetRootAsMessage(payload, 0)
            msg_type = union_msg.MsgType()

            if msg_type in self.MESSAGE_TYPE_MAP:
                fbs_klass, wamp_klass = self.MESSAGE_TYPE_MAP[msg_type]
                fbs_msg = fbs_klass()
                _tab = union_msg.Msg()
                fbs_msg.Init(_tab.Bytes, _tab.Pos)
                msg = wamp_klass(from_fbs=fbs_msg)
                return [msg]
            else:
                raise NotImplementedError('message type {} not yet implemented for WAMP-FlatBuffers'.format(msg_type))

    IObjectSerializer.register(FlatBuffersObjectSerializer)

    __all__.append('FlatBuffersObjectSerializer')
    SERID_TO_OBJSER[FlatBuffersObjectSerializer.NAME] = FlatBuffersObjectSerializer

    class FlatBuffersSerializer(Serializer):

        SERIALIZER_ID = u"flatbuffers"
        """
        ID used as part of the WebSocket subprotocol name to identify the
        serializer with WAMP-over-WebSocket.
        """

        RAWSOCKET_SERIALIZER_ID = 5
        """
        ID used in lower four bits of second octet in RawSocket opening
        handshake identify the serializer with WAMP-over-RawSocket.
        """

        MIME_TYPE = u"application/x-flatbuffers"
        """
        MIME type announced in HTTP request/response headers when running
        WAMP-over-Longpoll HTTP fallback.
        """

        def __init__(self, batched=False):
            """

            :param batched: Flag to control whether to put this serialized into batched mode.
            :type batched: bool
            """
            Serializer.__init__(self, FlatBuffersObjectSerializer(batched=batched))
            if batched:
                self.SERIALIZER_ID = u"flatbuffers.batched"

    ISerializer.register(FlatBuffersSerializer)
    SERID_TO_SER[FlatBuffersSerializer.SERIALIZER_ID] = FlatBuffersSerializer

    __all__.append('FlatBuffersSerializer')


def create_transport_serializer(serializer_id):
    batched = False
    if '.' in serializer_id:
        l = serializer_id.split('.')
        serializer_id = l[0]
        if len(l) > 1 and l[1] == 'batched':
            batched = True

    if serializer_id in SERID_TO_SER:
        return SERID_TO_SER[serializer_id](batched=batched)
    else:
        raise RuntimeError('could not create serializer for "{}" (available: {})'.format(serializer_id, sorted(SERID_TO_SER.keys())))


def create_transport_serializers(transport):
    """
    Create a list of serializers to use with a WAMP protocol factory.
    """
    serializers = []
    for serializer_id in transport.serializers:
        serializers.append(create_transport_serializer(serializer_id))
    return serializers
