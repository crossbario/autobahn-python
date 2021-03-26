:mod:`autobahn.wamp.websocket`
==============================

.. py:module:: autobahn.wamp.websocket


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.websocket.WampWebSocketServerProtocol
   autobahn.wamp.websocket.WampWebSocketClientProtocol
   autobahn.wamp.websocket.WampWebSocketServerFactory
   autobahn.wamp.websocket.WampWebSocketClientFactory



.. class:: WampWebSocketServerProtocol

   Bases: :class:`autobahn.wamp.websocket.WampWebSocketProtocol`

   Mixin for WAMP-over-WebSocket server transports.

   .. attribute:: STRICT_PROTOCOL_NEGOTIATION
      :annotation: = True

      

   .. method:: onConnect(self, request)

      Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onConnect`



.. class:: WampWebSocketClientProtocol

   Bases: :class:`autobahn.wamp.websocket.WampWebSocketProtocol`

   Mixin for WAMP-over-WebSocket client transports.

   .. attribute:: STRICT_PROTOCOL_NEGOTIATION
      :annotation: = True

      

   .. method:: onConnect(self, response)

      Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onConnect`



.. class:: WampWebSocketServerFactory(factory, serializers=None)


   Bases: :class:`autobahn.wamp.websocket.WampWebSocketFactory`

   Mixin for WAMP-over-WebSocket server transport factories.


.. class:: WampWebSocketClientFactory(factory, serializers=None)


   Bases: :class:`autobahn.wamp.websocket.WampWebSocketFactory`

   Mixin for WAMP-over-WebSocket client transport factories.


