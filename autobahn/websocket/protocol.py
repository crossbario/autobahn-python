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

import binascii
import hashlib
import base64
import struct
import random
import os
import pickle
import copy
import json
import six

from pprint import pformat
from collections import deque

from autobahn import __version__

from autobahn.websocket.interfaces import IWebSocketChannel, \
    IWebSocketChannelFrameApi, \
    IWebSocketChannelStreamingApi

from autobahn.websocket.types import ConnectionRequest, ConnectionResponse

from autobahn.util import Stopwatch, newid, wildcards2patterns
from autobahn.websocket.utf8validator import Utf8Validator
from autobahn.websocket.xormasker import XorMaskerNull, createXorMasker
from autobahn.websocket.compress import PERMESSAGE_COMPRESSION_EXTENSION

from six.moves import urllib
import txaio

if six.PY3:
    # Python 3
    # noinspection PyShadowingBuiltins
    xrange = range

# The Python urlparse module currently does not contain the ws/wss
# schemes, so we add those dynamically (which is a hack of course).
# Since the urllib from six.moves does not seem to expose the stuff
# we monkey patch here, we do it manually.
#
# Important: if you change this stuff (you shouldn't), make sure
# _all_ our unit tests for WS URLs succeed
#
if not six.PY3:
    # Python 2
    import urlparse
else:
    # Python 3
    from urllib import parse as urlparse

wsschemes = ["ws", "wss"]
urlparse.uses_relative.extend(wsschemes)
urlparse.uses_netloc.extend(wsschemes)
urlparse.uses_params.extend(wsschemes)
urlparse.uses_query.extend(wsschemes)
urlparse.uses_fragment.extend(wsschemes)

__all__ = ("createWsUrl",
           "parseWsUrl",
           "ConnectionRequest",
           "ConnectionResponse",
           "Timings",
           "WebSocketProtocol",
           "WebSocketFactory",
           "WebSocketServerProtocol",
           "WebSocketServerFactory",
           "WebSocketClientProtocol",
           "WebSocketClientFactory")


def createWsUrl(hostname, port=None, isSecure=False, path=None, params=None):
    """
    Create a WebSocket URL from components.

    :param hostname: WebSocket server hostname.
    :type hostname: str
    :param port: WebSocket service port or None (to select default ports 80/443 depending on isSecure).
    :type port: int
    :param isSecure: Set True for secure WebSocket ("wss" scheme).
    :type isSecure: bool
    :param path: Path component of addressed resource (will be properly URL escaped).
    :type path: str
    :param params: A dictionary of key-values to construct the query component of the addressed resource (will be properly URL escaped).
    :type params: dict

    :returns: str -- Constructed WebSocket URL.
    """
    if port is not None:
        netloc = "%s:%d" % (hostname, port)
    else:
        if isSecure:
            netloc = "%s:443" % hostname
        else:
            netloc = "%s:80" % hostname
    if isSecure:
        scheme = "wss"
    else:
        scheme = "ws"
    if path is not None:
        ppath = urllib.parse.quote(path)
    else:
        ppath = "/"
    if params is not None:
        query = urllib.parse.urlencode(params)
    else:
        query = None
    return urllib.parse.urlunparse((scheme, netloc, ppath, None, query, None))


def parseWsUrl(url):
    """
    Parses as WebSocket URL into it's components and returns a tuple (isSecure, host, port, resource, path, params).

    isSecure is a flag which is True for wss URLs.
    host is the hostname or IP from the URL.
    port is the port from the URL or standard port derived from scheme (ws = 80, wss = 443).
    resource is the /resource name/ from the URL, the /path/ together with the (optional) /query/ component.
    path is the /path/ component properly unescaped.
    params is the /query) component properly unescaped and returned as dictionary.

    :param url: A valid WebSocket URL, i.e. `ws://localhost:9000/myresource?param1=23&param2=666`
    :type url: str

    :returns: tuple -- A tuple (isSecure, host, port, resource, path, params)
    """
    parsed = urlparse.urlparse(url)
    if not parsed.hostname or parsed.hostname == "":
        raise Exception("invalid WebSocket URL: missing hostname")
    if parsed.scheme not in ["ws", "wss"]:
        raise Exception("invalid WebSocket URL: bogus protocol scheme '%s'" % parsed.scheme)
    if parsed.port is None or parsed.port == "":
        if parsed.scheme == "ws":
            port = 80
        else:
            port = 443
    else:
        port = int(parsed.port)
    if parsed.fragment is not None and parsed.fragment != "":
        raise Exception("invalid WebSocket URL: non-empty fragment '%s" % parsed.fragment)
    if parsed.path is not None and parsed.path != "":
        ppath = parsed.path
        path = urllib.parse.unquote(ppath)
    else:
        ppath = "/"
        path = ppath
    if parsed.query is not None and parsed.query != "":
        resource = ppath + "?" + parsed.query
        params = urlparse.parse_qs(parsed.query)
    else:
        resource = ppath
        params = {}
    return parsed.scheme == "wss", parsed.hostname, port, resource, path, params


class TrafficStats(object):

    def __init__(self):
        self.reset()

    def reset(self):
        # all of the following only tracks data messages, not control frames, not handshaking
        #
        self.outgoingOctetsWireLevel = 0
        self.outgoingOctetsWebSocketLevel = 0
        self.outgoingOctetsAppLevel = 0
        self.outgoingWebSocketFrames = 0
        self.outgoingWebSocketMessages = 0

        self.incomingOctetsWireLevel = 0
        self.incomingOctetsWebSocketLevel = 0
        self.incomingOctetsAppLevel = 0
        self.incomingWebSocketFrames = 0
        self.incomingWebSocketMessages = 0

        # the following track any traffic before the WebSocket connection
        # reaches STATE_OPEN (this includes WebSocket opening handshake
        # proxy handling and such)
        self.preopenOutgoingOctetsWireLevel = 0
        self.preopenIncomingOctetsWireLevel = 0

    def __json__(self):

        # compression ratio = compressed size / uncompressed size
        #
        if self.outgoingOctetsAppLevel > 0:
            outgoingCompressionRatio = float(self.outgoingOctetsWebSocketLevel) / float(self.outgoingOctetsAppLevel)
        else:
            outgoingCompressionRatio = None
        if self.incomingOctetsAppLevel > 0:
            incomingCompressionRatio = float(self.incomingOctetsWebSocketLevel) / float(self.incomingOctetsAppLevel)
        else:
            incomingCompressionRatio = None

        # protocol overhead = non-payload size / payload size
        #
        if self.outgoingOctetsWebSocketLevel > 0:
            outgoingWebSocketOverhead = float(self.outgoingOctetsWireLevel - self.outgoingOctetsWebSocketLevel) / float(self.outgoingOctetsWebSocketLevel)
        else:
            outgoingWebSocketOverhead = None
        if self.incomingOctetsWebSocketLevel > 0:
            incomingWebSocketOverhead = float(self.incomingOctetsWireLevel - self.incomingOctetsWebSocketLevel) / float(self.incomingOctetsWebSocketLevel)
        else:
            incomingWebSocketOverhead = None

        return {'outgoingOctetsWireLevel': self.outgoingOctetsWireLevel,
                'outgoingOctetsWebSocketLevel': self.outgoingOctetsWebSocketLevel,
                'outgoingOctetsAppLevel': self.outgoingOctetsAppLevel,
                'outgoingCompressionRatio': outgoingCompressionRatio,
                'outgoingWebSocketOverhead': outgoingWebSocketOverhead,
                'outgoingWebSocketFrames': self.outgoingWebSocketFrames,
                'outgoingWebSocketMessages': self.outgoingWebSocketMessages,
                'preopenOutgoingOctetsWireLevel': self.preopenOutgoingOctetsWireLevel,

                'incomingOctetsWireLevel': self.incomingOctetsWireLevel,
                'incomingOctetsWebSocketLevel': self.incomingOctetsWebSocketLevel,
                'incomingOctetsAppLevel': self.incomingOctetsAppLevel,
                'incomingCompressionRatio': incomingCompressionRatio,
                'incomingWebSocketOverhead': incomingWebSocketOverhead,
                'incomingWebSocketFrames': self.incomingWebSocketFrames,
                'incomingWebSocketMessages': self.incomingWebSocketMessages,
                'preopenIncomingOctetsWireLevel': self.preopenIncomingOctetsWireLevel}

    def __str__(self):
        return json.dumps(self.__json__())


class FrameHeader(object):
    """
    Thin-wrapper for storing WebSocket frame metadata.

    FOR INTERNAL USE ONLY!
    """

    def __init__(self, opcode, fin, rsv, length, mask):
        """
        Constructor.

        :param opcode: Frame opcode (0-15).
        :type opcode: int
        :param fin: Frame FIN flag.
        :type fin: bool
        :param rsv: Frame reserved flags (0-7).
        :type rsv: int
        :param length: Frame payload length.
        :type length: int
        :param mask: Frame mask (binary string) or None.
        :type mask: str
        """
        self.opcode = opcode
        self.fin = fin
        self.rsv = rsv
        self.length = length
        self.mask = mask


def parseHttpHeader(data):
    """
    Parses the beginning of a HTTP request header (the data up to the \n\n line) into a pair
    of status line and HTTP headers dictionary.
    Header keys are normalized to all-lower-case.

    FOR INTERNAL USE ONLY!

    :param data: The HTTP header data up to the \n\n line.
    :type data: str

    :returns: tuple -- Tuple of HTTP status line, headers and headers count.
    """
    raw = data.decode('utf8').splitlines()
    http_status_line = raw[0].strip()
    http_headers = {}
    http_headers_cnt = {}
    for h in raw[1:]:
        i = h.find(":")
        if i > 0:
            # HTTP header keys are case-insensitive
            key = h[:i].strip().lower()

            # not sure if UTF-8 is allowed for HTTP header values..
            value = h[i + 1:].strip()

            # handle HTTP headers split across multiple lines
            if key in http_headers:
                http_headers[key] += ", %s" % value
                http_headers_cnt[key] += 1
            else:
                http_headers[key] = value
                http_headers_cnt[key] = 1
        else:
            # skip bad HTTP header
            pass
    return http_status_line, http_headers, http_headers_cnt


class Timings(object):
    """
    Helper class to track timings by key. This class also supports item access,
    iteration and conversion to string.
    """

    def __init__(self):
        self._stopwatch = Stopwatch()
        self._timings = {}

    def track(self, key):
        """
        Track elapsed for key.

        :param key: Key under which to track the timing.
        :type key: str
        """
        self._timings[key] = self._stopwatch.elapsed()

    def diff(self, startKey, endKey, formatted=True):
        """
        Get elapsed difference between two previously tracked keys.

        :param startKey: First key for interval (older timestamp).
        :type startKey: str
        :param endKey: Second key for interval (younger timestamp).
        :type endKey: str
        :param formatted: If ``True``, format computed time period and return string.
        :type formatted: bool

        :returns: float or str -- Computed time period in seconds (or formatted string).
        """
        if endKey in self._timings and startKey in self._timings:
            d = self._timings[endKey] - self._timings[startKey]
            if formatted:
                if d < 0.00001:  # 10us
                    s = "%d ns" % round(d * 1000000000.)
                elif d < 0.01:  # 10ms
                    s = "%d us" % round(d * 1000000.)
                elif d < 10:  # 10s
                    s = "%d ms" % round(d * 1000.)
                else:
                    s = "%d s" % round(d)
                return s.rjust(8)
            else:
                return d
        else:
            if formatted:
                return "n.a.".rjust(8)
            else:
                return None

    def __getitem__(self, key):
        return self._timings.get(key, None)

    def __iter__(self):
        return self._timings.__iter__()

    def __str__(self):
        return pformat(self._timings)


