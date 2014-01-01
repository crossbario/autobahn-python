Introduction
============

The class :class:`autobahn.websocket.protocol.WebSocketProtocol` implements the
WebSocket protocol.

Though you will use methods and override callbacks from this class, you must
implement your clients/servers by deriving from the classes
:class:`autobahn.websocket.protocol.WebSocketClientProtocol` and
:class:`autobahn.websocket.protocol.WebSocketServerProtocol`.


Class Diagrams
--------------


* :class:`autobahn.websocket.protocol.WebSocketProtocol`
* :class:`autobahn.websocket.protocol.WebSocketClientProtocol`
* :class:`autobahn.websocket.protocol.WebSocketServerProtocol`
* :class:`autobahn.wamp.WampClientProtocol`
* :class:`autobahn.wamp.WampServerProtocol`

.. image:: protocolclasses.png


* :class:`autobahn.websocket.protocol.WebSocketClientFactory`
* :class:`autobahn.websocket.protocol.WebSocketServerFactory`
* :class:`autobahn.wamp.WampClientFactory`
* :class:`autobahn.wamp.WampServerFactory`

.. image:: factoryclasses.png


Basic API
---------

Most of the time, the basic API offered by *AutobahnPython*
will be the one you want to use. It is easy to use and gets out of your way.

The basic API is the one to use, unless you have specific needs (frame-based
processing or streaming), in which case Autobahn provides an advanced
API (see below).

The basic API consists of the following methods and callbacks

  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onOpen`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessage`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onClose`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendMessage`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendClose`


Advanced API
------------

A WebSockets message consists of a potentially unlimited number of
fragments ("message frames"), each of which can have a payload between 0
and 2^63 octets.

The implementation of the basic API is message-based, and thus has to buffer
all data received for a message frame, and buffer all frames received for
a message, and only when the message finally ends, flattens all buffered
data and fires :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessage`.

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

API for prepared message processing:
  * :func:`autobahn.websocket.protocol.WebSocketFactory.prepareMessage`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendPreparedMessage`

API for frame-based processing:

  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageBegin`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageFrame`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageEnd`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.beginMessage`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendMessageFrame`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.endMessage`

API for streaming processing:

  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageBegin`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageFrameBegin`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageFrameData`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageFrameEnd`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageEnd`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.beginMessage`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.beginMessageFrame`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendMessageFrameData`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.endMessage`

The advanced API for frame-based/streaming processing of WebSockets
messages also provides access to extension points in the WebSockets
protocol (you also normally won't use) - namely "reserved bits" and
"reserved opcodes".

Additionally, the advanced API provides methods and callbacks to do
your own processing of WebSockets Pings and Pongs. Normally, it is
unnecessary to do that, Autobahn will do the right thing under the hood.
Anyway, if you want, you can do.

API for explicit Ping/Pong processing:

  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onPing`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onPong`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendPing`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendPong`
