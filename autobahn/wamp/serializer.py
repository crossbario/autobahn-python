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

from __future__ import absolute_import

import six
import struct

from autobahn.wamp.interfaces import IObjectSerializer, ISerializer
from autobahn.wamp.exception import ProtocolError
from autobahn.wamp import message

# note: __all__ must be a list here, since we dynamically
# extend it depending on availability of more serializers
__all__ = ['Serializer',
           'JsonObjectSerializer',
           'JsonSerializer']


class Serializer(object):
    """
    Base class for WAMP serializers. A WAMP serializer is the core glue between
    parsed WAMP message objects and the bytes on wire (the transport).
    """

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
        Constructor.

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
                raise ProtocolError("invalid serialization of WAMP message (binary {0}, but expected {1})".format(isBinary, self._serializer.BINARY))

        try:
            raw_msgs = self._serializer.unserialize(payload)
        except Exception as e:
            raise ProtocolError("invalid serialization of WAMP message ({0})".format(e))

        msgs = []

        for raw_msg in raw_msgs:

            if type(raw_msg) != list:
                raise ProtocolError("invalid type {0} for WAMP message".format(type(raw_msg)))

            if len(raw_msg) == 0:
                raise ProtocolError(u"missing message type in WAMP message")

            message_type = raw_msg[0]

            if type(message_type) != int:
                raise ProtocolError("invalid type {0} for WAMP message type".format(type(message_type)))

            Klass = self.MESSAGE_TYPE_MAP.get(message_type)

            if Klass is None:
                raise ProtocolError("invalid WAMP message type {0}".format(message_type))

            # this might again raise `ProtocolError` ..
            msg = Klass.parse(raw_msg)

            msgs.append(msg)

        return msgs


##
# JSON serialization is always supported
##
try:
    # try import accelerated JSON implementation
    ##
    import ujson

    _json = ujson

    def _loads(val):
        return ujson.loads(val, precise_float=True)

    def _dumps(obj):
        return ujson.dumps(obj, double_precision=15, ensure_ascii=False)

except ImportError:
    # fallback to stdlib implementation
    ##
    import json

    _json = json

    _loads = json.loads

    def _dumps(obj):
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=False)

finally:
    class JsonObjectSerializer(object):

        JSON_MODULE = _json
        """
      The JSON module used (either stdib builtin or ujson).
      """

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


class JsonSerializer(Serializer):

    SERIALIZER_ID = "json"
    """
    ID used as part of the WebSocket subprotocol name to identify the
    serializer with WAMP-over-WebSocket.
    """

    RAWSOCKET_SERIALIZER_ID = 1
    """
    ID used in lower four bits of second octet in RawSocket opening
    handshake identify the serializer with WAMP-over-RawSocket.
    """

    MIME_TYPE = "application/json"
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
            self.SERIALIZER_ID = "json.batched"


ISerializer.register(JsonSerializer)


##
# MsgPack serialization depends on the `msgpack` package being available
##
try:
    import msgpack
except ImportError:
    pass
else:

    class MsgPackObjectSerializer(object):

        BINARY = True
        """
      Flag that indicates whether this serializer needs a binary clean transport.
      """

        ENABLE_V5 = True
        """
      Enable version 5 of the MsgPack specification (which differentiates
      between strings and binary).
      """

        def __init__(self, batched=False, pack_kwargs=None, unpack_kwargs=None):
            """
            Ctor.

            :param batched: Flag that controls whether serializer operates in batched mode.
            :type batched: bool
            :param pack_kwargs = Keyword arguments passed to msgpack.packb().
            :type pack_kwargs dict
            :param unpack_kwargs = Keyword arguments passed to msgpack.unpackb().
            :type unpack_kwargs dict
            """
            self._batched = batched
            self._pack_kwargs = pack_kwargs or {}
            self._pack_kwargs.setdefault('use_bin_type', self.ENABLE_V5)
            self._unpack_kwargs = unpack_kwargs or {}
            self._unpack_kwargs.setdefault('encoding', 'utf-8')

        def serialize(self, obj):
            """
            Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.serialize`
            """
            data = msgpack.packb(obj, **self._pack_kwargs)
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
                    msgs.append(msgpack.unpackb(data, **self._unpack_kwargs))

                    # advance until everything consumed
                    i = i + 4 + l

                if i != N:
                    raise Exception("batch format error [3]")
                return msgs

            else:
                return [msgpack.unpackb(payload, **self._unpack_kwargs)]

    IObjectSerializer.register(MsgPackObjectSerializer)

    __all__.append('MsgPackObjectSerializer')

    class MsgPackSerializer(Serializer):

        SERIALIZER_ID = "msgpack"
        """
        ID used as part of the WebSocket subprotocol name to identify the
        serializer with WAMP-over-WebSocket.
        """

        RAWSOCKET_SERIALIZER_ID = 2
        """
        ID used in lower four bits of second octet in RawSocket opening
        handshake identify the serializer with WAMP-over-RawSocket.
        """

        MIME_TYPE = "application/x-msgpack"
        """
        MIME type announced in HTTP request/response headers when running
        WAMP-over-Longpoll HTTP fallback.
        """

        def __init__(self, batched=False, pack_kwargs=None, unpack_kwargs=None):
            """
            Ctor.

            :param batched: Flag to control whether to put this serialized into batched mode.
            :type batched: bool
            :param pack_kwargs = Keyword arguments passed to msgpack.packb().
            :type pack_kwargs dict
            :param unpack_kwargs = Keyword arguments passed to msgpack.unpackb().
            :type unpack_kwargs dict
            """
            Serializer.__init__(self, MsgPackObjectSerializer(batched, pack_kwargs, unpack_kwargs))
            if batched:
                self.SERIALIZER_ID = "msgpack.batched"

    ISerializer.register(MsgPackSerializer)

    __all__.append('MsgPackSerializer')
