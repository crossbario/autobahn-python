Module ``autobahn.asyncio``
===========================

Autobahn asyncio specific classes. These are used when asyncio is run as the underlying networking framework.


Component
---------

The component API provides a high-level functional style method of defining and running WAMP components including authentication configuration

.. autoclass:: autobahn.asyncio.component.Component
    :members:

.. autofunction:: autobahn.asyncio.component.run


WebSocket Protocols and Factories
---------------------------------

Classes for WebSocket clients and servers using asyncio.

.. autoclass:: autobahn.asyncio.websocket.WebSocketServerProtocol
    :members:

.. autoclass:: autobahn.asyncio.websocket.WebSocketClientProtocol
    :members:

.. autoclass:: autobahn.asyncio.websocket.WebSocketServerFactory
    :members:

.. autoclass:: autobahn.asyncio.websocket.WebSocketClientFactory
    :members:


WAMP-over-WebSocket Protocols and Factories
-------------------------------------------

Classes for WAMP-WebSocket clients and servers using asyncio.

.. autoclass:: autobahn.asyncio.websocket.WampWebSocketServerProtocol
    :members:

.. autoclass:: autobahn.asyncio.websocket.WampWebSocketClientProtocol
    :members:

.. autoclass:: autobahn.asyncio.websocket.WampWebSocketServerFactory
    :members:

.. autoclass:: autobahn.asyncio.websocket.WampWebSocketClientFactory
    :members:


WAMP-over-RawSocket Protocols and Factories
-------------------------------------------

Classes for WAMP-RawSocket clients and servers using asyncio.

.. autoclass:: autobahn.asyncio.rawsocket.WampRawSocketServerProtocol
    :members:

.. autoclass:: autobahn.asyncio.rawsocket.WampRawSocketClientProtocol
    :members:

.. autoclass:: autobahn.asyncio.rawsocket.WampRawSocketServerFactory
    :members:

.. autoclass:: autobahn.asyncio.rawsocket.WampRawSocketClientFactory
    :members:


WAMP Sessions
-------------

Classes for WAMP sessions using asyncio.

.. autoclass:: autobahn.asyncio.wamp.ApplicationSession
    :members:

.. autoclass:: autobahn.asyncio.wamp.ApplicationRunner
    :members:
