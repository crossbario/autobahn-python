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

from twisted.internet import reactor, protocol
from twisted.python import log
import binascii
import hashlib
import base64
import struct
import random
import urlparse
import os


class WebSocketProtocol(protocol.Protocol):
   """
   A Twisted Protocol class for WebSockets. This class is used by both WebSocket
   client and server protocol version. It is unusable standalone, for example
   the WebSockets initial handshake is implemented in derived class differently
   for clients and servers.
   """

   ## WebSockets protocol state
   ##
   STATE_CLOSED = 0
   STATE_CONNECTING = 1
   STATE_OPEN = 2

   ## WebSockets protocol close codes
   ##
   CLOSE_STATUS_CODE_NORMAL = 1000
   CLOSE_STATUS_CODE_GOING_AWAY = 1001
   CLOSE_STATUS_CODE_PROTOCOL_ERROR = 1002
   CLOSE_STATUS_CODE_PAYLOAD_NOT_ACCEPTED = 1003
   CLOSE_STATUS_CODE_FRAME_TOO_LARGE = 1004
   CLOSE_STATUS_CODE_NULL = 1005 # MUST NOT be set in close frame!
   CLOSE_STATUS_CODE_CONNECTION_LOST = 1006 # MUST NOT be set in close frame!
   CLOSE_STATUS_CODE_TEXT_FRAME_NOT_UTF8 = 1007

   def onOpen(self):
      """
      Callback when initial handshake was completed. Now you may send messages!
      Default implementation does nothing.

      Override in derived class.
      """
      if self.debug:
         log.msg("onOpen()")

   def onMessage(self, msg, binary):
      """
      Callback when message was received. Default implementation does nothing.

      Override in derived class.
      """
      if self.debug:
         log.msg("onMessage()")

   def onPing(self, payload):
      """
      Callback when Ping was received. Default implementation responds
      with a Pong.

      Override in derived class.
      """
      if self.debug:
         log.msg("onPing()")
      self.sendPong(payload)

   def onPong(self, payload):
      """
      Callback when Pong was received. Default implementation does nothing.

      Override in derived class.
      """
      if self.debug:
         log.msg("onPong()")

   def onClose(self, code, reason):
      """
      Callback when Close was received. The default implementation answer with Close,
      which is how a WebSockets server should behave.

      Override in derived class.
      """
      if self.debug:
         log.msg("received CLOSE for %s (%s, %s)" % (self.peerstr, code, reason))
      self.sendClose(code, "ok, you asked me to close, I do;)")
      self.transport.loseConnection()


   def __init__(self):
      self.state = WebSocketProtocol.STATE_CLOSED


   def connectionMade(self):
      """
      This is called by Twisted framework when a new TCP connection has been established
      and handed over to a Protocol instance (an instance of this class).
      """
      self.debug = self.factory.debug
      self.transport.setTcpNoDelay(True)
      self.peer = self.transport.getPeer()
      self.peerstr = "%s:%d" % (self.peer.host, self.peer.port)
      self.state = WebSocketProtocol.STATE_CONNECTING
      self.data = ""


   def connectionLost(self, reason):
      """
      This is called by Twisted framework when a TCP connection was lost.
      """
      self.state = WebSocketProtocol.STATE_CLOSED


   def dataReceived(self, data):
      """
      This is called by Twisted framework upon receiving data on TCP connection.
      """
      if data:
         if self.debug:
            log.msg("RX from %s : %s" % (self.peerstr, binascii.b2a_hex(data)))
         self.data += data

      ## WebSocket is open (handshake was completed)
      ##
      if self.state == WebSocketProtocol.STATE_OPEN:

         while self.processData():
            pass

      ## WebSocket needs handshake
      ##
      elif self.state == WebSocketProtocol.STATE_CONNECTING:

         ## the implementation of processHandshake() in derived
         ## class needs to perform client or server handshake
         ## from other party here ..
         ##
         self.processHandshake()

      ## should not arrive here (invalid state)
      ##
      else:
         raise Exception("invalid state")


   def processHandshake(self):
      """
      Process WebSockets handshake.
      """
      raise Exception("must implement handshake (client or server) in derived class")


   def sendData(self, raw, chopsize = None):
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
         n = len(raw)
         done = False
         while not done:
            j = i + chopsize
            if j >= n:
               done = True
               j = n
            if self.debug:
               log.msg("TX to %s : %s" % (self.peerstr, binascii.b2a_hex(raw[i:j])))
            self.transport.write(raw[i:j])

            ## This is where the "magic" happens. We give up control to the
            ## Twisted reactor, which calls into the OS Select(), which will
            ## then send out outstanding data. I suspect this Twisted call is
            ## probably not "intended" to be called by Twisted users, but it is
            ## the only "way" I found to work to attain the intended result.
            ##
            reactor.doSelect(0)

            i += chopsize
      else:
         if self.debug:
            log.msg("TX to %s : %s" % (self.peerstr, binascii.b2a_hex(raw)))
         self.transport.write(raw)


   def processData(self):
      """
      After WebSockets handshake has been completed, this procedure will do all
      subsequent processing of incoming bytes.
      """
      if self.current_frame is None:

         buffered_len = len(self.data)

         ## start of new frame
         ##
         if buffered_len >= 2: # need minimum frame length

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
               self.sendClose(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, "RSV != 0 and no extension negotiated")

            ## all client-to-server frames MUST be masked
            ##
            if self.isServer and not frame_masked:
               self.sendClose(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, "unmasked client to server frame")

            ## check frame
            ##
            if frame_opcode > 7: # control frame (have MSB in opcode set)

               ## control frames MUST NOT be fragmented
               ##
               if not frame_fin:
                  self.sendClose(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, "fragmented control frame")
               ## control frames MUST have payload 125 octets or less
               ##
               if frame_payload_len1 > 125:
                  self.sendClose(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, "control frame with payload length > 125 octets")
               ## check for reserved control frame opcodes
               ##
               if frame_opcode not in [8, 9, 10]:
                  self.sendClose(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, "control frame using reserved opcode %d" % frame_opcode)

            else: # data frame

               ## check for reserved data frame opcodes
               ##
               if frame_opcode not in [0, 1, 2]:
                  self.sendClose(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, "data frame using reserved opcode %d" % frame_opcode)

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

               ## EXTENDED PAYLOAD LEN
               ##
               if frame_payload_len1 == 126:
                  frame_payload_len = struct.unpack("!H", self.data[i:i+2])[0]
                  i += 2
               elif frame_payload_len1 == 127:
                  frame_payload_len = struct.unpack("!Q", self.data[i:i+8])[0]
                  i += 8
               else:
                  frame_payload_len = frame_payload_len1

               ## frame mask (all client-to-server frames MUST be masked!)
               ##
               frame_mask = []
               if frame_masked:
                  for j in range(i, i + 4):
                     frame_mask.append(ord(self.data[j]))
                  i += 4

               ## ok, got complete frame header
               ##
               self.current_frame = (frame_header_len, frame_fin, frame_rsv, frame_opcode, frame_masked, frame_mask, frame_payload_len)

               ## remember rest (payload of current frame and everything thereafter)
               ##
               self.data = self.data[i:]

            else:
               return False # need more data
         else:
            return False # need more data

      if self.current_frame is not None:

         buffered_len = len(self.data)

         frame_header_len, frame_fin, frame_rsv, frame_opcode, frame_masked, frame_mask, frame_payload_len = self.current_frame

         if buffered_len >= frame_payload_len:

            ## unmask payload
            ##
            if frame_masked:
               payload = ''.join([chr(ord(self.data[k]) ^ frame_mask[k % 4]) for k in range(0, frame_payload_len)])
            else:
               payload = self.data[:frame_payload_len]

            ## buffer rest and reset current_frame
            ##
            self.data = self.data[frame_payload_len:]
            self.current_frame = None

            ## now process frame
            ##
            self.onFrame(frame_fin, frame_opcode, payload)

            return len(self.data) > 0 # reprocess when buffered data left

         else:
            return False # need more data

      else:
         return False # need more data


   def onFrame(self, fin, opcode, payload):
      """
      Process a completely received frame.
      """
      ## DATA frame
      ##
      if opcode in [0, 1, 2]:

         ## check opcode vs protocol message state
         ##
         if self.msg_type is None:
            if opcode in [1, 2]:
               self.msg_type = opcode
            else:
               self.sendClose(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, "received continuation frame outside fragmented message")
         else:
            if opcode == 0:
               pass
            else:
               self.sendClose(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, "received non-continuation frame while in fragmented message")

         ## buffer message payload
         ##
         self.msg_payload.append(payload)

         ## final message fragment?
         ##
         if fin:
            msg = ''.join(self.msg_payload)
            self.onMessage(msg, self.msg_type == 2)
            self.msg_payload = []
            self.msg_type = None

      ## CLOSE frame
      ##
      elif opcode == 8:

         code = None
         reason = None

         plen = len(payload)
         if plen > 0:

            ## If there is a body, the first two bytes of the body MUST be a 2-byte
            ## unsigned integer (in network byte order) representing a status code
            ##
            if plen < 2:
               pass
            code = struct.unpack("!H", payload[0:2])[0]

            ## Following the 2-byte integer the body MAY contain UTF-8
            ## encoded data with value /reason/, the interpretation of which is not
            ## defined by this specification.
            ##
            if plen > 2:
               try:
                  reason = unicode(payload[2:], 'utf8')
               except UnicodeDecodeError:
                  pass

         self.onClose(code, reason)

      ## PING frame
      ##
      elif opcode == 9:
         self.onPing(payload)

      ## PONG frame
      ##
      elif opcode == 10:
         self.onPong(payload)

      else:
         raise Exception("logic error processing frame with opcode %d" % opcode)


   def sendFrame(self, opcode, payload, fin = True, rsv = 0, mask = None, payload_len = None, chopsize = None, sync = False):
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
      if payload_len:
         if payload_len < 1 or len(payload) < 1:
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
      if mask or not self.isServer:
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
         plm = ''.join([chr(ord(pl[k]) ^ frame_mask[k % 4]) for k in range(0, l)])
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

      self.sendData(raw, chopsize)

      if sync:
         reactor.doSelect(0)


   def sendPing(self, payload):
      """
      Send out Ping to peer. Payload can be arbitrary, but length must be less than 126 octets.
      A peer is expected to Pong back the payload a soon as "practical". When more than 1 Ping
      is outstanding at the peer, the peer may elect to respond only to the last Ping.
      """
      l = len(payload)
      if l > 125:
         raise Exception("invalid payload for PING (payload length must be <= 125, was %d)" % l)
      self.sendFrame(opcode = 9, payload = payload)


   def sendPong(self, payload):
      """
      Send out Pong to peer. Payload can be arbitrary, but length must be less than 126 octets.
      A Pong frame MAY be sent unsolicited.  This serves as a unidirectional heartbeat.
      A response to an unsolicited pong is "not expected".
      """
      l = len(payload)
      if l > 125:
         raise Exception("invalid payload for PONG (payload length must be <= 125, was %d)" % l)
      self.sendFrame(opcode = 10, payload = payload)


   def sendClose(self, status_code = None, status_reason = None):
      """
      Send out close to peer.
      """
      plen = 0
      payload = ""

      if status_code is not None:

         if (not (status_code >= 3000 and status_code <= 3999)) and \
            (not (status_code >= 4000 and status_code <= 4999)) and \
            status_code not in [WebSocketProtocol.CLOSE_STATUS_CODE_NORMAL,
                                WebSocketProtocol.CLOSE_STATUS_CODE_GOING_AWAY,
                                WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR,
                                WebSocketProtocol.CLOSE_STATUS_CODE_PAYLOAD_NOT_ACCEPTED,
                                WebSocketProtocol.CLOSE_STATUS_CODE_FRAME_TOO_LARGE,
                                WebSocketProtocol.CLOSE_STATUS_CODE_TEXT_FRAME_NOT_UTF8]:
            raise Exception("invalid status code %d for close frame" % status_code)

         payload = struct.pack("!H", status_code)
         plen = 2

         if status_reason is not None:
            reason = status_reason.encode("UTF-8")
            plen += len(reason)

         if plen > 125:
            raise Exception("close frame payload larger than 125 octets")

         payload += reason

      else:
         if status_reason is not None:
            raise Exception("status reason without status code in close frame")

      self.sendFrame(opcode = 8, payload = payload)


   def sendMessage(self, payload, binary = False, payload_frag_size = None):
      """
      Send out data message. You can send text or binary message, and optionally
      specifiy a payload fragment size. When the latter is given, the payload will
      be split up into frames with payload <= the payload_frag_size given.
      """
      ## (initial) frame opcode
      ##
      if binary:
         opcode = 2
      else:
         opcode = 1

      ## send unfragmented
      ##
      if payload_frag_size is None or len(payload) <= payload_frag_size:
         self.sendFrame(opcode = opcode, payload = payload)

      ## send data message in fragments
      ##
      else:
         if payload_frag_size < 1:
            raise Exception("payload fragment size must be at least 1 (was %d)" % payload_frag_size)
         i = 0
         n = len(payload)
         done = False
         first = True
         while not done:
            j = i + payload_frag_size
            if j > n:
               done = True
               j = n
            if first:
               self.sendFrame(opcode = opcode, payload = payload, fin = done)
               first = False
            else:
               self.sendFrame(opcode = 0, payload = payload, fin = done)
            i += payload_frag_size


