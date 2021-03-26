:mod:`autobahn.asyncio.websocket`
=================================

.. py:module:: autobahn.asyncio.websocket


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.asyncio.websocket.WebSocketServerProtocol
   autobahn.asyncio.websocket.WebSocketClientProtocol
   autobahn.asyncio.websocket.WebSocketServerFactory
   autobahn.asyncio.websocket.WebSocketClientFactory
   autobahn.asyncio.websocket.WampWebSocketServerProtocol
   autobahn.asyncio.websocket.WampWebSocketServerFactory
   autobahn.asyncio.websocket.WampWebSocketClientProtocol
   autobahn.asyncio.websocket.WampWebSocketClientFactory



.. class:: WebSocketServerProtocol


   Bases: :class:`autobahn.asyncio.websocket.WebSocketAdapterProtocol`, :class:`autobahn.websocket.protocol.WebSocketServerProtocol`

   Base class for asyncio-based WebSocket server protocols.

   Implements:

   * :class:`autobahn.websocket.interfaces.IWebSocketChannel`

   .. attribute:: log
      

      

   .. method:: get_channel_id(self, channel_id_type=None)

      Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`



.. class:: WebSocketClientProtocol


   Bases: :class:`autobahn.asyncio.websocket.WebSocketAdapterProtocol`, :class:`autobahn.websocket.protocol.WebSocketClientProtocol`

   Base class for asyncio-based WebSocket client protocols.

   Implements:

   * :class:`autobahn.websocket.interfaces.IWebSocketChannel`

   .. attribute:: log
      

      

   .. method:: _onConnect(self, response)


   .. method:: startTLS(self)


   .. method:: get_channel_id(self, channel_id_type=None)

      Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`


   .. method:: _create_transport_details(self)

      Internal helper.
      Base class calls this to create a TransportDetails



.. class:: WebSocketServerFactory(*args, **kwargs)


   Bases: :class:`autobahn.asyncio.websocket.WebSocketAdapterFactory`, :class:`protocol.WebSocketServerFactory`

   Base class for asyncio-based WebSocket server factories.

   Implements:

   * :class:`autobahn.websocket.interfaces.IWebSocketServerChannelFactory`

   .. attribute:: protocol
      

      


.. class:: WebSocketClientFactory(*args, **kwargs)


   Bases: :class:`autobahn.asyncio.websocket.WebSocketAdapterFactory`, :class:`autobahn.websocket.protocol.WebSocketClientFactory`

   Base class for asyncio-based WebSocket client factories.

   Implements:

   * :class:`autobahn.websocket.interfaces.IWebSocketClientChannelFactory`


.. class:: WampWebSocketServerProtocol


   Bases: :class:`autobahn.wamp.websocket.WampWebSocketServerProtocol`, :class:`autobahn.asyncio.websocket.WebSocketServerProtocol`

   asyncio-based WAMP-over-WebSocket server protocol.

   Implements:

   * :class:`autobahn.wamp.interfaces.ITransport`


.. class:: WampWebSocketServerFactory(factory, *args, **kwargs)


   Bases: :class:`autobahn.wamp.websocket.WampWebSocketServerFactory`, :class:`autobahn.asyncio.websocket.WebSocketServerFactory`

   asyncio-based WAMP-over-WebSocket server factory.

   .. attribute:: protocol
      

      


.. class:: WampWebSocketClientProtocol


   Bases: :class:`autobahn.wamp.websocket.WampWebSocketClientProtocol`, :class:`autobahn.asyncio.websocket.WebSocketClientProtocol`

   asyncio-based WAMP-over-WebSocket client protocols.

   Implements:

   * :class:`autobahn.wamp.interfaces.ITransport`


.. class:: WampWebSocketClientFactory(factory, *args, **kwargs)


   Bases: :class:`autobahn.wamp.websocket.WampWebSocketClientFactory`, :class:`autobahn.asyncio.websocket.WebSocketClientFactory`

   asyncio-based WAMP-over-WebSocket client factory.

   .. attribute:: protocol
      

      