class WebSocketProtocol(object):
    """
    Protocol base class for WebSocket.

    This class implements:

      * :class:`autobahn.websocket.interfaces.IWebSocketChannel`
      * :class:`autobahn.websocket.interfaces.IWebSocketChannelFrameApi`
      * :class:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi`
    """

    SUPPORTED_SPEC_VERSIONS = [10, 11, 12, 13, 14, 15, 16, 17, 18]
    """
    WebSocket protocol spec (draft) versions supported by this implementation.
    Use of version 18 indicates RFC6455. Use of versions < 18 indicate actual
    draft spec versions (Hybi-Drafts).
    """

    SUPPORTED_PROTOCOL_VERSIONS = [8, 13]
    """
    WebSocket protocol versions supported by this implementation.
    """

    SPEC_TO_PROTOCOL_VERSION = {10: 8, 11: 8, 12: 8, 13: 13, 14: 13, 15: 13, 16: 13, 17: 13, 18: 13}
    """
    Mapping from protocol spec (draft) version to protocol version.
    """

    PROTOCOL_TO_SPEC_VERSION = {8: 12, 13: 18}
    """
    Mapping from protocol version to the latest protocol spec (draft) version
    using that protocol version.
    """

    DEFAULT_SPEC_VERSION = 18
    """
    Default WebSocket protocol spec version this implementation speaks: final
    RFC6455.
    """

    _WS_MAGIC = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    """
    Protocol defined magic used during WebSocket handshake (used in Hybi-drafts
    and final RFC6455.
    """

    _QUEUED_WRITE_DELAY = 0.00001
    """
    For synched/chopped writes, this is the reactor reentry delay in seconds.
    """

    MESSAGE_TYPE_TEXT = 1
    """
    WebSocket text message type (UTF-8 payload).
    """

    MESSAGE_TYPE_BINARY = 2
    """
    WebSocket binary message type (arbitrary binary payload).
    """

    # WebSocket protocol state:
    # (STATE_PROXY_CONNECTING) => STATE_CONNECTING => STATE_OPEN => STATE_CLOSING => STATE_CLOSED
    #
    STATE_CLOSED = 0
    STATE_CONNECTING = 1
    STATE_CLOSING = 2
    STATE_OPEN = 3
    STATE_PROXY_CONNECTING = 4

    # Streaming Send State
    SEND_STATE_GROUND = 0
    SEND_STATE_MESSAGE_BEGIN = 1
    SEND_STATE_INSIDE_MESSAGE = 2
    SEND_STATE_INSIDE_MESSAGE_FRAME = 3

    # WebSocket protocol close codes
    #
    CLOSE_STATUS_CODE_NORMAL = 1000
    """Normal close of connection."""

    CLOSE_STATUS_CODE_GOING_AWAY = 1001
    """Going away."""

    CLOSE_STATUS_CODE_PROTOCOL_ERROR = 1002
    """Protocol error."""

    CLOSE_STATUS_CODE_UNSUPPORTED_DATA = 1003
    """Unsupported data."""

    CLOSE_STATUS_CODE_RESERVED1 = 1004
    """RESERVED"""

    CLOSE_STATUS_CODE_NULL = 1005  # MUST NOT be set in close frame!
    """No status received. (MUST NOT be used as status code when sending a close)."""

    CLOSE_STATUS_CODE_ABNORMAL_CLOSE = 1006  # MUST NOT be set in close frame!
    """Abnormal close of connection. (MUST NOT be used as status code when sending a close)."""

    CLOSE_STATUS_CODE_INVALID_PAYLOAD = 1007
    """Invalid frame payload data."""

    CLOSE_STATUS_CODE_POLICY_VIOLATION = 1008
    """Policy violation."""

    CLOSE_STATUS_CODE_MESSAGE_TOO_BIG = 1009
    """Message too big."""

    CLOSE_STATUS_CODE_MANDATORY_EXTENSION = 1010
    """Mandatory extension."""

    CLOSE_STATUS_CODE_INTERNAL_ERROR = 1011
    """The peer encountered an unexpected condition or internal error."""

    CLOSE_STATUS_CODE_TLS_HANDSHAKE_FAILED = 1015  # MUST NOT be set in close frame!
    """TLS handshake failed, i.e. server certificate could not be verified. (MUST NOT be used as status code when sending a close)."""

    CLOSE_STATUS_CODES_ALLOWED = [CLOSE_STATUS_CODE_NORMAL,
                                  CLOSE_STATUS_CODE_GOING_AWAY,
                                  CLOSE_STATUS_CODE_PROTOCOL_ERROR,
                                  CLOSE_STATUS_CODE_UNSUPPORTED_DATA,
                                  CLOSE_STATUS_CODE_INVALID_PAYLOAD,
                                  CLOSE_STATUS_CODE_POLICY_VIOLATION,
                                  CLOSE_STATUS_CODE_MESSAGE_TOO_BIG,
                                  CLOSE_STATUS_CODE_MANDATORY_EXTENSION,
                                  CLOSE_STATUS_CODE_INTERNAL_ERROR]
    """Status codes allowed to send in close."""

    CONFIG_ATTRS_COMMON = ['debug',
                           'debugCodePaths',
                           'logOctets',
                           'logFrames',
                           'trackTimings',
                           'utf8validateIncoming',
                           'applyMask',
                           'maxFramePayloadSize',
                           'maxMessagePayloadSize',
                           'autoFragmentSize',
                           'failByDrop',
                           'echoCloseCodeReason',
                           'openHandshakeTimeout',
                           'closeHandshakeTimeout',
                           'tcpNoDelay',
                           'autoPingInterval',
                           'autoPingTimeout',
                           'autoPingSize']
    """
    Configuration attributes common to servers and clients.
    """

    CONFIG_ATTRS_SERVER = ['versions',
                           'webStatus',
                           'requireMaskedClientFrames',
                           'maskServerFrames',
                           'perMessageCompressionAccept',
                           'serveFlashSocketPolicy',
                           'flashSocketPolicy',
                           'allowedOrigins',
                           'allowedOriginsPatterns',
                           'maxConnections']
    """
    Configuration attributes specific to servers.
    """

    CONFIG_ATTRS_CLIENT = ['version',
                           'acceptMaskedServerFrames',
                           'maskClientFrames',
                           'serverConnectionDropTimeout',
                           'perMessageCompressionOffers',
                           'perMessageCompressionAccept']
    """
    Configuration attributes specific to clients.
    """

    log = txaio.make_logger()

    def __init__(self):
        #: a Future/Deferred that fires when we hit STATE_CLOSED
        self.is_closed = txaio.create_future()

    def onOpen(self):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onOpen`
        """
        self.log.debug("WebSocketProtocol.onOpen")

    def onMessageBegin(self, isBinary):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageBegin`
        """
        self.message_is_binary = isBinary
        self.message_data = []
        self.message_data_total_length = 0

    def onMessageFrameBegin(self, length):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageFrameBegin`
        """
        self.frame_length = length
        self.frame_data = []
        self.message_data_total_length += length
        if not self.failedByMe:
            if 0 < self.maxMessagePayloadSize < self.message_data_total_length:
                self.wasMaxMessagePayloadSizeExceeded = True
                self.failConnection(
                    WebSocketProtocol.CLOSE_STATUS_CODE_MESSAGE_TOO_BIG,
                    "message exceeds payload limit of %d octets" % self.maxMessagePayloadSize
                )
            elif 0 < self.maxFramePayloadSize < length:
                self.wasMaxFramePayloadSizeExceeded = True
                self.failConnection(
                    WebSocketProtocol.CLOSE_STATUS_CODE_POLICY_VIOLATION,
                    "frame exceeds payload limit of %d octets" % self.maxFramePayloadSize
                )

    def onMessageFrameData(self, payload):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageFrameData`
        """
        if not self.failedByMe:
            if self.websocket_version == 0:
                self.message_data_total_length += len(payload)
                if 0 < self.maxMessagePayloadSize < self.message_data_total_length:
                    self.wasMaxMessagePayloadSizeExceeded = True
                    self.failConnection(WebSocketProtocol.CLOSE_STATUS_CODE_MESSAGE_TOO_BIG, "message exceeds payload limit of %d octets" % self.maxMessagePayloadSize)
                self.message_data.append(payload)
            else:
                self.frame_data.append(payload)

    def onMessageFrameEnd(self):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageFrameEnd`
        """
        if not self.failedByMe:
            self._onMessageFrame(self.frame_data)

        self.frame_data = None

    def onMessageFrame(self, payload):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageFrame`
        """
        if not self.failedByMe:
            self.message_data.extend(payload)

    def onMessageEnd(self):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageEnd`
        """
        if not self.failedByMe:
            payload = b''.join(self.message_data)
            if self.trackedTimings:
                self.trackedTimings.track("onMessage")
            self._onMessage(payload, self.message_is_binary)

        self.message_data = None

    def onMessage(self, payload, isBinary):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessage`
        """
        if self.debug:
            self.log.debug("WebSocketProtocol.onMessage")

    def onPing(self, payload):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onPing`
        """
        if self.debug:
            self.log.debug("WebSocketProtocol.onPing")
        if self.state == WebSocketProtocol.STATE_OPEN:
            self.sendPong(payload)

    def onPong(self, payload):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onPong`
        """
        if self.debug:
            self.log.debug("WebSocketProtocol.onPong")

    def onClose(self, wasClean, code, reason):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onClose`
        """
        if self.debugCodePaths:
            s = "WebSocketProtocol.onClose:\n"
            s += "wasClean=%s\n" % wasClean
            s += "code=%s\n" % code
            s += "reason=%s\n" % reason
            s += "self.closedByMe=%s\n" % self.closedByMe
            s += "self.failedByMe=%s\n" % self.failedByMe
            s += "self.droppedByMe=%s\n" % self.droppedByMe
            s += "self.wasClean=%s\n" % self.wasClean
            s += "self.wasNotCleanReason=%s\n" % self.wasNotCleanReason
            s += "self.localCloseCode=%s\n" % self.localCloseCode
            s += "self.localCloseReason=%s\n" % self.localCloseReason
            s += "self.remoteCloseCode=%s\n" % self.remoteCloseCode
            s += "self.remoteCloseReason=%s\n" % self.remoteCloseReason
            self.log.debug(s)

    def onCloseFrame(self, code, reasonRaw):
        """
        Callback when a Close frame was received. The default implementation answers by
        sending a Close when no Close was sent before. Otherwise it drops
        the TCP connection either immediately (when we are a server) or after a timeout
        (when we are a client and expect the server to drop the TCP).

        :param code: Close status code, if there was one (:class:`WebSocketProtocol`.CLOSE_STATUS_CODE_*).
        :type code: int or None
        :param reasonRaw: Close reason (when present, a status code MUST have been also be present).
        :type reason: str or None
        """
        if self.debugCodePaths:
            self.log.debug("WebSocketProtocol.onCloseFrame")

        self.remoteCloseCode = code

        # reserved close codes: 0-999, 1004, 1005, 1006, 1011-2999, >= 5000
        #
        if code is not None and (code < 1000 or (1000 <= code <= 2999 and code not in WebSocketProtocol.CLOSE_STATUS_CODES_ALLOWED) or code >= 5000):
            if self.protocolViolation("invalid close code %d" % code):
                return True

        # closing reason
        #
        if reasonRaw is None:
            self.remoteCloseReason = None
        else:
            # we use our own UTF-8 validator to get consistent and fully conformant
            # UTF-8 validation behavior
            u = Utf8Validator()
            val = u.validate(reasonRaw)
            if not val[0]:
                if self.invalidPayload("invalid close reason (non-UTF-8 payload)"):
                    return True
            self.remoteCloseReason = reasonRaw.decode('utf8')

        # handle receive of close frame depending on protocol state
        #
        if self.state == WebSocketProtocol.STATE_CLOSING:
            # We already initiated the closing handshake, so this
            # is the peer's reply to our close frame.

            # cancel any closing HS timer if present
            #
            if self.closeHandshakeTimeoutCall is not None:
                if self.debugCodePaths:
                    self.log.debug("closeHandshakeTimeoutCall.cancel")
                self.closeHandshakeTimeoutCall.cancel()
                self.closeHandshakeTimeoutCall = None

            self.wasClean = True

            if self.factory.isServer:
                # When we are a server, we immediately drop the TCP.
                self.dropConnection(abort=True)
            else:
                # When we are a client, the server should drop the TCP
                # If that doesn't happen, we do. And that will set wasClean = False.
                if self.serverConnectionDropTimeout > 0:
                    call = txaio.call_later(
                        self.serverConnectionDropTimeout,
                        self.onServerConnectionDropTimeout,
                    )
                    self.serverConnectionDropTimeoutCall = call

        elif self.state == WebSocketProtocol.STATE_OPEN:
            # The peer initiates a closing handshake, so we reply
            # by sending close frame.

            self.wasClean = True

            if self.websocket_version == 0:
                self.sendCloseFrame(isReply=True)
            else:
                # Either reply with same code/reason, or code == NORMAL/reason=None
                if self.echoCloseCodeReason:
                    self.sendCloseFrame(code=code, reasonUtf8=self.remoteCloseReason, isReply=True)
                else:
                    self.sendCloseFrame(code=WebSocketProtocol.CLOSE_STATUS_CODE_NORMAL, isReply=True)

            if self.factory.isServer:
                # When we are a server, we immediately drop the TCP.
                self.dropConnection(abort=False)
            else:
                # When we are a client, we expect the server to drop the TCP,
                # and when the server fails to do so, a timeout in sendCloseFrame()
                # will set wasClean = False back again.
                pass

        elif self.state == WebSocketProtocol.STATE_CLOSED:
            # The peer initiated a closing handshake but dropped the TCP immediately.
            self.wasClean = False

        else:
            # STATE_PROXY_CONNECTING, STATE_CONNECTING
            raise Exception("logic error")

    def onServerConnectionDropTimeout(self):
        """
        We (a client) expected the peer (a server) to drop the connection,
        but it didn't (in time self.serverConnectionDropTimeout).
        So we drop the connection, but set self.wasClean = False.
        """
        self.serverConnectionDropTimeoutCall = None
        if self.state != WebSocketProtocol.STATE_CLOSED:
            if self.debugCodePaths:
                self.log.debug("onServerConnectionDropTimeout")
            self.wasClean = False
            self.wasNotCleanReason = "server did not drop TCP connection (in time)"
            self.wasServerConnectionDropTimeout = True
            self.dropConnection(abort=True)
        else:
            if self.debugCodePaths:
                self.log.debug("skipping onServerConnectionDropTimeout since connection is already closed")

    def onOpenHandshakeTimeout(self):
        """
        We expected the peer to complete the opening handshake with to us.
        It didn't do so (in time self.openHandshakeTimeout).
        So we drop the connection, but set self.wasClean = False.
        """
        self.openHandshakeTimeoutCall = None
        if self.state in [WebSocketProtocol.STATE_CONNECTING, WebSocketProtocol.STATE_PROXY_CONNECTING]:
            if self.debugCodePaths:
                self.log.debug("onOpenHandshakeTimeout fired")
            self.wasClean = False
            self.wasNotCleanReason = "peer did not finish (in time) the opening handshake"
            self.wasOpenHandshakeTimeout = True
            self.dropConnection(abort=True)
        elif self.state == WebSocketProtocol.STATE_OPEN:
            if self.debugCodePaths:
                self.log.debug("skipping onOpenHandshakeTimeout since WebSocket connection is open (opening handshake already finished)")
        elif self.state == WebSocketProtocol.STATE_CLOSING:
            if self.debugCodePaths:
                self.log.debug("skipping onOpenHandshakeTimeout since WebSocket connection is closing")
        elif self.state == WebSocketProtocol.STATE_CLOSED:
            if self.debugCodePaths:
                self.log.debug("skipping onOpenHandshakeTimeout since WebSocket connection already closed")
        else:
            # should not arrive here
            raise Exception("logic error")

    def onCloseHandshakeTimeout(self):
        """
        We expected the peer to respond to us initiating a close handshake. It didn't
        respond (in time self.closeHandshakeTimeout) with a close response frame though.
        So we drop the connection, but set self.wasClean = False.
        """
        self.closeHandshakeTimeoutCall = None
        if self.state != WebSocketProtocol.STATE_CLOSED:
            if self.debugCodePaths:
                self.log.debug("onCloseHandshakeTimeout fired")
            self.wasClean = False
            self.wasNotCleanReason = "peer did not respond (in time) in closing handshake"
            self.wasCloseHandshakeTimeout = True
            self.dropConnection(abort=True)
        else:
            if self.debugCodePaths:
                self.log.debug("skipping onCloseHandshakeTimeout since connection is already closed")

    def onAutoPingTimeout(self):
        """
        When doing automatic ping/pongs to detect broken connection, the peer
        did not reply in time to our ping. We drop the connection.
        """
        if self.debugCodePaths:
            self.log.debug("Auto ping/pong: onAutoPingTimeout fired")

        self.autoPingTimeoutCall = None
        self.dropConnection(abort=True)

    def dropConnection(self, abort=False):
        """
        Drop the underlying TCP connection.
        """
        if self.state != WebSocketProtocol.STATE_CLOSED:
            self.log.debug("dropping connection: {reason}", reason=self.wasNotCleanReason)
            self.droppedByMe = True

            # this code-path will be hit (*without* hitting
            # _connectionLost) in some timeout scenarios (unit-tests
            # cover these). However, sometimes we hit both.
            self.state = WebSocketProtocol.STATE_CLOSED
            txaio.resolve(self.is_closed, self)

            self._closeConnection(abort)
        else:
            if self.debugCodePaths:
                self.log.debug("skipping dropConnection since connection is already closed")

    def failConnection(self, code=CLOSE_STATUS_CODE_GOING_AWAY, reason="Going Away"):
        """
        Fails the WebSocket connection.
        """
        if self.state != WebSocketProtocol.STATE_CLOSED:
            self.log.debug("Failing connection: {code}: {reason}", code=code, reason=reason)

            self.failedByMe = True

            if self.failByDrop:
                # brutally drop the TCP connection
                self.wasClean = False
                self.wasNotCleanReason = "I failed the WebSocket connection by dropping the TCP connection"
                self.dropConnection(abort=True)

            else:
                if self.state != WebSocketProtocol.STATE_CLOSING:
                    # perform WebSocket closing handshake
                    self.sendCloseFrame(code=code, reasonUtf8=reason.encode("UTF-8")[:125 - 2], isReply=False)
                else:
                    # already performing closing handshake .. we now drop the TCP
                    # (this can happen e.g. if we encounter a 2nd protocol violation during closing HS)
                    self.dropConnection(abort=False)

        else:
            if self.debugCodePaths:
                self.log.debug("skipping failConnection since connection is already closed")

    def protocolViolation(self, reason):
        """
        Fired when a WebSocket protocol violation/error occurs.

        :param reason: Protocol violation that was encountered (human readable).
        :type reason: str

        :returns: bool -- True, when any further processing should be discontinued.
        """
        if self.debugCodePaths:
            self.log.debug("Protocol violation : %s" % reason)
        self.failConnection(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, reason)
        if self.failByDrop:
            return True
        else:
            # if we don't immediately drop the TCP, we need to skip the invalid frame
            # to continue to later receive the closing handshake reply
            return False

    def invalidPayload(self, reason):
        """
        Fired when invalid payload is encountered. Currently, this only happens
        for text message when payload is invalid UTF-8 or close frames with
        close reason that is invalid UTF-8.

        :param reason: What was invalid for the payload (human readable).
        :type reason: str

        :returns: bool -- True, when any further processing should be discontinued.
        """
        if self.debugCodePaths:
            self.log.debug("Invalid payload : %s" % reason)
        self.failConnection(WebSocketProtocol.CLOSE_STATUS_CODE_INVALID_PAYLOAD, reason)
        if self.failByDrop:
            return True
        else:
            # if we don't immediately drop the TCP, we need to skip the invalid frame
            # to continue to later receive the closing handshake reply
            return False

    def setTrackTimings(self, enable):
        """
        Enable/disable tracking of detailed timings.

        :param enable: Turn time tracking on/off.
        :type enable: bool
        """
        if not hasattr(self, 'trackTimings') or self.trackTimings != enable:
            self.trackTimings = enable
            if self.trackTimings:
                self.trackedTimings = Timings()
            else:
                self.trackedTimings = None

    def _connectionMade(self):
        """
        This is called by network framework when a new TCP connection has been established
        and handed over to a Protocol instance (an instance of this class).
        """
        # copy default options from factory (so we are not affected by changed on
        # those), but only copy if not already set on protocol instance (allow
        # to set configuration individually)
        #
        configAttrLog = []
        for configAttr in self.CONFIG_ATTRS:
            if not hasattr(self, configAttr):
                setattr(self, configAttr, getattr(self.factory, configAttr))
                configAttrSource = self.factory.__class__.__name__
            else:
                configAttrSource = self.__class__.__name__
            configAttrLog.append((configAttr, getattr(self, configAttr), configAttrSource))

        if self.debug:
            # self.log.debug(configAttrLog)
            self.log.debug("\n" + pformat(configAttrLog))

        # permessage-compress extension
        self._perMessageCompress = None

        # Time tracking
        self.trackedTimings = None
        self.setTrackTimings(self.trackTimings)

        # Traffic stats
        self.trafficStats = TrafficStats()

        # initial state
        if not self.factory.isServer and self.factory.proxy is not None:
            self.state = WebSocketProtocol.STATE_PROXY_CONNECTING
        else:
            self.state = WebSocketProtocol.STATE_CONNECTING
        self.send_state = WebSocketProtocol.SEND_STATE_GROUND
        self.data = b""

        # for chopped/synched sends, we need to queue to maintain
        # ordering when recalling the reactor to actually "force"
        # the octets to wire (see test/trickling in the repo)
        self.send_queue = deque()
        self.triggered = False

        # incremental UTF8 validator
        self.utf8validator = Utf8Validator()

        # track when frame/message payload sizes (incoming) were exceeded
        self.wasMaxFramePayloadSizeExceeded = False
        self.wasMaxMessagePayloadSizeExceeded = False

        # the following vars are related to connection close handling/tracking

        # True, iff I have initiated closing HS (that is, did send close first)
        self.closedByMe = False

        # True, iff I have failed the WS connection (i.e. due to protocol error)
        # Failing can be either by initiating close HS or brutal drop (this is
        # controlled by failByDrop option)
        self.failedByMe = False

        # True, iff I dropped the TCP connection (called transport.loseConnection())
        self.droppedByMe = False

        # True, iff full WebSocket closing handshake was performed (close frame sent
        # and received) _and_ the server dropped the TCP (which is its responsibility)
        self.wasClean = False

        # When self.wasClean = False, the reason (what happened)
        self.wasNotCleanReason = None

        # When we are a client, and we expected the server to drop the TCP, but that
        # didn't happen in time, this gets True
        self.wasServerConnectionDropTimeout = False

        # When the initial WebSocket opening handshake times out, this gets True
        self.wasOpenHandshakeTimeout = False

        # When we initiated a closing handshake, but the peer did not respond in
        # time, this gets True
        self.wasCloseHandshakeTimeout = False

        # True, iff I dropped the TCP connection because we fully served the
        # Flash Socket Policy File after a policy file request.
        self.wasServingFlashSocketPolicyFile = False

        # The close code I sent in close frame (if any)
        self.localCloseCode = None

        # The close reason I sent in close frame (if any)
        self.localCloseReason = None

        # The close code the peer sent me in close frame (if any)
        self.remoteCloseCode = None

        # The close reason the peer sent me in close frame (if any)
        self.remoteCloseReason = None

        # timers, which might get set up later, and remembered here to get canceled
        # when appropriate
        if not self.factory.isServer:
            self.serverConnectionDropTimeoutCall = None
        self.openHandshakeTimeoutCall = None
        self.closeHandshakeTimeoutCall = None

        # set opening handshake timeout handler
        if self.openHandshakeTimeout > 0:
            self.openHandshakeTimeoutCall = txaio.call_later(self.openHandshakeTimeout, self.onOpenHandshakeTimeout)

        self.autoPingTimeoutCall = None
        self.autoPingPending = None
        self.autoPingPendingCall = None

    def _connectionLost(self, reason):
        """
        This is called by network framework when a transport connection was
        lost.
        """
        # cancel any server connection drop timer if present
        #
        self.log.debug('_connectionLost: {reason}', reason=txaio.failure_message(reason))
        if not self.factory.isServer and self.serverConnectionDropTimeoutCall is not None:
            if self.debugCodePaths:
                self.log.debug("serverConnectionDropTimeoutCall.cancel")
            self.serverConnectionDropTimeoutCall.cancel()
            self.serverConnectionDropTimeoutCall = None

        # cleanup auto ping/pong timers
        #
        if self.autoPingPendingCall:
            if self.debugCodePaths:
                self.log.debug("Auto ping/pong: canceling autoPingPendingCall upon lost connection")
            self.autoPingPendingCall.cancel()
            self.autoPingPendingCall = None

        if self.autoPingTimeoutCall:
            if self.debugCodePaths:
                self.log.debug("Auto ping/pong: canceling autoPingTimeoutCall upon lost connection")
            self.autoPingTimeoutCall.cancel()
            self.autoPingTimeoutCall = None

        # check required here because in some scenarios dropConnection
        # will already have resolved the Future/Deferred.
        if self.state != WebSocketProtocol.STATE_CLOSED:
            self.state = WebSocketProtocol.STATE_CLOSED
            txaio.resolve(self.is_closed, self)

        if self.wasServingFlashSocketPolicyFile:
            if self.debug:
                self.log.debug("connection dropped after serving Flash Socket Policy File")
        else:
            if not self.wasClean:
                if not self.droppedByMe and self.wasNotCleanReason is None:
                    self.wasNotCleanReason = "peer dropped the TCP connection without previous WebSocket closing handshake"
                self._onClose(self.wasClean, WebSocketProtocol.CLOSE_STATUS_CODE_ABNORMAL_CLOSE, "connection was closed uncleanly (%s)" % self.wasNotCleanReason)
            else:
                self._onClose(self.wasClean, self.remoteCloseCode, self.remoteCloseReason)

    def logRxOctets(self, data):
        """
        Hook fired right after raw octets have been received, but only when
        self.logOctets == True.
        """
        self.log.debug("RX Octets from %s : octets = %s" % (self.peer, binascii.b2a_hex(data)))

    def logTxOctets(self, data, sync):
        """
        Hook fired right after raw octets have been sent, but only when
        self.logOctets == True.
        """
        self.log.debug("TX Octets to %s : sync = %s, octets = %s" % (self.peer, sync, binascii.b2a_hex(data)))

    def logRxFrame(self, frameHeader, payload):
        """
        Hook fired right after WebSocket frame has been received and decoded,
        but only when self.logFrames == True.
        """
        data = b''.join(payload)
        info = (self.peer,
                frameHeader.fin,
                frameHeader.rsv,
                frameHeader.opcode,
                binascii.b2a_hex(frameHeader.mask) if frameHeader.mask else "-",
                frameHeader.length,
                data if frameHeader.opcode == 1 else binascii.b2a_hex(data))

        self.log.debug("RX Frame from %s : fin = %s, rsv = %s, opcode = %s, mask = %s, length = %s, payload = %s" % info)

    def logTxFrame(self, frameHeader, payload, repeatLength, chopsize, sync):
        """
        Hook fired right after WebSocket frame has been encoded and sent, but
        only when self.logFrames == True.
        """
        info = (self.peer,
                frameHeader.fin,
                frameHeader.rsv,
                frameHeader.opcode,
                binascii.b2a_hex(frameHeader.mask) if frameHeader.mask else "-",
                frameHeader.length,
                repeatLength,
                chopsize,
                sync,
                payload if frameHeader.opcode == 1 else binascii.b2a_hex(payload))

        self.log.debug("TX Frame to %s : fin = %s, rsv = %s, opcode = %s, mask = %s, length = %s, repeat_length = %s, chopsize = %s, sync = %s, payload = %s" % info)

    def _dataReceived(self, data):
        """
        This is called by network framework upon receiving data on transport
        connection.
        """
        if self.state == WebSocketProtocol.STATE_OPEN:
            self.trafficStats.incomingOctetsWireLevel += len(data)
        elif self.state == WebSocketProtocol.STATE_CONNECTING or self.state == WebSocketProtocol.STATE_PROXY_CONNECTING:
            self.trafficStats.preopenIncomingOctetsWireLevel += len(data)

        if self.logOctets:
            self.logRxOctets(data)
        self.data += data
        self.consumeData()

    def consumeData(self):
        """
        Consume buffered (incoming) data.
        """
        # WebSocket is open (handshake was completed) or close was sent
        #
        if self.state == WebSocketProtocol.STATE_OPEN or self.state == WebSocketProtocol.STATE_CLOSING:

            # process until no more buffered data left or WS was closed
            #
            while self.processData() and self.state != WebSocketProtocol.STATE_CLOSED:
                pass

        # need to establish proxy connection
        #
        elif self.state == WebSocketProtocol.STATE_PROXY_CONNECTING:

            self.processProxyConnect()

        # WebSocket needs handshake
        #
        elif self.state == WebSocketProtocol.STATE_CONNECTING:

            # the implementation of processHandshake() in derived
            # class needs to perform client or server handshake
            # from other party here ..
            #
            self.processHandshake()

        # we failed the connection .. don't process any more data!
        #
        elif self.state == WebSocketProtocol.STATE_CLOSED:

            # ignore any data received after WS was closed
            #
            if self.debugCodePaths:
                self.log.debug("received data in STATE_CLOSED")

        # should not arrive here (invalid state)
        #
        else:
            raise Exception("invalid state")

    def processProxyConnect(self):
        """
        Process proxy connect.
        """
        raise Exception("must implement proxy connect (client or server) in derived class")

    def processHandshake(self):
        """
        Process WebSocket handshake.
        """
        raise Exception("must implement handshake (client or server) in derived class")

    def _trigger(self):
        """
        Trigger sending stuff from send queue (which is only used for
        chopped/synched writes).
        """
        if not self.triggered:
            self.triggered = True
            self._send()

    def _send(self):
        """
        Send out stuff from send queue. For details how this works, see
        test/trickling in the repo.
        """
        if len(self.send_queue) > 0:
            e = self.send_queue.popleft()

            if self.state != WebSocketProtocol.STATE_CLOSED:

                self.transport.write(e[0])

                if self.state == WebSocketProtocol.STATE_OPEN:
                    self.trafficStats.outgoingOctetsWireLevel += len(e[0])
                elif self.state == WebSocketProtocol.STATE_CONNECTING or self.state == WebSocketProtocol.STATE_PROXY_CONNECTING:
                    self.trafficStats.preopenOutgoingOctetsWireLevel += len(e[0])

                if self.logOctets:
                    self.logTxOctets(e[0], e[1])
            else:
                if self.debugCodePaths:
                    self.log.debug("skipped delayed write, since connection is closed")
            # we need to reenter the reactor to make the latter
            # reenter the OS network stack, so that octets
            # can get on the wire. Note: this is a "heuristic",
            # since there is no (easy) way to really force out
            # octets from the OS network stack to wire.
            txaio.call_later(WebSocketProtocol._QUEUED_WRITE_DELAY, self._send)
        else:
            self.triggered = False

    def sendData(self, data, sync=False, chopsize=None):
        """
        Wrapper for self.transport.write which allows to give a chopsize.
        When asked to chop up writing to TCP stream, we write only chopsize
        octets and then give up control to select() in underlying reactor so
        that bytes get onto wire immediately. Note that this is different from
        and unrelated to WebSocket data message fragmentation. Note that this
        is also different from the TcpNoDelay option which can be set on the
        socket.
        """
        if chopsize and chopsize > 0:
            i = 0
            n = len(data)
            done = False
            while not done:
                j = i + chopsize
                if j >= n:
                    done = True
                    j = n
                self.send_queue.append((data[i:j], True))
                i += chopsize
            self._trigger()
        else:
            if sync or len(self.send_queue) > 0:
                self.send_queue.append((data, sync))
                self._trigger()
            else:
                self.transport.write(data)

                if self.state == WebSocketProtocol.STATE_OPEN:
                    self.trafficStats.outgoingOctetsWireLevel += len(data)
                elif self.state == WebSocketProtocol.STATE_CONNECTING or self.state == WebSocketProtocol.STATE_PROXY_CONNECTING:
                    self.trafficStats.preopenOutgoingOctetsWireLevel += len(data)

                if self.logOctets:
                    self.logTxOctets(data, False)

    def sendPreparedMessage(self, preparedMsg):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendPreparedMessage`
        """
        if self._perMessageCompress is None or preparedMsg.doNotCompress:
            self.sendData(preparedMsg.payloadHybi)
        else:
            self.sendMessage(preparedMsg.payload, preparedMsg.binary)

    def processData(self):
        """
        After WebSocket handshake has been completed, this procedure will do
        all subsequent processing of incoming bytes.
        """
        buffered_len = len(self.data)

        # outside a frame, that is we are awaiting data which starts a new frame
        #
        if self.current_frame is None:

            # need minimum of 2 octets to for new frame
            #
            if buffered_len >= 2:

                # FIN, RSV, OPCODE
                #
                if six.PY3:
                    b = self.data[0]
                else:
                    b = ord(self.data[0])
                frame_fin = (b & 0x80) != 0
                frame_rsv = (b & 0x70) >> 4
                frame_opcode = b & 0x0f

                # MASK, PAYLOAD LEN 1
                #
                if six.PY3:
                    b = self.data[1]
                else:
                    b = ord(self.data[1])
                frame_masked = (b & 0x80) != 0
                frame_payload_len1 = b & 0x7f

                # MUST be 0 when no extension defining
                # the semantics of RSV has been negotiated
                #
                if frame_rsv != 0:
                    if self._perMessageCompress is not None and frame_rsv == 4:
                        pass
                    else:
                        if self.protocolViolation("RSV = %d and no extension negotiated" % frame_rsv):
                            return False

                # all client-to-server frames MUST be masked
                #
                if self.factory.isServer and self.requireMaskedClientFrames and not frame_masked:
                    if self.protocolViolation("unmasked client-to-server frame"):
                        return False

                # all server-to-client frames MUST NOT be masked
                #
                if not self.factory.isServer and not self.acceptMaskedServerFrames and frame_masked:
                    if self.protocolViolation("masked server-to-client frame"):
                        return False

                # check frame
                #
                if frame_opcode > 7:  # control frame (have MSB in opcode set)

                    # control frames MUST NOT be fragmented
                    #
                    if not frame_fin:
                        if self.protocolViolation("fragmented control frame"):
                            return False

                    # control frames MUST have payload 125 octets or less
                    #
                    if frame_payload_len1 > 125:
                        if self.protocolViolation("control frame with payload length > 125 octets"):
                            return False

                    # check for reserved control frame opcodes
                    #
                    if frame_opcode not in [8, 9, 10]:
                        if self.protocolViolation("control frame using reserved opcode %d" % frame_opcode):
                            return False

                    # close frame : if there is a body, the first two bytes of the body MUST be a 2-byte
                    # unsigned integer (in network byte order) representing a status code
                    #
                    if frame_opcode == 8 and frame_payload_len1 == 1:
                        if self.protocolViolation("received close control frame with payload len 1"):
                            return False

                    # control frames MUST NOT be compressed
                    #
                    if self._perMessageCompress is not None and frame_rsv == 4:
                        if self.protocolViolation("received compressed control frame [%s]" % self._perMessageCompress.EXTENSION_NAME):
                            return False

                else:  # data frame

                    # check for reserved data frame opcodes
                    #
                    if frame_opcode not in [0, 1, 2]:
                        if self.protocolViolation("data frame using reserved opcode %d" % frame_opcode):
                            return False

                    # check opcode vs message fragmentation state 1/2
                    #
                    if not self.inside_message and frame_opcode == 0:
                        if self.protocolViolation("received continuation data frame outside fragmented message"):
                            return False

                    # check opcode vs message fragmentation state 2/2
                    #
                    if self.inside_message and frame_opcode != 0:
                        if self.protocolViolation("received non-continuation data frame while inside fragmented message"):
                            return False

                    # continuation data frames MUST NOT have the compressed bit set
                    #
                    if self._perMessageCompress is not None and frame_rsv == 4 and self.inside_message:
                        if self.protocolViolation("received continuation data frame with compress bit set [%s]" % self._perMessageCompress.EXTENSION_NAME):
                            return False

                # compute complete header length
                #
                if frame_masked:
                    mask_len = 4
                else:
                    mask_len = 0

                if frame_payload_len1 < 126:
                    frame_header_len = 2 + mask_len
                elif frame_payload_len1 == 126:
                    frame_header_len = 2 + 2 + mask_len
                elif frame_payload_len1 == 127:
                    frame_header_len = 2 + 8 + mask_len
                else:
                    raise Exception("logic error")

                # only proceed when we have enough data buffered for complete
                # frame header (which includes extended payload len + mask)
                #
                if buffered_len >= frame_header_len:

                    # minimum frame header length (already consumed)
                    #
                    i = 2

                    # extract extended payload length
                    #
                    if frame_payload_len1 == 126:
                        frame_payload_len = struct.unpack("!H", self.data[i:i + 2])[0]
                        if frame_payload_len < 126:
                            if self.protocolViolation("invalid data frame length (not using minimal length encoding)"):
                                return False
                        i += 2
                    elif frame_payload_len1 == 127:
                        frame_payload_len = struct.unpack("!Q", self.data[i:i + 8])[0]
                        if frame_payload_len > 0x7FFFFFFFFFFFFFFF:  # 2**63
                            if self.protocolViolation("invalid data frame length (>2^63)"):
                                return False
                        if frame_payload_len < 65536:
                            if self.protocolViolation("invalid data frame length (not using minimal length encoding)"):
                                return False
                        i += 8
                    else:
                        frame_payload_len = frame_payload_len1

                    # when payload is masked, extract frame mask
                    #
                    frame_mask = None
                    if frame_masked:
                        frame_mask = self.data[i:i + 4]
                        i += 4

                    if frame_masked and frame_payload_len > 0 and self.applyMask:
                        self.current_frame_masker = createXorMasker(frame_mask, frame_payload_len)
                    else:
                        self.current_frame_masker = XorMaskerNull()

                    # remember rest (payload of current frame after header and everything thereafter)
                    #
                    self.data = self.data[i:]

                    # ok, got complete frame header
                    #
                    self.current_frame = FrameHeader(frame_opcode,
                                                     frame_fin,
                                                     frame_rsv,
                                                     frame_payload_len,
                                                     frame_mask)

                    # process begin on new frame
                    #
                    self.onFrameBegin()

                    # reprocess when frame has no payload or and buffered data left
                    #
                    return frame_payload_len == 0 or len(self.data) > 0

                else:
                    return False  # need more data
            else:
                return False  # need more data

        # inside a started frame
        #
        else:

            # cut out rest of frame payload
            #
            rest = self.current_frame.length - self.current_frame_masker.pointer()
            if buffered_len >= rest:
                data = self.data[:rest]
                length = rest
                self.data = self.data[rest:]
            else:
                data = self.data
                length = buffered_len
                self.data = b''

            if length > 0:
                # unmask payload
                #
                payload = self.current_frame_masker.process(data)
            else:
                # we also process empty payloads, since we need to fire
                # our hooks (at least for streaming processing, this is
                # necessary for correct protocol state transitioning)
                #
                payload = b''

            # process frame data
            #
            fr = self.onFrameData(payload)
            # noinspection PySimplifyBooleanCheck
            if fr is False:
                return False

            # fire frame end handler when frame payload is complete
            #
            if self.current_frame_masker.pointer() == self.current_frame.length:
                fr = self.onFrameEnd()
                # noinspection PySimplifyBooleanCheck
                if fr is False:
                    return False

            # reprocess when no error occurred and buffered data left
            #
            return len(self.data) > 0

    def onFrameBegin(self):
        """
        Begin of receive new frame.
        """
        if self.current_frame.opcode > 7:
            self.control_frame_data = []
        else:
            # new message started
            #
            if not self.inside_message:

                self.inside_message = True

                # setup decompressor
                #
                if self._perMessageCompress is not None and self.current_frame.rsv == 4:
                    self._isMessageCompressed = True
                    self._perMessageCompress.startDecompressMessage()
                else:
                    self._isMessageCompressed = False

                # setup UTF8 validator
                #
                if self.current_frame.opcode == WebSocketProtocol.MESSAGE_TYPE_TEXT and self.utf8validateIncoming:
                    self.utf8validator.reset()
                    self.utf8validateIncomingCurrentMessage = True
                    self.utf8validateLast = (True, True, 0, 0)
                else:
                    self.utf8validateIncomingCurrentMessage = False

                # track timings
                #
                if self.trackedTimings:
                    self.trackedTimings.track("onMessageBegin")

                # fire onMessageBegin
                #
                self._onMessageBegin(self.current_frame.opcode == WebSocketProtocol.MESSAGE_TYPE_BINARY)

            self._onMessageFrameBegin(self.current_frame.length)

    def onFrameData(self, payload):
        """
        New data received within frame.
        """
        if self.current_frame.opcode > 7:
            self.control_frame_data.append(payload)
        else:
            # decompress frame payload
            #
            if self._isMessageCompressed:
                compressedLen = len(payload)
                if self.debug:
                    self.log.debug("RX compressed [%d]: %s" % (compressedLen, binascii.b2a_hex(payload)))

                payload = self._perMessageCompress.decompressMessageData(payload)
                uncompressedLen = len(payload)
            else:
                l = len(payload)
                compressedLen = l
                uncompressedLen = l

            if self.state == WebSocketProtocol.STATE_OPEN:
                self.trafficStats.incomingOctetsWebSocketLevel += compressedLen
                self.trafficStats.incomingOctetsAppLevel += uncompressedLen

            # incrementally validate UTF-8 payload
            #
            if self.utf8validateIncomingCurrentMessage:
                self.utf8validateLast = self.utf8validator.validate(payload)
                if not self.utf8validateLast[0]:
                    if self.invalidPayload("encountered invalid UTF-8 while processing text message at payload octet index %d" % self.utf8validateLast[3]):
                        return False

            self._onMessageFrameData(payload)

    def onFrameEnd(self):
        """
        End of frame received.
        """
        if self.current_frame.opcode > 7:
            if self.logFrames:
                self.logRxFrame(self.current_frame, self.control_frame_data)
            self.processControlFrame()
        else:
            if self.state == WebSocketProtocol.STATE_OPEN:
                self.trafficStats.incomingWebSocketFrames += 1
            if self.logFrames:
                self.logRxFrame(self.current_frame, self.frame_data)

            self._onMessageFrameEnd()

            if self.current_frame.fin:

                # handle end of compressed message
                #
                if self._isMessageCompressed:
                    self._perMessageCompress.endDecompressMessage()

                # verify UTF8 has actually ended
                #
                if self.utf8validateIncomingCurrentMessage:
                    if not self.utf8validateLast[1]:
                        if self.invalidPayload("UTF-8 text message payload ended within Unicode code point at payload octet index %d" % self.utf8validateLast[3]):
                            return False

                # if self.debug:
                #   self.log.debug("Traffic statistics:\n" + str(self.trafficStats))

                if self.state == WebSocketProtocol.STATE_OPEN:
                    self.trafficStats.incomingWebSocketMessages += 1

                self._onMessageEnd()
                self.inside_message = False

        self.current_frame = None

    def processControlFrame(self):
        """
        Process a completely received control frame.
        """
        payload = b''.join(self.control_frame_data)
        self.control_frame_data = None

        # CLOSE frame
        #
        if self.current_frame.opcode == 8:

            code = None
            reasonRaw = None
            ll = len(payload)
            if ll > 1:
                code = struct.unpack("!H", payload[0:2])[0]
                if ll > 2:
                    reasonRaw = payload[2:]

            if self.onCloseFrame(code, reasonRaw):
                return False

        # PING frame
        #
        elif self.current_frame.opcode == 9:
            self._onPing(payload)

        # PONG frame
        #
        elif self.current_frame.opcode == 10:

            # auto ping/pong processing
            #
            if self.autoPingPending:
                try:
                    if payload == self.autoPingPending:
                        if self.debugCodePaths:
                            self.log.debug("Auto ping/pong: received pending pong for auto-ping/pong")

                        if self.autoPingTimeoutCall:
                            self.autoPingTimeoutCall.cancel()

                        self.autoPingPending = None
                        self.autoPingTimeoutCall = None

                        if self.autoPingInterval:
                            self.autoPingPendingCall = txaio.call_later(self.autoPingInterval, self._sendAutoPing)
                    else:
                        if self.debugCodePaths:
                            self.log.debug("Auto ping/pong: received non-pending pong")
                except:
                    if self.debugCodePaths:
                        self.log.debug("Auto ping/pong: received non-pending pong")

            # fire app-level callback
            #
            self._onPong(payload)

        else:
            # we might arrive here, when protocolViolation
            # wants us to continue anyway
            pass

        return True

    def sendFrame(self,
                  opcode,
                  payload=b'',
                  fin=True,
                  rsv=0,
                  mask=None,
                  payload_len=None,
                  chopsize=None,
                  sync=False):
        """
        Send out frame. Normally only used internally via sendMessage(),
        sendPing(), sendPong() and sendClose().

        This method deliberately allows to send invalid frames (that is frames
        invalid per-se, or frames invalid because of protocol state). Other
        than in fuzzing servers, calling methods will ensure that no invalid
        frames are sent.

        In addition, this method supports explicit specification of payload
        length. When payload_len is given, it will always write that many
        octets to the stream. It'll wrap within payload, resending parts of
        that when more octets were requested The use case is again for fuzzing
        server which want to sent increasing amounts of payload data to peers
        without having to construct potentially large messages themselves.
        """
        if payload_len is not None:
            if len(payload) < 1:
                raise Exception("cannot construct repeated payload with length %d from payload of length %d" % (payload_len, len(payload)))
            l = payload_len
            pl = b''.join([payload for _ in range(payload_len / len(payload))]) + payload[:payload_len % len(payload)]
        else:
            l = len(payload)
            pl = payload

        # first byte
        #
        b0 = 0
        if fin:
            b0 |= (1 << 7)
        b0 |= (rsv % 8) << 4
        b0 |= opcode % 128

        # second byte, payload len bytes and mask
        #
        b1 = 0
        if mask or (not self.factory.isServer and self.maskClientFrames) or (self.factory.isServer and self.maskServerFrames):
            b1 |= 1 << 7
            if not mask:
                mask = struct.pack("!I", random.getrandbits(32))
                mv = mask
            else:
                mv = b''

            # mask frame payload
            #
            if l > 0 and self.applyMask:
                masker = createXorMasker(mask, l)
                plm = masker.process(pl)
            else:
                plm = pl

        else:
            mv = b''
            plm = pl

        el = b''
        if l <= 125:
            b1 |= l
        elif l <= 0xFFFF:
            b1 |= 126
            el = struct.pack("!H", l)
        elif l <= 0x7FFFFFFFFFFFFFFF:
            b1 |= 127
            el = struct.pack("!Q", l)
        else:
            raise Exception("invalid payload length")

        if six.PY3:
            raw = b''.join([b0.to_bytes(1, 'big'), b1.to_bytes(1, 'big'), el, mv, plm])
        else:
            raw = b''.join([chr(b0), chr(b1), el, mv, plm])

        if opcode in [0, 1, 2]:
            self.trafficStats.outgoingWebSocketFrames += 1

        if self.logFrames:
            frameHeader = FrameHeader(opcode, fin, rsv, l, mask)
            self.logTxFrame(frameHeader, payload, payload_len, chopsize, sync)

        # send frame octets
        #
        self.sendData(raw, sync, chopsize)

    def sendPing(self, payload=None):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendPing`
        """
        if self.state != WebSocketProtocol.STATE_OPEN:
            return
        if payload:
            l = len(payload)
            if l > 125:
                raise Exception("invalid payload for PING (payload length must be <= 125, was %d)" % l)
            self.sendFrame(opcode=9, payload=payload)
        else:
            self.sendFrame(opcode=9)

    def _sendAutoPing(self):
        # Sends an automatic ping and sets up a timeout.
        if self.debugCodePaths:
            self.log.debug("Auto ping/pong: sending ping auto-ping/pong")

        self.autoPingPendingCall = None

        self.autoPingPending = newid(self.autoPingSize).encode('utf8')

        self.sendPing(self.autoPingPending)

        if self.autoPingTimeout:
            if self.debugCodePaths:
                self.log.debug("Auto ping/pong: expecting ping in {0} seconds for auto-ping/pong".format(self.autoPingTimeout))
            self.autoPingTimeoutCall = txaio.call_later(self.autoPingTimeout, self.onAutoPingTimeout)

    def sendPong(self, payload=None):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendPong`
        """
        if self.state != WebSocketProtocol.STATE_OPEN:
            return
        if payload:
            l = len(payload)
            if l > 125:
                raise Exception("invalid payload for PONG (payload length must be <= 125, was %d)" % l)
            self.sendFrame(opcode=10, payload=payload)
        else:
            self.sendFrame(opcode=10)

    def sendCloseFrame(self, code=None, reasonUtf8=None, isReply=False):
        """
        Send a close frame and update protocol state. Note, that this is
        an internal method which deliberately allows not send close
        frame with invalid payload.
        """
        if self.state == WebSocketProtocol.STATE_CLOSING:
            if self.debugCodePaths:
                self.log.debug("ignoring sendCloseFrame since connection is closing")

        elif self.state == WebSocketProtocol.STATE_CLOSED:
            if self.debugCodePaths:
                self.log.debug("ignoring sendCloseFrame since connection already closed")

        elif self.state in [WebSocketProtocol.STATE_PROXY_CONNECTING, WebSocketProtocol.STATE_CONNECTING]:
            raise Exception("cannot close a connection not yet connected")

        elif self.state == WebSocketProtocol.STATE_OPEN:

            # construct Hybi close frame payload and send frame
            payload = b''
            if code is not None:
                payload += struct.pack("!H", code)
            if reasonUtf8 is not None:
                payload += reasonUtf8
            self.sendFrame(opcode=8, payload=payload)

            # update state
            self.state = WebSocketProtocol.STATE_CLOSING
            self.closedByMe = not isReply

            # remember payload of close frame we sent
            self.localCloseCode = code
            self.localCloseReason = reasonUtf8

            # drop connection when timeout on receiving close handshake reply
            if self.closedByMe and self.closeHandshakeTimeout > 0:
                self.closeHandshakeTimeoutCall = txaio.call_later(self.closeHandshakeTimeout, self.onCloseHandshakeTimeout)

        else:
            raise Exception("logic error")

    def sendClose(self, code=None, reason=None):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendClose`
        """
        if code is not None:
            if type(code) != int:
                raise Exception("invalid type %s for close code" % type(code))
            if code != 1000 and not (3000 <= code <= 4999):
                raise Exception("invalid close code %d" % code)

        if reason is not None:
            if code is None:
                raise Exception("close reason without close code")

            if type(reason) not in (str, six.text_type):
                # If it's not UTF-8 encodable (str or unicode), coerce it to a
                # string so we can close properly.
                reason = str(reason)

            reasonUtf8 = reason.encode("utf8")

            if len(reasonUtf8) + 2 > 125:
                # If it's too long, truncate it. A partial message is not
                # unlikely (for example, an exception), and it is better to
                # give the start of the message than drop the connection
                # forever.
                reasonUtf8 = reasonUtf8[:120] + b"..."
                assert not len(reasonUtf8) + 2 > 125
        else:
            reasonUtf8 = None
        self.sendCloseFrame(code=code, reasonUtf8=reasonUtf8, isReply=False)

    def beginMessage(self, isBinary=False, doNotCompress=False):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.beginMessage`
        """
        if self.state != WebSocketProtocol.STATE_OPEN:
            return

        # check if sending state is valid for this method
        #
        if self.send_state != WebSocketProtocol.SEND_STATE_GROUND:
            raise Exception("WebSocketProtocol.beginMessage invalid in current sending state")

        self.send_message_opcode = WebSocketProtocol.MESSAGE_TYPE_BINARY if isBinary else WebSocketProtocol.MESSAGE_TYPE_TEXT
        self.send_state = WebSocketProtocol.SEND_STATE_MESSAGE_BEGIN

        # setup compressor
        #
        if self._perMessageCompress is not None and not doNotCompress:
            self.send_compressed = True
            self._perMessageCompress.startCompressMessage()
        else:
            self.send_compressed = False

        self.trafficStats.outgoingWebSocketMessages += 1

    def beginMessageFrame(self, length):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.beginMessageFrame`
        """
        if self.state != WebSocketProtocol.STATE_OPEN:
            return

        # check if sending state is valid for this method
        #
        if self.send_state not in [WebSocketProtocol.SEND_STATE_MESSAGE_BEGIN, WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE]:
            raise Exception("WebSocketProtocol.beginMessageFrame invalid in current sending state [%d]" % self.send_state)

        if type(length) != int or length < 0 or length > 0x7FFFFFFFFFFFFFFF:  # 2**63
            raise Exception("invalid value for message frame length")

        self.send_message_frame_length = length

        self.trafficStats.outgoingWebSocketFrames += 1

        if (not self.factory.isServer and self.maskClientFrames) or (self.factory.isServer and self.maskServerFrames):
            # automatic mask:
            # - client-to-server masking (if not deactivated)
            # - server-to-client masking (if activated)
            #
            self.send_message_frame_mask = struct.pack("!I", random.getrandbits(32))

        else:
            # no mask
            #
            self.send_message_frame_mask = None

        # payload masker
        #
        if self.send_message_frame_mask and length > 0 and self.applyMask:
            self.send_message_frame_masker = createXorMasker(self.send_message_frame_mask, length)
        else:
            self.send_message_frame_masker = XorMaskerNull()

        # first byte
        #
        # FIN = false .. since with streaming, we don't know when message ends
        b0 = 0
        if self.send_state == WebSocketProtocol.SEND_STATE_MESSAGE_BEGIN:

            b0 |= self.send_message_opcode % 128

            if self.send_compressed:
                b0 |= (4 % 8) << 4

            self.send_state = WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE
        else:
            pass  # message continuation frame

        # second byte, payload len bytes and mask
        #
        b1 = 0
        if self.send_message_frame_mask:
            b1 |= 1 << 7
            mv = self.send_message_frame_mask
        else:
            mv = b''

        el = b''
        if length <= 125:
            b1 |= length
        elif length <= 0xFFFF:
            b1 |= 126
            el = struct.pack("!H", length)
        elif length <= 0x7FFFFFFFFFFFFFFF:
            b1 |= 127
            el = struct.pack("!Q", length)
        else:
            raise Exception("invalid payload length")

        # write message frame header
        #
        if six.PY3:
            header = b''.join([b0.to_bytes(1, 'big'), b1.to_bytes(1, 'big'), el, mv])
        else:
            header = b''.join([chr(b0), chr(b1), el, mv])

        self.sendData(header)

        # now we are inside message frame ..
        #
        self.send_state = WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE_FRAME

    def sendMessageFrameData(self, payload, sync=False):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendMessageFrameData`
        """
        if self.state != WebSocketProtocol.STATE_OPEN:
            return

        if not self.send_compressed:
            self.trafficStats.outgoingOctetsAppLevel += len(payload)
        self.trafficStats.outgoingOctetsWebSocketLevel += len(payload)

        if self.send_state != WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE_FRAME:
            raise Exception("WebSocketProtocol.sendMessageFrameData invalid in current sending state")

        rl = len(payload)
        if self.send_message_frame_masker.pointer() + rl > self.send_message_frame_length:
            l = self.send_message_frame_length - self.send_message_frame_masker.pointer()
            rest = -(rl - l)
            pl = payload[:l]
        else:
            l = rl
            rest = self.send_message_frame_length - self.send_message_frame_masker.pointer() - l
            pl = payload

        # mask frame payload
        #
        plm = self.send_message_frame_masker.process(pl)

        # send frame payload
        #
        self.sendData(plm, sync=sync)

        # if we are done with frame, move back into "inside message" state
        #
        if self.send_message_frame_masker.pointer() >= self.send_message_frame_length:
            self.send_state = WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE

        # when =0 : frame was completed exactly
        # when >0 : frame is still uncomplete and that much amount is still left to complete the frame
        # when <0 : frame was completed and there was this much unconsumed data in payload argument
        #
        return rest

    def endMessage(self):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.endMessage`
        """
        if self.state != WebSocketProtocol.STATE_OPEN:
            return

        # check if sending state is valid for this method
        #
        # if self.send_state != WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE:
        #   raise Exception("WebSocketProtocol.endMessage invalid in current sending state [%d]" % self.send_state)

        if self.send_compressed:
            payload = self._perMessageCompress.endCompressMessage()
            self.trafficStats.outgoingOctetsWebSocketLevel += len(payload)
        else:
            # send continuation frame with empty payload and FIN set to end message
            payload = b''
        self.sendFrame(opcode=0, payload=payload, fin=True)

        self.send_state = WebSocketProtocol.SEND_STATE_GROUND

    def sendMessageFrame(self, payload, sync=False):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendMessageFrame`
        """
        if self.state != WebSocketProtocol.STATE_OPEN:
            return

        if self.send_compressed:
            self.trafficStats.outgoingOctetsAppLevel += len(payload)
            payload = self._perMessageCompress.compressMessageData(payload)

        self.beginMessageFrame(len(payload))
        self.sendMessageFrameData(payload, sync)

    def sendMessage(self,
                    payload,
                    isBinary=False,
                    fragmentSize=None,
                    sync=False,
                    doNotCompress=False):
        """
        Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendMessage`
        """
        assert(type(payload) == bytes)

        if self.state != WebSocketProtocol.STATE_OPEN:
            return

        if self.trackedTimings:
            self.trackedTimings.track("sendMessage")

        # (initial) frame opcode
        #
        if isBinary:
            opcode = 2
        else:
            opcode = 1

        self.trafficStats.outgoingWebSocketMessages += 1

        # setup compressor
        #
        if self._perMessageCompress is not None and not doNotCompress:
            sendCompressed = True

            self._perMessageCompress.startCompressMessage()

            self.trafficStats.outgoingOctetsAppLevel += len(payload)

            payload1 = self._perMessageCompress.compressMessageData(payload)
            payload2 = self._perMessageCompress.endCompressMessage()
            payload = b''.join([payload1, payload2])

            self.trafficStats.outgoingOctetsWebSocketLevel += len(payload)

        else:
            sendCompressed = False
            l = len(payload)
            self.trafficStats.outgoingOctetsAppLevel += l
            self.trafficStats.outgoingOctetsWebSocketLevel += l

        # explicit fragmentSize arguments overrides autoFragmentSize setting
        #
        if fragmentSize is not None:
            pfs = fragmentSize
        else:
            if self.autoFragmentSize > 0:
                pfs = self.autoFragmentSize
            else:
                pfs = None

        # send unfragmented
        #
        if pfs is None or len(payload) <= pfs:
            self.sendFrame(opcode=opcode, payload=payload, sync=sync, rsv=4 if sendCompressed else 0)

        # send data message in fragments
        #
        else:
            if pfs < 1:
                raise Exception("payload fragment size must be at least 1 (was %d)" % pfs)
            n = len(payload)
            i = 0
            done = False
            first = True
            while not done:
                j = i + pfs
                if j > n:
                    done = True
                    j = n
                if first:
                    self.sendFrame(opcode=opcode, payload=payload[i:j], fin=done, sync=sync, rsv=4 if sendCompressed else 0)
                    first = False
                else:
                    self.sendFrame(opcode=0, payload=payload[i:j], fin=done, sync=sync)
                i += pfs

        # if self.debug:
        #   self.log.debug("Traffic statistics:\n" + str(self.trafficStats))

    def _parseExtensionsHeader(self, header, removeQuotes=True):
        """
        Parse the Sec-WebSocket-Extensions header.
        """
        extensions = []
        exts = [str(x.strip()) for x in header.split(',')]
        for e in exts:
            if e != "":
                ext = [x.strip() for x in e.split(";")]
                if len(ext) > 0:
                    extension = ext[0].lower()
                    params = {}
                    for p in ext[1:]:
                        p = [x.strip() for x in p.split("=")]
                        key = p[0].lower()
                        if len(p) > 1:
                            value = "=".join(p[1:])
                            if removeQuotes:
                                if len(value) > 0 and value[0] == '"':
                                    value = value[1:]
                                if len(value) > 0 and value[-1] == '"':
                                    value = value[:-1]
                        else:
                            value = True
                        if key not in params:
                            params[key] = []
                        params[key].append(value)
                    extensions.append((extension, params))
                else:
                    pass  # should not arrive here
        return extensions


IWebSocketChannel.register(WebSocketProtocol)
IWebSocketChannelFrameApi.register(WebSocketProtocol)
IWebSocketChannelStreamingApi.register(WebSocketProtocol)


class PreparedMessage(object):
    """
    Encapsulates a prepared message to be sent later once or multiple
    times on one or more WebSocket connections.
    This can be used for optimizing Broadcast/PubSub.
    """

    def __init__(self, payload, isBinary, applyMask, doNotCompress):
        """
        Ctor for a prepared message.

        :param payload: The message payload.
        :type payload: str
        :param isBinary: Provide `True` for binary payload.
        :type isBinary: bool
        :param applyMask: Provide `True` if WebSocket message is to be masked (required for client to server WebSocket messages).
        :type applyMask: bool
        :param doNotCompress: Iff `True`, never compress this message. This
            only applies when WebSocket compression has been negotiated on the
            WebSocket connection. Use when you know the payload incompressible
            (e.g. encrypted or already compressed).
        :type doNotCompress: bool
        """
        if not doNotCompress:
            # we need to store original payload for compressed WS
            # connections (cannot compress/frame in advanced when
            # compression is on, and context takeover is off)
            self.payload = payload
            self.binary = isBinary
        self.doNotCompress = doNotCompress

        l = len(payload)

        # first byte
        #
        b0 = ((1 << 7) | 2) if isBinary else ((1 << 7) | 1)

        # second byte, payload len bytes and mask
        #
        if applyMask:
            b1 = 1 << 7
            mask = struct.pack("!I", random.getrandbits(32))
            if l == 0:
                plm = payload
            else:
                plm = createXorMasker(mask, l).process(payload)
        else:
            b1 = 0
            mask = b''
            plm = payload

        # payload extended length
        #
        el = b''
        if l <= 125:
            b1 |= l
        elif l <= 0xFFFF:
            b1 |= 126
            el = struct.pack("!H", l)
        elif l <= 0x7FFFFFFFFFFFFFFF:
            b1 |= 127
            el = struct.pack("!Q", l)
        else:
            raise Exception("invalid payload length")

        # raw WS message (single frame)
        #
        if six.PY3:
            self.payloadHybi = b''.join([b0.to_bytes(1, 'big'), b1.to_bytes(1, 'big'), el, mask, plm])
        else:
            self.payloadHybi = b''.join([chr(b0), chr(b1), el, mask, plm])


class WebSocketFactory(object):
    """
    Mixin for
    :class:`autobahn.websocket.protocol.WebSocketClientFactory` and
    :class:`autobahn.websocket.protocol.WebSocketServerFactory`.
    """

    def prepareMessage(self, payload, isBinary=False, doNotCompress=False):
        """
        Prepare a WebSocket message. This can be later sent on multiple
        instances of :class:`autobahn.websocket.WebSocketProtocol` using
        :meth:`autobahn.websocket.WebSocketProtocol.sendPreparedMessage`.

        By doing so, you can avoid the (small) overhead of framing the
        *same* payload into WebSocket messages multiple times when that
        same payload is to be sent out on multiple connections.

        :param payload: The message payload.
        :type payload: bytes
        :param isBinary: `True` iff payload is binary, else the payload must be
            UTF-8 encoded text.
        :type isBinary: bool
        :param doNotCompress: Iff `True`, never compress this message. This
            only applies when WebSocket compression has been negotiated on the
            WebSocket connection. Use when you know the payload incompressible
            (e.g. encrypted or already compressed).
        :type doNotCompress: bool

        :returns: obj -- An instance of :class:`autobahn.websocket.protocol.PreparedMessage`.
        """
        applyMask = not self.isServer
        return PreparedMessage(payload, isBinary, applyMask, doNotCompress)


class WebSocketServerProtocol(WebSocketProtocol):
    """
    Protocol base class for WebSocket servers.
    """

    CONFIG_ATTRS = WebSocketProtocol.CONFIG_ATTRS_COMMON + WebSocketProtocol.CONFIG_ATTRS_SERVER

    def onConnect(self, request):
        """
        Callback fired during WebSocket opening handshake when new WebSocket client
        connection is about to be established.

        When you want to accept the connection, return the accepted protocol
        from list of WebSocket (sub)protocols provided by client or `None` to
        speak no specific one or when the client protocol list was empty.

        You may also return a pair of `(protocol, headers)` to send additional
        HTTP headers, with `headers` being a dictionary of key-values.

        Throw :class:`autobahn.websocket.http.HttpException` when you don't want
        to accept the WebSocket connection request.

        :param request: WebSocket connection request information.
        :type request: instance of :class:`autobahn.websocket.protocol.ConnectionRequest`
        """
        return None

    def _connectionMade(self):
        """
        Called by network framework when new transport connection from client was
        accepted. Default implementation will prepare for initial WebSocket opening
        handshake. When overriding in derived class, make sure to call this base class
        implementation *before* your code.
        """
        WebSocketProtocol._connectionMade(self)
        self.factory.countConnections += 1
        if self.debug:
            self.log.debug("connection accepted from peer %s" % self.peer)

    def _connectionLost(self, reason):
        """
        Called by network framework when established transport connection from client
        was lost. Default implementation will tear down all state properly.
        When overriding in derived class, make sure to call this base class
        implementation *after* your code.
        """
        WebSocketProtocol._connectionLost(self, reason)
        self.factory.countConnections -= 1

    def processProxyConnect(self):
        raise Exception("Autobahn isn't a proxy server")

    def processHandshake(self):
        """
        Process WebSocket opening handshake request from client.
        """
        # only proceed when we have fully received the HTTP request line and all headers
        #
        end_of_header = self.data.find(b"\x0d\x0a\x0d\x0a")
        if end_of_header >= 0:

            self.http_request_data = self.data[:end_of_header + 4]
            if self.debug:
                self.log.debug("received HTTP request:\n\n%s\n\n" % self.http_request_data)

            # extract HTTP status line and headers
            #
            (self.http_status_line, self.http_headers, http_headers_cnt) = parseHttpHeader(self.http_request_data)

            # validate WebSocket opening handshake client request
            #
            if self.debug:
                self.log.debug("received HTTP status line in opening handshake : %s" % str(self.http_status_line))
                self.log.debug("received HTTP headers in opening handshake : %s" % str(self.http_headers))

            # HTTP Request line : METHOD, VERSION
            #
            rl = self.http_status_line.split()
            if len(rl) != 3:
                return self.failHandshake("Bad HTTP request status line '%s'" % self.http_status_line)
            if rl[0].strip() != "GET":
                return self.failHandshake("HTTP method '%s' not allowed" % rl[0], 405)
            vs = rl[2].strip().split("/")
            if len(vs) != 2 or vs[0] != "HTTP" or vs[1] not in ["1.1"]:
                return self.failHandshake("Unsupported HTTP version '%s'" % rl[2], 505)

            # HTTP Request line : REQUEST-URI
            #
            self.http_request_uri = rl[1].strip()
            try:
                (scheme, netloc, path, params, query, fragment) = urllib.parse.urlparse(self.http_request_uri)

                # FIXME: check that if absolute resource URI is given,
                # the scheme/netloc matches the server
                if scheme != "" or netloc != "":
                    pass

                # Fragment identifiers are meaningless in the context of WebSocket
                # URIs, and MUST NOT be used on these URIs.
                if fragment != "":
                    return self.failHandshake("HTTP requested resource contains a fragment identifier '%s'" % fragment)

                # resource path and query parameters .. this will get forwarded
                # to onConnect()
                self.http_request_path = path
                self.http_request_params = urllib.parse.parse_qs(query)
            except:
                return self.failHandshake("Bad HTTP request resource - could not parse '%s'" % rl[1].strip())

            # Host
            #
            if 'host' not in self.http_headers:
                return self.failHandshake("HTTP Host header missing in opening handshake request")

            if http_headers_cnt["host"] > 1:
                return self.failHandshake("HTTP Host header appears more than once in opening handshake request")

            self.http_request_host = self.http_headers["host"].strip()

            if self.http_request_host.find(":") >= 0 and not self.http_request_host.endswith(']'):
                (h, p) = self.http_request_host.rsplit(":", 1)
                try:
                    port = int(str(p.strip()))
                except ValueError:
                    return self.failHandshake("invalid port '%s' in HTTP Host header '%s'" % (str(p.strip()), str(self.http_request_host)))

                # do port checking only if externalPort or URL was set
                if self.factory.externalPort:
                    if port != self.factory.externalPort:
                        return self.failHandshake("port %d in HTTP Host header '%s' does not match server listening port %s" % (port, str(self.http_request_host), self.factory.externalPort))
                else:
                    if self.debugCodePaths:
                        self.log.debug("skipping opening handshake port checking - neither WS URL nor external port set")

                self.http_request_host = h

            else:
                # do port checking only if externalPort or URL was set
                if self.factory.externalPort:
                    if not ((self.factory.isSecure and self.factory.externalPort == 443) or (not self.factory.isSecure and self.factory.externalPort == 80)):
                        return self.failHandshake("missing port in HTTP Host header '%s' and server runs on non-standard port %d (wss = %s)" % (str(self.http_request_host), self.factory.externalPort, self.factory.isSecure))
                else:
                    if self.debugCodePaths:
                        self.log.debug("skipping opening handshake port checking - neither WS URL nor external port set")

            # Upgrade
            #
            if 'upgrade' not in self.http_headers:
                # When no WS upgrade, render HTML server status page
                #
                if self.webStatus:
                    if 'redirect' in self.http_request_params and len(self.http_request_params['redirect']) > 0:
                        # To specify an URL for redirection, encode the URL, i.e. from JavaScript:
                        #
                        # var url = encodeURIComponent("http://autobahn.ws/python");
                        #
                        # and append the encoded string as a query parameter 'redirect'
                        #
                        # http://localhost:9000?redirect=http%3A%2F%2Fautobahn.ws%2Fpython
                        # https://localhost:9000?redirect=https%3A%2F%2Ftwitter.com%2F
                        #
                        # This will perform an immediate HTTP-303 redirection. If you provide
                        # an additional parameter 'after' (int >= 0), the redirection happens
                        # via Meta-Refresh in the rendered HTML status page, i.e.
                        #
                        # https://localhost:9000/?redirect=https%3A%2F%2Ftwitter.com%2F&after=3
                        #
                        url = self.http_request_params['redirect'][0]
                        if 'after' in self.http_request_params and len(self.http_request_params['after']) > 0:
                            after = int(self.http_request_params['after'][0])
                            if self.debugCodePaths:
                                self.log.debug("HTTP Upgrade header missing : render server status page and meta-refresh-redirecting to %s after %d seconds" % (url, after))
                            self.sendServerStatus(url, after)
                        else:
                            if self.debugCodePaths:
                                self.log.debug("HTTP Upgrade header missing : 303-redirecting to %s" % url)
                            self.sendRedirect(url)
                    else:
                        if self.debugCodePaths:
                            self.log.debug("HTTP Upgrade header missing : render server status page")
                        self.sendServerStatus()
                    self.dropConnection(abort=False)
                    return
                else:
                    return self.failHandshake("HTTP Upgrade header missing", 426)  # Upgrade Required
            upgradeWebSocket = False
            for u in self.http_headers["upgrade"].split(","):
                if u.strip().lower() == "websocket":
                    upgradeWebSocket = True
                    break
            if not upgradeWebSocket:
                return self.failHandshake("HTTP Upgrade headers do not include 'websocket' value (case-insensitive) : %s" % self.http_headers["upgrade"])

            # Connection
            #
            if 'connection' not in self.http_headers:
                return self.failHandshake("HTTP Connection header missing")
            connectionUpgrade = False
            for c in self.http_headers["connection"].split(","):
                if c.strip().lower() == "upgrade":
                    connectionUpgrade = True
                    break
            if not connectionUpgrade:
                return self.failHandshake("HTTP Connection headers do not include 'upgrade' value (case-insensitive) : %s" % self.http_headers["connection"])

            # Sec-WebSocket-Version PLUS determine mode: Hybi or Hixie
            #
            if 'sec-websocket-version' not in self.http_headers:
                if self.debugCodePaths:
                    self.log.debug("Hixie76 protocol detected")
                return self.failHandshake("WebSocket connection denied - Hixie76 protocol not supported.")
            else:
                if self.debugCodePaths:
                    self.log.debug("Hybi protocol detected")
                if http_headers_cnt["sec-websocket-version"] > 1:
                    return self.failHandshake("HTTP Sec-WebSocket-Version header appears more than once in opening handshake request")
                try:
                    version = int(self.http_headers["sec-websocket-version"])
                except ValueError:
                    return self.failHandshake("could not parse HTTP Sec-WebSocket-Version header '%s' in opening handshake request" % self.http_headers["sec-websocket-version"])

            if version not in self.versions:

                # respond with list of supported versions (descending order)
                #
                sv = sorted(self.versions)
                sv.reverse()
                svs = ','.join([str(x) for x in sv])
                return self.failHandshake("WebSocket version %d not supported (supported versions: %s)" % (version, svs),
                                          400,  # Bad Request
                                          [("Sec-WebSocket-Version", svs)])
            else:
                # store the protocol version we are supposed to talk
                self.websocket_version = version

            # Sec-WebSocket-Protocol
            #
            if 'sec-websocket-protocol' in self.http_headers:
                protocols = [str(x.strip()) for x in self.http_headers["sec-websocket-protocol"].split(",")]
                # check for duplicates in protocol header
                pp = {}
                for p in protocols:
                    if p in pp:
                        return self.failHandshake("duplicate protocol '%s' specified in HTTP Sec-WebSocket-Protocol header" % p)
                    else:
                        pp[p] = 1
                # ok, no duplicates, save list in order the client sent it
                self.websocket_protocols = protocols
            else:
                self.websocket_protocols = []

            # Origin / Sec-WebSocket-Origin
            # http://tools.ietf.org/html/draft-ietf-websec-origin-02
            #
            if self.websocket_version < 13:
                # Hybi, but only < Hybi-13
                websocket_origin_header_key = 'sec-websocket-origin'
            else:
                # RFC6455, >= Hybi-13
                websocket_origin_header_key = "origin"

            self.websocket_origin = ""
            if websocket_origin_header_key in self.http_headers:
                if http_headers_cnt[websocket_origin_header_key] > 1:
                    return self.failHandshake("HTTP Origin header appears more than once in opening handshake request")
                self.websocket_origin = self.http_headers[websocket_origin_header_key].strip()
            else:
                # non-browser clients are allowed to omit this header
                pass

            # check allowed WebSocket origins
            #
            origin_is_allowed = False
            for origin_pattern in self.allowedOriginsPatterns:
                if origin_pattern.match(self.websocket_origin):
                    origin_is_allowed = True
                    break
            if not origin_is_allowed:
                return self.failHandshake("WebSocket connection denied: origin '{0}' not allowed".format(self.websocket_origin))

            # Sec-WebSocket-Key
            #
            if 'sec-websocket-key' not in self.http_headers:
                return self.failHandshake("HTTP Sec-WebSocket-Key header missing")
            if http_headers_cnt["sec-websocket-key"] > 1:
                return self.failHandshake("HTTP Sec-WebSocket-Key header appears more than once in opening handshake request")
            key = self.http_headers["sec-websocket-key"].strip()
            if len(key) != 24:  # 16 bytes => (ceil(128/24)*24)/6 == 24
                return self.failHandshake("bad Sec-WebSocket-Key (length must be 24 ASCII chars) '%s'" % key)
            if key[-2:] != "==":  # 24 - ceil(128/6) == 2
                return self.failHandshake("bad Sec-WebSocket-Key (invalid base64 encoding) '%s'" % key)
            for c in key[:-2]:
                if c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/":
                    return self.failHandshake("bad character '%s' in Sec-WebSocket-Key (invalid base64 encoding) '%s'" % (c, key))

            # Sec-WebSocket-Extensions
            #
            self.websocket_extensions = []
            if 'sec-websocket-extensions' in self.http_headers:
                if http_headers_cnt["sec-websocket-extensions"] > 1:
                    return self.failHandshake("HTTP Sec-WebSocket-Extensions header appears more than once in opening handshake request")
                else:
                    # extensions requested/offered by client
                    #
                    self.websocket_extensions = self._parseExtensionsHeader(self.http_headers["sec-websocket-extensions"])

            # Ok, got complete HS input, remember rest (if any)
            #
            self.data = self.data[end_of_header + 4:]

            # store WS key
            #
            # noinspection PyUnboundLocalVariable
            self._wskey = key

            # DoS protection
            #
            if self.maxConnections > 0 and self.factory.countConnections > self.maxConnections:

                # maximum number of concurrent connections reached
                #
                self.failHandshake("maximum number of connections reached", code=503)  # Service Unavailable

            else:
                # WebSocket handshake validated => produce opening handshake response
                #
                request = ConnectionRequest(self.peer,
                                            self.http_headers,
                                            self.http_request_host,
                                            self.http_request_path,
                                            self.http_request_params,
                                            self.websocket_version,
                                            self.websocket_origin,
                                            self.websocket_protocols,
                                            self.websocket_extensions)
                # Now fire onConnect() on derived class, to give that class a chance to accept or deny
                # the connection. onConnect() may throw, in which case the connection is denied, or it
                # may return a protocol from the protocols provided by client or None.
                self._onConnect(request)

        elif self.serveFlashSocketPolicy or self.debug:
            flash_policy_file_request = self.data.find(b"<policy-file-request/>\x00")
            if flash_policy_file_request >= 0:
                if self.debug:
                    self.log.debug("received Flash Socket Policy File request")

                if self.serveFlashSocketPolicy:
                    if self.debug:
                        self.log.debug("sending Flash Socket Policy File :\n%s" % self.flashSocketPolicy)

                    self.sendData(self.flashSocketPolicy.encode('utf8'))

                    self.wasServingFlashSocketPolicyFile = True

                    self.dropConnection()
                else:
                    if self.debug:
                        self.log.debug("No Flash Policy File served. You might want to serve a Flask Socket Policy file on the destination port since you received a request for it. See WebSocketServerFactory.serveFlashSocketPolicy and WebSocketServerFactory.flashSocketPolicy")

    def succeedHandshake(self, res):
        """
        Callback after onConnect() returns successfully. Generates the response for the handshake.
        """
        protocol = None
        headers = {}
        if type(res) == tuple:
            if len(res) > 0:
                protocol = res[0]
            if len(res) > 1:
                headers = res[1]
        else:
            protocol = res

        if protocol is not None and not (protocol in self.websocket_protocols):
            raise Exception("protocol accepted must be from the list client sent or None")

        self.websocket_protocol_in_use = protocol
        key = self._wskey

        # extensions effectively in use for this connection
        #
        self.websocket_extensions_in_use = []

        extensionResponse = []

        # gets filled with permessage-compress offers from the client
        #
        pmceOffers = []

        # handle WebSocket extensions
        #
        for (extension, params) in self.websocket_extensions:

            if self.debug:
                self.log.debug("parsed WebSocket extension '%s' with params '%s'" % (extension, params))

            # process permessage-compress extension
            #
            if extension in PERMESSAGE_COMPRESSION_EXTENSION:

                PMCE = PERMESSAGE_COMPRESSION_EXTENSION[extension]

                try:
                    offer = PMCE['Offer'].parse(params)
                    pmceOffers.append(offer)
                except Exception as e:
                    return self.failHandshake(str(e))

            else:
                if self.debug:
                    self.log.debug("client requested '%s' extension we don't support or which is not activated" % extension)

        # handle permessage-compress offers by the client
        #
        if len(pmceOffers) > 0:
            accept = self.perMessageCompressionAccept(pmceOffers)
            if accept is not None:
                PMCE = PERMESSAGE_COMPRESSION_EXTENSION[accept.EXTENSION_NAME]
                self._perMessageCompress = PMCE['PMCE'].createFromOfferAccept(self.factory.isServer, accept)
                self.websocket_extensions_in_use.append(self._perMessageCompress)
                extensionResponse.append(accept.getExtensionString())
            else:
                if self.debug:
                    self.log.debug("client request permessage-compress extension, but we did not accept any offer [%s]" % pmceOffers)

        # build response to complete WebSocket handshake
        #
        response = "HTTP/1.1 101 Switching Protocols\x0d\x0a"

        if self.factory.server is not None and self.factory.server != "":
            response += "Server: %s\x0d\x0a" % self.factory.server

        response += "X-Powered-By: AutobahnPython/{0}\x0d\x0a".format(__version__)

        response += "Upgrade: WebSocket\x0d\x0a"
        response += "Connection: Upgrade\x0d\x0a"

        # optional, user supplied additional HTTP headers
        #
        # headers from factory, headers from onConnect
        for headers_source in (self.factory.headers.items(), headers.items()):
            for uh in headers_source:
                if isinstance(uh[1], six.string_types):
                    header_values = [uh[1]]
                else:
                    try:
                        header_values = iter(uh[1])
                    except TypeError:
                        header_values = [uh[1]]

                for header_value in header_values:
                    response += "%s: %s\x0d\x0a" % (uh[0], header_value)

        if self.websocket_protocol_in_use is not None:
            response += "Sec-WebSocket-Protocol: %s\x0d\x0a" % str(self.websocket_protocol_in_use)

        # compute Sec-WebSocket-Accept
        #
        sha1 = hashlib.sha1()
        # noinspection PyUnboundLocalVariable
        sha1.update(key.encode('utf8') + WebSocketProtocol._WS_MAGIC)
        sec_websocket_accept = base64.b64encode(sha1.digest())

        response += "Sec-WebSocket-Accept: %s\x0d\x0a" % sec_websocket_accept.decode()

        # agreed extensions
        #
        if len(extensionResponse) > 0:
            response += "Sec-WebSocket-Extensions: %s\x0d\x0a" % ', '.join(extensionResponse)

        # end of HTTP response headers
        response += "\x0d\x0a"
        response_body = None

        # send out opening handshake response
        #
        if self.debug:
            self.log.debug("sending HTTP response:\n\n%s" % response)
        self.sendData(response.encode('utf8'))

        if response_body:
            if self.debug:
                self.log.debug("sending HTTP response body:\n\n%s" % binascii.b2a_hex(response_body))
            self.sendData(response_body)

        # save response for testsuite
        #
        self.http_response_data = response

        # opening handshake completed, move WebSocket connection into OPEN state
        #
        self.state = WebSocketProtocol.STATE_OPEN

        # cancel any opening HS timer if present
        #
        if self.openHandshakeTimeoutCall is not None:
            if self.debugCodePaths:
                self.log.debug("openHandshakeTimeoutCall.cancel")
            self.openHandshakeTimeoutCall.cancel()
            self.openHandshakeTimeoutCall = None

        # init state
        #
        self.inside_message = False
        self.current_frame = None

        # automatic ping/pong
        #
        if self.autoPingInterval:
            self.autoPingPendingCall = txaio.call_later(self.autoPingInterval, self._sendAutoPing)

        # fire handler on derived class
        #
        if self.trackedTimings:
            self.trackedTimings.track("onOpen")
        self._onOpen()

        # process rest, if any
        #
        if len(self.data) > 0:
            self.consumeData()

    def failHandshake(self, reason, code=400, responseHeaders=None):
        """
        During opening handshake the client request was invalid, we send a HTTP
        error response and then drop the connection.
        """
        self.wasNotCleanReason = reason
        self.log.info("failing WebSocket opening handshake ('{reason}')", reason=reason)
        self.sendHttpErrorResponse(code, reason, responseHeaders)
        self.dropConnection(abort=False)

    def sendHttpErrorResponse(self, code, reason, responseHeaders=None):
        """
        Send out HTTP error response.
        """
        response = "HTTP/1.1 {0} {1}\x0d\x0a".format(code, reason)
        if responseHeaders:
            for h in responseHeaders:
                response += "{0}: {1}\x0d\x0a".format(h[0], h[1])
        response += "\x0d\x0a"
        self.sendData(response.encode('utf8'))

    def sendHtml(self, html):
        """
        Send HTML page HTTP response.
        """
        responseBody = html.encode('utf8')
        response = "HTTP/1.1 200 OK\x0d\x0a"
        if self.factory.server is not None and self.factory.server != "":
            response += "Server: %s\x0d\x0a" % self.factory.server
        response += "Content-Type: text/html; charset=UTF-8\x0d\x0a"
        response += "Content-Length: %d\x0d\x0a" % len(responseBody)
        response += "\x0d\x0a"
        self.sendData(response.encode('utf8'))
        self.sendData(responseBody)

    def sendRedirect(self, url):
        """
        Send HTTP Redirect (303) response.
        """
        response = "HTTP/1.1 303\x0d\x0a"
        if self.factory.server is not None and self.factory.server != "":
            response += "Server: %s\x0d\x0a" % self.factory.server
        response += "Location: %s\x0d\x0a" % url
        response += "\x0d\x0a"
        self.sendData(response.encode('utf8'))

    def sendServerStatus(self, redirectUrl=None, redirectAfter=0):
        """
        Used to send out server status/version upon receiving a HTTP/GET without
        upgrade to WebSocket header (and option serverStatus is True).
        """
        if redirectUrl:
            redirect = """<meta http-equiv="refresh" content="%d;URL='%s'">""" % (redirectAfter, redirectUrl)
        else:
            redirect = ""
        html = """
<!DOCTYPE html>
<html>
   <head>
      %s
      <style>
         body {
            color: #fff;
            background-color: #027eae;
            font-family: "Segoe UI", "Lucida Grande", "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: 16px;
         }

         a, a:visited, a:hover {
            color: #fff;
         }
      </style>
   </head>
   <body>
      <h1>AutobahnPython %s</h1>
      <p>
         I am not Web server, but a <b>WebSocket Endpoint</b>.
      </p>
      <p>
         You can talk to me using the <a href="http://tools.ietf.org/html/rfc6455">WebSocket</a> protocol.
      </p>
      <p>
         For more information, please see:
         <ul>
            <li><a href="http://autobahn.ws/python">AutobahnPython</a></li>
         </ul>
      </p>
   </body>
</html>
""" % (redirect, __version__)
        self.sendHtml(html)


class WebSocketServerFactory(WebSocketFactory):
    """
    A protocol factory for WebSocket servers.
    """

    protocol = WebSocketServerProtocol
    """
    The protocol to be spoken. Must be derived from :class:`autobahn.websocket.protocol.WebSocketServerProtocol`.
    """

    isServer = True
    """
    Flag indicating if this factory is client- or server-side.
    """

    def __init__(self,
                 url=None,
                 protocols=None,
                 server="AutobahnPython/%s" % __version__,
                 headers=None,
                 externalPort=None,
                 debug=False,
                 debugCodePaths=False):
        """
        Create instance of WebSocket server factory.

        :param url: The WebSocket URL this factory is working for, e.g. `ws://myhost.com/somepath`.
                    For non-TCP transports like pipes or Unix domain sockets, provide `None`.
                    This will use an implicit URL of `ws://localhost`.
        :type url: str
        :param protocols: List of subprotocols the server supports. The subprotocol used is the first from the list of subprotocols announced by the client that is contained in this list.
        :type protocols: list of strings
        :param server: Server as announced in HTTP response header during opening handshake or None (default: `AutobahnWebSocket/?.?.?`).
        :type server: str
        :param headers: An optional mapping of additional HTTP headers to send during the WebSocket opening handshake.
        :type headers: dict
        :param externalPort: Optionally, the external visible port this factory will be reachable under (i.e. when running behind a L2/L3 forwarding device).
        :type externalPort: int
        :param debug: Debug mode (default: `False`).
        :type debug: bool
        :param debugCodePaths: Debug code paths mode (default: `False`).
        :type debugCodePaths: bool
        """
        self.debug = debug
        self.debugCodePaths = debugCodePaths

        self.logOctets = debug
        self.logFrames = debug

        self.trackTimings = False

        # seed RNG which is used for WS frame masks generation
        random.seed()

        # default WS session parameters
        #
        self.setSessionParameters(url, protocols, server, headers, externalPort)

        # default WebSocket protocol options
        #
        self.resetProtocolOptions()

        # number of currently connected clients
        #
        self.countConnections = 0

    def setSessionParameters(self,
                             url=None,
                             protocols=None,
                             server=None,
                             headers=None,
                             externalPort=None):
        """
        Set WebSocket session parameters.

        :param url: The WebSocket URL this factory is working for, e.g. `ws://myhost.com/somepath`.
                    For non-TCP transports like pipes or Unix domain sockets, provide `None`.
                    This will use an implicit URL of `ws://localhost`.
        :type url: str
        :param protocols: List of subprotocols the server supports. The subprotocol used is the first from the list of subprotocols announced by the client that is contained in this list.
        :type protocols: list of strings
        :param server: Server as announced in HTTP response header during opening handshake.
        :type server: str
        :param headers: An optional mapping of additional HTTP headers to send during the WebSocket opening handshake.
        :type headers: dict
        :param externalPort: Optionally, the external visible port this server will be reachable under (i.e. when running behind a L2/L3 forwarding device).
        :type externalPort: int
        """
        # parse WebSocket URI into components
        (isSecure, host, port, resource, path, params) = parseWsUrl(url or "ws://localhost")
        if len(params) > 0:
            raise Exception("query parameters specified for server WebSocket URL")
        self.url = url
        self.isSecure = isSecure
        self.host = host
        self.port = port
        self.resource = resource
        self.path = path
        self.params = params

        self.protocols = protocols or []
        self.server = server
        self.headers = headers or {}

        if externalPort:
            self.externalPort = externalPort
        elif url:
            self.externalPort = self.port
        else:
            self.externalPort = None

    def resetProtocolOptions(self):
        """
        Reset all WebSocket protocol options to defaults.
        """
        self.versions = WebSocketProtocol.SUPPORTED_PROTOCOL_VERSIONS
        self.webStatus = True
        self.utf8validateIncoming = True
        self.requireMaskedClientFrames = True
        self.maskServerFrames = False
        self.applyMask = True
        self.maxFramePayloadSize = 0
        self.maxMessagePayloadSize = 0
        self.autoFragmentSize = 0
        self.failByDrop = True
        self.echoCloseCodeReason = False
        self.openHandshakeTimeout = 5
        self.closeHandshakeTimeout = 1
        self.tcpNoDelay = True
        self.serveFlashSocketPolicy = False
        self.flashSocketPolicy = u'''<cross-domain-policy>
     <allow-access-from domain="*" to-ports="*" />
</cross-domain-policy>\x00'''

        # permessage-XXX extension
        #
        self.perMessageCompressionAccept = lambda _: None

        # automatic ping/pong ("heartbeating")
        #
        self.autoPingInterval = 0
        self.autoPingTimeout = 0
        self.autoPingSize = 4

        # check WebSocket origin against this list
        self.allowedOrigins = ["*"]
        self.allowedOriginsPatterns = wildcards2patterns(self.allowedOrigins)

        # maximum number of concurrent connections
        self.maxConnections = 0

    def setProtocolOptions(self,
                           versions=None,
                           webStatus=None,
                           utf8validateIncoming=None,
                           maskServerFrames=None,
                           requireMaskedClientFrames=None,
                           applyMask=None,
                           maxFramePayloadSize=None,
                           maxMessagePayloadSize=None,
                           autoFragmentSize=None,
                           failByDrop=None,
                           echoCloseCodeReason=None,
                           openHandshakeTimeout=None,
                           closeHandshakeTimeout=None,
                           tcpNoDelay=None,
                           perMessageCompressionAccept=None,
                           autoPingInterval=None,
                           autoPingTimeout=None,
                           autoPingSize=None,
                           serveFlashSocketPolicy=None,
                           flashSocketPolicy=None,
                           allowedOrigins=None,
                           maxConnections=None):
        """
        Set WebSocket protocol options used as defaults for new protocol instances.

        :param versions: The WebSocket protocol versions accepted by the server (default: :func:`autobahn.websocket.protocol.WebSocketProtocol.SUPPORTED_PROTOCOL_VERSIONS`).
        :type versions: list of ints or None
        :param webStatus: Return server status/version on HTTP/GET without WebSocket upgrade header (default: `True`).
        :type webStatus: bool or None
        :param utf8validateIncoming: Validate incoming UTF-8 in text message payloads (default: `True`).
        :type utf8validateIncoming: bool or None
        :param maskServerFrames: Mask server-to-client frames (default: `False`).
        :type maskServerFrames: bool or None
        :param requireMaskedClientFrames: Require client-to-server frames to be masked (default: `True`).
        :type requireMaskedClientFrames: bool or None
        :param applyMask: Actually apply mask to payload when mask it present. Applies for outgoing and incoming frames (default: `True`).
        :type applyMask: bool or None
        :param maxFramePayloadSize: Maximum frame payload size that will be accepted when receiving or `0` for unlimited (default: `0`).
        :type maxFramePayloadSize: int or None
        :param maxMessagePayloadSize: Maximum message payload size (after reassembly of fragmented messages) that will be accepted when receiving or `0` for unlimited (default: `0`).
        :type maxMessagePayloadSize: int or None
        :param autoFragmentSize: Automatic fragmentation of outgoing data messages (when using the message-based API) into frames with payload length `<=` this size or `0` for no auto-fragmentation (default: `0`).
        :type autoFragmentSize: int or None
        :param failByDrop: Fail connections by dropping the TCP connection without performing closing handshake (default: `True`).
        :type failbyDrop: bool or None
        :param echoCloseCodeReason: Iff true, when receiving a close, echo back close code/reason. Otherwise reply with `code == 1000, reason = ""` (default: `False`).
        :type echoCloseCodeReason: bool or None
        :param openHandshakeTimeout: Opening WebSocket handshake timeout, timeout in seconds or `0` to deactivate (default: `0`).
        :type openHandshakeTimeout: float or None
        :param closeHandshakeTimeout: When we expect to receive a closing handshake reply, timeout in seconds (default: `1`).
        :type closeHandshakeTimeout: float or None
        :param tcpNoDelay: TCP NODELAY ("Nagle") socket option (default: `True`).
        :type tcpNoDelay: bool or None
        :param perMessageCompressionAccept: Acceptor function for offers.
        :type perMessageCompressionAccept: callable or None
        :param autoPingInterval: Automatically send WebSocket pings every given seconds. When the peer does not respond
           in `autoPingTimeout`, drop the connection. Set to `0` to disable. (default: `0`).
        :type autoPingInterval: float or None
        :param autoPingTimeout: Wait this many seconds for the peer to respond to automatically sent pings. If the
           peer does not respond in time, drop the connection. Set to `0` to disable. (default: `0`).
        :type autoPingTimeout: float or None
        :param autoPingSize: Payload size for automatic pings/pongs. Must be an integer from `[4, 125]`. (default: `4`).
        :type autoPingSize: int or None
        :param serveFlashSocketPolicy: Serve the Flash Socket Policy when we receive a policy file request on this protocol. (default: `False`).
        :type serveFlashSocketPolicy: bool or None
        :param flashSocketPolicy: The flash socket policy to be served when we are serving the Flash Socket Policy on this protocol
           and when Flash tried to connect to the destination port. It must end with a null character.
        :type flashSocketPolicy: str or None
        :param allowedOrigins: A list of allowed WebSocket origins (with '*' as a wildcard character).
        :type allowedOrigins: list or None
        :param maxConnections: Maximum number of concurrent connections. Set to `0` to disable (default: `0`).
        :type maxConnections: int or None
        """
        if versions is not None:
            for v in versions:
                if v not in WebSocketProtocol.SUPPORTED_PROTOCOL_VERSIONS:
                    raise Exception("invalid WebSocket protocol version %s (allowed values: %s)" % (v, str(WebSocketProtocol.SUPPORTED_PROTOCOL_VERSIONS)))
            if set(versions) != set(self.versions):
                self.versions = versions

        if webStatus is not None and webStatus != self.webStatus:
            self.webStatus = webStatus

        if utf8validateIncoming is not None and utf8validateIncoming != self.utf8validateIncoming:
            self.utf8validateIncoming = utf8validateIncoming

        if requireMaskedClientFrames is not None and requireMaskedClientFrames != self.requireMaskedClientFrames:
            self.requireMaskedClientFrames = requireMaskedClientFrames

        if maskServerFrames is not None and maskServerFrames != self.maskServerFrames:
            self.maskServerFrames = maskServerFrames

        if applyMask is not None and applyMask != self.applyMask:
            self.applyMask = applyMask

        if maxFramePayloadSize is not None and maxFramePayloadSize != self.maxFramePayloadSize:
            self.maxFramePayloadSize = maxFramePayloadSize

        if maxMessagePayloadSize is not None and maxMessagePayloadSize != self.maxMessagePayloadSize:
            self.maxMessagePayloadSize = maxMessagePayloadSize

        if autoFragmentSize is not None and autoFragmentSize != self.autoFragmentSize:
            self.autoFragmentSize = autoFragmentSize

        if failByDrop is not None and failByDrop != self.failByDrop:
            self.failByDrop = failByDrop

        if echoCloseCodeReason is not None and echoCloseCodeReason != self.echoCloseCodeReason:
            self.echoCloseCodeReason = echoCloseCodeReason

        if openHandshakeTimeout is not None and openHandshakeTimeout != self.openHandshakeTimeout:
            self.openHandshakeTimeout = openHandshakeTimeout

        if closeHandshakeTimeout is not None and closeHandshakeTimeout != self.closeHandshakeTimeout:
            self.closeHandshakeTimeout = closeHandshakeTimeout

        if tcpNoDelay is not None and tcpNoDelay != self.tcpNoDelay:
            self.tcpNoDelay = tcpNoDelay

        if perMessageCompressionAccept is not None and perMessageCompressionAccept != self.perMessageCompressionAccept:
            self.perMessageCompressionAccept = perMessageCompressionAccept

        if autoPingInterval is not None and autoPingInterval != self.autoPingInterval:
            self.autoPingInterval = autoPingInterval

        if autoPingTimeout is not None and autoPingTimeout != self.autoPingTimeout:
            self.autoPingTimeout = autoPingTimeout

        if autoPingSize is not None and autoPingSize != self.autoPingSize:
            assert(type(autoPingSize) == float or type(autoPingSize) in six.integer_types)
            assert(4 <= autoPingSize <= 125)
            self.autoPingSize = autoPingSize

        if serveFlashSocketPolicy is not None and serveFlashSocketPolicy != self.serveFlashSocketPolicy:
            self.serveFlashSocketPolicy = serveFlashSocketPolicy

        if flashSocketPolicy is not None and flashSocketPolicy != self.flashSocketPolicy:
            self.flashSocketPolicy = flashSocketPolicy

        if allowedOrigins is not None and allowedOrigins != self.allowedOrigins:
            self.allowedOrigins = allowedOrigins
            self.allowedOriginsPatterns = wildcards2patterns(self.allowedOrigins)

        if maxConnections is not None and maxConnections != self.maxConnections:
            assert(type(maxConnections) in six.integer_types)
            assert(maxConnections >= 0)
            self.maxConnections = maxConnections

    def getConnectionCount(self):
        """
        Get number of currently connected clients.

        :returns: int -- Number of currently connected clients.
        """
        return self.countConnections


class WebSocketClientProtocol(WebSocketProtocol):
    """
    Protocol base class for WebSocket clients.
    """

    CONFIG_ATTRS = WebSocketProtocol.CONFIG_ATTRS_COMMON + WebSocketProtocol.CONFIG_ATTRS_CLIENT

    def onConnect(self, response):
        """
        Callback fired directly after WebSocket opening handshake when new WebSocket server
        connection was established.

        :param response: WebSocket connection response information.
        :type response: instance of :class:`autobahn.websocket.protocol.ConnectionResponse`
        """
        pass

    def _connectionMade(self):
        """
        Called by network framework when new transport connection to server was established. Default
        implementation will start the initial WebSocket opening handshake (or proxy connect).
        When overriding in derived class, make sure to call this base class
        implementation _before_ your code.
        """
        WebSocketProtocol._connectionMade(self)
        if self.debug:
            self.log.debug("connection to %s established" % self.peer)

        if not self.factory.isServer and self.factory.proxy is not None:
            # start by doing a HTTP/CONNECT for explicit proxies
            self.startProxyConnect()
        else:
            # immediately start with the WebSocket opening handshake
            self.startHandshake()

    def _connectionLost(self, reason):
        """
        Called by network framework when established transport connection to server was lost. Default
        implementation will tear down all state properly.
        When overriding in derived class, make sure to call this base class
        implementation _after_ your code.
        """
        WebSocketProtocol._connectionLost(self, reason)

    def startProxyConnect(self):
        """
        Connect to explicit proxy.
        """
        # construct proxy connect HTTP request
        #
        request = "CONNECT %s:%d HTTP/1.1\x0d\x0a" % (self.factory.host.encode("utf-8"), self.factory.port)
        request += "Host: %s:%d\x0d\x0a" % (self.factory.host.encode("utf-8"), self.factory.port)
        request += "\x0d\x0a"

        if self.debug:
            self.log.debug(request)

        self.sendData(request)

    def processProxyConnect(self):
        """
        Process HTTP/CONNECT response from server.
        """
        # only proceed when we have fully received the HTTP request line and all headers
        #
        end_of_header = self.data.find(b"\x0d\x0a\x0d\x0a")
        if end_of_header >= 0:

            http_response_data = self.data[:end_of_header + 4]
            if self.debug:
                self.log.debug("received HTTP response:\n\n%s\n\n" % http_response_data)

            # extract HTTP status line and headers
            #
            (http_status_line, http_headers, http_headers_cnt) = parseHttpHeader(http_response_data)

            # validate proxy connect response
            #
            if self.debug:
                self.log.debug("received HTTP status line for proxy connect request : %s" % str(http_status_line))
                self.log.debug("received HTTP headers for proxy connect request : %s" % str(http_headers))

            # Response Line
            #
            sl = http_status_line.split()
            if len(sl) < 2:
                return self.failProxyConnect("Bad HTTP response status line '%s'" % http_status_line)

            # HTTP version
            #
            http_version = sl[0].strip()
            if http_version != "HTTP/1.1":
                return self.failProxyConnect("Unsupported HTTP version ('%s')" % http_version)

            # HTTP status code
            #
            try:
                status_code = int(sl[1].strip())
            except ValueError:
                return self.failProxyConnect("Bad HTTP status code ('%s')" % sl[1].strip())

            if not (200 <= status_code < 300):

                # FIXME: handle redirects
                # FIXME: handle authentication required

                if len(sl) > 2:
                    reason = " - %s" % ''.join(sl[2:])
                else:
                    reason = ""
                return self.failProxyConnect("HTTP proxy connect failed (%d%s)" % (status_code, reason))

            # Ok, got complete response for HTTP/CONNECT, remember rest (if any)
            #
            self.data = self.data[end_of_header + 4:]

            # opening handshake completed, move WebSocket connection into OPEN state
            #
            self.state = WebSocketProtocol.STATE_CONNECTING

            # process rest of buffered data, if any
            #
            if len(self.data) > 0:
                self.consumeData()

            # now start WebSocket opening handshake
            #
            self.startHandshake()

    def failProxyConnect(self, reason):
        """
        During initial explicit proxy connect, the server response indicates some failure and we drop the
        connection.
        """
        if self.debug:
            self.log.debug("failing proxy connect ('%s')" % reason)
        self.dropConnection(abort=True)

    def startHandshake(self):
        """
        Start WebSocket opening handshake.
        """

        # construct WS opening handshake HTTP header
        #
        request = "GET %s HTTP/1.1\x0d\x0a" % self.factory.resource

        if self.factory.useragent is not None and self.factory.useragent != "":
            request += "User-Agent: %s\x0d\x0a" % self.factory.useragent

        request += "Host: %s:%d\x0d\x0a" % (self.factory.host, self.factory.port)
        request += "Upgrade: WebSocket\x0d\x0a"
        request += "Connection: Upgrade\x0d\x0a"

        # this seems to prohibit some non-compliant proxies from removing the
        # connection "Upgrade" header
        # See also:
        # http://www.ietf.org/mail-archive/web/hybi/current/msg09841.html
        # http://code.google.com/p/chromium/issues/detail?id=148908
        #
        request += "Pragma: no-cache\x0d\x0a"
        request += "Cache-Control: no-cache\x0d\x0a"

        # optional, user supplied additional HTTP headers
        #
        for uh in self.factory.headers.items():
            request += "%s: %s\x0d\x0a" % (uh[0], uh[1])

        # handshake random key
        #
        self.websocket_key = base64.b64encode(os.urandom(16))
        request += "Sec-WebSocket-Key: %s\x0d\x0a" % self.websocket_key.decode()

        # optional origin announced
        #
        if self.factory.origin:
            if self.version > 10:
                request += "Origin: %s\x0d\x0a" % self.factory.origin
            else:
                request += "Sec-WebSocket-Origin: %s\x0d\x0a" % self.factory.origin

        # optional list of WS subprotocols announced
        #
        if len(self.factory.protocols) > 0:
            request += "Sec-WebSocket-Protocol: %s\x0d\x0a" % ','.join(self.factory.protocols)

        # extensions
        #
        extensions = []

        # permessage-compress offers
        #
        for offer in self.perMessageCompressionOffers:
            extensions.append(offer.getExtensionString())

        if len(extensions) > 0:
            request += "Sec-WebSocket-Extensions: %s\x0d\x0a" % ', '.join(extensions)

        # set WS protocol version
        #
        request += "Sec-WebSocket-Version: %d\x0d\x0a" % WebSocketProtocol.SPEC_TO_PROTOCOL_VERSION[self.version]

        request += "\x0d\x0a"

        self.http_request_data = request.encode('utf8')
        self.sendData(self.http_request_data)

        if self.debug:
            self.log.debug(request)

    def processHandshake(self):
        """
        Process WebSocket opening handshake response from server.
        """
        # only proceed when we have fully received the HTTP request line and all headers
        #
        end_of_header = self.data.find(b"\x0d\x0a\x0d\x0a")
        if end_of_header >= 0:

            self.http_response_data = self.data[:end_of_header + 4]
            if self.debug:
                self.log.debug("received HTTP response:\n\n%s\n\n" % self.http_response_data)

            # extract HTTP status line and headers
            #
            (self.http_status_line, self.http_headers, http_headers_cnt) = parseHttpHeader(self.http_response_data)

            # validate WebSocket opening handshake server response
            #
            if self.debug:
                self.log.debug("received HTTP status line in opening handshake : %s" % str(self.http_status_line))
                self.log.debug("received HTTP headers in opening handshake : %s" % str(self.http_headers))

            # Response Line
            #
            sl = self.http_status_line.split()
            if len(sl) < 2:
                return self.failHandshake("Bad HTTP response status line '%s'" % self.http_status_line)

            # HTTP version
            #
            http_version = sl[0].strip()
            if http_version != "HTTP/1.1":
                return self.failHandshake("Unsupported HTTP version ('%s')" % http_version)

            # HTTP status code
            #
            try:
                status_code = int(sl[1].strip())
            except ValueError:
                return self.failHandshake("Bad HTTP status code ('%s')" % sl[1].strip())
            if status_code != 101:  # Switching Protocols

                # FIXME: handle redirects
                # FIXME: handle authentication required

                if len(sl) > 2:
                    reason = " - %s" % ''.join(sl[2:])
                else:
                    reason = ""
                return self.failHandshake("WebSocket connection upgrade failed (%d%s)" % (status_code, reason))

            # Upgrade
            #
            if 'upgrade' not in self.http_headers:
                return self.failHandshake("HTTP Upgrade header missing")
            if self.http_headers["upgrade"].strip().lower() != "websocket":
                return self.failHandshake("HTTP Upgrade header different from 'websocket' (case-insensitive) : %s" % self.http_headers["upgrade"])

            # Connection
            #
            if 'connection' not in self.http_headers:
                return self.failHandshake("HTTP Connection header missing")
            connectionUpgrade = False
            for c in self.http_headers["connection"].split(","):
                if c.strip().lower() == "upgrade":
                    connectionUpgrade = True
                    break
            if not connectionUpgrade:
                return self.failHandshake("HTTP Connection header does not include 'upgrade' value (case-insensitive) : %s" % self.http_headers["connection"])

            # compute Sec-WebSocket-Accept
            #
            if 'sec-websocket-accept' not in self.http_headers:
                return self.failHandshake("HTTP Sec-WebSocket-Accept header missing in opening handshake reply")
            else:
                if http_headers_cnt["sec-websocket-accept"] > 1:
                    return self.failHandshake("HTTP Sec-WebSocket-Accept header appears more than once in opening handshake reply")
                sec_websocket_accept_got = self.http_headers["sec-websocket-accept"].strip()

                sha1 = hashlib.sha1()
                sha1.update(self.websocket_key + WebSocketProtocol._WS_MAGIC)
                sec_websocket_accept = base64.b64encode(sha1.digest()).decode()

                if sec_websocket_accept_got != sec_websocket_accept:
                    return self.failHandshake("HTTP Sec-WebSocket-Accept bogus value : expected %s / got %s" % (sec_websocket_accept, sec_websocket_accept_got))

            # Sec-WebSocket-Extensions
            #

            # extensions effectively in use for this connection
            #
            self.websocket_extensions_in_use = []

            if 'sec-websocket-extensions' in self.http_headers:

                if http_headers_cnt["sec-websocket-extensions"] > 1:
                    return self.failHandshake("HTTP Sec-WebSocket-Extensions header appears more than once in opening handshake reply")
                else:
                    # extensions select by server
                    #
                    websocket_extensions = self._parseExtensionsHeader(self.http_headers["sec-websocket-extensions"])

                # process extensions selected by server
                #
                for (extension, params) in websocket_extensions:

                    if self.debug:
                        self.log.debug("parsed WebSocket extension '%s' with params '%s'" % (extension, params))

                    # process permessage-compress extension
                    #
                    if extension in PERMESSAGE_COMPRESSION_EXTENSION:

                        # check that server only responded with 1 configuration ("PMCE")
                        #
                        if self._perMessageCompress is not None:
                            return self.failHandshake("multiple occurrence of a permessage-compress extension")

                        PMCE = PERMESSAGE_COMPRESSION_EXTENSION[extension]

                        try:
                            pmceResponse = PMCE['Response'].parse(params)
                        except Exception as e:
                            return self.failHandshake(str(e))

                        accept = self.perMessageCompressionAccept(pmceResponse)

                        if accept is None:
                            return self.failHandshake("WebSocket permessage-compress extension response from server denied by client")

                        self._perMessageCompress = PMCE['PMCE'].createFromResponseAccept(self.factory.isServer, accept)

                        self.websocket_extensions_in_use.append(self._perMessageCompress)

                    else:
                        return self.failHandshake("server wants to use extension '%s' we did not request, haven't implemented or did not enable" % extension)

            # handle "subprotocol in use" - if any
            #
            self.websocket_protocol_in_use = None
            if 'sec-websocket-protocol' in self.http_headers:
                if http_headers_cnt["sec-websocket-protocol"] > 1:
                    return self.failHandshake("HTTP Sec-WebSocket-Protocol header appears more than once in opening handshake reply")
                sp = str(self.http_headers["sec-websocket-protocol"].strip())
                if sp != "":
                    if sp not in self.factory.protocols:
                        return self.failHandshake("subprotocol selected by server (%s) not in subprotocol list requested by client (%s)" % (sp, str(self.factory.protocols)))
                    else:
                        # ok, subprotocol in use
                        #
                        self.websocket_protocol_in_use = sp

            # Ok, got complete HS input, remember rest (if any)
            #
            self.data = self.data[end_of_header + 4:]

            # opening handshake completed, move WebSocket connection into OPEN state
            #
            self.state = WebSocketProtocol.STATE_OPEN

            # cancel any opening HS timer if present
            #
            if self.openHandshakeTimeoutCall is not None:
                if self.debugCodePaths:
                    self.log.debug("openHandshakeTimeoutCall.cancel")
                self.openHandshakeTimeoutCall.cancel()
                self.openHandshakeTimeoutCall = None

            # init state
            #
            self.inside_message = False
            self.current_frame = None
            self.websocket_version = self.version

            # we handle this symmetrical to server-side .. that is, give the
            # client a chance to bail out .. i.e. on no subprotocol selected
            # by server
            try:
                response = ConnectionResponse(self.peer,
                                              self.http_headers,
                                              self.websocket_version,
                                              self.websocket_protocol_in_use,
                                              self.websocket_extensions_in_use)

                self._onConnect(response)

            except Exception as e:
                # immediately close the WS connection
                #
                self.failConnection(1000, str(e))
            else:
                # fire handler on derived class
                #
                if self.trackedTimings:
                    self.trackedTimings.track("onOpen")
                self._onOpen()

            # process rest, if any
            #
            if len(self.data) > 0:
                self.consumeData()

    def failHandshake(self, reason):
        """
        During opening handshake the server response is invalid and we drop the
        connection.
        """
        self.wasNotCleanReason = reason
        self.log.info("failing WebSocket opening handshake ('{reason}')", reason=reason)
        self.dropConnection(abort=True)


class WebSocketClientFactory(WebSocketFactory):
    """
    A protocol factory for WebSocket clients.
    """

    protocol = WebSocketClientProtocol
    """
    The protocol to be spoken. Must be derived from :class:`autobahn.websocket.protocol.WebSocketClientProtocol`.
    """

    isServer = False
    """
    Flag indicating if this factory is client- or server-side.
    """

    def __init__(self,
                 url=None,
                 origin=None,
                 protocols=None,
                 useragent="AutobahnPython/%s" % __version__,
                 headers=None,
                 proxy=None,
                 debug=False,
                 debugCodePaths=False):
        """
        Create instance of WebSocket client factory.

        Note that you MUST provide URL either here or set using
        :meth:`autobahn.websocket.WebSocketClientFactory.setSessionParameters`
        *before* the factory is started.

        :param url: WebSocket URL this factory will connect to, e.g. `ws://myhost.com/somepath?param1=23`.
                    For non-TCP transports like pipes or Unix domain sockets, provide `None`.
                    This will use an implicit URL of `ws://localhost`.
        :type url: str
        :param origin: The origin to be sent in WebSocket opening handshake or None (default: `None`).
        :type origin: str
        :param protocols: List of subprotocols the client should announce in WebSocket opening handshake (default: `[]`).
        :type protocols: list of strings
        :param useragent: User agent as announced in HTTP request header or None (default: `AutobahnWebSocket/?.?.?`).
        :type useragent: str
        :param headers: An optional mapping of additional HTTP headers to send during the WebSocket opening handshake.
        :type headers: dict
        :param proxy: Explicit proxy server to use (`hostname:port` or `IP:port`), e.g. `192.168.1.100:8080`.
        :type proxy: str
        :param debug: Debug mode (default: `False`).
        :type debug: bool
        :param debugCodePaths: Debug code paths mode (default: `False`).
        :type debugCodePaths: bool
        """
        self.debug = debug
        self.debugCodePaths = debugCodePaths

        self.logOctets = debug
        self.logFrames = debug

        self.trackTimings = False

        # seed RNG which is used for WS opening handshake key and WS frame masks generation
        random.seed()

        # default WS session parameters
        #
        self.setSessionParameters(url, origin, protocols, useragent, headers, proxy)

        # default WebSocket protocol options
        #
        self.resetProtocolOptions()

    def setSessionParameters(self,
                             url=None,
                             origin=None,
                             protocols=None,
                             useragent=None,
                             headers=None,
                             proxy=None):
        """
        Set WebSocket session parameters.

        :param url: WebSocket URL this factory will connect to, e.g. `ws://myhost.com/somepath?param1=23`.
                    For non-TCP transports like pipes or Unix domain sockets, provide `None`.
                    This will use an implicit URL of `ws://localhost`.
        :type url: str
        :param origin: The origin to be sent in opening handshake.
        :type origin: str
        :param protocols: List of WebSocket subprotocols the client should announce in opening handshake.
        :type protocols: list of strings
        :param useragent: User agent as announced in HTTP request header during opening handshake.
        :type useragent: str
        :param headers: An optional mapping of additional HTTP headers to send during the WebSocket opening handshake.
        :type headers: dict
        """
        # parse WebSocket URI into components
        (isSecure, host, port, resource, path, params) = parseWsUrl(url or "ws://localhost")
        self.url = url
        self.isSecure = isSecure
        self.host = host
        self.port = port
        self.resource = resource
        self.path = path
        self.params = params

        self.origin = origin
        self.protocols = protocols or []
        self.useragent = useragent
        self.headers = headers or {}

        self.proxy = proxy

    def resetProtocolOptions(self):
        """
        Reset all WebSocket protocol options to defaults.
        """
        self.version = WebSocketProtocol.DEFAULT_SPEC_VERSION
        self.utf8validateIncoming = True
        self.acceptMaskedServerFrames = False
        self.maskClientFrames = True
        self.applyMask = True
        self.maxFramePayloadSize = 0
        self.maxMessagePayloadSize = 0
        self.autoFragmentSize = 0
        self.failByDrop = True
        self.echoCloseCodeReason = False
        self.serverConnectionDropTimeout = 1
        self.openHandshakeTimeout = 5
        self.closeHandshakeTimeout = 1
        self.tcpNoDelay = True

        # permessage-XXX extensions
        #
        self.perMessageCompressionOffers = []
        self.perMessageCompressionAccept = lambda _: None

        # automatic ping/pong ("heartbeating")
        #
        self.autoPingInterval = 0
        self.autoPingTimeout = 0
        self.autoPingSize = 4

    def setProtocolOptions(self,
                           version=None,
                           utf8validateIncoming=None,
                           acceptMaskedServerFrames=None,
                           maskClientFrames=None,
                           applyMask=None,
                           maxFramePayloadSize=None,
                           maxMessagePayloadSize=None,
                           autoFragmentSize=None,
                           failByDrop=None,
                           echoCloseCodeReason=None,
                           serverConnectionDropTimeout=None,
                           openHandshakeTimeout=None,
                           closeHandshakeTimeout=None,
                           tcpNoDelay=None,
                           perMessageCompressionOffers=None,
                           perMessageCompressionAccept=None,
                           autoPingInterval=None,
                           autoPingTimeout=None,
                           autoPingSize=None):
        """
        Set WebSocket protocol options used as defaults for _new_ protocol instances.

        :param version: The WebSocket protocol spec (draft) version to be used (default: :func:`autobahn.websocket.protocol.WebSocketProtocol.SUPPORTED_PROTOCOL_VERSIONS`).
        :param utf8validateIncoming: Validate incoming UTF-8 in text message payloads (default: `True`).
        :type utf8validateIncoming: bool
        :param acceptMaskedServerFrames: Accept masked server-to-client frames (default: `False`).
        :type acceptMaskedServerFrames: bool
        :param maskClientFrames: Mask client-to-server frames (default: `True`).
        :type maskClientFrames: bool
        :param applyMask: Actually apply mask to payload when mask it present. Applies for outgoing and incoming frames (default: `True`).
        :type applyMask: bool
        :param maxFramePayloadSize: Maximum frame payload size that will be accepted when receiving or `0` for unlimited (default: `0`).
        :type maxFramePayloadSize: int
        :param maxMessagePayloadSize: Maximum message payload size (after reassembly of fragmented messages) that will be accepted when receiving or `0` for unlimited (default: `0`).
        :type maxMessagePayloadSize: int
        :param autoFragmentSize: Automatic fragmentation of outgoing data messages (when using the message-based API) into frames with payload length `<=` this size or `0` for no auto-fragmentation (default: `0`).
        :type autoFragmentSize: int
        :param failByDrop: Fail connections by dropping the TCP connection without performing closing handshake (default: `True`).
        :type failbyDrop: bool
        :param echoCloseCodeReason: Iff true, when receiving a close, echo back close code/reason. Otherwise reply with `code == 1000, reason = ""` (default: `False`).
        :type echoCloseCodeReason: bool
        :param serverConnectionDropTimeout: When the client expects the server to drop the TCP, timeout in seconds (default: `1`).
        :type serverConnectionDropTimeout: float
        :param openHandshakeTimeout: Opening WebSocket handshake timeout, timeout in seconds or `0` to deactivate (default: `0`).
        :type openHandshakeTimeout: float
        :param closeHandshakeTimeout: When we expect to receive a closing handshake reply, timeout in seconds (default: `1`).
        :type closeHandshakeTimeout: float
        :param tcpNoDelay: TCP NODELAY ("Nagle"): bool socket option (default: `True`).
        :type tcpNoDelay: bool
        :param perMessageCompressionOffers: A list of offers to provide to the server for the permessage-compress WebSocket extension. Must be a list of instances of subclass of PerMessageCompressOffer.
        :type perMessageCompressionOffers: list of instance of subclass of PerMessageCompressOffer
        :param perMessageCompressionAccept: Acceptor function for responses.
        :type perMessageCompressionAccept: callable
        :param autoPingInterval: Automatically send WebSocket pings every given seconds. When the peer does not respond
           in `autoPingTimeout`, drop the connection. Set to `0` to disable. (default: `0`).
        :type autoPingInterval: float or None
        :param autoPingTimeout: Wait this many seconds for the peer to respond to automatically sent pings. If the
           peer does not respond in time, drop the connection. Set to `0` to disable. (default: `0`).
        :type autoPingTimeout: float or None
        :param autoPingSize: Payload size for automatic pings/pongs. Must be an integer from `[4, 125]`. (default: `4`).
        :type autoPingSize: int
        """
        if version is not None:
            if version not in WebSocketProtocol.SUPPORTED_SPEC_VERSIONS:
                raise Exception("invalid WebSocket draft version %s (allowed values: %s)" % (version, str(WebSocketProtocol.SUPPORTED_SPEC_VERSIONS)))
            if version != self.version:
                self.version = version

        if utf8validateIncoming is not None and utf8validateIncoming != self.utf8validateIncoming:
            self.utf8validateIncoming = utf8validateIncoming

        if acceptMaskedServerFrames is not None and acceptMaskedServerFrames != self.acceptMaskedServerFrames:
            self.acceptMaskedServerFrames = acceptMaskedServerFrames

        if maskClientFrames is not None and maskClientFrames != self.maskClientFrames:
            self.maskClientFrames = maskClientFrames

        if applyMask is not None and applyMask != self.applyMask:
            self.applyMask = applyMask

        if maxFramePayloadSize is not None and maxFramePayloadSize != self.maxFramePayloadSize:
            self.maxFramePayloadSize = maxFramePayloadSize

        if maxMessagePayloadSize is not None and maxMessagePayloadSize != self.maxMessagePayloadSize:
            self.maxMessagePayloadSize = maxMessagePayloadSize

        if autoFragmentSize is not None and autoFragmentSize != self.autoFragmentSize:
            self.autoFragmentSize = autoFragmentSize

        if failByDrop is not None and failByDrop != self.failByDrop:
            self.failByDrop = failByDrop

        if echoCloseCodeReason is not None and echoCloseCodeReason != self.echoCloseCodeReason:
            self.echoCloseCodeReason = echoCloseCodeReason

        if serverConnectionDropTimeout is not None and serverConnectionDropTimeout != self.serverConnectionDropTimeout:
            self.serverConnectionDropTimeout = serverConnectionDropTimeout

        if openHandshakeTimeout is not None and openHandshakeTimeout != self.openHandshakeTimeout:
            self.openHandshakeTimeout = openHandshakeTimeout

        if closeHandshakeTimeout is not None and closeHandshakeTimeout != self.closeHandshakeTimeout:
            self.closeHandshakeTimeout = closeHandshakeTimeout

        if tcpNoDelay is not None and tcpNoDelay != self.tcpNoDelay:
            self.tcpNoDelay = tcpNoDelay

        if perMessageCompressionOffers is not None and pickle.dumps(perMessageCompressionOffers) != pickle.dumps(self.perMessageCompressionOffers):
            if type(perMessageCompressionOffers) == list:
                #
                # FIXME: more rigorous verification of passed argument
                #
                self.perMessageCompressionOffers = copy.deepcopy(perMessageCompressionOffers)
            else:
                raise Exception("invalid type %s for perMessageCompressionOffers - expected list" % type(perMessageCompressionOffers))

        if perMessageCompressionAccept is not None and perMessageCompressionAccept != self.perMessageCompressionAccept:
            self.perMessageCompressionAccept = perMessageCompressionAccept

        if autoPingInterval is not None and autoPingInterval != self.autoPingInterval:
            self.autoPingInterval = autoPingInterval

        if autoPingTimeout is not None and autoPingTimeout != self.autoPingTimeout:
            self.autoPingTimeout = autoPingTimeout

        if autoPingSize is not None and autoPingSize != self.autoPingSize:
            assert(type(autoPingSize) == float or type(autoPingSize) in six.integer_types)
            assert(4 <= autoPingSize <= 125)
            self.autoPingSize = autoPingSize
