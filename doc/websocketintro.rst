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

The message-based API is implemented in the following methods and callbacks

  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onOpen`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendMessage`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessage`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendClose`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onClose`


Prepared Messages
-----------------

In case you want to send a single WebSocket message to multiple peers, AutobahnPython provides an optimized way of sending using

  * :func:`autobahn.websocket.protocol.WebSocketFactory.prepareMessage`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendPreparedMessage`


Handshake Hooks
---------------

AutobahnPython allows you to hook into the initial WebSocket opening handshake (e.g. for handling HTTP cookies, subprotocols, etc):

  * :func:`autobahn.websocket.protocol.WebSocketServerProtocol.onConnect`
  * :func:`autobahn.websocket.protocol.WebSocketClientProtocol.onConnect`


Ping/Pong Processing
--------------------

The basic API also allows for explicit processing of WebSocket Pings and Pongs:

  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onPing`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onPong`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendPing`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendPong`

Note that explicit processing of Pings/Pongs is unnecessary normally - AutobahnPython will do the right thing under the hood.


Interface Definition
--------------------

The basic API has the following interface definition:

.. autoclass:: autobahn.websocket.interfaces.IWebSocketChannel
   :members:



Advanced WebSocket
==================

A WebSockets message consists of a potentially unlimited number of
fragments ("message frames"), each of which can have a payload between `0`
and `2^63` octets.

The implementation of the basic API is message-based, and thus has to buffer
all data received for a message frame, and buffer all frames received for
a message, and only when the message finally ends, flattens all buffered
data and fires :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessage`.

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

API for frame-based processing is implemented in:

  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageBegin`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageFrame`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageEnd`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.beginMessage`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendMessageFrame`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.endMessage`

and has the following definition:

.. autoclass:: autobahn.websocket.interfaces.IWebSocketChannelFrameApi
   :members:


Streaming API
-------------

API for streaming processing is implemented in:

  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageBegin`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageFrameBegin`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageFrameData`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageFrameEnd`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.onMessageEnd`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.beginMessage`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.beginMessageFrame`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.sendMessageFrameData`
  * :func:`autobahn.websocket.protocol.WebSocketProtocol.endMessage`

and has the following definition:

.. autoclass:: autobahn.websocket.interfaces.IWebSocketChannelStreamingApi
   :members:
