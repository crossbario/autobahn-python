:mod:`autobahn.twisted.websocket`
=================================

.. py:module:: autobahn.twisted.websocket


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.websocket.WebSocketAdapterProtocol
   autobahn.twisted.websocket.WebSocketServerProtocol
   autobahn.twisted.websocket.WebSocketClientProtocol
   autobahn.twisted.websocket.WebSocketAdapterFactory
   autobahn.twisted.websocket.WebSocketServerFactory
   autobahn.twisted.websocket.WebSocketClientFactory
   autobahn.twisted.websocket.WrappingWebSocketAdapter
   autobahn.twisted.websocket.WrappingWebSocketServerProtocol
   autobahn.twisted.websocket.WrappingWebSocketClientProtocol
   autobahn.twisted.websocket.WrappingWebSocketServerFactory
   autobahn.twisted.websocket.WrappingWebSocketClientFactory
   autobahn.twisted.websocket.WampWebSocketServerProtocol
   autobahn.twisted.websocket.WampWebSocketServerFactory
   autobahn.twisted.websocket.WampWebSocketClientProtocol
   autobahn.twisted.websocket.WampWebSocketClientFactory



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.twisted.websocket.create_client_agent
   autobahn.twisted.websocket.connectWS
   autobahn.twisted.websocket.listenWS


.. function:: create_client_agent(reactor)

   :returns: an instance implementing IWebSocketClientAgent


.. class:: WebSocketAdapterProtocol

   Bases: :class:`twisted.internet.protocol.Protocol`

   Adapter class for Twisted WebSocket client and server protocols.

   .. attribute:: log
      

      

   .. attribute:: peer
      

      

   .. attribute:: peer_transport
      

      

   .. method:: connectionMade(self)

      Called when a connection is made.

      This may be considered the initializer of the protocol, because
      it is called when the connection is completed.  For clients,
      this is called once the connection to the server has been
      established; for servers, this is called after an accept() call
      stops blocking and a socket has been received.  If you need to
      send any greeting or initial message, do it here.


   .. method:: connectionLost(self, reason)

      Called when the connection is shut down.

      Clear any circular references here, and any external references
      to this Protocol.  The connection has been closed.

      @type reason: L{twisted.python.failure.Failure}


   .. method:: dataReceived(self, data)

      Called whenever data is received.

      Use this method to translate to a higher-level message.  Usually, some
      callback will be made upon the receipt of each complete protocol
      message.

      @param data: a string of indeterminate length.  Please keep in mind
          that you will probably need to buffer some data, as partial
          (or multiple) protocol messages may be received!  I recommend
          that unit tests for protocols call through to this method with
          differing chunk sizes, down to one byte at a time.


   .. method:: _closeConnection(self, abort=False)


   .. method:: _onOpen(self)


   .. method:: _onMessageBegin(self, isBinary)


   .. method:: _onMessageFrameBegin(self, length)


   .. method:: _onMessageFrameData(self, payload)


   .. method:: _onMessageFrameEnd(self)


   .. method:: _onMessageFrame(self, payload)


   .. method:: _onMessageEnd(self)


   .. method:: _onMessage(self, payload, isBinary)


   .. method:: _onPing(self, payload)


   .. method:: _onPong(self, payload)


   .. method:: _onClose(self, wasClean, code, reason)


   .. method:: registerProducer(self, producer, streaming)

      Register a Twisted producer with this protocol.

      :param producer: A Twisted push or pull producer.
      :type producer: object
      :param streaming: Producer type.
      :type streaming: bool


   .. method:: unregisterProducer(self)

      Unregister Twisted producer with this protocol.



