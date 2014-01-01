*****************
WebSocket Servers
*****************

The classes

 * :class:`autobahn.twisted.websocket.WebSocketServerProtocol`
 * :class:`autobahn.twisted.websocket.WebSocketServerFactory`

are the base classes you derive from to implement Twisted-based WebSocket servers.

The classes

 * :class:`autobahn.asyncio.websocket.WebSocketServerProtocol`
 * :class:`autobahn.asyncio.websocket.WebSocketServerFactory`

are the base classes you derive from to implement Asyncio-based WebSocket servers.



WebSocket Server Protocol
=========================

Both Twisted and Asyncio server protocols share the following functionality.

.. autoclass:: autobahn.websocket.protocol.WebSocketServerProtocol
   :show-inheritance:
   :members: onConnect

.. autoclass:: autobahn.websocket.protocol.ConnectionRequest
   :members: __init__


Twisted WebSocket Server Protocol
---------------------------------

To create a Twisted-based WebSocket server, subclass the following protocol class.

.. autoclass:: autobahn.twisted.websocket.WebSocketServerProtocol
   :show-inheritance:


Asyncio WebSocket Server Protocol
---------------------------------

To create an Asyncio-based WebSocket server, subclass the following protocol class.

.. autoclass:: autobahn.asyncio.websocket.WebSocketServerProtocol
   :show-inheritance:



WebSocket Server Factory
========================

Both Twisted and Asyncio server factories share the following functionality.

.. autoclass:: autobahn.websocket.protocol.WebSocketServerFactory
   :show-inheritance:
   :members: protocol,
             isServer,
             __init__,
             setSessionParameters,
             setProtocolOptions,
             resetProtocolOptions,
             getConnectionCount


Twisted WebSocket Server Factory
--------------------------------

To create a Twisted-based WebSocket server, use the following factory class.

.. autoclass:: autobahn.twisted.websocket.WebSocketServerFactory
   :show-inheritance:
   :members: __init__


Asyncio WebSocket Server Factory
--------------------------------

To create an Asyncio-based WebSocket server, use the following factory class.

.. autoclass:: autobahn.asyncio.websocket.WebSocketServerFactory
   :show-inheritance:
   :members: __init__
