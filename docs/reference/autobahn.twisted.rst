Module ``autobahn.twisted``
===========================

Autobahn Twisted specific classes. These are used when Twisted is run as the underlying networking framework.


WebSocket Protocols and Factories
---------------------------------

Base classes for WebSocket clients and servers using Twisted.

.. autoclass:: autobahn.twisted.websocket.WebSocketServerProtocol
    :members:

.. autoclass:: autobahn.twisted.websocket.WebSocketClientProtocol
    :members:

.. autoclass:: autobahn.twisted.websocket.WebSocketServerFactory
    :members:

.. autoclass:: autobahn.twisted.websocket.WebSocketClientFactory
    :members:


WAMP-over-WebSocket Protocols and Factories
-------------------------------------------

Base classes for WAMP-WebSocket clients and servers using Twisted.

.. autoclass:: autobahn.twisted.websocket.WampWebSocketServerProtocol
    :members:

.. autoclass:: autobahn.twisted.websocket.WampWebSocketClientProtocol
    :members:

.. autoclass:: autobahn.twisted.websocket.WampWebSocketServerFactory
    :members:

.. autoclass:: autobahn.twisted.websocket.WampWebSocketClientFactory
    :members:


WAMP-over-RawSocket Protocols and Factories
-------------------------------------------

Base classes for WAMP-RawSocket clients and servers using Twisted.

.. autoclass:: autobahn.twisted.rawsocket.WampRawSocketServerProtocol
    :members:

.. autoclass:: autobahn.twisted.rawsocket.WampRawSocketClientProtocol
    :members:

.. autoclass:: autobahn.twisted.rawsocket.WampRawSocketServerFactory
    :members:

.. autoclass:: autobahn.twisted.rawsocket.WampRawSocketClientFactory
    :members:
