Server
======

The classes :class:`autobahn.websocket.WebSocketServerProtocol` and
:class:`autobahn.websocket.WebSocketServerFactory` are the base classes
you derive from to implement WebSocket servers.


Factory
-------

To create your actual server, you need a factory with the protocol attribute
set to your protocol.

You may either use :class:`autobahn.websocket.WebSocketServerFactory` directly
and without modification or you can derive from that class when you want to
extend it's behavior i.e. with state that is available for all client connections.


.. autoclass:: autobahn.websocket.WebSocketServerFactory
   :members: protocol,
             __init__,
             setSessionParameters,
             setProtocolOptions,
             resetProtocolOptions,
             getConnectionCount,
             startFactory,
             stopFactory


Protocol
--------

Usually, you implement your WebSocket server by creating a protocol that
derives from :class:`autobahn.websocket.WebSocketServerProtocol`.

This class in turn derives from :class:`autobahn.websocket.WebSocketProtocol`,
which is where you find all the callbacks and methods.


.. autoclass:: autobahn.websocket.WebSocketServerProtocol
   :members: onConnect,
             connectionMade,
             connectionLost
