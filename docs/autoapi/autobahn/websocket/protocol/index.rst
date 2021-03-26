:mod:`autobahn.websocket.protocol`
==================================

.. py:module:: autobahn.websocket.protocol


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.websocket.protocol.WebSocketProtocol
   autobahn.websocket.protocol.WebSocketFactory
   autobahn.websocket.protocol.WebSocketServerProtocol
   autobahn.websocket.protocol.WebSocketServerFactory
   autobahn.websocket.protocol.WebSocketClientProtocol
   autobahn.websocket.protocol.WebSocketClientFactory



.. class:: WebSocketProtocol


   Bases: :class:`autobahn.util.ObservableMixin`

   Protocol base class for WebSocket.

   This class implements:

     * :class:`autobahn.websocket.interfaces.IWebSocketChannel`
     * :class:`autobahn.websocket.interfaces.IWebSocketChannelFrameApi`
     * :class:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi`

   .. attribute:: peer
      :annotation: = <never connected>

      

   .. attribute:: SUPPORTED_SPEC_VERSIONS
      :annotation: = [10, 11, 12, 13, 14, 15, 16, 17, 18]

      WebSocket protocol spec (draft) versions supported by this implementation.
      Use of version 18 indicates RFC6455. Use of versions < 18 indicate actual
      draft spec versions (Hybi-Drafts).


   .. attribute:: SUPPORTED_PROTOCOL_VERSIONS
      :annotation: = [8, 13]

      WebSocket protocol versions supported by this implementation.


   .. attribute:: SPEC_TO_PROTOCOL_VERSION
      

      Mapping from protocol spec (draft) version to protocol version.


   .. attribute:: PROTOCOL_TO_SPEC_VERSION
      

      Mapping from protocol version to the latest protocol spec (draft) version
      using that protocol version.


   .. attribute:: DEFAULT_SPEC_VERSION
      :annotation: = 18

      Default WebSocket protocol spec version this implementation speaks: final
      RFC6455.


   .. attribute:: _WS_MAGIC
      :annotation: = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

      Protocol defined magic used during WebSocket handshake (used in Hybi-drafts
      and final RFC6455.


   .. attribute:: _QUEUED_WRITE_DELAY
      :annotation: = 1e-05

      For synched/chopped writes, this is the reactor reentry delay in seconds.


   .. attribute:: MESSAGE_TYPE_TEXT
      :annotation: = 1

      WebSocket text message type (UTF-8 payload).


   .. attribute:: MESSAGE_TYPE_BINARY
      :annotation: = 2

      WebSocket binary message type (arbitrary binary payload).


   .. attribute:: STATE_CLOSED
      :annotation: = 0

      

   .. attribute:: STATE_CONNECTING
      :annotation: = 1

      

   .. attribute:: STATE_CLOSING
      :annotation: = 2

      

   .. attribute:: STATE_OPEN
      :annotation: = 3

      

   .. attribute:: STATE_PROXY_CONNECTING
      :annotation: = 4

      

   .. attribute:: SEND_STATE_GROUND
      :annotation: = 0

      

   .. attribute:: SEND_STATE_MESSAGE_BEGIN
      :annotation: = 1

      

   .. attribute:: SEND_STATE_INSIDE_MESSAGE
      :annotation: = 2

      

   .. attribute:: SEND_STATE_INSIDE_MESSAGE_FRAME
      :annotation: = 3

      

   .. attribute:: CLOSE_STATUS_CODE_NORMAL
      :annotation: = 1000

      Normal close of connection.


   .. attribute:: CLOSE_STATUS_CODE_GOING_AWAY
      :annotation: = 1001

      Going away.


   .. attribute:: CLOSE_STATUS_CODE_PROTOCOL_ERROR
      :annotation: = 1002

      Protocol error.


   .. attribute:: CLOSE_STATUS_CODE_UNSUPPORTED_DATA
      :annotation: = 1003

      Unsupported data.


   .. attribute:: CLOSE_STATUS_CODE_RESERVED1
      :annotation: = 1004

      RESERVED


   .. attribute:: CLOSE_STATUS_CODE_NULL
      :annotation: = 1005

      No status received. (MUST NOT be used as status code when sending a close).


   .. attribute:: CLOSE_STATUS_CODE_ABNORMAL_CLOSE
      :annotation: = 1006

      Abnormal close of connection. (MUST NOT be used as status code when sending a close).


   .. attribute:: CLOSE_STATUS_CODE_INVALID_PAYLOAD
      :annotation: = 1007

      Invalid frame payload data.


   .. attribute:: CLOSE_STATUS_CODE_POLICY_VIOLATION
      :annotation: = 1008

      Policy violation.


   .. attribute:: CLOSE_STATUS_CODE_MESSAGE_TOO_BIG
      :annotation: = 1009

      Message too big.


   .. attribute:: CLOSE_STATUS_CODE_MANDATORY_EXTENSION
      :annotation: = 1010

      Mandatory extension.


   .. attribute:: CLOSE_STATUS_CODE_INTERNAL_ERROR
      :annotation: = 1011

      The peer encountered an unexpected condition or internal error.


   .. attribute:: CLOSE_STATUS_CODE_SERVICE_RESTART
      :annotation: = 1012

      Service restart.


   .. attribute:: CLOSE_STATUS_CODE_TRY_AGAIN_LATER
      :annotation: = 1013

      Try again later.


   .. attribute:: CLOSE_STATUS_CODE_UNASSIGNED1
      :annotation: = 1014

      Unassiged.


   .. attribute:: CLOSE_STATUS_CODE_TLS_HANDSHAKE_FAILED
      :annotation: = 1015

      TLS handshake failed, i.e. server certificate could not be verified. (MUST NOT be used as status code when sending a close).


   .. attribute:: CLOSE_STATUS_CODES_ALLOWED
      

      Status codes allowed to send in close.


   .. attribute:: CONFIG_ATTRS_COMMON
      :annotation: = ['logOctets', 'logFrames', 'trackTimings', 'utf8validateIncoming', 'applyMask', 'maxFramePayloadSize', 'maxMessagePayloadSize', 'autoFragmentSize', 'failByDrop', 'echoCloseCodeReason', 'openHandshakeTimeout', 'closeHandshakeTimeout', 'tcpNoDelay', 'autoPingInterval', 'autoPingTimeout', 'autoPingSize']

      Configuration attributes common to servers and clients.


   .. attribute:: CONFIG_ATTRS_SERVER
      :annotation: = ['versions', 'webStatus', 'requireMaskedClientFrames', 'maskServerFrames', 'perMessageCompressionAccept', 'serveFlashSocketPolicy', 'flashSocketPolicy', 'allowedOrigins', 'allowedOriginsPatterns', 'allowNullOrigin', 'maxConnections', 'trustXForwardedFor']

      Configuration attributes specific to servers.


   .. attribute:: CONFIG_ATTRS_CLIENT
      :annotation: = ['version', 'acceptMaskedServerFrames', 'maskClientFrames', 'serverConnectionDropTimeout', 'perMessageCompressionOffers', 'perMessageCompressionAccept']

      Configuration attributes specific to clients.


   .. method:: onOpen(self)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onOpen`


   .. method:: onMessageBegin(self, isBinary)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageBegin`


   .. method:: onMessageFrameBegin(self, length)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageFrameBegin`


   .. method:: onMessageFrameData(self, payload)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageFrameData`


   .. method:: onMessageFrameEnd(self)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageFrameEnd`


   .. method:: onMessageFrame(self, payload)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageFrame`


   .. method:: onMessageEnd(self)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessageEnd`


   .. method:: onMessage(self, payload, isBinary)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessage`


   .. method:: onPing(self, payload)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onPing`


   .. method:: onPong(self, payload)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onPong`


   .. method:: onClose(self, wasClean, code, reason)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.onClose`


   .. method:: onCloseFrame(self, code, reasonRaw)

      Callback when a Close frame was received. The default implementation answers by
      sending a Close when no Close was sent before. Otherwise it drops
      the TCP connection either immediately (when we are a server) or after a timeout
      (when we are a client and expect the server to drop the TCP).

      :param code: Close status code, if there was one (:class:`WebSocketProtocol`.CLOSE_STATUS_CODE_*).
      :type code: int
      :param reasonRaw: Close reason (when present, a status code MUST have been also be present).
      :type reasonRaw: bytes


   .. method:: onServerConnectionDropTimeout(self)

      We (a client) expected the peer (a server) to drop the connection,
      but it didn't (in time self.serverConnectionDropTimeout).
      So we drop the connection, but set self.wasClean = False.


   .. method:: onOpenHandshakeTimeout(self)

      We expected the peer to complete the opening handshake with to us.
      It didn't do so (in time self.openHandshakeTimeout).
      So we drop the connection, but set self.wasClean = False.


   .. method:: onCloseHandshakeTimeout(self)

      We expected the peer to respond to us initiating a close handshake. It didn't
      respond (in time self.closeHandshakeTimeout) with a close response frame though.
      So we drop the connection, but set self.wasClean = False.


   .. method:: onAutoPingTimeout(self)

      When doing automatic ping/pongs to detect broken connection, the peer
      did not reply in time to our ping. We drop the connection.


   .. method:: dropConnection(self, abort=False)

      Drop the underlying TCP connection.


   .. method:: _max_message_size_exceeded(self, msg_size, max_msg_size, reason)


   .. method:: _fail_connection(self, code=CLOSE_STATUS_CODE_GOING_AWAY, reason='going away')

      Fails the WebSocket connection.


   .. method:: _protocol_violation(self, reason)

      Fired when a WebSocket protocol violation/error occurs.

      :param reason: Protocol violation that was encountered (human readable).
      :type reason: str

      :returns: bool -- True, when any further processing should be discontinued.


   .. method:: _invalid_payload(self, reason)

      Fired when invalid payload is encountered. Currently, this only happens
      for text message when payload is invalid UTF-8 or close frames with
      close reason that is invalid UTF-8.

      :param reason: What was invalid for the payload (human readable).
      :type reason: str

      :returns: bool -- True, when any further processing should be discontinued.


   .. method:: setTrackTimings(self, enable)

      Enable/disable tracking of detailed timings.

      :param enable: Turn time tracking on/off.
      :type enable: bool


   .. method:: _connectionMade(self)

      This is called by network framework when a new TCP connection has been established
      and handed over to a Protocol instance (an instance of this class).


   .. method:: _connectionLost(self, reason)

      This is called by network framework when a transport connection was
      lost.


   .. method:: logRxOctets(self, data)

      Hook fired right after raw octets have been received, but only when
      self.logOctets == True.


   .. method:: logTxOctets(self, data, sync)

      Hook fired right after raw octets have been sent, but only when
      self.logOctets == True.


   .. method:: logRxFrame(self, frameHeader, payload)

      Hook fired right after WebSocket frame has been received and decoded,
      but only when self.logFrames == True.


   .. method:: logTxFrame(self, frameHeader, payload, repeatLength, chopsize, sync)

      Hook fired right after WebSocket frame has been encoded and sent, but
      only when self.logFrames == True.


   .. method:: _dataReceived(self, data)

      This is called by network framework upon receiving data on transport
      connection.


   .. method:: consumeData(self)

      Consume buffered (incoming) data.


   .. method:: processProxyConnect(self)

      Process proxy connect.


   .. method:: processHandshake(self)

      Process WebSocket handshake.


   .. method:: _trigger(self)

      Trigger sending stuff from send queue (which is only used for
      chopped/synched writes).


   .. method:: _send(self)

      Send out stuff from send queue. For details how this works, see
      test/trickling in the repo.


   .. method:: sendData(self, data, sync=False, chopsize=None)

      Wrapper for self.transport.write which allows to give a chopsize.
      When asked to chop up writing to TCP stream, we write only chopsize
      octets and then give up control to select() in underlying reactor so
      that bytes get onto wire immediately. Note that this is different from
      and unrelated to WebSocket data message fragmentation. Note that this
      is also different from the TcpNoDelay option which can be set on the
      socket.


   .. method:: sendPreparedMessage(self, preparedMsg)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendPreparedMessage`


   .. method:: processData(self)

      After WebSocket handshake has been completed, this procedure will do
      all subsequent processing of incoming bytes.


   .. method:: onFrameBegin(self)

      Begin of receive new frame.


   .. method:: onFrameData(self, payload)

      New data received within frame.


   .. method:: onFrameEnd(self)

      End of frame received.


   .. method:: processControlFrame(self)

      Process a completely received control frame.


   .. method:: sendFrame(self, opcode, payload=b'', fin=True, rsv=0, mask=None, payload_len=None, chopsize=None, sync=False)

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


   .. method:: sendPing(self, payload=None)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendPing`


   .. method:: _sendAutoPing(self)


   .. method:: _cancelAutoPingTimeoutCall(self)

      When data is received from client, use it in leu of timely PONG response - cancel pending timeout call
      that will drop connection


   .. method:: sendPong(self, payload=None)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendPong`


   .. method:: sendCloseFrame(self, code=None, reasonUtf8=None, isReply=False)

      Send a close frame and update protocol state. Note, that this is
      an internal method which deliberately allows not send close
      frame with invalid payload.


   .. method:: sendClose(self, code=None, reason=None)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendClose`


   .. method:: beginMessage(self, isBinary=False, doNotCompress=False)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.beginMessage`


   .. method:: beginMessageFrame(self, length)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.beginMessageFrame`


   .. method:: sendMessageFrameData(self, payload, sync=False)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendMessageFrameData`


   .. method:: endMessage(self)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.endMessage`


   .. method:: sendMessageFrame(self, payload, sync=False)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendMessageFrame`


   .. method:: sendMessage(self, payload, isBinary=False, fragmentSize=None, sync=False, doNotCompress=False)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendMessage`


   .. method:: _parseExtensionsHeader(self, header, removeQuotes=True)

      Parse the Sec-WebSocket-Extensions header.



