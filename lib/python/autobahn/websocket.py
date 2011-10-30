###############################################################################
##
##  Copyright 2011 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

## The Python urlparse module currently does not contain the ws/wss
## schemes, so we add those dynamically (which is a hack of course).
##
import urlparse
wsschemes = ["ws", "wss"]
urlparse.uses_relative.extend(wsschemes)
urlparse.uses_netloc.extend(wsschemes)
urlparse.uses_params.extend(wsschemes)
urlparse.uses_query.extend(wsschemes)
urlparse.uses_fragment.extend(wsschemes)

from twisted.internet import reactor, protocol
from twisted.python import log
import urllib
import binascii
import hashlib
import base64
import struct
import random
import os
from collections import deque
from utf8validator import Utf8Validator
from httpstatus import *
import autobahn # need autobahn.version


def createWsUrl(hostname, port = None, isSecure = False, path = None, params = None):
   """
   Create a WbeSocket URL from components.

   :param hostname: WebSocket server hostname.
   :type hostname: str
   :param port: WebSocket service port or None (to select default ports 80/443 depending on isSecure).
   :type port: int
   :param isSecure: Set True for secure WebSockets ("wss" scheme).
   :type isSecure: bool
   :param path: Path component of addressed resource (will be properly URL escaped).
   :type path: str
   :param params: A dictionary of key-values to construct the query component of the addressed resource (will be properly URL escaped).
   :type params: dict
   :returns str -- Constructed WebSocket URL.
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
      ppath = urllib.quote(path)
   else:
      ppath = "/"
   if params is not None:
      query = urllib.urlencode(params)
   else:
      query = None
   return urlparse.urlunparse((scheme, netloc, ppath, None, query, None))


def parseWsUrl(url):
   """
   Parses as WebSocket URL into it's components and returns a tuple (isSecure, host, port, resource, path, params).

   isSecure is a flag which is True for wss URLs.
   host is the hostname or IP from the URL.
   port is the port from the URL or standard port derived from scheme (ws = 80, wss = 443).
   resource is the /resource name/ from the URL, the /path/ together with the (optional) /query/ component.
   path is the /path/ component properly unescaped.
   params is the /query) component properly unescaped and returned as dictionary.

   :param url: A valid WebSocket URL, i.e. ws://localhost:9000/myresource?param1=23&param2=666
   :type url: str
   :returns: tuple -- A tuple (isSecure, host, port, resource, path, params)
   """
   parsed = urlparse.urlparse(url)
   if parsed.scheme not in ["ws", "wss"]:
      raise Exception("invalid WebSocket scheme '%s'" % parsed.scheme)
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
      path = urllib.unquote(ppath)
   else:
      ppath = "/"
      path = ppath
   if parsed.query is not None and parsed.query != "":
      resource = ppath + "?" + parsed.query
      params = urlparse.parse_qs(parsed.query)
   else:
      resource = ppath
      params = {}
   return (parsed.scheme == "wss", parsed.hostname, port, resource, path, params)


def connectWS(factory, contextFactory = None, timeout = 30, bindAddress = None):
   """
   Establish WebSockets connection to a server. The connection parameters like target
   host, port, resource and others are provided via the factory.

   :param factory: The WebSockets protocol factory to be used for creating client protocol instances.
   :type factory: An :class:`autobahn.websocket.WebSocketClientFactory` instance.
   :param contextFactory: SSL context factory, required for secure WebSockets connections ("wss").
   :type contextFactory: A twisted.internet.ssl.ClientContextFactory instance.
   :param timeout: Number of seconds to wait before assuming the connection has failed.
   :type timeout: int
   :param bindAddress: A (host, port) tuple of local address to bind to, or None.
   :type bindAddress: tuple
   :returns: obj -- An object which provides twisted.interface.IConnector.
   """
   if factory.isSecure:
      if contextFactory is None:
         raise Exception("Secure WebSocket connection requested, but no SSL context factory given")
      conn = reactor.connectSSL(factory.host, factory.port, factory, contextFactory, timeout, bindAddress)
   else:
      conn = reactor.connectTCP(factory.host, factory.port, factory, timeout, bindAddress)
   return conn


def listenWS(factory, contextFactory = None, backlog = 50, interface = ''):
   """
   Listen for incoming WebSocket connections from clients. The connection parameters like
   listening port and others are provided via the factory.

   :param factory: The WebSockets protocol factory to be used for creating server protocol instances.
   :type factory: An :class:`autobahn.websocket.WebSocketServerFactory` instance.
   :param contextFactory: SSL context factory, required for secure WebSockets connections ("wss").
   :type contextFactory: A twisted.internet.ssl.ContextFactory.
   :param backlog: Size of the listen queue.
   :type backlog: int
   :param interface: The interface (derived from hostname given) to bind to, defaults to '' (all).
   :type interface: str
   :returns: obj -- An object that provides twisted.interface.IListeningPort.
   """
   if factory.isSecure:
      if contextFactory is None:
         raise Exception("Secure WebSocket listen requested, but no SSL context factory given")
      listener = reactor.listenSSL(factory.port, factory, contextFactory, backlog, interface)
   else:
      listener = reactor.listenTCP(factory.port, factory, backlog, interface)
   return listener


class FrameHeader:
   """
   Thin-wrapper for storing WebSockets frame metadata and current frame pointer.

   FOR INTERNAL USE ONLY!
   """

   def __init__(self, opcode, fin, rsv, length, mask, mask_array):
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
      :param mask: Frame mask (or None) as (binary) string.
      :type mask: str
      :param mask_array: Frame mask (or None) as array (of length 4) of ints.
      :type mask_array: array of ints
      """
      self.opcode = opcode
      self.fin = fin
      self.rsv = rsv
      self.length = length
      self.ptr = 0
      self.mask = mask
      self.mask_array = mask_array


class HttpException():
   """
   Throw an instance of this class to deny a WebSockets connection
   during handshake in :meth:`autobahn.websocket.WebSocketServerProtocol.onConnect`.
   You can find definitions of HTTP status codes in module :mod:`autobahn.httpstatus`.
   """

   def __init__(self, code, reason):
      """
      Constructor.

      :param code: HTTP error code.
      :type code: int
      :param reason: HTTP error reason.
      :type reason: str
      """
      self.code = code
      self.reason = reason


class ConnectionRequest():
   """
   Thin-wrapper for WebSockets connection request information
   provided in :meth:`autobahn.websocket.WebSocketServerProtocol.onConnect` when a WebSockets
   client establishes a connection to a WebSockets server.
   """
   def __init__(self, peer, peerstr, headers, host, path, params, version, origin, protocols, extensions):
      """
      Constructor.

      :param peer: IP address/port of the connecting client.
      :type peer: object
      :param peerstr: IP address/port of the connecting client as string.
      :type peerstr: str
      :param headers: HTTP headers from opening handshake request.
      :type headers: dict
      :param host: Host from opening handshake HTTP header.
      :type host: str
      :param path: Path from requested HTTP resource URI. For example, a resource URI of "/myservice?foo=23&foo=66&bar=2" will be parsed to "/myservice".
      :type path: str
      :param params: Query parameters (if any) from requested HTTP resource URI. For example, a resource URI of "/myservice?foo=23&foo=66&bar=2" will be parsed to {'foo': ['23', '66'], 'bar': ['2']}.
      :type params: dict of arrays of strings
      :param version: The WebSockets protocol version the client announced (and will be spoken, when connection is accepted).
      :type version: int
      :param origin: The WebSockets origin header or None. Note that this only a reliable source of information for browser clients!
      :type origin: str
      :param protocols: The WebSockets (sub)protocols the client announced. You must select and return one of those (or None) in :meth:`autobahn.websocket.WebSocketServerProtocol.onConnect`.
      :type protocols: array of strings
      :param extensions: The WebSockets extensions the client requested and the server accepted (and thus will be spoken, when WS connection is established).
      :type extensions: array of strings
      """
      self.peer = peer
      self.peerstr = peerstr
      self.headers = headers
      self.host = host
      self.path = path
      self.params = params
      self.version = version
      self.origin = origin
      self.protocols = protocols
      self.extensions = extensions


def parseHttpHeader(data):
   """
   Parses the beginning of a HTTP request header (the data up to the \n\n line) into a pair
   of status line and HTTP headers dictionary.
   Header keys are normalized to all-lower-case.

   FOR INTERNAL USE ONLY!

   :param data: The HTTP header data up to the \n\n line.
   :type data: str
   """
   raw = data.splitlines()
   http_status_line = raw[0].strip()
   http_headers = {}
   http_headers_cnt = {}
   for h in raw[1:]:
      i = h.find(":")
      if i > 0:
         ## HTTP header keys are case-insensitive
         key = h[:i].strip().lower()

         ## not sure if UTF-8 is allowed for HTTP header values..
         value = h[i+1:].strip().decode("utf-8")

         ## handle HTTP headers split across multiple lines
         if http_headers.has_key(key):
            http_headers[key] += ", %s" % value
            http_headers_cnt[key] += 1
         else:
            http_headers[key] = value
            http_headers_cnt[key] = 1
      else:
         # skip bad HTTP header
         pass
   return (http_status_line, http_headers, http_headers_cnt)


