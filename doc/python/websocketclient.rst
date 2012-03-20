Client
======

The classes :class:`autobahn.websocket.WebSocketClientProtocol` and
:class:`autobahn.websocket.WebSocketClientFactory` are the base classes
you derive from to implement WebSocket clients.


Factory
-------

To create your actual client, you need a factory with the protocol attribute
set to your protocol.

You may either use :class:`autobahn.websocket.WebSocketClientFactory` directly
and without modification or you can derive from that class when you want to
extend it's behavior i.e. with state that is available for all client connections.


.. autoclass:: autobahn.websocket.WebSocketClientFactory
   :members: protocol,
             __init__,
             setSessionParameters,
             setProtocolOptions,
             resetProtocolOptions,
             clientConnectionFailed,
             clientConnectionLost



Protocol
--------

Usually, you implement your WebSocket client by creating a protocol that
derives from :class:`autobahn.websocket.WebSocketClientProtocol`.

This class in turn derives from :class:`autobahn.websocket.WebSocketProtocol`,
which is where you find all the callbacks and methods.


.. autoclass:: autobahn.websocket.WebSocketClientProtocol
   :members: onConnect,
             connectionMade,
             connectionLost
