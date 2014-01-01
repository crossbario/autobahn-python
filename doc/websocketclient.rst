*****************
WebSocket Clients
*****************

The classes

 * :class:`autobahn.twisted.websocket.WebSocketClientProtocol`
 * :class:`autobahn.twisted.websocket.WebSocketClientFactory`

are the base classes you derive from to implement Twisted-based WebSocket clients.

The classes

 * :class:`autobahn.asyncio.websocket.WebSocketClientProtocol`
 * :class:`autobahn.asyncio.websocket.WebSocketClientFactory`

are the base classes you derive from to implement Asyncio-based WebSocket clients.



WebSocket Client Protocol
=========================

Both Twisted and Asyncio client protocols share the following functionality.

.. autoclass:: autobahn.websocket.protocol.WebSocketClientProtocol
   :show-inheritance:
   :members: onConnect

.. autoclass:: autobahn.websocket.protocol.ConnectionResponse
   :members: __init__


Twisted WebSocket Client Protocol
---------------------------------

To create a Twisted-based WebSocket client, subclass the following protocol class.

.. autoclass:: autobahn.twisted.websocket.WebSocketClientProtocol
   :show-inheritance:


Asyncio WebSocket Client Protocol
---------------------------------

To create an Asyncio-based WebSocket client, subclass the following protocol class.

.. autoclass:: autobahn.asyncio.websocket.WebSocketClientProtocol
   :show-inheritance:



WebSocket Client Factory
========================

Both Twisted and Asyncio client factories share the following functionality.

.. autoclass:: autobahn.websocket.protocol.WebSocketClientFactory
   :members: protocol,
             isServer,
             __init__,
             setSessionParameters,
             setProtocolOptions,
             resetProtocolOptions


Twisted WebSocket Client Factory
--------------------------------

To create a Twisted-based WebSocket client, use the following factory class.

.. autoclass:: autobahn.twisted.websocket.WebSocketClientFactory
   :show-inheritance:
   :members: __init__


Asyncio WebSocket Client Factory
--------------------------------

To create an Asyncio-based WebSocket client, use the following factory class.

.. autoclass:: autobahn.asyncio.websocket.WebSocketClientFactory
   :show-inheritance:
   :members: __init__