class WebSocketProtocol(protocol.Protocol):
   """
   A Twisted Protocol class for WebSockets. This class is used by both WebSocket
   client and server protocol version. It is unusable standalone, for example
   the WebSockets initial handshake is implemented in derived class differently
   for clients and servers.
   """

   SUPPORTED_SPEC_VERSIONS = [10, 11, 12, 13, 14, 15, 16, 17]
   """
   WebSockets protocol spec (draft) versions supported by this implementation.
   """

   SUPPORTED_PROTOCOL_VERSIONS = [8, 13]
   """
   WebSockets protocol versions supported by this implementation.
   """

   SPEC_TO_PROTOCOL_VERSION = {10: 8, 11: 8, 12: 8, 13: 13, 14: 13, 15: 13, 16: 13, 17: 13}
   """
   Mapping from protocol spec (draft) version to protocol version.
   """

   PROTOCOL_TO_SPEC_VERSION = {8: 12, 13: 17}
   """
   Mapping from protocol version to the latest protocol spec (draft) version
   using that protocol version.
   """

   DEFAULT_SPEC_VERSION = 10
   """
   Default WebSockets protocol spec (draft) version this implementation speaks.
   We use Hybi-10, since this is what is currently targeted by widely distributed
   browsers (namely Firefox 8 and the like).
   """

   WS_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
   """Protocol defined magic used during WebSocket handshake."""

   QUEUED_WRITE_DELAY = 0.00001
   """For synched/chopped writes, this is the reactor reentry delay in seconds."""

   MESSAGE_TYPE_TEXT = 1
   """WebSockets text message type (UTF-8 payload)."""

   MESSAGE_TYPE_BINARY = 2
   """WebSockets binary message type (arbitrary binary payload)."""

   ## WebSockets protocol state:
   ## STATE_CONNECTING => STATE_OPEN => STATE_CLOSING => STATE_CLOSED
   ##
   STATE_CLOSED = 0
   STATE_CONNECTING = 1
   STATE_CLOSING = 2
   STATE_OPEN = 3

   ## Streaming Send State
   SEND_STATE_GROUND = 0
   SEND_STATE_MESSAGE_BEGIN = 1
   SEND_STATE_INSIDE_MESSAGE = 2
   SEND_STATE_INSIDE_MESSAGE_FRAME = 3

   ## WebSockets protocol close codes
   ##
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

   CLOSE_STATUS_CODE_NULL = 1005 # MUST NOT be set in close frame!
   """No status received. (MUST NOT be used as status code when sending a close)."""

   CLOSE_STATUS_CODE_ABNORMAL_CLOSE = 1006 # MUST NOT be set in close frame!
   """Abnormal close of connection. (MUST NOT be used as status code when sending a close)."""

   CLOSE_STATUS_CODE_INVALID_PAYLOAD = 1007
   """Invalid frame payload data."""

   CLOSE_STATUS_CODE_POLICY_VIOLATION = 1008
   """Policy violation."""

   CLOSE_STATUS_CODE_MESSAGE_TOO_BIG = 1009
   """Message too big."""

   CLOSE_STATUS_CODE_MANDATORY_EXTENSION = 1010
   """Mandatory extension."""

   CLOSE_STATUS_CODES_ALLOWED = [CLOSE_STATUS_CODE_NORMAL,
                                 CLOSE_STATUS_CODE_GOING_AWAY,
                                 CLOSE_STATUS_CODE_PROTOCOL_ERROR,
                                 CLOSE_STATUS_CODE_UNSUPPORTED_DATA,
                                 CLOSE_STATUS_CODE_INVALID_PAYLOAD,
                                 CLOSE_STATUS_CODE_POLICY_VIOLATION,
                                 CLOSE_STATUS_CODE_MESSAGE_TOO_BIG,
                                 CLOSE_STATUS_CODE_MANDATORY_EXTENSION]
   """Status codes allowed to send in close."""


   def onOpen(self):
      """
      Callback when initial WebSockets handshake was completed. Now you may send messages.
      Default implementation does nothing. Override in derived class.
      """
      if self.debugCodePaths:
         log.msg("WebSocketProtocol.onOpen")


   def onMessageBegin(self, opcode):
      """
      Callback when receiving a new message has begun. Default implementation will
      prepare to buffer message frames. Override in derived class.

      :param opcode: Opcode of message.
      :type opcode: int
      """
      self.message_opcode = opcode
      self.message_data = []
      self.message_data_total_length = 0


   def onMessageFrameBegin(self, length, reserved):
      """
      Callback when receiving a new message frame has begun. Default implementation will
      prepare to buffer message frame data. Override in derived class.

      :param length: Payload length of message frame which is to be received.
      :type length: int
      :param reserved: Reserved bits set in frame (an integer from 0 to 7).
      :type reserved: int
      """
      if not self.failedByMe:
         self.message_data_total_length += length
         if self.maxMessagePayloadSize > 0 and self.message_data_total_length > self.maxMessagePayloadSize:
            self.wasMaxMessagePayloadSizeExceeded = True
            self.failConnection(WebSocketProtocol.CLOSE_STATUS_CODE_MESSAGE_TOO_BIG, "message exceeds payload limit of %d octets" % self.maxMessagePayloadSize)
         else:
            self.frame_length = length
            self.frame_reserved = reserved
            self.frame_data = []
            self.frame_data_total_length = 0


   def onMessageFrameData(self, payload):
      """
      Callback when receiving data witin message frame. Default implementation will
      buffer data for frame. Override in derived class.

      :param payload: Partial payload for message frame.
      :type payload: str
      """
      if not self.failedByMe:
         self.frame_data_total_length += len(payload)
         if self.maxFramePayloadSize > 0 and self.frame_data_total_length > self.maxFramePayloadSize:
            self.wasMaxFramePayloadSizeExceeded = True
            self.failConnection(WebSocketProtocol.CLOSE_STATUS_CODE_POLICY_VIOLATION, "frame exceeds payload limit of %d octets" % self.maxFramePayloadSize)
         else:
            self.frame_data.append(payload)


   def onMessageFrameEnd(self):
      """
      Callback when a message frame has been completely received. Default implementation
      will flatten the buffered frame data and callback onMessageFrame. Override
      in derived class.
      """
      if not self.failedByMe:
         data = bytearray().join(self.frame_data)
         self.logRxFrame(self.current_frame.fin, self.current_frame.rsv, self.current_frame.opcode, self.current_frame.mask is not None, self.current_frame.length, self.current_frame.mask, data)
         self.onMessageFrame(data, self.frame_reserved)


   def onMessageFrame(self, payload, reserved):
      """
      Callback fired when complete message frame has been received. Default implementation
      will buffer frame for message. Override in derived class.

      :param payload: Message frame payload.
      :type payload: str
      :param reserved: Reserved bits set in frame (an integer from 0 to 7).
      :type reserved: int
      """
      if not self.failedByMe:
         self.message_data.append(payload)


   def onMessageEnd(self):
      """
      Callback when a message has been completely received. Default implementation
      will flatten the buffered frames and callback onMessage. Override
      in derived class.
      """
      if not self.failedByMe:
         data = bytearray().join(self.message_data)
         self.onMessage(str(data), self.message_opcode == WebSocketProtocol.MESSAGE_TYPE_BINARY)
         self.message_opcode = None
         self.message_data = None


   def onMessage(self, payload, binary):
      """
      Callback when a complete message was received. Default implementation does nothing.
      Override in derived class.

      :param payload: Message payload (UTF-8 encoded text string or binary string). Can also be an empty string, when message contained no payload.
      :type payload: str
      :param binary: If True, payload is binary, otherwise text.
      :type binary: bool
      """
      if self.debug:
         log.msg("WebSocketProtocol.onMessage")


   def onPing(self, payload):
      """
      Callback when Ping was received. Default implementation responds
      with a Pong. Override in derived class.

      :param payload: Payload of Ping, when there was any. Can be arbitrary, up to 125 octets.
      :type payload: str
      """
      if self.debug:
         log.msg("WebSocketProtocol.onPing")
      if self.state == WebSocketProtocol.STATE_OPEN:
         self.sendPong(payload)


   def onPong(self, payload):
      """
      Callback when Pong was received. Default implementation does nothing.
      Override in derived class.

      :param payload: Payload of Pong, when there was any. Can be arbitrary, up to 125 octets.
      """
      if self.debug:
         log.msg("WebSocketProtocol.onPong")


   def onClose(self, wasClean, code, reason):
      """
      Callback when the connection has been closed. Override in derived class.

      :param wasClean: True, iff the connection was closed cleanly.
      :type wasClean: bool
      :param code: None or close status code (sent by peer), if there was one (:class:`WebSocketProtocol`.CLOSE_STATUS_CODE_*).
      :type code: int
      :param reason: None or close reason (sent by peer) (when present, a status code MUST have been also be present).
      :type reason: str
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
         log.msg(s)


   def onCloseFrame(self, code, reasonRaw):
      """
      Callback when a Close frame was received. The default implementation answers by
      sending a Close when no Close was sent before. Otherwise it drops
      the TCP connection either immediately (when we are a server) or after a timeout
      (when we are a client and expect the server to drop the TCP).

      :param code: None or close status code, if there was one (:class:`WebSocketProtocol`.CLOSE_STATUS_CODE_*).
      :type code: int
      :param reason: None or close reason (when present, a status code MUST have been also be present).
      :type reason: str
      """
      if self.debugCodePaths:
         log.msg("WebSocketProtocol.onCloseFrame")

      self.remoteCloseCode = code
      self.remoteCloseReason = reasonRaw

      ## reserved close codes: 0-999, 1004, 1005, 1006, 1011-2999, >= 5000
      ##
      if code is not None and (code < 1000 or (code >= 1000 and code <= 2999 and code not in WebSocketProtocol.CLOSE_STATUS_CODES_ALLOWED) or code >= 5000):
         if self.protocolViolation("invalid close code %d" % code):
            return True

      ## closing reason
      ##
      if reasonRaw is not None:
         ## we use our own UTF-8 validator to get consistent and fully conformant
         ## UTF-8 validation behavior
         u = Utf8Validator()
         val = u.validate(bytearray(reasonRaw))
         if not val[0]:
            if self.invalidPayload("invalid close reason (non-UTF-8 payload)"):
               return True

      if self.state == WebSocketProtocol.STATE_CLOSING:
         ## We already initiated the closing handshake, so this
         ## is the peer's reply to our close frame.

         self.wasClean = True

         if self.isServer:
            ## When we are a server, we immediately drop the TCP.
            self.dropConnection()
         else:
            ## When we are a client, the server should drop the TCP
            ## If that doesn't happen, we do. And that will set wasClean = False.
            reactor.callLater(self.serverConnectionDropTimeout, self.onServerConnectionDropTimeout)

      elif self.state == WebSocketProtocol.STATE_OPEN:
         ## The peer initiates a closing handshake, so we reply
         ## by sending close frame.

         self.wasClean = True

         ## Either reply with same code/reason, or code == NORMAL/reason=None
         if self.echoCloseCodeReason:
            self.sendCloseFrame(code = code, reasonUtf8 = reason.encode("UTF-8"), isReply = True)
         else:
            self.sendCloseFrame(code = WebSocketProtocol.CLOSE_STATUS_CODE_NORMAL, isReply = True)

         if self.isServer:
            ## When we are a server, we immediately drop the TCP.
            self.dropConnection()
         else:
            ## When we are a client, we expect the server to drop the TCP,
            ## and when the server fails to do so, a timeout in sendCloseFrame()
            ## will set wasClean = False back again.
            pass

      else:
         ## STATE_CONNECTING, STATE_CLOSED
         raise Exception("logic error")


   def onServerConnectionDropTimeout(self):
      """
      We (a client) expected the peer (a server) to drop the connection,
      but it didn't (in time self.serverConnectionDropTimeout).
      So we drop the connection, but set self.wasClean = False.
      """
      if self.state != WebSocketProtocol.STATE_CLOSED:
         if self.debugCodePaths:
            log.msg("onServerConnectionDropTimeout")
         self.wasClean = False
         self.wasNotCleanReason = "server did not drop TCP connection (in time)"
         self.wasServerConnectionDropTimeout = True
         self.dropConnection()
      else:
         if self.debugCodePaths:
            log.msg("skipping onServerConnectionDropTimeout since connection is already closed")


   def onCloseHandshakeTimeout(self):
      """
      We expected the peer to respond to us initiating a close handshake. It didn't
      respond (in time self.closeHandshakeTimeout) with a close response frame though.
      So we drop the connection, but set self.wasClean = False.
      """
      if self.state != WebSocketProtocol.STATE_CLOSED:
         if self.debugCodePaths:
            log.msg("onCloseHandshakeTimeout fired")
         self.wasClean = False
         self.wasNotCleanReason = "peer did not respond (in time) in closing handshake"
         self.wasCloseHandshakeTimeout = True
         self.dropConnection()
      else:
         if self.debugCodePaths:
            log.msg("skipping onCloseHandshakeTimeout since connection is already closed")


   def dropConnection(self):
      """
      Drop the underlying TCP connection.
      """
      if self.state != WebSocketProtocol.STATE_CLOSED:
         if self.debugCodePaths:
            log.msg("dropping connection")
         self.droppedByMe = True
         self.state = WebSocketProtocol.STATE_CLOSED
         self.transport.loseConnection()
      else:
         if self.debugCodePaths:
            log.msg("skipping dropConnection since connection is already closed")


   def failConnection(self, code = CLOSE_STATUS_CODE_GOING_AWAY, reason = "Going Away"):
      """
      Fails the WebSockets connection.
      """
      if self.state != WebSocketProtocol.STATE_CLOSED:
         if self.debugCodePaths:
            log.msg("Failing connection : %s - %s" % (code, reason))
         self.failedByMe = True
         if self.failByDrop:
            ## brutally drop the TCP connection
            self.wasClean = False
            self.wasNotCleanReason = "I failed the WebSocket connection by dropping the TCP connection"
            self.dropConnection()
         else:
            ## perform WebSockets closing handshake
            if self.state != WebSocketProtocol.STATE_CLOSING:
               self.sendCloseFrame(code = code, reasonUtf8 = reason.encode("UTF-8"), isReply = False)
            else:
               if self.debugCodePaths:
                  log.msg("skipping failConnection since connection is already closing")
      else:
         if self.debugCodePaths:
            log.msg("skipping failConnection since connection is already closed")


   def protocolViolation(self, reason):
      """
      Fired when a WebSockets protocol violation/error occurs.

      :param reason: Protocol violation that was encountered (human readable).
      :type reason: str
      :returns: bool -- True, when any further processing should be discontinued.
      """
      if self.debugCodePaths:
         log.msg("Protocol violation : %s" % reason)
      self.failConnection(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, reason)
      if self.failByDrop:
         return True
      else:
         ## if we don't immediately drop the TCP, we need to skip the invalid frame
         ## to continue to later receive the closing handshake reply
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
         log.msg("Invalid payload : %s" % reason)
      self.failConnection(WebSocketProtocol.CLOSE_STATUS_CODE_INVALID_PAYLOAD, reason)
      if self.failByDrop:
         return True
      else:
         ## if we don't immediately drop the TCP, we need to skip the invalid frame
         ## to continue to later receive the closing handshake reply
         return False


   def connectionMade(self):
      """
      This is called by Twisted framework when a new TCP connection has been established
      and handed over to a Protocol instance (an instance of this class).
      """

      ## copy default options from factory (so we are not affected by changed on those)
      ##
      self.debug = self.factory.debug
      self.debugCodePaths = self.factory.debugCodePaths

      self.utf8validateIncoming = self.factory.utf8validateIncoming
      self.applyMask = self.factory.applyMask
      self.maxFramePayloadSize = self.factory.maxFramePayloadSize
      self.maxMessagePayloadSize = self.factory.maxMessagePayloadSize
      self.autoFragmentSize = self.factory.autoFragmentSize
      self.failByDrop = self.factory.failByDrop
      self.echoCloseCodeReason = self.factory.echoCloseCodeReason
      self.closeHandshakeTimeout = self.factory.closeHandshakeTimeout
      self.tcpNoDelay = self.factory.tcpNoDelay

      if self.isServer:
         #self.versions = self.factory.versions
         self.webStatus = self.factory.webStatus
         self.requireMaskedClientFrames = self.factory.requireMaskedClientFrames
         self.maskServerFrames = self.factory.maskServerFrames
      else:
         #self.version = self.factory.version
         self.acceptMaskedServerFrames = self.factory.acceptMaskedServerFrames
         self.maskClientFrames = self.factory.maskClientFrames
         self.serverConnectionDropTimeout = self.factory.serverConnectionDropTimeout

      ## Set "Nagle"
      self.transport.setTcpNoDelay(self.tcpNoDelay)

      ## the peer we are connected to
      self.peer = self.transport.getPeer()
      self.peerstr = "%s:%d" % (self.peer.host, self.peer.port)

      ## initial state
      self.state = WebSocketProtocol.STATE_CONNECTING
      self.send_state = WebSocketProtocol.SEND_STATE_GROUND
      self.data = ""

      ## for chopped/synched sends, we need to queue to maintain
      ## ordering when recalling the reactor to actually "force"
      ## the octets to wire (see test/trickling in the repo)
      self.send_queue = deque()
      self.triggered = False

      ## incremental UTF8 validator
      self.utf8validator = Utf8Validator()

      ## track when frame/message payload sizes (incoming) were exceeded
      self.wasMaxFramePayloadSizeExceeded = False
      self.wasMaxMessagePayloadSizeExceeded = False

      ## the following vars are related to connection close handling/tracking

      # True, iff I have initiated closing HS (that is, did send close first)
      self.closedByMe = False

      # True, iff I have failed the WS connection (i.e. due to protocol error)
      # Failing can be either by initiating close HS or brutal drop (this is
      # controlled by failByDrop option)
      self.failedByMe = False

      # True, iff I dropped the TCP connection (called transport.loseConnection())
      self.droppedByMe = False

      # True, iff full WebSockets closing handshake was performed (close frame sent
      # and received) _and_ the server dropped the TCP (which is its responsibility)
      self.wasClean = False

      # When self.wasClean = False, the reason (what happened)
      self.wasNotCleanReason = None

      # When we are a client, and we expected the server to drop the TCP, but that
      # didn't happen in time, this gets True
      self.wasServerConnectionDropTimeout = False

      # When we initiated a closing handshake, but the peer did not respond in
      # time, this gets True
      self.wasCloseHandshakeTimeout = False

      # The close code I sent in close frame (if any)
      self.localCloseCode = None

      # The close reason I sent in close frame (if any)
      self.localCloseReason = None

      # The close code the peer sent me in close frame (if any)
      self.remoteCloseCode = None

      # The close reason the peer sent me in close frame (if any)
      self.remoteCloseReason = None


   def connectionLost(self, reason):
      """
      This is called by Twisted framework when a TCP connection was lost.
      """
      self.state = WebSocketProtocol.STATE_CLOSED
      if not self.wasClean:
         if not self.droppedByMe and self.wasNotCleanReason is None:
            self.wasNotCleanReason = "peer dropped the TCP connection without previous WebSocket closing handshake"
         self.onClose(self.wasClean, WebSocketProtocol.CLOSE_STATUS_CODE_ABNORMAL_CLOSE, "connection was closed uncleanly (%s)" % self.wasNotCleanReason)
      else:
         self.onClose(self.wasClean, self.remoteCloseCode, self.remoteCloseReason)


   def logRxOctets(self, data):
      if self.debug:
         d = str(buffer(data))
         log.msg("RX Octets from %s : %s" % (self.peerstr, binascii.b2a_hex(d)))


   def logTxOctets(self, data, sync):
      if self.debug:
         d = str(buffer(data))
         log.msg("TX Octets to %s : %s" % (self.peerstr, binascii.b2a_hex(d)))


   def logRxFrame(self, fin, rsv, opcode, masked, payload_len, mask, payload):
      if self.debug:
         d = str(buffer(payload))
         if mask:
            mmask = binascii.b2a_hex(mask)
         else:
            mmask = str(mask)
         log.msg("RX Frame from %s : fin = %s, rsv = %s, opcode = %s, masked = %s, payload_len = %s, mask = %s, payload = %s" % (self.peerstr, str(fin), str(rsv), str(opcode), str(masked), str(payload_len), mmask, binascii.b2a_hex(d)))


   def logTxFrame(self, opcode, payload, fin, rsv, mask, payload_len, chopsize, sync):
      if self.debug:
         d = str(buffer(payload))
         if mask:
            mmask = binascii.b2a_hex(mask)
         else:
            mmask = str(mask)
         log.msg("TX Frame to %s : fin = %s, rsv = %s, opcode = %s, mask = %s, payload_len = %s, chopsize = %s, sync = %s, payload = %s" % (self.peerstr, str(fin), str(rsv), str(opcode), mmask, str(payload_len), str(chopsize), str(sync), binascii.b2a_hex(d)))


   def dataReceived(self, data):
      """
      This is called by Twisted framework upon receiving data on TCP connection.
      """
      self.logRxOctets(data)

      self.data += data
      self.consumeData()


   def consumeData(self):

      buffered_len = len(self.data)

      ## WebSocket is open (handshake was completed) or close was sent
      ##
      if self.state in [WebSocketProtocol.STATE_OPEN, WebSocketProtocol.STATE_CLOSING]:

         ## process until no more buffered data left or WS was closed
         ##
         while self.processData() and self.state != WebSocketProtocol.STATE_CLOSED:
            pass

      ## WebSocket needs handshake
      ##
      elif self.state == WebSocketProtocol.STATE_CONNECTING:

         ## the implementation of processHandshake() in derived
         ## class needs to perform client or server handshake
         ## from other party here ..
         ##
         self.processHandshake()

      ## we failed the connection .. don't process any more data!
      ##
      elif self.state == WebSocketProtocol.STATE_CLOSED:

         ## ignore any data received after WS was closed
         ##
         if self.debugCodePaths:
            log.msg("received data in STATE_CLOSED")

      ## should not arrive here (invalid state)
      ##
      else:
         raise Exception("invalid state")


   def processHandshake(self):
      """
      Process WebSockets handshake.
      """
      raise Exception("must implement handshake (client or server) in derived class")


   def registerProducer(self, producer, streaming):
      """
      Register a Twisted producer with this protocol.

      :param producer: A Twisted push or pull producer.
      :type producer: object
      :param streaming: Producer type.
      :type streaming: bool
      """
      self.transport.registerProducer(producer, streaming)


   def _trigger(self):
      """
      Trigger sending stuff from send queue (which is only used for chopped/synched writes).
      """
      if not self.triggered:
         self.triggered = True
         self._send()


   def _send(self):
      """
      Send out stuff from send queue. For details how this works, see test/trickling
      in the repo.
      """
      if len(self.send_queue) > 0:
         e = self.send_queue.popleft()
         if self.state != WebSocketProtocol.STATE_CLOSED:
            self.logTxOctets(e[0], e[1])
            self.transport.write(e[0])
         else:
            if self.debugCodePaths:
               log.msg("skipped delayed write, since connection is closed")
         # we need to reenter the reactor to make the latter
         # reenter the OS network stack, so that octets
         # can get on the wire. Note: this is a "heuristic",
         # since there is no (easy) way to really force out
         # octets from the OS network stack to wire.
         reactor.callLater(WebSocketProtocol.QUEUED_WRITE_DELAY, self._send)
      else:
         self.triggered = False


   def sendData(self, data, sync = False, chopsize = None):
      """
      Wrapper for self.transport.write which allows to give a chopsize.
      When asked to chop up writing to TCP stream, we write only chopsize octets
      and then give up control to select() in underlying reactor so that bytes
      get onto wire immediately. Note that this is different from and unrelated
      to WebSockets data message fragmentation. Note that this is also different
      from the TcpNoDelay option which can be set on the socket.
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
            self.logTxOctets(data, False)
            self.transport.write(data)


   def processData(self):
      """
      After WebSockets handshake has been completed, this procedure will do all
      subsequent processing of incoming bytes.
      """
      buffered_len = len(self.data)

      ## outside a frame, that is we are awaiting data which starts a new frame
      ##
      if self.current_frame is None:

         ## need minimum of 2 octets to for new frame
         ##
         if buffered_len >= 2:

            ## FIN, RSV, OPCODE
            ##
            b = ord(self.data[0])
            frame_fin = (b & 0x80) != 0
            frame_rsv = (b & 0x70) >> 4
            frame_opcode = b & 0x0f

            ## MASK, PAYLOAD LEN 1
            ##
            b = ord(self.data[1])
            frame_masked = (b & 0x80) != 0
            frame_payload_len1 = b & 0x7f

            ## MUST be 0 when no extension defining
            ## the semantics of RSV has been negotiated
            ##
            if frame_rsv != 0:
               if self.protocolViolation("RSV != 0 and no extension negotiated"):
                  return False

            ## all client-to-server frames MUST be masked
            ##
            if self.isServer and self.requireMaskedClientFrames and not frame_masked:
               if self.protocolViolation("unmasked client-to-server frame"):
                  return False

            ## all server-to-client frames MUST NOT be masked
            ##
            if not self.isServer and not self.acceptMaskedServerFrames and frame_masked:
               if self.protocolViolation("masked server-to-client frame"):
                  return False

            ## check frame
            ##
            if frame_opcode > 7: # control frame (have MSB in opcode set)

               ## control frames MUST NOT be fragmented
               ##
               if not frame_fin:
                  if self.protocolViolation("fragmented control frame"):
                     return False

               ## control frames MUST have payload 125 octets or less
               ##
               if frame_payload_len1 > 125:
                  if self.protocolViolation("control frame with payload length > 125 octets"):
                     return False

               ## check for reserved control frame opcodes
               ##
               if frame_opcode not in [8, 9, 10]:
                  if self.protocolViolation("control frame using reserved opcode %d" % frame_opcode):
                     return False

               ## close frame : if there is a body, the first two bytes of the body MUST be a 2-byte
               ## unsigned integer (in network byte order) representing a status code
               ##
               if frame_opcode == 8 and frame_payload_len1 == 1:
                  if self.protocolViolation("received close control frame with payload len 1"):
                     return False

            else: # data frame

               ## check for reserved data frame opcodes
               ##
               if frame_opcode not in [0, 1, 2]:
                  if self.protocolViolation("data frame using reserved opcode %d" % frame_opcode):
                     return False

               ## check opcode vs message fragmentation state 1/2
               ##
               if not self.inside_message and frame_opcode == 0:
                  if self.protocolViolation("received continuation data frame outside fragmented message"):
                     return False

               ## check opcode vs message fragmentation state 2/2
               ##
               if self.inside_message and frame_opcode != 0:
                  if self.protocolViolation("received non-continuation data frame while inside fragmented message"):
                     return False

            ## compute complete header length
            ##
            if frame_masked:
               mask_len = 4
            else:
               mask_len = 0

            if frame_payload_len1 <  126:
               frame_header_len = 2 + mask_len
            elif frame_payload_len1 == 126:
               frame_header_len = 2 + 2 + mask_len
            elif frame_payload_len1 == 127:
               frame_header_len = 2 + 8 + mask_len
            else:
               raise Exception("logic error")

            ## only proceed when we have enough data buffered for complete
            ## frame header (which includes extended payload len + mask)
            ##
            if buffered_len >= frame_header_len:

               i = 2

               ## extract extended payload length
               ##
               if frame_payload_len1 == 126:
                  frame_payload_len = struct.unpack("!H", self.data[i:i+2])[0]
                  if frame_payload_len < 126:
                     if self.protocolViolation("invalid data frame length (not using minimal length encoding)"):
                        return False
                  i += 2
               elif frame_payload_len1 == 127:
                  frame_payload_len = struct.unpack("!Q", self.data[i:i+8])[0]
                  if frame_payload_len > 0x7FFFFFFFFFFFFFFF: # 2**63
                     if self.protocolViolation("invalid data frame length (>2^63)"):
                        return False
                  if frame_payload_len < 65536:
                     if self.protocolViolation("invalid data frame length (not using minimal length encoding)"):
                        return False
                  i += 8
               else:
                  frame_payload_len = frame_payload_len1

               ## when payload is masked, extract frame mask
               ##
               frame_mask = None
               frame_mask_array = []
               if frame_masked:
                  frame_mask = self.data[i:i+4]
                  for j in range(0, 4):
                     frame_mask_array.append(ord(frame_mask[j]))
                  i += 4

               ## remember rest (payload of current frame after header and everything thereafter)
               ##
               self.data = self.data[i:]

               ## ok, got complete frame header
               ##
               self.current_frame = FrameHeader(frame_opcode, frame_fin, frame_rsv, frame_payload_len, frame_mask, frame_mask_array)

               ## process begin on new frame
               ##
               self.onFrameBegin()

               ## reprocess when frame has no payload or and buffered data left
               ##
               return frame_payload_len == 0 or len(self.data) > 0

            else:
               return False # need more data
         else:
            return False # need more data

      ## inside a started frame
      ##
      else:

         ## cut out rest of frame payload
         ##
         rest = self.current_frame.length - self.current_frame.ptr
         if buffered_len >= rest:
            payload = bytearray(self.data[:rest])
            length = rest
            self.data = self.data[rest:]
         else:
            payload = bytearray(self.data)
            length = buffered_len
            self.data = ""

         if length > 0:
            ## unmask payload
            ##
            if self.current_frame.mask and self.applyMask:
               for k in xrange(0, length):
                  payload[k] ^= self.current_frame.mask_array[(k + self.current_frame.ptr) % 4]

            ## process frame data
            ##
            fr = self.onFrameData(payload)
            if fr == False:
               return False

         ## advance payload pointer and fire frame end handler when frame payload is complete
         ##
         self.current_frame.ptr += length
         if self.current_frame.ptr == self.current_frame.length:
            fr = self.onFrameEnd()
            if fr == False:
               return False

         ## reprocess when no error occurred and buffered data left
         ##
         return len(self.data) > 0


   def onFrameBegin(self):
      if self.current_frame.opcode > 7:
         self.control_frame_data = bytearray()
      else:
         ## new message started
         ##
         if not self.inside_message:

            self.inside_message = True

            if self.current_frame.opcode == WebSocketProtocol.MESSAGE_TYPE_TEXT and self.utf8validateIncoming:
               self.utf8validator.reset()
               self.utf8validateIncomingCurrentMessage = True
               self.utf8validateLast = (True, True, 0, 0)
            else:
               self.utf8validateIncomingCurrentMessage = False

            self.onMessageBegin(self.current_frame.opcode)

         self.onMessageFrameBegin(self.current_frame.length, self.current_frame.rsv)


   def onFrameData(self, payload):
      if self.current_frame.opcode > 7:
         self.control_frame_data.extend(payload)
      else:
         ## incrementally validate UTF-8 payload
         ##
         if self.utf8validateIncomingCurrentMessage:
            self.utf8validateLast = self.utf8validator.validate(payload)
            if not self.utf8validateLast[0]:
               if self.invalidPayload("encountered invalid UTF-8 while processing text message at payload octet index %d" % self.utf8validateLast[3]):
                  return False

         self.onMessageFrameData(payload)


   def onFrameEnd(self):
      if self.current_frame.opcode > 7:
         self.processControlFrame()
      else:
         self.onMessageFrameEnd()
         if self.current_frame.fin:
            if self.utf8validateIncomingCurrentMessage:
               if not self.utf8validateLast[1]:
                  if self.invalidPayload("UTF-8 text message payload ended within Unicode code point at payload octet index %d" % self.utf8validateLast[3]):
                     return False
            self.onMessageEnd()
            self.inside_message = False
      self.current_frame = None


   def processControlFrame(self):
      payload = str(self.control_frame_data)
      self.control_frame_data = None

      self.logRxFrame(self.current_frame.fin, self.current_frame.rsv, self.current_frame.opcode, self.current_frame.mask is not None, self.current_frame.length, self.current_frame.mask, payload)

      ## CLOSE frame
      ##
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

      ## PING frame
      ##
      elif self.current_frame.opcode == 9:
         self.onPing(payload)

      ## PONG frame
      ##
      elif self.current_frame.opcode == 10:
         self.onPong(payload)

      else:
         ## we might arrive here, when protocolViolation
         ## wants us to continue anyway
         pass

      return True


   def sendFrame(self, opcode, payload = "", fin = True, rsv = 0, mask = None, payload_len = None, chopsize = None, sync = False):
      """
      Send out frame. Normally only used internally via sendMessage(), sendPing(), sendPong() and sendClose().

      This method deliberately allows to send invalid frames (that is frames invalid
      per-se, or frames invalid because of protocol state). Other than in fuzzing servers,
      calling methods will ensure that no invalid frames are sent.

      In addition, this method supports explicit specification of payload length.
      When payload_len is given, it will always write that many octets to the stream.
      It'll wrap within payload, resending parts of that when more octets were requested
      The use case is again for fuzzing server which want to sent increasing amounts
      of payload data to peers without having to construct potentially large messges
      themselfes.
      """
      if payload_len is not None:
         if len(payload) < 1:
            raise Exception("cannot construct repeated payload with length %d from payload of length %d" % (payload_len, len(payload)))
         l = payload_len
         pl = ''.join([payload for k in range(payload_len / len(payload))]) + payload[:payload_len % len(payload)]
      else:
         l = len(payload)
         pl = payload

      ## first byte
      ##
      b0 = 0
      if fin:
         b0 |= (1 << 7)
      b0 |= (rsv % 8) << 4
      b0 |= opcode % 128

      ## second byte, payload len bytes and mask
      ##
      b1 = 0
      el = ""
      if mask or (not self.isServer and self.maskClientFrames) or (self.isServer and self.maskServerFrames):
         b1 |= 1 << 7
         if mask:
            mv = struct.pack("!I", mask)
         else:
            mv = struct.pack("!I", random.getrandbits(32))

         frame_mask = []
         for j in range(0, 4):
            frame_mask.append(ord(mv[j]))

         ## mask frame payload
         ##
         if self.applyMask:
            pl_ba = bytearray(pl)
            for k in xrange(0, l):
               pl_ba[k] ^= frame_mask[k % 4]
            plm = str(pl_ba)
         else:
            plm = pl

      else:
         mv = ""
         plm = pl

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

      raw = ''.join([chr(b0), chr(b1), el, mv, plm])

      ## log frame TX
      ##
      if mv != "":
         mmv = binascii.b2a_hex(mv)
      else:
         mmv = None
      self.logTxFrame(opcode, payload, fin, rsv, mmv, payload_len, chopsize, sync)

      ## send frame octets
      ##
      self.sendData(raw, sync, chopsize)


   def sendPing(self, payload = None):
      """
      Send out Ping to peer. A peer is expected to Pong back the payload a soon
      as "practical". When more than 1 Ping is outstanding at a peer, the peer may
      elect to respond only to the last Ping.

      :param payload: An optional, arbitrary payload of length < 126 octets.
      :type payload: str
      """
      if self.state != WebSocketProtocol.STATE_OPEN:
         return
      if payload:
         l = len(payload)
         if l > 125:
            raise Exception("invalid payload for PING (payload length must be <= 125, was %d)" % l)
         self.sendFrame(opcode = 9, payload = payload)
      else:
         self.sendFrame(opcode = 9)


   def sendPong(self, payload = None):
      """
      Send out Pong to peer. A Pong frame MAY be sent unsolicited.
      This serves as a unidirectional heartbeat. A response to an unsolicited pong is "not expected".

      :param payload: An optional, arbitrary payload of length < 126 octets.
      :type payload: str
      """
      if self.state != WebSocketProtocol.STATE_OPEN:
         return
      if payload:
         l = len(payload)
         if l > 125:
            raise Exception("invalid payload for PONG (payload length must be <= 125, was %d)" % l)
         self.sendFrame(opcode = 10, payload = payload)
      else:
         self.sendFrame(opcode = 10)


   def sendCloseFrame(self, code = None, reasonUtf8 = None, isReply = False):
      """
      Send a close frame and update protocol state. Note, that this is
      an internal method which deliberately allows not send close
      frame with invalid payload.
      """

      if self.state == WebSocketProtocol.STATE_CLOSING:
         if self.debugCodePaths:
            log.msg("ignoring sendCloseFrame since connection is closing")

      elif self.state == WebSocketProtocol.STATE_CLOSED:
         if self.debugCodePaths:
            log.msg("ignoring sendCloseFrame since connection already closed")

      elif self.state == WebSocketProtocol.STATE_CONNECTING:
         raise Exception("cannot close a connection not yet connected")

      elif self.state == WebSocketProtocol.STATE_OPEN:

         ## construct close frame payload and send frame
         payload = ""
         if code is not None:
            payload += struct.pack("!H", code)
         if reasonUtf8 is not None:
            payload += reasonUtf8
         self.sendFrame(opcode = 8, payload = payload)

         ## update state
         self.state = WebSocketProtocol.STATE_CLOSING
         self.closedByMe = not isReply

         ## remember payload of close frame we sent
         self.localCloseCode = code
         self.localCloseReason = reasonUtf8

         ## drop connection when timeout on receiving close handshake reply
         if self.closedByMe:
            reactor.callLater(self.closeHandshakeTimeout, self.onCloseHandshakeTimeout)

      else:
         raise Exception("logic error")


   def sendClose(self, code = None, reason = None):
      """
      Starts a closing handshake.

      :param code: An optional close status code (:class:`WebSocketProtocol`.CLOSE_STATUS_CODE_NORMAL or 3000-4999).
      :type code: int
      :param reason: An optional close reason (a string that when present, a status code MUST also be present).
      :type reason: str
      """
      if code is not None:
         if type(code) != int:
            raise Exception("invalid type %s for close code" % type(code))
         if code != 1000 and not (code >= 3000 and code <= 4999):
            raise Exception("invalid close code %d" % code)
      if reason is not None:
         if code is None:
            raise Exception("close reason without close code")
         if type(reason) not in [str, unicode]:
            raise Exception("invalid type %s for close reason" % type(reason))
         reasonUtf8 = reason.encode("UTF-8")
         if len(reasonUtf8) + 2 > 125:
            raise Exception("close reason too long (%d)" % len(reasonUtf8))
      else:
         reasonUtf8 = None
      self.sendCloseFrame(code = code, reasonUtf8 = reasonUtf8, isReply = False)


   def beginMessage(self, opcode = MESSAGE_TYPE_TEXT):
      """
      Begin sending new message.

      :param opcode: Message type, normally either WebSocketProtocol.MESSAGE_TYPE_TEXT (default) or WebSocketProtocol.MESSAGE_TYPE_BINARY.
      """
      if self.state != WebSocketProtocol.STATE_OPEN:
         return
      ## check if sending state is valid for this method
      ##
      if self.send_state != WebSocketProtocol.SEND_STATE_GROUND:
         raise Exception("WebSocketProtocol.beginMessage invalid in current sending state")

      if opcode not in [1, 2]:
         raise Exception("use of reserved opcode %d" % opcode)

      ## move into "begin message" state and remember opcode for later (when sending first frame)
      ##
      self.send_state = WebSocketProtocol.SEND_STATE_MESSAGE_BEGIN
      self.send_message_opcode = opcode


   def beginMessageFrame(self, length, reserved = 0, mask = None):
      """
      Begin sending new message frame.

      :param length: Length of frame which is started. Must be >= 0 and <= 2^63.
      :type length: int
      :param reserved: Reserved bits for frame (an integer from 0 to 7). Note that reserved != 0 is only legal when an extension has been negoiated which defines semantics.
      :type reserved: int
      :param mask: Optional frame mask. When given, this is used. When None and the peer is a client, a mask will be internally generated. For servers None is default.
      :type mask: str
      """
      if self.state != WebSocketProtocol.STATE_OPEN:
         return
      ## check if sending state is valid for this method
      ##
      if self.send_state not in [WebSocketProtocol.SEND_STATE_MESSAGE_BEGIN, WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE]:
         raise Exception("WebSocketProtocol.beginMessageFrame invalid in current sending state")

      if (not type(length) in [int, long]) or length < 0 or length > 0x7FFFFFFFFFFFFFFF: # 2**63
         raise Exception("invalid value for message frame length")

      if type(reserved) is not int or reserved < 0 or reserved > 7:
         raise Exception("invalid value for reserved bits")

      self.send_message_frame_length = length
      self.send_message_frame_octets_sent = 0

      if mask:
         ## explicit mask given
         ##
         if type(mask) is not str:
            raise Exception("mask must be a (byte) string")
         if len(mask) != 4:
            raise Exception("mask must have length 4")
         self.send_message_frame_mask = mask
      elif (not self.isServer and self.maskClientFrames) or (self.isServer and self.maskServerFrames):
         ## automatic mask:
         ##  - client-to-server masking (if not deactivated)
         ##  - server-to-client masking (if activated)
         ##
         self.send_message_frame_mask = random.getrandbits(32)
      else:
         ## no mask
         ##
         self.send_message_frame_mask = None

      ## first byte
      ##
      b0 = (reserved % 8) << 4 # FIN = false .. since with streaming, we don't know when message ends

      if self.send_state == WebSocketProtocol.SEND_STATE_MESSAGE_BEGIN:
         self.send_state = WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE
         b0 |= self.send_message_opcode % 128
      else:
         pass # message continuation frame

      ## second byte, payload len bytes and mask
      ##
      b1 = 0
      el = ""
      if self.send_message_frame_mask:
         b1 |= 1 << 7
         mv = struct.pack("!I", self.send_message_frame_mask)
         self.send_message_frame_mask_array = []
         for j in range(0, 4):
            self.send_message_frame_mask_array.append(ord(mv[j]))
      else:
         mv = ""

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

      ## write message frame header
      ##
      header = ''.join([chr(b0), chr(b1), el, mv])
      self.sendData(header)

      ## now we are inside message frame ..
      ##
      self.send_state = WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE_FRAME


   def sendMessageFrameData(self, payload, sync = False):
      """
      Send out data when within message frame (message was begun, frame was begun).
      Note that the frame is automatically ended when enough data has been sent
      that is, there is no endMessageFrame, since you have begun the frame specifying
      the frame length, which implicitly defined the frame end. This is different from
      messages, which you begin and end, since a message can contain an unlimited number
      of frames.

      :param payload: Data to send.
      :returns: int -- When frame still incomplete, returns outstanding octets, when frame complete, returns <= 0, when < 0, the amount of unconsumed data in payload argument.
      """
      if self.state != WebSocketProtocol.STATE_OPEN:
         return
      ## check if sending state is valid for this method
      ##
      if self.send_state != WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE_FRAME:
         raise Exception("WebSocketProtocol.sendMessageFrameData invalid in current sending state")

      rl = len(payload)
      if self.send_message_frame_octets_sent + rl > self.send_message_frame_length:
         l = self.send_message_frame_length - self.send_message_frame_octets_sent
         rest = -(rl - l)
         pl_ba = bytearray(payload[:l])
      else:
         l = rl
         rest = self.send_message_frame_length - self.send_message_frame_octets_sent - l
         pl_ba = bytearray(payload)

      ## mask frame payload
      ##
      if self.send_message_frame_mask and self.applyMask:
         w = self.send_message_frame_octets_sent % 4
         for k in xrange(0, l):
            pl_ba[k] ^= self.send_message_frame_mask_array[(w + k) % 4]
            ## WARNING. This is silly: if you do it instead like the uncommended line, the memory footprint
            ## will run away ...