.. class:: WebSocketServerProtocol


   Bases: :class:`autobahn.twisted.websocket.WebSocketAdapterProtocol`, :class:`autobahn.websocket.protocol.WebSocketServerProtocol`

   Base class for Twisted-based WebSocket server protocols.

   Implements :class:`autobahn.websocket.interfaces.IWebSocketChannel`.

   .. attribute:: log
      

      

   .. method:: get_channel_id(self, channel_id_type=None)

      Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`



.. class:: WebSocketClientProtocol


   Bases: :class:`autobahn.twisted.websocket.WebSocketAdapterProtocol`, :class:`autobahn.websocket.protocol.WebSocketClientProtocol`

   Base class for Twisted-based WebSocket client protocols.

   Implements :class:`autobahn.websocket.interfaces.IWebSocketChannel`.

   .. attribute:: log
      

      

   .. method:: _onConnect(self, response)


   .. method:: startTLS(self)


   .. method:: get_channel_id(self, channel_id_type=None)

      Implements :func:`autobahn.wamp.interfaces.ITransport.get_channel_id`


   .. method:: _create_transport_details(self)

      Internal helper.
      Base class calls this to create a TransportDetails



.. class:: WebSocketAdapterFactory

   Bases: :class:`object`

   Adapter class for Twisted-based WebSocket client and server factories.


.. class:: WebSocketServerFactory(*args, **kwargs)


   Bases: :class:`autobahn.twisted.websocket.WebSocketAdapterFactory`, :class:`autobahn.websocket.protocol.WebSocketServerFactory`, :class:`twisted.internet.protocol.ServerFactory`

   Base class for Twisted-based WebSocket server factories.

   Implements :class:`autobahn.websocket.interfaces.IWebSocketServerChannelFactory`


.. class:: WebSocketClientFactory(*args, **kwargs)


   Bases: :class:`autobahn.twisted.websocket.WebSocketAdapterFactory`, :class:`autobahn.websocket.protocol.WebSocketClientFactory`, :class:`twisted.internet.protocol.ClientFactory`

   Base class for Twisted-based WebSocket client factories.

   Implements :class:`autobahn.websocket.interfaces.IWebSocketClientChannelFactory`


.. class:: WrappingWebSocketAdapter

   Bases: :class:`object`

   An adapter for stream-based transport over WebSocket.

   This follows `websockify <https://github.com/kanaka/websockify>`_
   and should be compatible with that.

   It uses WebSocket subprotocol negotiation and supports the
   following WebSocket subprotocols:

     - ``binary`` (or a compatible subprotocol)
     - ``base64``

   Octets are either transmitted as the payload of WebSocket binary
   messages when using the ``binary`` subprotocol (or an alternative
   binary compatible subprotocol), or encoded with Base64 and then
   transmitted as the payload of WebSocket text messages when using
   the ``base64`` subprotocol.

   .. method:: onConnect(self, requestOrResponse)


   .. method:: onOpen(self)


   .. method:: onMessage(self, payload, isBinary)


   .. method:: onClose(self, wasClean, code, reason)


   .. method:: write(self, data)


   .. method:: writeSequence(self, data)


   .. method:: loseConnection(self)


   .. method:: getPeer(self)


   .. method:: getHost(self)



.. class:: WrappingWebSocketServerProtocol


   Bases: :class:`autobahn.twisted.websocket.WrappingWebSocketAdapter`, :class:`autobahn.twisted.websocket.WebSocketServerProtocol`

   Server protocol for stream-based transport over WebSocket.


.. class:: WrappingWebSocketClientProtocol


   Bases: :class:`autobahn.twisted.websocket.WrappingWebSocketAdapter`, :class:`autobahn.twisted.websocket.WebSocketClientProtocol`

   Client protocol for stream-based transport over WebSocket.


.. class:: WrappingWebSocketServerFactory(factory, url, reactor=None, enableCompression=True, autoFragmentSize=0, subprotocol=None)


   Bases: :class:`autobahn.twisted.websocket.WebSocketServerFactory`

   Wrapping server factory for stream-based transport over WebSocket.

   .. method:: buildProtocol(self, addr)

      Create an instance of a subclass of Protocol.

      The returned instance will handle input on an incoming server
      connection, and an attribute "factory" pointing to the creating
      factory.

      Alternatively, L{None} may be returned to immediately close the
      new connection.

      Override this method to alter how Protocol instances get created.

      @param addr: an object implementing L{twisted.internet.interfaces.IAddress}


   .. method:: startFactory(self)

      This will be called before I begin listening on a Port or Connector.

      It will only be called once, even if the factory is connected
      to multiple ports.

      This can be used to perform 'unserialization' tasks that
      are best put off until things are actually running, such
      as connecting to a database, opening files, etcetera.


   .. method:: stopFactory(self)

      This will be called before I stop listening on all Ports/Connectors.

      This can be overridden to perform 'shutdown' tasks such as disconnecting
      database connections, closing files, etc.

      It will be called, for example, before an application shuts down,
      if it was connected to a port. User code should not call this function
      directly.



