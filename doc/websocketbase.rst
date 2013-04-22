Base
====

The class :class:`autobahn.websocket.WebSocketProtocol` implements the core
WebSockets protocol.

Though you will use methods and override callbacks from this class, you must
implement your clients/servers by deriving from the classes
:class:`autobahn.websocket.WebSocketClientProtocol` and
:class:`autobahn.websocket.WebSocketServerProtocol`.


Factory
-------

.. autoclass:: autobahn.websocket.WebSocketFactory
   :members: prepareMessage


Protocol
--------

The :class:`autobahn.websocket.WebSocketProtocol` is the core of Autobahn's
WebSocket implementation. It implements a Twisted protocol which speaks WebSockets.


.. autoclass:: autobahn.websocket.WebSocketProtocol
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
             registerProducer,
             SUPPORTED_SPEC_VERSIONS,
             SUPPORTED_PROTOCOL_VERSIONS,
             SPEC_TO_PROTOCOL_VERSION,
             PROTOCOL_TO_SPEC_VERSION,
             DEFAULT_SPEC_VERSION,
             DEFAULT_ALLOW_HIXIE76,
             MESSAGE_TYPE_TEXT,
             MESSAGE_TYPE_BINARY,
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
