**********************
WebSocket Introduction
**********************

Basic WebSocket
===============

**AutobahnPython** provides a Message-based API to WebSocket plus auxiliary methods and callbacks.

The message-based API closely resembles the API of WebSocket available to JavaScript in browsers.

Most of the time, this API is what you should use, unless you have specific needs (frame-based / streaming processing, see below).



Message-based Processing
------------------------

The interface :class:`autobahn.websocket.interfaces.IWebSocketChannel` defines the API for message-based WebSocket processing and consists of these callbacks and methods

The message-based API is implemented in the following methods and callbacks

  * :func:`autobahn.websocket.interfaces.IWebSocketChannel.onOpen`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendMessage`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessage`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendClose`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannel.onClose`


Prepared Messages
-----------------

In case you want to send a single WebSocket message to multiple peers, AutobahnPython provides an optimized way of sending using

  * :func:`autobahn.websocket.protocol.WebSocketFactory.prepareMessage`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendPreparedMessage`


Handshake Hooks
---------------

AutobahnPython allows you to hook into the initial WebSocket opening handshake (e.g. for handling HTTP cookies, subprotocols, etc):

  * :func:`autobahn.websocket.protocol.WebSocketServerProtocol.onConnect`
  * :func:`autobahn.websocket.protocol.WebSocketClientProtocol.onConnect`


Ping/Pong Processing
--------------------

The basic API also allows for explicit processing of WebSocket Pings and Pongs:

  * :func:`autobahn.websocket.interfaces.IWebSocketChannel.onPing`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannel.onPong`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendPing`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannel.sendPong`

Note that explicit processing of Pings/Pongs is unnecessary normally - AutobahnPython will do the right thing under the hood.


Implementation
--------------

The basic API is implemented in the following classes

* :class:`autobahn.websocket.protocol.WebSocketProtocol`
* :class:`autobahn.websocket.protocol.WebSocketServerProtocol`
* :class:`autobahn.websocket.protocol.WebSocketClientProtocol`
* :class:`autobahn.twisted.websocket.WebSocketServerProtocol`
* :class:`autobahn.twisted.websocket.WebSocketClientProtocol`
* :class:`autobahn.asyncio.websocket.WebSocketServerProtocol`
* :class:`autobahn.asyncio.websocket.WebSocketClientProtocol`



Advanced WebSocket
==================

A WebSockets message consists of a potentially unlimited number of
fragments ("message frames"), each of which can have a payload between `0`
and `2^63` octets.

The implementation of the basic API is message-based, and thus has to buffer
all data received for a message frame, and buffer all frames received for
a message, and only when the message finally ends, flattens all buffered
data and fires :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessage`.

Usually, when you produce/consume messages of small to limited size (like
say `<256k`), this is absolutely sufficient and convenient.

However, when you want to process messages consisting of a large number
of message fragments, or you want to process messages that contain message
fragments of large size, this buffering will result in excessive memory
consumption.

In these cases, you might want to process message fragments on a per
frame basis, or you may even want to process data incoming, as it arrives.

The advanced API provides you all the necessary methods and callbacks to
do WebSockets using frame-based processing or even completely streaming
processing - both sending and receiving.



Frame-based API
---------------

The interface :class:`autobahn.websocket.interfaces.IWebSocketChannelFrameApi` defines the API for frame-based WebSocket processing and consists of these callbacks and methods

  * :func:`autobahn.websocket.interfaces.IWebSocketChannelFrameApi.onMessageBegin`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelFrameApi.onMessageFrame`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelFrameApi.onMessageEnd`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelFrameApi.beginMessage`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelFrameApi.sendMessageFrame`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelFrameApi.endMessage`

is implemented in the following classes

* :class:`autobahn.websocket.protocol.WebSocketProtocol`
* :class:`autobahn.websocket.protocol.WebSocketServerProtocol`
* :class:`autobahn.websocket.protocol.WebSocketClientProtocol`
* :class:`autobahn.twisted.websocket.WebSocketServerProtocol`
* :class:`autobahn.twisted.websocket.WebSocketClientProtocol`
* :class:`autobahn.asyncio.websocket.WebSocketServerProtocol`
* :class:`autobahn.asyncio.websocket.WebSocketClientProtocol`



Streaming API
-------------

The interface :class:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi` defines the API for streaming WebSocket processing and consists of these callbacks and methods

  * :func:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi.onMessageBegin`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi.onMessageFrameBegin`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi.onMessageFrameData`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi.onMessageFrameEnd`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi.onMessageEnd`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi.beginMessage`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi.beginMessageFrame`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi.sendMessageFrameData`
  * :func:`autobahn.websocket.interfaces.IWebSocketChannelStreamingApi.endMessage`

is implemented in the following classes

* :class:`autobahn.websocket.protocol.WebSocketProtocol`
* :class:`autobahn.websocket.protocol.WebSocketServerProtocol`
* :class:`autobahn.websocket.protocol.WebSocketClientProtocol`
* :class:`autobahn.twisted.websocket.WebSocketServerProtocol`
* :class:`autobahn.twisted.websocket.WebSocketClientProtocol`
* :class:`autobahn.asyncio.websocket.WebSocketServerProtocol`
* :class:`autobahn.asyncio.websocket.WebSocketClientProtocol`
