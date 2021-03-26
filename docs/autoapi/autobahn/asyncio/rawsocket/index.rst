:mod:`autobahn.asyncio.rawsocket`
=================================

.. py:module:: autobahn.asyncio.rawsocket


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.asyncio.rawsocket.WampRawSocketServerProtocol
   autobahn.asyncio.rawsocket.WampRawSocketClientProtocol
   autobahn.asyncio.rawsocket.WampRawSocketServerFactory
   autobahn.asyncio.rawsocket.WampRawSocketClientFactory



.. class:: WampRawSocketServerProtocol


   Bases: :class:`autobahn.asyncio.rawsocket.WampRawSocketMixinGeneral`, :class:`autobahn.asyncio.rawsocket.WampRawSocketMixinAsyncio`, :class:`autobahn.asyncio.rawsocket.RawSocketServerProtocol`

   asyncio-based WAMP-over-RawSocket server protocol.

   Implements:

       * :class:`autobahn.wamp.interfaces.ITransport`

   .. method:: supports_serializer(self, ser_id)


   .. method:: get_channel_id(self, channel_id_type=None)

      Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`



.. class:: WampRawSocketClientProtocol


   Bases: :class:`autobahn.asyncio.rawsocket.WampRawSocketMixinGeneral`, :class:`autobahn.asyncio.rawsocket.WampRawSocketMixinAsyncio`, :class:`autobahn.asyncio.rawsocket.RawSocketClientProtocol`

   asyncio-based WAMP-over-RawSocket client protocol.

   Implements:

       * :class:`autobahn.wamp.interfaces.ITransport`

   .. method:: serializer_id(self)
      :property:


   .. method:: get_channel_id(self, channel_id_type=None)

      Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`



.. class:: WampRawSocketServerFactory(factory, serializers=None)


   Bases: :class:`autobahn.asyncio.rawsocket.WampRawSocketFactory`

   asyncio-based WAMP-over-RawSocket server protocol factory.

   .. attribute:: protocol
      

      


.. class:: WampRawSocketClientFactory(factory, serializer=None)


   Bases: :class:`autobahn.asyncio.rawsocket.WampRawSocketFactory`

   asyncio-based WAMP-over-RawSocket client factory.

   .. attribute:: protocol
      

      


