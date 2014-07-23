*********
WebSocket
*********

The classes

 * :class:`autobahn.websocket.protocol.WebSocketProtocol`
 * :class:`autobahn.websocket.protocol.WebSocketFactory`

implement the core WebSocket protocol.

Though you will use methods and override callbacks from above classes, you implement your WebSocket clients and servers by deriving from the following classes.

Twisted-based clients and servers:

* :class:`autobahn.twisted.websocket.WebSocketClientProtocol`
* :class:`autobahn.twisted.websocket.WebSocketClientFactory`
* :class:`autobahn.twisted.websocket.WebSocketServerProtocol`
* :class:`autobahn.twisted.websocket.WebSocketServerFactory`

Asyncio-based clients and servers:

* :class:`autobahn.asyncio.websocket.WebSocketClientProtocol`
* :class:`autobahn.asyncio.websocket.WebSocketClientFactory`
* :class:`autobahn.asyncio.websocket.WebSocketServerProtocol`
* :class:`autobahn.asyncio.websocket.WebSocketServerFactory`


WebSocket Protocol
==================

Both WebSocket client and server protocols share the following functionality.

.. autoclass:: autobahn.websocket.protocol.WebSocketProtocol
   :members: onOpen,
             onClose,
             onPing,
             onPong,
             onMessageBegin,
             onMessageFrameBegin,
             onMessageFrameData,
             onMessageFrameEnd,
             onMessageFrame,
             onMessageEnd,
             onMessage,
             sendClose,
             sendPing,
             sendPong,
             beginMessage,
             beginMessageFrame,
             sendMessageFrameData,
             endMessage,
             sendMessageFrame,
             sendMessage,
             sendPreparedMessage,
             SUPPORTED_SPEC_VERSIONS,
             SUPPORTED_PROTOCOL_VERSIONS,
             SPEC_TO_PROTOCOL_VERSION,
             PROTOCOL_TO_SPEC_VERSION,
             DEFAULT_SPEC_VERSION,
             DEFAULT_ALLOW_HIXIE76,
             CLOSE_STATUS_CODE_NORMAL,
             CLOSE_STATUS_CODE_GOING_AWAY,
             CLOSE_STATUS_CODE_PROTOCOL_ERROR,
             CLOSE_STATUS_CODE_UNSUPPORTED_DATA,
             CLOSE_STATUS_CODE_NULL,
             CLOSE_STATUS_CODE_ABNORMAL_CLOSE,
             CLOSE_STATUS_CODE_INVALID_PAYLOAD,
             CLOSE_STATUS_CODE_POLICY_VIOLATION,
             CLOSE_STATUS_CODE_MESSAGE_TOO_BIG,
             CLOSE_STATUS_CODE_MANDATORY_EXTENSION



WebSocket Factory
=================

Both WebSocket client and server factories share the following functionality.

.. autoclass:: autobahn.websocket.protocol.WebSocketFactory
   :members: prepareMessage

.. autoclass:: autobahn.websocket.protocol.PreparedMessage
   :members: __init__
