WebSockets Protocol
===================

Introduction
------------

The class :class:`autobahn.websocket.WebSocketProtocol` implements the core
WebSockets protocol.

Though you will use methods and override callbacks from this class, you must
implement your clients/servers by deriving from the classes
:class:`autobahn.websocket.WebSocketClientProtocol` and
:class:`autobahn.websocket.WebSocketServerProtocol`.

Basic API
---------

Most of the time, the basic API offered by Autobahn WebSockets for Python
will be the one you want to use. It is easy to use and gets out of your way.

The basic API is the one to use, unless you have specific needs (frame-based
processing or streaming), in which case Autobahn provides an advanced
API (see below).

The basic API consists of the following methods and callbacks

  * :func:`autobahn.websocket.WebSocketProtocol.onOpen`
  * :func:`autobahn.websocket.WebSocketProtocol.onMessage`
  * :func:`autobahn.websocket.WebSocketProtocol.onClose`
  * :func:`autobahn.websocket.WebSocketProtocol.sendMessage`
  * :func:`autobahn.websocket.WebSocketProtocol.sendClose`


Advanced API
------------

A WebSockets message consists of a potentially unlimited number of
fragments ("message frames"), each of which can have a payload between 0
and 2^63 octets.

The implementation of the basic API is message-based, and thus has to buffer
all data received for a message frame, and buffer all frames received for
a message, and only when the message finally ends, flattens all buffered
data and fires :func:`autobahn.websocket.WebSocketProtocol.onMessage`.

Usually, when you produce/consume messages of small to limited size (like
say <256k), this is absolutely sufficient and convenient.

However, when you want to process messages consisting of a large number
of message fragments, or you want to process messages that contain message
fragments of large size, this buffering will result in excessive memory
consumption.

In these cases, you might want to process message fragments on a per
frame basis, or you may even want to process data incoming, as it arrives.

The advanced API provides you all the necessary methods and callbacks to
do WebSockets using frame-based processing or even completely streaming
processing - both sending and receiving.

In the Autobahn source repository, under "demo/streaming/" you can find
a demonstration of use. The example there implements a WebSockets client
which sends random bytes to a WebSockets server which computes SHA-256
for received data. Three possible implementations are shown: a message-
based, a frame-based and a streaming.

API for frame-based processing:

  * :func:`autobahn.websocket.WebSocketProtocol.onMessageBegin`
  * :func:`autobahn.websocket.WebSocketProtocol.onMessageFrame`
  * :func:`autobahn.websocket.WebSocketProtocol.onMessageEnd`
  * :func:`autobahn.websocket.WebSocketProtocol.beginMessage`
  * :func:`autobahn.websocket.WebSocketProtocol.sendMessageFrame`
  * :func:`autobahn.websocket.WebSocketProtocol.endMessage`

API for streaming processing:

  * :func:`autobahn.websocket.WebSocketProtocol.onMessageBegin`
  * :func:`autobahn.websocket.WebSocketProtocol.onMessageFrameBegin`
  * :func:`autobahn.websocket.WebSocketProtocol.onMessageFrameData`
  * :func:`autobahn.websocket.WebSocketProtocol.onMessageFrameEnd`
  * :func:`autobahn.websocket.WebSocketProtocol.onMessageEnd`
  * :func:`autobahn.websocket.WebSocketProtocol.beginMessage`
  * :func:`autobahn.websocket.WebSocketProtocol.beginMessageFrame`
  * :func:`autobahn.websocket.WebSocketProtocol.sendMessageFrameData`
  * :func:`autobahn.websocket.WebSocketProtocol.endMessage`

The advanced API for frame-based/streaming processing of WebSockets
messages also provides access to extension points in the WebSockets
protocol (you also normally won't use) - namely "reserved bits" and
"reserved opcodes".

Additionally, the advanced API provides methods and callbacks to do
your own processing of WebSockets Pings and Pongs. Normally, it is
unnecessary to do that, Autobahn will do the right thing under the hood.
Anyway, if you want, you can do.

API for explicit Ping/Pong processing:

  * :func:`autobahn.websocket.WebSocketProtocol.onPing`
  * :func:`autobahn.websocket.WebSocketProtocol.onPong`
  * :func:`autobahn.websocket.WebSocketProtocol.sendPing`
  * :func:`autobahn.websocket.WebSocketProtocol.sendPong`


Classes
-------

.. autoclass:: autobahn.websocket.WebSocketProtocol
   :members: MESSAGE_TYPE_TEXT,
             MESSAGE_TYPE_BINARY,
             CLOSE_STATUS_CODE_NORMAL,
             CLOSE_STATUS_CODE_GOING_AWAY,
             CLOSE_STATUS_CODE_PROTOCOL_ERROR,
             CLOSE_STATUS_CODE_PAYLOAD_NOT_ACCEPTED,
             CLOSE_STATUS_CODE_FRAME_TOO_LARGE,
             CLOSE_STATUS_CODE_NULL,
             CLOSE_STATUS_CODE_CONNECTION_LOST,
             CLOSE_STATUS_CODE_TEXT_FRAME_NOT_UTF8,
             onOpen,
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
             sendMessage