#            pl_ba[k] ^= self.send_message_frame_mask_array[(self.send_message_frame_octets_sent + k) % 4]

      ## send frame payload
      ##
      self.sendData(str(pl_ba), sync = sync)

      pl_ba = None

      ## advance frame payload pointer and check if frame payload was completely sent
      ##
      self.send_message_frame_octets_sent += l

      ## if we are done with frame, move back into "inside message" state
      ##
      if self.send_message_frame_octets_sent >= self.send_message_frame_length:
         self.send_state = WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE

      ## when =0 : frame was completed exactly
      ## when >0 : frame is still uncomplete and that much amount is still left to complete the frame
      ## when <0 : frame was completed and there was this much unconsumed data in payload argument
      ##
      return rest


   def endMessage(self):
      """
      End a previously begun message. No more frames may be sent (for that message). You have to
      begin a new message before sending again.
      """
      if self.state != WebSocketProtocol.STATE_OPEN:
         return
      ## check if sending state is valid for this method
      ##
      if self.send_state != WebSocketProtocol.SEND_STATE_INSIDE_MESSAGE:
         raise Exception("WebSocketProtocol.endMessage invalid in current sending state [%d]" % self.send_state)
      self.sendFrame(opcode = 0, fin = True)
      self.send_state = WebSocketProtocol.SEND_STATE_GROUND


   def sendMessageFrame(self, payload, reserved = 0, mask = None, sync = False):
      """
      When a message has begun, send a complete message frame in one go.
      """
      if self.state != WebSocketProtocol.STATE_OPEN:
         return
      self.beginMessageFrame(len(payload), reserved, mask)
      self.sendMessageFrameData(payload, sync)


   def sendMessage(self, payload, binary = False, payload_frag_size = None, sync = False):
      """
      Send out a message in one go.

      You can send text or binary message, and optionally
      specifiy a payload fragment size. When the latter is given, the payload will
      be split up into frames with payload <= the payload_frag_size given.
      """
      if self.state != WebSocketProtocol.STATE_OPEN:
         return
      ## (initial) frame opcode
      ##
      if binary:
         opcode = 2
      else:
         opcode = 1

      ## explicit payload_frag_size arguments overrides autoFragmentSize setting
      ##
      if payload_frag_size is not None:
         pfs = payload_frag_size
      else:
         if self.autoFragmentSize > 0:
            pfs = self.autoFragmentSize
         else:
            pfs = None

      ## send unfragmented
      ##
      if pfs is None or len(payload) <= pfs:
         self.sendFrame(opcode = opcode, payload = payload, sync = sync)

      ## send data message in fragments
      ##
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
               self.sendFrame(opcode = opcode, payload = payload[i:j], fin = done, sync = sync)
               first = False
            else:
               self.sendFrame(opcode = 0, payload = payload[i:j], fin = done, sync = sync)
            i += pfs


