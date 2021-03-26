:mod:`autobahn.websocket.compress_snappy`
=========================================

.. py:module:: autobahn.websocket.compress_snappy


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.websocket.compress_snappy.PerMessageSnappyMixin
   autobahn.websocket.compress_snappy.PerMessageSnappyOffer
   autobahn.websocket.compress_snappy.PerMessageSnappyOfferAccept
   autobahn.websocket.compress_snappy.PerMessageSnappyResponse
   autobahn.websocket.compress_snappy.PerMessageSnappyResponseAccept
   autobahn.websocket.compress_snappy.PerMessageSnappy



.. class:: PerMessageSnappyMixin

   Bases: :class:`object`

   Mixin class for this extension.

   .. attribute:: EXTENSION_NAME
      :annotation: = permessage-snappy

      Name of this WebSocket extension.



.. class:: PerMessageSnappyOffer(accept_no_context_takeover=True, request_no_context_takeover=False)


   Bases: :class:`autobahn.websocket.compress_base.PerMessageCompressOffer`, :class:`autobahn.websocket.compress_snappy.PerMessageSnappyMixin`

   Set of extension parameters for `permessage-snappy` WebSocket extension
   offered by a client to a server.

   .. method:: parse(cls, params)
      :classmethod:

      Parses a WebSocket extension offer for `permessage-snappy` provided by a client to a server.

      :param params: Output from :func:`autobahn.websocket.WebSocketProtocol._parseExtensionsHeader`.
      :type params: list

      :returns: A new instance of :class:`autobahn.compress.PerMessageSnappyOffer`.
      :rtype: obj


   .. method:: get_extension_string(self)

      Returns the WebSocket extension configuration string as sent to the server.

      :returns: PMCE configuration string.
      :rtype: str


   .. method:: __json__(self)

      Returns a JSON serializable object representation.

      :returns: JSON serializable representation.
      :rtype: dict


   .. method:: __repr__(self)

      Returns Python object representation that can be eval'ed to reconstruct the object.

      :returns: Python string representation.
      :rtype: str



.. class:: PerMessageSnappyOfferAccept(offer, request_no_context_takeover=False, no_context_takeover=None)


   Bases: :class:`autobahn.websocket.compress_base.PerMessageCompressOfferAccept`, :class:`autobahn.websocket.compress_snappy.PerMessageSnappyMixin`

   Set of parameters with which to accept an `permessage-snappy` offer
   from a client by a server.

   .. method:: get_extension_string(self)

      Returns the WebSocket extension configuration string as sent to the server.

      :returns: PMCE configuration string.
      :rtype: str


   .. method:: __json__(self)

      Returns a JSON serializable object representation.

      :returns: JSON serializable representation.
      :rtype: dict


   .. method:: __repr__(self)

      Returns Python object representation that can be eval'ed to reconstruct the object.

      :returns: Python string representation.
      :rtype: str



.. class:: PerMessageSnappyResponse(client_no_context_takeover, server_no_context_takeover)


   Bases: :class:`autobahn.websocket.compress_base.PerMessageCompressResponse`, :class:`autobahn.websocket.compress_snappy.PerMessageSnappyMixin`

   Set of parameters for `permessage-snappy` responded by server.

   .. method:: parse(cls, params)
      :classmethod:

      Parses a WebSocket extension response for `permessage-snappy` provided by a server to a client.

      :param params: Output from :func:`autobahn.websocket.WebSocketProtocol._parseExtensionsHeader`.
      :type params: list

      :returns: A new instance of :class:`autobahn.compress.PerMessageSnappyResponse`.
      :rtype: obj


   .. method:: __json__(self)

      Returns a JSON serializable object representation.

      :returns: JSON serializable representation.
      :rtype: dict


   .. method:: __repr__(self)

      Returns Python object representation that can be eval'ed to reconstruct the object.

      :returns: Python string representation.
      :rtype: str



.. class:: PerMessageSnappyResponseAccept(response, no_context_takeover=None)


   Bases: :class:`autobahn.websocket.compress_base.PerMessageCompressResponseAccept`, :class:`autobahn.websocket.compress_snappy.PerMessageSnappyMixin`

   Set of parameters with which to accept an `permessage-snappy` response
   from a server by a client.

   .. method:: __json__(self)

      Returns a JSON serializable object representation.

      :returns: JSON serializable representation.
      :rtype: dict


   .. method:: __repr__(self)

      Returns Python object representation that can be eval'ed to reconstruct the object.

      :returns: Python string representation.
      :rtype: str



.. class:: PerMessageSnappy(is_server, server_no_context_takeover, client_no_context_takeover)


   Bases: :class:`autobahn.websocket.compress_base.PerMessageCompress`, :class:`autobahn.websocket.compress_snappy.PerMessageSnappyMixin`

   `permessage-snappy` WebSocket extension processor.

   .. method:: create_from_response_accept(cls, is_server, accept)
      :classmethod:


   .. method:: create_from_offer_accept(cls, is_server, accept)
      :classmethod:


   .. method:: __json__(self)


   .. method:: __repr__(self)

      Return repr(self).


   .. method:: start_compress_message(self)


   .. method:: compress_message_data(self, data)


   .. method:: end_compress_message(self)


   .. method:: start_decompress_message(self)


   .. method:: decompress_message_data(self, data)


   .. method:: end_decompress_message(self)



