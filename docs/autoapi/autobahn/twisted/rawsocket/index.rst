:mod:`autobahn.twisted.rawsocket`
=================================

.. py:module:: autobahn.twisted.rawsocket


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.rawsocket.WampRawSocketServerProtocol
   autobahn.twisted.rawsocket.WampRawSocketClientProtocol
   autobahn.twisted.rawsocket.WampRawSocketServerFactory
   autobahn.twisted.rawsocket.WampRawSocketClientFactory



.. class:: WampRawSocketServerProtocol


   Bases: :class:`autobahn.twisted.rawsocket.WampRawSocketProtocol`

   Twisted-based WAMP-over-RawSocket server protocol.

   Implements:

       * :class:`autobahn.wamp.interfaces.ITransport`

   .. method:: dataReceived(self, data)

      Convert int prefixed strings into calls to stringReceived.


   .. method:: get_channel_id(self, channel_id_type=None)

      Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`



.. class:: WampRawSocketClientProtocol


   Bases: :class:`autobahn.twisted.rawsocket.WampRawSocketProtocol`

   Twisted-based WAMP-over-RawSocket client protocol.

   Implements:

       * :class:`autobahn.wamp.interfaces.ITransport`

   .. method:: connectionMade(self)

      Called when a connection is made.

      This may be considered the initializer of the protocol, because
      it is called when the connection is completed.  For clients,
      this is called once the connection to the server has been
      established; for servers, this is called after an accept() call
      stops blocking and a socket has been received.  If you need to
      send any greeting or initial message, do it here.


   .. method:: dataReceived(self, data)

      Convert int prefixed strings into calls to stringReceived.


   .. method:: get_channel_id(self, channel_id_type=None)

      Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`



.. class:: WampRawSocketServerFactory(factory, serializers=None)


   Bases: :class:`autobahn.twisted.rawsocket.WampRawSocketFactory`

   Twisted-based WAMP-over-RawSocket server protocol factory.

   .. attribute:: protocol
      

      


.. class:: WampRawSocketClientFactory(factory, serializer=None)


   Bases: :class:`autobahn.twisted.rawsocket.WampRawSocketFactory`

   Twisted-based WAMP-over-RawSocket client protocol factory.

   .. attribute:: protocol
      

      