class WebSocketServerProtocol(WebSocketProtocol):
   """
   A Twisted protocol for WebSockets servers.
   """

   def onConnect(self, connectionRequest):
      """
      Callback fired during WebSocket opening handshake when new WebSocket client
      connection is about to be established.

      Throw HttpException when you don't want to accept the WebSocket
      connection request. For example, throw a
      HttpException(httpstatus.HTTP_STATUS_CODE_UNAUTHORIZED[0], "You are not authorized for this!").

      When you want to accept the connection, return the accepted protocol
      from list of WebSockets (sub)protocols provided by client or None to
      speak no specific one or when the client list was empty.

      :param connectionRequest: WebSocket connection request information.
      :type connectionRequest: instance of :class:`autobahn.websocket.ConnectionRequest`
      """
      return None


   def connectionMade(self):
      """
      Called by Twisted when new TCP connection from client was accepted. Default
      implementation will prepare for initial WebSocket opening handshake.
      When overriding in derived class, make sure to call this base class
      implementation _before_ your code.
      """
      self.isServer = True
      WebSocketProtocol.connectionMade(self)
      self.factory.countConnections += 1
      if self.debug:
         log.msg("connection accepted from peer %s" % self.peerstr)


   def connectionLost(self, reason):
      """
      Called by Twisted when established TCP connection from client was lost. Default
      implementation will tear down all state properly.
      When overriding in derived class, make sure to call this base class
      implementation _after_ your code.
      """
      WebSocketProtocol.connectionLost(self, reason)
      self.factory.countConnections -= 1
      if self.debug:
         log.msg("connection from %s lost" % self.peerstr)


   def processHandshake(self):
      """
      Process WebSockets opening handshake request from client.
      """
      ## only proceed when we have fully received the HTTP request line and all headers
      ##
      end_of_header = self.data.find("\x0d\x0a\x0d\x0a")
      if end_of_header >= 0:

         self.http_request_data = self.data[:end_of_header + 4]
         if self.debug:
            log.msg("received HTTP request:\n\n%s\n\n" % self.http_request_data)

         ## extract HTTP status line and headers
         ##
         (self.http_status_line, self.http_headers, http_headers_cnt) = parseHttpHeader(self.http_request_data)

         ## remember rest (after HTTP headers, if any)
         ##
         self.data = self.data[end_of_header + 4:]

         ## validate WebSocket opening handshake client request
         ##
         if self.debug:
            log.msg("received HTTP status line in opening handshake : %s" % str(self.http_status_line))
            log.msg("received HTTP headers in opening handshake : %s" % str(self.http_headers))

         ## HTTP Request line : METHOD, VERSION
         ##
         rl = self.http_status_line.split()
         if len(rl) != 3:
            return self.failHandshake("Bad HTTP request status line '%s'" % self.http_status_line)
         if rl[0].strip() != "GET":
            return self.failHandshake("HTTP method '%s' not allowed" % rl[0], HTTP_STATUS_CODE_METHOD_NOT_ALLOWED[0])
         vs = rl[2].strip().split("/")
         if len(vs) != 2 or vs[0] != "HTTP" or vs[1] not in ["1.1"]:
            return self.failHandshake("Unsupported HTTP version '%s'" % rl[2], HTTP_STATUS_CODE_UNSUPPORTED_HTTP_VERSION[0])

         ## HTTP Request line : REQUEST-URI
         ##
         self.http_request_uri = rl[1].strip()
         try:
            (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(self.http_request_uri)

            ## FIXME: check that if absolute resource URI is given,
            ## the scheme/netloc matches the server
            if scheme != "" or netloc != "":
               pass

            ## Fragment identifiers are meaningless in the context of WebSocket
            ## URIs, and MUST NOT be used on these URIs.
            if fragment != "":
               return self.failHandshake("HTTP requested resource contains a fragment identifier '%s'" % fragment)

            ## resource path and query parameters .. this will get forwarded
            ## to onConnect()
            self.http_request_path = path
            self.http_request_params = urlparse.parse_qs(query)
         except:
            return self.failHandshake("Bad HTTP request resource - could not parse '%s'" % rl[1].strip())

         ## Host
         ##
         if not self.http_headers.has_key("host"):
            return self.failHandshake("HTTP Host header missing in opening handshake request")
         if http_headers_cnt["host"] > 1:
            return self.failHandshake("HTTP Host header appears more than once in opening handshake request")
         self.http_request_host = self.http_headers["host"].strip()
         if self.http_request_host.find(":") >= 0:
            (h, p) = self.http_request_host.split(":")
            try:
               port = int(p.strip())
               if port != self.factory.port:
                  return self.failHandshake("port %d in HTTP Host header '%s' does not match server listening port %d" % (port, str(self.http_request_host), self.factory.port))
            except:
               return self.failHandshake("invalid port '%s' in HTTP Host header '%s'" % (p.strip(), str(self.http_request_host)))
         else:
            if not ((self.factory.isSecure and self.factory.port == 443) or (not self.factory.isSecure and self.factory.port == 80)):
               return self.failHandshake("missing port in HTTP Host header '%s' and server runs on non-standard port %d (wss = %s)" % (str(self.http_request_host), self.factory.port, self.factory.isSecure))

         ## Upgrade
         ##
         if not self.http_headers.has_key("upgrade"):
            ## When no WS upgrade, render HTML server status page
            ##
            if self.webStatus:
               self.sendServerStatus()
               self.dropConnection()
               return
            else:
               return self.failHandshake("HTTP Upgrade header missing", HTTP_STATUS_CODE_UPGRADE_REQUIRED[0])
         upgradeWebSocket = False
         for u in self.http_headers["upgrade"].split(","):
            if u.strip().lower() == "websocket":
               upgradeWebSocket = True
               break
         if not upgradeWebSocket:
            return self.failHandshake("HTTP Upgrade headers do not include 'websocket' value (case-insensitive) : %s" % self.http_headers["upgrade"])

         ## Connection
         ##
         if not self.http_headers.has_key("connection"):
            return self.failHandshake("HTTP Connection header missing")
         connectionUpgrade = False
         for c in self.http_headers["connection"].split(","):
            if c.strip().lower() == "upgrade":
               connectionUpgrade = True
               break
         if not connectionUpgrade:
            return self.failHandshake("HTTP Connection headers do not include 'upgrade' value (case-insensitive) : %s" % self.http_headers["connection"])

         ## Sec-WebSocket-Version
         ##
         if not self.http_headers.has_key("sec-websocket-version"):
            return self.failHandshake("HTTP Sec-WebSocket-Version header missing in opening handshake request")
         try:

            if http_headers_cnt["sec-websocket-version"] > 1:
               return self.failHandshake("HTTP Sec-WebSocket-Version header appears more than once in opening handshake request")

            version = int(self.http_headers["sec-websocket-version"])

            if version not in self.factory.versions:

               ## respond with list of supported versions (descending order)
               ##
               sv = sorted(self.factory.versions)
               sv.reverse()
               svs = ','.join([str(x) for x in sv])
               return self.failHandshake("Sec-WebSocket-Version %d not supported (supported versions: %s)" % (version, svs),
                                         HTTP_STATUS_CODE_BAD_REQUEST[0],
                                         [("Sec-WebSocket-Version", svs)])
            else:
               self.websocket_version = version
         except:
            return self.failHandshake("could not parse HTTP Sec-WebSocket-Version header '%s' in opening handshake request" % self.http_headers["sec-websocket-version"])

         ## Sec-WebSocket-Protocol
         ##
         if self.http_headers.has_key("sec-websocket-protocol"):
            protocols = [x.strip() for x in self.http_headers["sec-websocket-protocol"].split(",")]
            # check for duplicates in protocol header
            pp = {}
            for p in protocols:
               if pp.has_key(p):
                  return self.failHandshake("duplicate protocol '%s' specified in HTTP Sec-WebSocket-Protocol header" % p)
               else:
                  pp[p] = 1
            # ok, no duplicates, save list in order the client sent it
            self.websocket_protocols = protocols
         else:
            self.websocket_protocols = []

         ## Sec-WebSocket-Origin
         ## http://tools.ietf.org/html/draft-ietf-websec-origin-02
         ##
         self.websocket_origin = None
         if self.websocket_version < 13:
            websocket_origin_header_key = "sec-websocket-origin"
         else:
            websocket_origin_header_key = "origin"
         if self.http_headers.has_key(websocket_origin_header_key):
            if http_headers_cnt[websocket_origin_header_key] > 1:
               return self.failHandshake("HTTP Origin header appears more than once in opening handshake request")
            self.websocket_origin = self.http_headers[websocket_origin_header_key].strip()

         ## Sec-WebSocket-Extensions
         ##

         ## extensions requested by client
         self.websocket_extensions = []
         ## extensions selected by server
         self.websocket_extensions_in_use = []

         if self.http_headers.has_key("sec-websocket-extensions"):
            extensions = [x.strip() for x in self.http_headers["sec-websocket-extensions"].split(',')]
            if len(extensions) > 0:
               self.websocket_extensions = extensions
               if self.debug:
                  log.msg("client requested extensions we don't support (%s)" % str(extensions))

         ## Sec-WebSocket-Key
         ## http://tools.ietf.org/html/rfc4648#section-4
         ##
         if not self.http_headers.has_key("sec-websocket-key"):
            return self.failHandshake("HTTP Sec-WebSocket-Key header missing")
         if http_headers_cnt["sec-websocket-key"] > 1:
            return self.failHandshake("HTTP Sec-WebSocket-Key header appears more than once in opening handshake request")
         key = self.http_headers["sec-websocket-key"].strip()
         if len(key) != 24: # 16 bytes => (ceil(128/24)*24)/6 == 24
            return self.failHandshake("bad Sec-WebSocket-Key (length must be 24 ASCII chars) '%s'" % key)
         if key[-2:] != "==": # 24 - ceil(128/6) == 2
            return self.failHandshake("bad Sec-WebSocket-Key (invalid base64 encoding) '%s'" % key)
         for c in key[:-2]:
            if c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/":
               return self.failHandshake("bad character '%s' in Sec-WebSocket-Key (invalid base64 encoding) '%s'" (c, key))

         ## WebSocket handshake validated => produce opening handshake response

         ## Now fire onConnect() on derived class, to give that class a chance to accept or deny
         ## the connection. onConnect() may throw, in which case the connection is denied, or it
         ## may return a protocol from the protocols provided by client or None.
         ##
         try:
            connectionRequest = ConnectionRequest(self.peer,
                                                  self.peerstr,
                                                  self.http_headers,
                                                  self.http_request_host,
                                                  self.http_request_path,
                                                  self.http_request_params,
                                                  self.websocket_version,
                                                  self.websocket_origin,
                                                  self.websocket_protocols,
                                                  self.websocket_extensions)

            ## onConnect() will return the selected subprotocol or None
            ## or raise an HttpException
            ##
            protocol = self.onConnect(connectionRequest)

            if protocol is not None and not (protocol in self.websocket_protocols):
               raise Exception("protocol accepted must be from the list client sent or None")

            self.websocket_protocol_in_use = protocol

         except HttpException, e:
            return self.failHandshake(e.reason, e.code)
            #return self.sendHttpRequestFailure(e.code, e.reason)

         except Exception, e:
            log.msg("Exception raised in onConnect() - %s" % str(e))
            return self.failHandshake("Internal Server Error", HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR[0])


         ## compute Sec-WebSocket-Accept
         ##
         sha1 = hashlib.sha1()
         sha1.update(key + WebSocketProtocol.WS_MAGIC)
         sec_websocket_accept = base64.b64encode(sha1.digest())

         ## send response to complete WebSocket handshake
         ##
         response  = "HTTP/1.1 %d Switching Protocols\x0d\x0a" % HTTP_STATUS_CODE_SWITCHING_PROTOCOLS[0]

         if self.factory.server is not None and self.factory.server != "":
            response += "Server: %s\x0d\x0a" % self.factory.server.encode("utf-8")

         response += "Upgrade: websocket\x0d\x0a"
         response += "Connection: Upgrade\x0d\x0a"
         response += "Sec-WebSocket-Accept: %s\x0d\x0a" % sec_websocket_accept

         if len(self.websocket_extensions_in_use) > 0:
            response += "Sec-WebSocket-Extensions: %s\x0d\x0a" % ','.join(self.websocket_extensions_in_use)

         if self.websocket_protocol_in_use is not None:
            response += "Sec-WebSocket-Protocol: %s\x0d\x0a" % self.websocket_protocol_in_use

         response += "\x0d\x0a"
         self.http_response_data = response

         self.sendData(self.http_response_data)

         ## opening handshake completed, move WebSockets connection into OPEN state
         ##
         self.state = WebSocketProtocol.STATE_OPEN
         self.current_frame = None
         self.inside_message = False

         ## fire handler on derived class
         ##
         self.onOpen()

         ## process rest, if any
         ##
         if len(self.data) > 0:
            self.consumeData()


   def failHandshake(self, reason, code = HTTP_STATUS_CODE_BAD_REQUEST[0], responseHeaders = []):
      """
      During opening handshake the client request was invalid, we send a HTTP
      error response and then drop the connection.
      """
      if self.debug:
         log.msg("failing WebSockets opening handshake ('%s')" % reason)
      self.sendHttpErrorResponse(code, reason, responseHeaders)
      self.dropConnection()


   def sendHttpErrorResponse(self, code, reason, responseHeaders = []):
      """
      Send out HTTP error response.
      """
      response  = "HTTP/1.1 %d %s\x0d\x0a" % (code, reason)
      for h in responseHeaders:
         response += "%s: %s\x0d\x0a" % h
      response += "\x0d\x0a"
      self.sendData(response)


   def sendHtml(self, html):
      raw = html.encode("utf-8")
      response  = "HTTP/1.1 %d %s\x0d\x0a" % (HTTP_STATUS_CODE_OK[0], HTTP_STATUS_CODE_OK[1])
      if self.factory.server is not None and self.factory.server != "":
         response += "Server: %s\x0d\x0a" % self.factory.server.encode("utf-8")
      response += "Content-Type: text/html; charset=UTF-8\x0d\x0a"
      response += "Content-Length: %d\x0d\x0a" % len(raw)
      response += "\x0d\x0a"
      response += raw
      self.sendData(response)


   def sendServerStatus(self):
      """
      Used to send out server status/version upon receiving a HTTP/GET without
      upgrade to WebSocket header (and option serverStatus is True).
      """
      html = """
<!DOCTYPE html>
<html>
   <body>
      <h1>Autobahn WebSockets %s</h1>
      <p>I am not Web server, but a WebSocket endpoint. You can talk to me
      in the WebSocket protocol versions %s.</p>
      <p>For more information, please visit <a href="http://www.tavendo.de/autobahn">my homepage</a>.</p>
   </body>
</html>
""" % (str(autobahn.version), str(sorted(WebSocketProtocol.SUPPORTED_PROTOCOL_VERSIONS)))
      self.sendHtml(html)


class WebSocketServerFactory(protocol.ServerFactory):
   """
   A Twisted factory for WebSockets server protocols.
   """

   protocol = WebSocketServerProtocol
   """
   The protocol to be spoken. Must be derived from :class:`autobahn.websocket.WebSocketServerProtocol`.
   """


   def __init__(self,

                ## WebSockect session parameters
                url = None,
                protocols = [],
                server = "AutobahnWebSockets/%s" % autobahn.version,

                ## debugging
                debug = False,
                debugCodePaths = False):
      """
      Create instance of WebSocket server factory.

      Note that you MUST set URL either here or using setSessionParameters() _before_ the factory is started.

      :param url: WebSocket listening URL - ("ws:" | "wss:") "//" host [ ":" port ] path [ "?" query ].
      :type url: str
      :param protocols: List of subprotocols the server supports. The subprotocol used is the first from the list of subprotocols announced by the client that is contained in this list.
      :type protocols: list of strings
      :param server: Server as announced in HTTP response header during opening handshake or None (default: "AutobahnWebSockets/x.x.x").
      :type server: str
      :param debug: Debug mode (default: False).
      :type debug: bool
      :param debugCodePaths: Debug code paths mode (default: False).
      :type debugCodePaths: bool
      """
      self.debug = debug
      self.debugCodePaths = debugCodePaths

      ## seed RNG which is used for WS frame masks generation
      random.seed()

      ## default WS session parameters
      ##
      self.setSessionParameters(url, protocols, server)

      ## default WebSocket protocol options
      ##
      self.resetProtocolOptions()

      ## number of currently connected clients
      ##
      self.countConnections = 0


   def setSessionParameters(self, url = None, protocols = [], server = None):
      """
      Set WebSocket session parameters.

      :param url: WebSocket listening URL - ("ws:" | "wss:") "//" host [ ":" port ].
      :type url: str
      :param origin: The origin to be sent in opening handshake.
      :type origin: str
      :param protocols: List of WebSocket subprotocols the client should announce in opening handshake.
      :type protocols: list of strings
      :param server: Server as announced in HTTP response header during opening handshake.
      :type server: str
      """
      if url is not None:
         ## parse WebSocket URI into components
         (isSecure, host, port, resource, path, params) = parseWsUrl(url)
         if path != "/":
            raise Exception("path specified for server WebSocket URL")
         if len(params) > 0:
            raise Exception("query parameters specified for server WebSocket URL")
         self.url = url
         self.isSecure = isSecure
         self.host = host
         self.port = port
      else:
         self.url = None
         self.isSecure = None
         self.host = None
         self.port = None

      self.protocols = protocols
      self.server = server


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
      self.closeHandshakeTimeout = 1
      self.tcpNoDelay = True


   def setProtocolOptions(self,
                          versions = None,
                          webStatus = None,
                          utf8validateIncoming = None,
                          maskServerFrames = None,
                          requireMaskedClientFrames = None,
                          applyMask = None,
                          maxFramePayloadSize = None,
                          maxMessagePayloadSize = None,
                          autoFragmentSize = None,
                          failByDrop = None,
                          echoCloseCodeReason = None,
                          closeHandshakeTimeout = None,
                          tcpNoDelay = None):
      """
      Set WebSocket protocol options used as defaults for new protocol instances.

      :param versions: The WebSockets protocol versions accepted by the server (default: WebSocketProtocol.SUPPORTED_PROTOCOL_VERSIONS).
      :type versions: list of ints
      :param webStatus: Return server status/version on HTTP/GET without WebSocket upgrade header (default: True).
      :type webStatus: bool
      :param utf8validateIncoming: Validate incoming UTF-8 in text message payloads (default: True).
      :type utf8validateIncoming: bool
      :param maskServerFrames: Mask server-to-client frames (default: False).
      :type maskServerFrames: bool
      :param requireMaskedClientFrames: Require client-to-server frames to be masked (default: True).
      :type requireMaskedClientFrames: bool
      :param applyMask: Actually apply mask to payload when mask it present. Applies for outgoing and incoming frames (default: True).
      :type applyMask: bool
      :param maxFramePayloadSize: Maximum frame payload size that will be accepted when receiving or 0 for unlimited (default: 0).
      :type maxFramePayloadSize: int
      :param maxMessagePayloadSize: Maximum message payload size (after reassembly of fragmented messages) that will be accepted when receiving or 0 for unlimited (default: 0).
      :type maxMessagePayloadSize: int
      :param autoFragmentSize: Automatic fragmentation of outgoing data messages (when using the message-based API) into frames with payload length <= this size or 0 for no auto-fragmentation (default: 0).
      :type autoFragmentSize: int
      :param failByDrop: Fail connections by dropping the TCP connection without performaing closing handshake (default: True).
      :type failbyDrop: bool
      :param echoCloseCodeReason: Iff true, when receiving a close, echo back close code/reason. Otherwise reply with code == NORMAL, reason = "" (default: False).
      :type echoCloseCodeReason: bool
      :param closeHandshakeTimeout: When we expect to receive a closing handshake reply, timeout in seconds (default: 1).
      :type closeHandshakeTimeout: float
      :param tcpNoDelay: TCP NODELAY ("Nagle") socket option (default: True).
      :type tcpNoDelay: bool
      """
      if versions is not None:
         for v in versions:
            if v not in WebSocketProtocol.SUPPORTED_PROTOCOL_VERSIONS:
               raise Exception("invalid WebSockets protocol version %s (allowed values: %s)" % (v, str(WebSocketProtocol.SUPPORTED_PROTOCOL_VERSIONS)))
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

      if closeHandshakeTimeout is not None and closeHandshakeTimeout != self.closeHandshakeTimeout:
         self.closeHandshakeTimeout = closeHandshakeTimeout

      if tcpNoDelay is not None and tcpNoDelay != self.tcpNoDelay:
         self.tcpNoDelay = tcpNoDelay


   def getConnectionCount(self):
      """
      Get number of currently connected clients.

      :returns: int -- Number of currently connected clients.
      """
      return self.countConnections


   def startFactory(self):
      """
      Called by Twisted before starting to listen on port for incoming connections.
      Default implementation does nothing. Override in derived class when appropriate.
      """
      pass


   def stopFactory(self):
      """
      Called by Twisted before stopping to listen on port for incoming connections.
      Default implementation does nothing. Override in derived class when appropriate.
      """
      pass


class WebSocketClientProtocol(WebSocketProtocol):
   """
   Client protocol for WebSockets.
   """

   def connectionMade(self):
      """
      Called by Twisted when new TCP connection to server was established. Default
      implementation will start the initial WebSocket opening handshake.
      When overriding in derived class, make sure to call this base class
      implementation _before_ your code.
      """
      self.isServer = False
      WebSocketProtocol.connectionMade(self)
      if self.debug:
         log.msg("connection to %s established" % self.peerstr)
      self.startHandshake()


   def connectionLost(self, reason):
      """
      Called by Twisted when established TCP connection to server was lost. Default
      implementation will tear down all state properly.
      When overriding in derived class, make sure to call this base class
      implementation _after_ your code.
      """
      WebSocketProtocol.connectionLost(self, reason)
      if self.debug:
         log.msg("connection to %s lost" % self.peerstr)


   def startHandshake(self):
      """
      Start WebSockets opening handshake.
      """

      ## construct WS opening handshake HTTP header
      ##
      request  = "GET %s HTTP/1.1\x0d\x0a" % self.factory.resource.encode("utf-8")

      if self.factory.useragent is not None and self.factory.useragent != "":
         request += "User-Agent: %s\x0d\x0a" % self.factory.useragent.encode("utf-8")

      request += "Host: %s:%d\x0d\x0a" % (self.factory.host.encode("utf-8"), self.factory.port)
      request += "Upgrade: websocket\x0d\x0a"
      request += "Connection: Upgrade\x0d\x0a"

      ## handshake random key
      ##
      self.websocket_key = base64.b64encode(os.urandom(16))
      request += "Sec-WebSocket-Key: %s\x0d\x0a" % self.websocket_key

      ## optional origin announced
      ##
      if self.factory.origin:
         if self.factory.version > 10:
            request += "Origin: %d\x0d\x0a" % self.factory.origin.encode("utf-8")
         else:
            request += "Sec-WebSocket-Origin: %d\x0d\x0a" % self.factory.origin.encode("utf-8")

      ## optional list of WS subprotocols announced
      ##
      if len(self.factory.protocols) > 0:
         request += "Sec-WebSocket-Protocol: %s\x0d\x0a" % ','.join(self.factory.protocols)

      ## set WS protocol version depending on WS spec version
      ##
      request += "Sec-WebSocket-Version: %d\x0d\x0a" % WebSocketProtocol.SPEC_TO_PROTOCOL_VERSION[self.factory.version]

      request += "\x0d\x0a"
      self.http_request_data = request

      if self.debug:
         log.msg(self.http_request_data)

      self.sendData(self.http_request_data)


   def processHandshake(self):
      """
      Process WebSockets opening handshake response from server.
      """
      ## only proceed when we have fully received the HTTP request line and all headers
      ##
      end_of_header = self.data.find("\x0d\x0a\x0d\x0a")
      if end_of_header >= 0:

         self.http_response_data = self.data[:end_of_header + 4]
         if self.debug:
            log.msg("received HTTP response:\n\n%s\n\n" % self.http_response_data)

         ## extract HTTP status line and headers
         ##
         (self.http_status_line, self.http_headers, http_headers_cnt) = parseHttpHeader(self.http_response_data)

         ## remember rest (after HTTP headers, if any)
         ##
         self.data = self.data[end_of_header + 4:]

         ## validate WebSocket opening handshake server response
         ##
         if self.debug:
            log.msg("received HTTP status line in opening handshake : %s" % str(self.http_status_line))
            log.msg("received HTTP headers in opening handshake : %s" % str(self.http_headers))

         ## Response Line
         ##
         sl = self.http_status_line.split()
         if len(sl) < 2:
            return self.failHandshake("Bad HTTP response status line '%s'" % self.http_status_line)

         ## HTTP version
         ##
         http_version = sl[0].strip()
         if http_version != "HTTP/1.1":
            return self.failHandshake("Unsupported HTTP version ('%s')" % http_version)

         ## HTTP status code
         ##
         try:
            status_code = int(sl[1].strip())
         except:
            return self.failHandshake("Bad HTTP status code ('%s')" % sl[1].strip())
         if status_code != HTTP_STATUS_CODE_SWITCHING_PROTOCOLS[0]:

            ## FIXME: handle redirects
            ## FIXME: handle authentication required

            if len(sl) > 2:
               reason = " - %s" % sl[2].strip()
            else:
               reason = ""
            return self.failHandshake("WebSockets connection upgrade failed (%d%s)" % (status_code, reason))

         ## Upgrade
         ##
         if not self.http_headers.has_key("upgrade"):
            return self.failHandshake("HTTP Upgrade header missing")
         if self.http_headers["upgrade"].strip().lower() != "websocket":
            return self.failHandshake("HTTP Upgrade header different from 'websocket' (case-insensitive) : %s" % self.http_headers["upgrade"])

         ## Connection
         ##
         if not self.http_headers.has_key("connection"):
            return self.failHandshake("HTTP Connection header missing")
         connectionUpgrade = False
         for c in self.http_headers["connection"].split(","):
            if c.strip().lower() == "upgrade":
               connectionUpgrade = True
               break
         if not connectionUpgrade:
            return self.failHandshake("HTTP Connection header does not include 'upgrade' value (case-insensitive) : %s" % self.http_headers["connection"])

         ## compute Sec-WebSocket-Accept
         ##
         if not self.http_headers.has_key("sec-websocket-accept"):
            return self.failHandshake("HTTP Sec-WebSocket-Accept header missing in opening handshake reply")
         else:
            if http_headers_cnt["sec-websocket-accept"] > 1:
               return self.failHandshake("HTTP Sec-WebSocket-Accept header appears more than once in opening handshake reply")
            sec_websocket_accept_got = self.http_headers["sec-websocket-accept"].strip()

            sha1 = hashlib.sha1()
            sha1.update(self.websocket_key + WebSocketProtocol.WS_MAGIC)
            sec_websocket_accept = base64.b64encode(sha1.digest())

            if sec_websocket_accept_got != sec_websocket_accept:
               return self.failHandshake("HTTP Sec-WebSocket-Accept bogus value : expected %s / got %s" % (sec_websocket_accept, sec_websocket_accept_got))

         ## handle "extensions in use" - if any
         ##
         self.websocket_extensions_in_use = []
         if self.http_headers.has_key("sec-websocket-extensions"):
            if http_headers_cnt["sec-websocket-extensions"] > 1:
               return self.failHandshake("HTTP Sec-WebSocket-Extensions header appears more than once in opening handshake reply")
            exts = self.http_headers["sec-websocket-extensions"].strip()
            ##
            ## we don't support any extension, but if we did, we needed
            ## to set self.websocket_extensions_in_use here, and don't fail the handshake
            ##
            return self.failHandshake("server wants to use extensions (%s), but no extensions implemented" % exts)

         ## handle "subprotocol in use" - if any
         ##
         self.websocket_protocol_in_use = None
         if self.http_headers.has_key("sec-websocket-protocol"):
            if http_headers_cnt["sec-websocket-protocol"] > 1:
               return self.failHandshake("HTTP Sec-WebSocket-Protocol header appears more than once in opening handshake reply")
            sp = self.http_headers["sec-websocket-protocol"].strip()
            if sp != "":
               if sp not in self.factory.protocols:
                  return self.failHandshake("subprotocol selected by server (%s) not in subprotocol list requested by client (%s)" % (sp, str(self.factory.protocols)))
               else:
                  ## ok, subprotocol in use
                  ##
                  self.websocket_protocol_in_use = sp

         ## opening handshake completed, move WebSockets connection into OPEN state
         ##
         self.state = WebSocketProtocol.STATE_OPEN
         self.current_frame = None
         self.inside_message = False

         ## fire handler on derived class
         ##
         self.onOpen()

         ## process rest, if any
         ##
         if len(self.data) > 0:
            self.consumeData()


   def failHandshake(self, reason):
      """
      During opening handshake the server response is invalid and we drop the
      connection.
      """
      if self.debug:
         log.msg("failing WebSockets opening handshake ('%s')" % reason)
      self.dropConnection()


class WebSocketClientFactory(protocol.ClientFactory):
   """
   A Twisted factory for WebSockets client protocols.
   """

   protocol = WebSocketClientProtocol
   """
   The protocol to be spoken. Must be derived from :class:`autobahn.websocket.WebSocketClientProtocol`.
   """


   def __init__(self,

                ## WebSockect session parameters
                url = None,
                origin = None,
                protocols = [],
                useragent = "AutobahnWebSockets/%s" % autobahn.version,

                ## debugging
                debug = False,
                debugCodePaths = False):
      """
      Create instance of WebSocket client factory.

      Note that you MUST set URL either here or using setSessionParameters() _before_ the factory is started.

      :param url: WebSocket URL to connect to - ("ws:" | "wss:") "//" host [ ":" port ] path [ "?" query ].
      :type url: str
      :param origin: The origin to be sent in WebSockets opening handshake or None (default: None).
      :type origin: str
      :param protocols: List of subprotocols the client should announce in WebSockets opening handshake (default: []).
      :type protocols: list of strings
      :param useragent: User agent as announced in HTTP request header or None (default: "AutobahnWebSockets/x.x.x").
      :type useragent: str
      :param debug: Debug mode (default: False).
      :type debug: bool
      :param debugCodePaths: Debug code paths mode (default: False).
      :type debugCodePaths: bool
      """
      self.debug = debug
      self.debugCodePaths = debugCodePaths

      ## seed RNG which is used for WS opening handshake key and WS frame masks generation
      random.seed()

      ## default WS session parameters
      ##
      self.setSessionParameters(url, origin, protocols, useragent)

      ## default WebSocket protocol options
      ##
      self.resetProtocolOptions()


   def setSessionParameters(self, url = None, origin = None, protocols = [], useragent = None):
      """
      Set WebSocket session parameters.

      :param url: WebSocket URL to connect to - ("ws:" | "wss:") "//" host [ ":" port ] path [ "?" query ].
      :type url: str
      :param origin: The origin to be sent in opening handshake.
      :type origin: str
      :param protocols: List of WebSocket subprotocols the client should announce in opening handshake.
      :type protocols: list of strings
      :param useragent: User agent as announced in HTTP request header during opening handshake.
      :type useragent: str
      """
      if url is not None:
         ## parse WebSocket URI into components
         (isSecure, host, port, resource, path, params) = parseWsUrl(url)
         self.url = url
         self.isSecure = isSecure
         self.host = host
         self.port = port
         self.resource = resource
         self.path = path
         self.params = params
      else:
         self.url = None
         self.isSecure = None
         self.host = None
         self.port = None
         self.resource = None
         self.path = None
         self.params = None

      self.origin = origin
      self.protocols = protocols
      self.useragent = useragent


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
      self.closeHandshakeTimeout = 1
      self.tcpNoDelay = True


   def setProtocolOptions(self,
                          version = None,
                          utf8validateIncoming = None,
                          acceptMaskedServerFrames = None,
                          maskClientFrames = None,
                          applyMask = None,
                          maxFramePayloadSize = None,
                          maxMessagePayloadSize = None,
                          autoFragmentSize = None,
                          failByDrop = None,
                          echoCloseCodeReason = None,
                          serverConnectionDropTimeout = None,
                          closeHandshakeTimeout = None,
                          tcpNoDelay = None):
      """
      Set WebSocket protocol options used as defaults for _new_ protocol instances.

      :param version: The WebSockets protocol spec (draft) version to be used (default: WebSocketProtocol.DEFAULT_SPEC_VERSION).
      :type version: int
      :param utf8validateIncoming: Validate incoming UTF-8 in text message payloads (default: True).
      :type utf8validateIncoming: bool
      :param acceptMaskedServerFrames: Accept masked server-to-client frames (default: False).
      :type acceptMaskedServerFrames: bool
      :param maskClientFrames: Mask client-to-server frames (default: True).
      :type maskClientFrames: bool
      :param applyMask: Actually apply mask to payload when mask it present. Applies for outgoing and incoming frames (default: True).
      :type applyMask: bool
      :param maxFramePayloadSize: Maximum frame payload size that will be accepted when receiving or 0 for unlimited (default: 0).
      :type maxFramePayloadSize: int
      :param maxMessagePayloadSize: Maximum message payload size (after reassembly of fragmented messages) that will be accepted when receiving or 0 for unlimited (default: 0).
      :type maxMessagePayloadSize: int
      :param autoFragmentSize: Automatic fragmentation of outgoing data messages (when using the message-based API) into frames with payload length <= this size or 0 for no auto-fragmentation (default: 0).
      :type autoFragmentSize: int
      :param failByDrop: Fail connections by dropping the TCP connection without performing closing handshake (default: True).
      :type failbyDrop: bool
      :param echoCloseCodeReason: Iff true, when receiving a close, echo back close code/reason. Otherwise reply with code == NORMAL, reason = "" (default: False).
      :type echoCloseCodeReason: bool
      :param serverConnectionDropTimeout: When the client expects the server to drop the TCP, timeout in seconds (default: 1).
      :type serverConnectionDropTimeout: float
      :param closeHandshakeTimeout: When we expect to receive a closing handshake reply, timeout in seconds (default: 1).
      :type closeHandshakeTimeout: float
      :param tcpNoDelay: TCP NODELAY ("Nagle") socket option (default: True).
      :type tcpNoDelay: bool
      """

      if version is not None:
         if version not in WebSocketProtocol.SUPPORTED_SPEC_VERSIONS:
            raise Exception("invalid WebSockets draft version %s (allowed values: %s)" % (version, str(WebSocketProtocol.SUPPORTED_SPEC_VERSIONS)))
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

      if closeHandshakeTimeout is not None and closeHandshakeTimeout != self.closeHandshakeTimeout:
         self.closeHandshakeTimeout = closeHandshakeTimeout

      if tcpNoDelay is not None and tcpNoDelay != self.tcpNoDelay:
         self.tcpNoDelay = tcpNoDelay


   def clientConnectionFailed(self, connector, reason):
      """
      Called by Twisted when the connection to server has failed. Default implementation
      will stop the reactor. Override in derived class when appropriate.
      """
      reactor.stop()


   def clientConnectionLost(self, connector, reason):
      """
      Called by Twisted when the connection to server was lost. Default implementation
      will stop the reactor. Override in derived class when appropriate.
      """
      reactor.stop()