.. class:: WebSocketFactory

   Bases: :class:`object`

   Mixin for
   :class:`autobahn.websocket.protocol.WebSocketClientFactory` and
   :class:`autobahn.websocket.protocol.WebSocketServerFactory`.

   .. method:: prepareMessage(self, payload, isBinary=False, doNotCompress=False)

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



.. class:: WebSocketServerProtocol


   Bases: :class:`autobahn.websocket.protocol.WebSocketProtocol`

   Protocol base class for WebSocket servers.

   .. attribute:: log
      

      

   .. attribute:: CONFIG_ATTRS
      

      

   .. method:: onConnect(self, request)

      Callback fired during WebSocket opening handshake when new WebSocket client
      connection is about to be established.

      When you want to accept the connection, return the accepted protocol
      from list of WebSocket (sub)protocols provided by client or `None` to
      speak no specific one or when the client protocol list was empty.

      You may also return a pair of `(protocol, headers)` to send additional
      HTTP headers, with `headers` being a dictionary of key-values.

      Throw :class:`autobahn.websocket.types.ConnectionDeny` when you don't want
      to accept the WebSocket connection request.

      :param request: WebSocket connection request information.
      :type request: instance of :class:`autobahn.websocket.protocol.ConnectionRequest`


   .. method:: _connectionMade(self)

      Called by network framework when new transport connection from client was
      accepted. Default implementation will prepare for initial WebSocket opening
      handshake. When overriding in derived class, make sure to call this base class
      implementation *before* your code.


   .. method:: _connectionLost(self, reason)

      Called by network framework when established transport connection from client
      was lost. Default implementation will tear down all state properly.
      When overriding in derived class, make sure to call this base class
      implementation *after* your code.


   .. method:: processProxyConnect(self)

      Process proxy connect.


   .. method:: processHandshake(self)

      Process WebSocket opening handshake request from client.


   .. method:: succeedHandshake(self, res)

      Callback after onConnect() returns successfully. Generates the response for the handshake.


   .. method:: failHandshake(self, reason, code=400, responseHeaders=None)

      During opening handshake the client request was invalid, we send a HTTP
      error response and then drop the connection.


   .. method:: sendHttpErrorResponse(self, code, reason, responseHeaders=None)

      Send out HTTP error response.


   .. method:: sendHtml(self, html)

      Send HTML page HTTP response.


   .. method:: sendRedirect(self, url)

      Send HTTP Redirect (303) response.


   .. method:: sendServerStatus(self, redirectUrl=None, redirectAfter=0)

      Used to send out server status/version upon receiving a HTTP/GET without
      upgrade to WebSocket header (and option serverStatus is True).



