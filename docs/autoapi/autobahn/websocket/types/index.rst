:mod:`autobahn.websocket.types`
===============================

.. py:module:: autobahn.websocket.types


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.websocket.types.ConnectionRequest
   autobahn.websocket.types.ConnectionResponse
   autobahn.websocket.types.ConnectionAccept
   autobahn.websocket.types.Message
   autobahn.websocket.types.IncomingMessage
   autobahn.websocket.types.OutgoingMessage



.. class:: ConnectionRequest(peer, headers, host, path, params, version, origin, protocols, extensions)


   Bases: :class:`object`

   Thin-wrapper for WebSocket connection request information provided in
   :meth:`autobahn.websocket.protocol.WebSocketServerProtocol.onConnect` when
   a WebSocket client want to establish a connection to a WebSocket server.

   .. attribute:: __slots__
      :annotation: = ['peer', 'headers', 'host', 'path', 'params', 'version', 'origin', 'protocols', 'extensions']

      

   .. method:: __json__(self)


   .. method:: __str__(self)

      Return str(self).



.. class:: ConnectionResponse(peer, headers, version, protocol, extensions)


   Bases: :class:`object`

   Thin-wrapper for WebSocket connection response information provided in
   :meth:`autobahn.websocket.protocol.WebSocketClientProtocol.onConnect` when
   a WebSocket server has accepted a connection request by a client.

   .. attribute:: __slots__
      :annotation: = ['peer', 'headers', 'version', 'protocol', 'extensions']

      

   .. method:: __json__(self)


   .. method:: __str__(self)

      Return str(self).



.. class:: ConnectionAccept(subprotocol=None, headers=None)


   Bases: :class:`object`

   Used by WebSocket servers to accept an incoming WebSocket connection.
   If the client announced one or multiple subprotocols, the server MUST
   select one of the subprotocols announced by the client.

   .. attribute:: __slots__
      :annotation: = ['subprotocol', 'headers']

      


.. exception:: ConnectionDeny(code, reason=None)


   Bases: :class:`Exception`

   Throw an instance of this class to deny a WebSocket connection
   during handshake in :meth:`autobahn.websocket.protocol.WebSocketServerProtocol.onConnect`.

   .. attribute:: __slots__
      :annotation: = ['code', 'reason']

      

   .. attribute:: BAD_REQUEST
      :annotation: = 400

      Bad Request. The request cannot be fulfilled due to bad syntax.


   .. attribute:: FORBIDDEN
      :annotation: = 403

      Forbidden. The request was a legal request, but the server is refusing to respond to it.[2] Unlike a 401 Unauthorized response, authenticating will make no difference.


   .. attribute:: NOT_FOUND
      :annotation: = 404

      Not Found. The requested resource could not be found but may be available again in the future.[2] Subsequent requests by the client are permissible.


   .. attribute:: NOT_ACCEPTABLE
      :annotation: = 406

      Not Acceptable. The requested resource is only capable of generating content not acceptable according to the Accept headers sent in the request.


   .. attribute:: REQUEST_TIMEOUT
      :annotation: = 408

      Request Timeout. The server timed out waiting for the request. According to W3 HTTP specifications: 'The client did not produce a request within the time that the server was prepared to wait. The client MAY repeat the request without modifications at any later time.


   .. attribute:: INTERNAL_SERVER_ERROR
      :annotation: = 500

      Internal Server Error. A generic error message, given when no more specific message is suitable.


   .. attribute:: NOT_IMPLEMENTED
      :annotation: = 501

      Not Implemented. The server either does not recognize the request method, or it lacks the ability to fulfill the request.


   .. attribute:: SERVICE_UNAVAILABLE
      :annotation: = 503

      Service Unavailable. The server is currently unavailable (because it is overloaded or down for maintenance). Generally, this is a temporary state.



.. class:: Message

   Bases: :class:`object`

   Abstract base class for WebSocket messages.

   .. attribute:: __slots__
      :annotation: = []

      


.. class:: IncomingMessage(payload, is_binary=False)


   Bases: :class:`autobahn.websocket.types.Message`

   An incoming WebSocket message.

   .. attribute:: __slots__
      :annotation: = ['payload', 'is_binary']

      


.. class:: OutgoingMessage(payload, is_binary=False, skip_compress=False)


   Bases: :class:`autobahn.websocket.types.Message`

   An outgoing WebSocket message.

   .. attribute:: __slots__
      :annotation: = ['payload', 'is_binary', 'skip_compress']

      