class HttpException():
   def __init__(self, code, reason):
      self.code = code
      self.reason = reason


class WebSocketServiceConnection(WebSocketProtocol):
   """
   Server protocol for WebSockets.
   """

   ##
   ## The following set of methods is intended to be overridden in subclasses
   ##

   def onConnect(self, host, uri, origin, protocols):
      """
      Callback when new WebSocket client connection is established.
      Throw HttpException when you don't want to accept WebSocket connection.
      Return accepted protocol from list of protocols provided by client or None.

      Override in derived class.
      """
      pass

   def connectionMade(self):
      WebSocketProtocol.connectionMade(self)
      if self.debug:
         log.msg("WebSocketServiceConnection.connectionMade")
         log.msg("connection accepted from %s" % self.peerstr)
      self.http_request = None
      self.http_headers = {}
      self.isServer = True


   def connectionLost(self, reason):
      WebSocketProtocol.connectionLost(self, reason)
      if self.debug:
         log.msg("WebSocketServiceConnection.connectionLost")
         log.msg("connection from %s lost" % self.peerstr)


   def processHandshake(self):
      """
      Process WebSockets handshake.
      """
      ## only proceed when we have fully received the HTTP request line and all headers
      ##
      end_of_header = self.data.find("\x0d\x0a\x0d\x0a")
      if end_of_header >= 0:

         ## extract HTTP headers
         ##
         ## FIXME: properly handle headers split accross multiple lines
         ##
         raw = self.data[:end_of_header].splitlines()
         self.http_request = raw[0].strip()
         for h in raw[1:]:
            i = h.find(":")
            if i > 0:
               key = h[:i].strip()
               value = h[i+1:].strip()
               self.http_headers[key] = value

         ## remember rest (after HTTP headers, if any)
         ##
         self.data = self.data[end_of_header + 4:]

         ## self.http_request & self.http_headers are now set
         ## => validate WebSocket handshake
         ##

         if self.debug:
            log.msg("received request line in handshake : %s" % str(self.http_request))
            log.msg("received headers in handshake : %s" % str(self.http_headers))

         ## HTTP Request line : METHOD, VERSION
         ##
         rl = self.http_request.split(" ")
         if len(rl) != 3:
            return self.sendHttpBadRequest("bad HTTP request line '%s'" % self.http_request)
         if rl[0] != "GET":
            return self.sendHttpBadRequest("illegal HTTP method '%s'" % rl[0])
         vs = rl[2].split("/")
         if len(vs) != 2 or vs[0] != "HTTP" or vs[1] not in ["1.1"]:
            return self.sendHttpBadRequest("bad HTTP version '%s'" % rl[2])

         ## HTTP Request line : REQUEST-URI
         ##
         ## FIXME: checking
         ##
         self.http_request_uri = rl[1]
         (scheme, loc, path, params, query, fragment) = urlparse.urlparse(self.http_request_uri)
         if fragment != "":
            return self.sendHttpBadRequest("HTTP Request URI with fragment identifier")
         self.http_request_path = path
         self.http_request_params = urlparse.parse_qs(query)

         ## Host
         ##
         ## FIXME: checking
         ##
         if not self.http_headers.has_key("Host"):
            return self.sendHttpBadRequest("HTTP Host header missing")
         self.http_request_host = self.http_headers["Host"].strip()

         ## Upgrade
         ##
         if not self.http_headers.has_key("Upgrade"):
            return self.sendHttpBadRequest("HTTP Upgrade header missing")
         if self.http_headers["Upgrade"] != "websocket":
            return self.sendHttpBadRequest("HTTP Upgrade header different from 'websocket'")

         ## Connection
         ##
         if not self.http_headers.has_key("Connection"):
            return self.sendHttpBadRequest("HTTP Connection header missing")
         connectionUpgrade = False
         for c in self.http_headers["Connection"].split(","):
            if c.strip() == "Upgrade":
               connectionUpgrade = True
               break
         if not connectionUpgrade:
            return self.sendHttpBadRequest("HTTP Connection header does not include 'Upgrade' value")

         ## Sec-WebSocket-Version
         ##
         if not self.http_headers.has_key("Sec-WebSocket-Version"):
            return self.sendHttpBadRequest("HTTP Sec-WebSocket-Version header missing")
         try:
            version = int(self.http_headers["Sec-WebSocket-Version"])
            if version < 8:
               return self.sendHttpBadRequest("Sec-WebSocket-Version %d not supported (only >= 8)" % version)
            else:
               self.websocket_version = version
         except:
            return self.sendHttpBadRequest("could not parse HTTP Sec-WebSocket-Version header '%s'" % self.http_headers["Sec-WebSocket-Version"])

         ## Sec-WebSocket-Protocol
         ##
         ##
         if self.http_headers.has_key("Sec-WebSocket-Protocol"):
            protocols = self.http_headers["Sec-WebSocket-Protocol"].split(",")
            # check for duplicates in protocol header
            pp = {}
            for p in protocols:
               if pp.has_key(p):
                  return self.sendHttpBadRequest("duplicate protocol '%s' specified in HTTP Sec-WebSocket-Protocol header" % p)
               else:
                  pp[p] = 1
            # ok, no duplicates, save list in order the client sent it
            self.websocket_protocols = protocols
         else:
            self.websocket_protocols = []

         ## Sec-WebSocket-Origin
         ## http://tools.ietf.org/html/draft-ietf-websec-origin-02
         ##
         ## FIXME: checking
         ##
         if self.http_headers.has_key("Sec-WebSocket-Origin"):
            origin = self.http_headers["Sec-WebSocket-Origin"].strip()
            if origin == "null":
               self.websocket_origin = None
            else:
               self.websocket_origin = origin
         else:
            self.websocket_origin = None

         ## Sec-WebSocket-Extensions
         ##
         if self.http_headers.has_key("Sec-WebSocket-Extensions"):
            pass

         ## Sec-WebSocket-Key
         ## http://tools.ietf.org/html/rfc4648#section-4
         ##
         if not self.http_headers.has_key("Sec-WebSocket-Key"):
            return self.sendHttpBadRequest("HTTP Sec-WebSocket-Version header missing")
         key = self.http_headers["Sec-WebSocket-Key"].strip()
         if len(key) != 24: # 16 bytes => (ceil(128/24)*24)/6 == 24
            return self.sendHttpBadRequest("bad Sec-WebSocket-Key (length must be 24 ASCII chars) '%s'" % key)
         if key[-2:] != "==": # 24 - ceil(128/6) == 2
            return self.sendHttpBadRequest("bad Sec-WebSocket-Key (invalid base64 encoding) '%s'" % key)
         for c in key[:-2]:
            if c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/":
               return self.sendHttpBadRequest("bad character '%s' in Sec-WebSocket-Key (invalid base64 encoding) '%s'" (c, key))

         ## WebSocket handshake validated
         ## => produce response

         # request Host, request URI, origin, protocols
         try:
            protocol = self.onConnect(self.http_request_host, self.http_request_uri, self.websocket_origin, self.websocket_protocols)
            if protocol and not (protocol in self.websocket_protocols):
               raise Exception("protocol accepted must be from the list client sent or null")
         except HttpException, e:
            return self.sendHttpRequestFailure(e.code, e.reason)

         ## compute Sec-WebSocket-Accept
         ##
         magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
         sha1 = hashlib.sha1()
         sha1.update(key + magic)
         sec_websocket_accept = base64.b64encode(sha1.digest())

         ## send response to complete WebSocket handshake
         ##
         response  = "HTTP/1.1 101 Switching Protocols\x0d\x0a"
         response += "Upgrade: websocket\x0d\x0a"
         response += "Connection: Upgrade\x0d\x0a"
         response += "Sec-WebSocket-Accept: %s\x0d\x0a" % sec_websocket_accept
         if protocol:
            response += "Sec-WebSocket-Protocol: %s\x0d\x0a" % protocol
         response += "\x0d\x0a"

         if self.debug:
            log.msg("send handshake : %s" % response)
         self.sendData(response)

         ## move into OPEN state
         ##
         self.state = WebSocketProtocol.STATE_OPEN
         self.current_frame = None
         self.msg_payload = []
         self.msg_type = None

         ## fire handler on derived class
         ##
         self.onOpen()

         ## process rest, if any
         ##
         if len(self.data) > 0:
            self.dataReceived(None)


   def sendHttpBadRequest(self, reason):
      """
      When problems/errors happen during WebSockets handshake, send HTTP
      Bad Request Error and terminate.
      """
      self.sendHttpRequestFailure(400, reason)


   def sendHttpRequestFailure(self, code, reason):
      """
      Send out HTTP error.
      """
      response  = "HTTP/1.1 %d %s\x0d\x0a" % (code, reason)
      response += "\x0d\x0a"
      if self.debug:
         log.msg("send handshake failure : %s" % response)
      self.sendData(response)
      self.transport.loseConnection()


class WebSocketService(protocol.ServerFactory):
   """
   Server factory for WebSockets.
   """

   protocol = WebSocketServiceConnection

   def __init__(self, debug = False):
      self.debug = debug

   def startFactory(self):
      pass

   def stopFactory(self):
      pass


class WebSocketClientConnection(WebSocketProtocol):
   """
   Client protocol for WebSockets.
   """

   def __init__(self, debug = False):
      self.debug = debug

   def onOpen(self):
      self.sendPing("ping from client")

   def onPong(self, payload):
      log.msg("PONG : " + payload)

   def connectionMade(self):
      WebSocketProtocol.connectionMade(self)
      if self.debug:
         log.msg("connection to %s established" % self.peerstr)
      self.http_request = None
      self.http_headers = {}
      self.isServer = False
      self.startHandshake()


   def connectionLost(self, reason):
      WebSocketProtocol.connectionLost(self, reason)
      if self.debug:
         log.msg("connection to %s lost" % self.peerstr)


   def startHandshake(self):
      # GET /chat HTTP/1.1
      # Host: server.example.com
      # Upgrade: websocket
      # Connection: Upgrade
      # Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
      # Sec-WebSocket-Origin: http://example.com
      # Sec-WebSocket-Protocol: chat, superchat
      # Sec-WebSocket-Version: 8
      self.websocket_key = base64.b64encode(os.urandom(16))
      log.msg(self.peerstr)

      request  = "GET / HTTP/1.1\x0d\x0a"
      request += "Host: localhost:9000\x0d\x0a"
      request += "Upgrade: websocket\x0d\x0a"
      request += "Connection: Upgrade\x0d\x0a"
      request += "Sec-WebSocket-Key: %s\x0d\x0a" % self.websocket_key
      request += "Sec-WebSocket-Version: 8\x0d\x0a"
      request += "\x0d\x0a"

      self.sendData(request)


   def processHandshake(self):
      """
      Process WebSockets handshake.
      """
      ## only proceed when we have fully received the HTTP request line and all headers
      ##
      end_of_header = self.data.find("\x0d\x0a\x0d\x0a")
      if end_of_header >= 0:

         ## extract HTTP headers
         ##
         ## FIXME: properly handle headers split accross multiple lines
         ##
         raw = self.data[:end_of_header].splitlines()
         self.http_request = raw[0].strip()
         for h in raw[1:]:
            i = h.find(":")
            if i > 0:
               key = h[:i].strip()
               value = h[i+1:].strip()
               self.http_headers[key] = value

         ## remember rest (after HTTP headers, if any)
         ##
         self.data = self.data[end_of_header + 4:]

         ## self.http_request & self.http_headers are now set
         ## => validate WebSocket handshake
         ##

         if self.debug:
            log.msg("received request line in handshake : %s" % str(self.http_request))
            log.msg("received headers in handshake : %s" % str(self.http_headers))

         ## Response Line
         ##
         if self.http_request != "HTTP/1.1 101 Switching Protocols":
            pass

         ## Upgrade
         ##
         if not self.http_headers.has_key("Upgrade"):
            return self.sendHttpBadRequest("HTTP Upgrade header missing")
         if self.http_headers["Upgrade"] != "websocket":
            return self.sendHttpBadRequest("HTTP Upgrade header different from 'websocket'")

         ## Connection
         ##
         if not self.http_headers.has_key("Connection"):
            return self.sendHttpBadRequest("HTTP Connection header missing")
         connectionUpgrade = False
         for c in self.http_headers["Connection"].split(","):
            if c.strip() == "Upgrade":
               connectionUpgrade = True
               break
         if not connectionUpgrade:
            return self.sendHttpBadRequest("HTTP Connection header does not include 'Upgrade' value")

         ## compute Sec-WebSocket-Accept
         ##
         if not self.http_headers.has_key("Sec-WebSocket-Accept"):
            return self.sendHttpBadRequest("HTTP Sec-WebSocket-Accept header missing")
         else:
            magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            sha1 = hashlib.sha1()
            sha1.update(self.websocket_key + magic)
            sec_websocket_accept = base64.b64encode(sha1.digest())

            if self.http_headers["Sec-WebSocket-Accept"] != sec_websocket_accept:
               pass

         log.msg(sec_websocket_accept)

         ## move into OPEN state
         ##
         self.state = WebSocketProtocol.STATE_OPEN
         self.current_frame = None
         self.msg_payload = []
         self.msg_type = None

         ## fire handler on derived class
         ##
         self.onOpen()

         ## process rest, if any
         ##
         if len(self.data) > 0:
            self.dataReceived(None)



class WebSocketClient(protocol.ClientFactory):
   """
   Client factory for WebSockets.
   """

   protocol = WebSocketClientConnection

   def __init__(self, debug = False):
      self.debug = debug
      random.seed()

   def clientConnectionFailed(self, connector, reason):
      print "Connection failed - goodbye!"
      reactor.stop()

   def clientConnectionLost(self, connector, reason):
      print "Connection lost - goodbye!"
      reactor.stop()