.. class:: WebSocketServerFactory(url=None, protocols=None, server='AutobahnPython/%s' % __version__, headers=None, externalPort=None)


   Bases: :class:`autobahn.websocket.protocol.WebSocketFactory`

   A protocol factory for WebSocket servers.

   Implements :func:`autobahn.websocket.interfaces.IWebSocketServerChannelFactory`

   .. attribute:: log
      

      

   .. attribute:: protocol
      

      The protocol to be spoken. Must be derived from :class:`autobahn.websocket.protocol.WebSocketServerProtocol`.


   .. attribute:: isServer
      :annotation: = True

      Flag indicating if this factory is client- or server-side.


   .. method:: setSessionParameters(self, url=None, protocols=None, server=None, headers=None, externalPort=None)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketServerChannelFactory.setSessionParameters`


   .. method:: resetProtocolOptions(self)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketServerChannelFactory.resetProtocolOptions`


   .. method:: setProtocolOptions(self, versions=None, webStatus=None, utf8validateIncoming=None, maskServerFrames=None, requireMaskedClientFrames=None, applyMask=None, maxFramePayloadSize=None, maxMessagePayloadSize=None, autoFragmentSize=None, failByDrop=None, echoCloseCodeReason=None, openHandshakeTimeout=None, closeHandshakeTimeout=None, tcpNoDelay=None, perMessageCompressionAccept=None, autoPingInterval=None, autoPingTimeout=None, autoPingSize=None, serveFlashSocketPolicy=None, flashSocketPolicy=None, allowedOrigins=None, allowNullOrigin=False, maxConnections=None, trustXForwardedFor=None)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketServerChannelFactory.setProtocolOptions`


   .. method:: getConnectionCount(self)

      Get number of currently connected clients.

      :returns: int -- Number of currently connected clients.



.. class:: WebSocketClientProtocol


   Bases: :class:`autobahn.websocket.protocol.WebSocketProtocol`

   Protocol base class for WebSocket clients.

   .. attribute:: log
      

      

   .. attribute:: CONFIG_ATTRS
      

      

   .. method:: onConnecting(self, transport_details)

      :param transport_details: a :class:`autobahn.websocket.types.TransportDetails`

      Callback fired after the connection is established, but before the
      handshake has started. This may return a
      :class:`autobahn.websocket.types.ConnectingRequest` instance
      (or a future which resolves to one) to control aspects of the
      handshake (or None for defaults)


   .. method:: onConnect(self, response)

      Callback fired directly after WebSocket opening handshake when new WebSocket server
      connection was established.

      :param response: WebSocket connection response information.
      :type response: instance of :class:`autobahn.websocket.protocol.ConnectionResponse`


   .. method:: _connectionMade(self)

      Called by network framework when new transport connection to server was established. Default
      implementation will start the initial WebSocket opening handshake (or proxy connect).
      When overriding in derived class, make sure to call this base class
      implementation _before_ your code.


   .. method:: _connectionLost(self, reason)

      Called by network framework when established transport connection to server was lost. Default
      implementation will tear down all state properly.
      When overriding in derived class, make sure to call this base class
      implementation _after_ your code.


   .. method:: startProxyConnect(self)

      Connect to explicit proxy.


   .. method:: processProxyConnect(self)

      Process HTTP/CONNECT response from server.


   .. method:: failProxyConnect(self, reason)

      During initial explicit proxy connect, the server response indicates some failure and we drop the
      connection.


   .. method:: startHandshake(self)

      Start WebSocket opening handshake.


   .. method:: _actuallyStartHandshake(self, request_options)

      Internal helper.

      Actually send the WebSocket opening handshake after receiving
      valid request options.


   .. method:: processHandshake(self)

      Process WebSocket opening handshake response from server.


   .. method:: failHandshake(self, reason)

      During opening handshake the server response is invalid and we drop the
      connection.



.. class:: WebSocketClientFactory(url=None, origin=None, protocols=None, useragent='AutobahnPython/%s' % __version__, headers=None, proxy=None)


   Bases: :class:`autobahn.websocket.protocol.WebSocketFactory`

   A protocol factory for WebSocket clients.

   Implements :func:`autobahn.websocket.interfaces.IWebSocketClientChannelFactory`

   .. attribute:: log
      

      

   .. attribute:: protocol
      

      The protocol to be spoken. Must be derived from :class:`autobahn.websocket.protocol.WebSocketClientProtocol`.


   .. attribute:: isServer
      :annotation: = False

      Flag indicating if this factory is client- or server-side.


   .. method:: setSessionParameters(self, url=None, origin=None, protocols=None, useragent=None, headers=None, proxy=None)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketClientChannelFactory.setSessionParameters`


   .. method:: resetProtocolOptions(self)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketClientChannelFactory.resetProtocolOptions`


   .. method:: setProtocolOptions(self, version=None, utf8validateIncoming=None, acceptMaskedServerFrames=None, maskClientFrames=None, applyMask=None, maxFramePayloadSize=None, maxMessagePayloadSize=None, autoFragmentSize=None, failByDrop=None, echoCloseCodeReason=None, serverConnectionDropTimeout=None, openHandshakeTimeout=None, closeHandshakeTimeout=None, tcpNoDelay=None, perMessageCompressionOffers=None, perMessageCompressionAccept=None, autoPingInterval=None, autoPingTimeout=None, autoPingSize=None)

      Implements :func:`autobahn.websocket.interfaces.IWebSocketClientChannelFactory.setProtocolOptions`



