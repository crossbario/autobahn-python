:mod:`autobahn.websocket.compress_bzip2`
========================================

.. py:module:: autobahn.websocket.compress_bzip2


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.websocket.compress_bzip2.PerMessageBzip2Mixin
   autobahn.websocket.compress_bzip2.PerMessageBzip2Offer
   autobahn.websocket.compress_bzip2.PerMessageBzip2OfferAccept
   autobahn.websocket.compress_bzip2.PerMessageBzip2Response
   autobahn.websocket.compress_bzip2.PerMessageBzip2ResponseAccept
   autobahn.websocket.compress_bzip2.PerMessageBzip2



.. class:: PerMessageBzip2Mixin

   Bases: :class:`object`

   Mixin class for this extension.

   .. attribute:: EXTENSION_NAME
      :annotation: = permessage-bzip2

      Name of this WebSocket extension.


   .. attribute:: COMPRESS_LEVEL_PERMISSIBLE_VALUES
      :annotation: = [1, 2, 3, 4, 5, 6, 7, 8, 9]

      Permissible value for compression level parameter.



.. class:: PerMessageBzip2Offer(accept_max_compress_level=True, request_max_compress_level=0)


   Bases: :class:`autobahn.websocket.compress_base.PerMessageCompressOffer`, :class:`autobahn.websocket.compress_bzip2.PerMessageBzip2Mixin`

   Set of extension parameters for `permessage-bzip2` WebSocket extension
   offered by a client to a server.

   .. method:: parse(cls, params)
      :classmethod:

      Parses a WebSocket extension offer for `permessage-bzip2` provided by a client to a server.

      :param params: Output from :func:`autobahn.websocket.WebSocketProtocol._parseExtensionsHeader`.
      :type params: list

      :returns: object -- A new instance of :class:`autobahn.compress.PerMessageBzip2Offer`.


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



.. class:: PerMessageBzip2OfferAccept(offer, request_max_compress_level=0, compress_level=None)


   Bases: :class:`autobahn.websocket.compress_base.PerMessageCompressOfferAccept`, :class:`autobahn.websocket.compress_bzip2.PerMessageBzip2Mixin`

   Set of parameters with which to accept an `permessage-bzip2` offer
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



.. class:: PerMessageBzip2Response(client_max_compress_level, server_max_compress_level)


   Bases: :class:`autobahn.websocket.compress_base.PerMessageCompressResponse`, :class:`autobahn.websocket.compress_bzip2.PerMessageBzip2Mixin`

   Set of parameters for `permessage-bzip2` responded by server.

   .. method:: parse(cls, params)
      :classmethod:

      Parses a WebSocket extension response for `permessage-bzip2` provided by a server to a client.

      :param params: Output from :func:`autobahn.websocket.WebSocketProtocol._parseExtensionsHeader`.
      :type params: list

      :returns: A new instance of :class:`autobahn.compress.PerMessageBzip2Response`.
      :rtype: obj


   .. method:: __json__(self)

      Returns a JSON serializable object representation.

      :returns: JSON serializable representation.
      :rtype: dict


   .. method:: __repr__(self)

      Returns Python object representation that can be eval'ed to reconstruct the object.

      :returns: Python string representation.
      :rtype: str



.. class:: PerMessageBzip2ResponseAccept(response, compress_level=None)


   Bases: :class:`autobahn.websocket.compress_base.PerMessageCompressResponseAccept`, :class:`autobahn.websocket.compress_bzip2.PerMessageBzip2Mixin`

   Set of parameters with which to accept an `permessage-bzip2` response
   from a server by a client.

   .. method:: __json__(self)

      Returns a JSON serializable object representation.

      :returns: JSON serializable representation.
      :rtype: dict


   .. method:: __repr__(self)

      Returns Python object representation that can be eval'ed to reconstruct the object.

      :returns: Python string representation.
      :rtype: str



.. class:: PerMessageBzip2(is_server, server_max_compress_level, client_max_compress_level)


   Bases: :class:`autobahn.websocket.compress_base.PerMessageCompress`, :class:`autobahn.websocket.compress_bzip2.PerMessageBzip2Mixin`

   `permessage-bzip2` WebSocket extension processor.

   .. attribute:: DEFAULT_COMPRESS_LEVEL
      :annotation: = 9

      

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