.. class:: WrappingWebSocketClientFactory(factory, url, reactor=None, enableCompression=True, autoFragmentSize=0, subprotocol=None)


   Bases: :class:`autobahn.twisted.websocket.WebSocketClientFactory`

   Wrapping client factory for stream-based transport over WebSocket.

   .. method:: buildProtocol(self, addr)

      Create an instance of a subclass of Protocol.

      The returned instance will handle input on an incoming server
      connection, and an attribute "factory" pointing to the creating
      factory.

      Alternatively, L{None} may be returned to immediately close the
      new connection.

      Override this method to alter how Protocol instances get created.

      @param addr: an object implementing L{twisted.internet.interfaces.IAddress}



.. function:: connectWS(factory, contextFactory=None, timeout=30, bindAddress=None)

   Establish WebSocket connection to a server. The connection parameters like target
   host, port, resource and others are provided via the factory.

   :param factory: The WebSocket protocol factory to be used for creating client protocol instances.
   :type factory: An :class:`autobahn.websocket.WebSocketClientFactory` instance.

   :param contextFactory: SSL context factory, required for secure WebSocket connections ("wss").
   :type contextFactory: A `twisted.internet.ssl.ClientContextFactory <http://twistedmatrix.com/documents/current/api/twisted.internet.ssl.ClientContextFactory.html>`_ instance.

   :param timeout: Number of seconds to wait before assuming the connection has failed.
   :type timeout: int

   :param bindAddress: A (host, port) tuple of local address to bind to, or None.
   :type bindAddress: tuple

   :returns: The connector.
   :rtype: An object which implements `twisted.interface.IConnector <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IConnector.html>`_.


.. function:: listenWS(factory, contextFactory=None, backlog=50, interface='')

   Listen for incoming WebSocket connections from clients. The connection parameters like
   listening port and others are provided via the factory.

   :param factory: The WebSocket protocol factory to be used for creating server protocol instances.
   :type factory: An :class:`autobahn.websocket.WebSocketServerFactory` instance.

   :param contextFactory: SSL context factory, required for secure WebSocket connections ("wss").
   :type contextFactory: A twisted.internet.ssl.ContextFactory.

   :param backlog: Size of the listen queue.
   :type backlog: int

   :param interface: The interface (derived from hostname given) to bind to, defaults to '' (all).
   :type interface: str

   :returns: The listening port.
   :rtype: An object that implements `twisted.interface.IListeningPort <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IListeningPort.html>`_.


.. class:: WampWebSocketServerProtocol


   Bases: :class:`autobahn.wamp.websocket.WampWebSocketServerProtocol`, :class:`autobahn.twisted.websocket.WebSocketServerProtocol`

   Twisted-based WAMP-over-WebSocket server protocol.

   Implements:

   * :class:`autobahn.wamp.interfaces.ITransport`


.. class:: WampWebSocketServerFactory(factory, *args, **kwargs)


   Bases: :class:`autobahn.wamp.websocket.WampWebSocketServerFactory`, :class:`autobahn.twisted.websocket.WebSocketServerFactory`

   Twisted-based WAMP-over-WebSocket server protocol factory.

   .. attribute:: protocol
      

      


.. class:: WampWebSocketClientProtocol


   Bases: :class:`autobahn.wamp.websocket.WampWebSocketClientProtocol`, :class:`autobahn.twisted.websocket.WebSocketClientProtocol`

   Twisted-based WAMP-over-WebSocket client protocol.

   Implements:

   * :class:`autobahn.wamp.interfaces.ITransport`


.. class:: WampWebSocketClientFactory(factory, *args, **kwargs)


   Bases: :class:`autobahn.wamp.websocket.WampWebSocketClientFactory`, :class:`autobahn.twisted.websocket.WebSocketClientFactory`

   Twisted-based WAMP-over-WebSocket client protocol factory.

   .. attribute:: protocol
      

      


