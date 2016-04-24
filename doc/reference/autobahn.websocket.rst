autobahn.websocket
==================

This module contains the parts of the public API that are related to WebSocket and which are independent of the networking framework (Twisted/asyncio) used.


WebSocket Connection Establishment
----------------------------------

Objects of the following classes are used in the initial WebSocket opening handshake for negotiation.

.. autoclass:: autobahn.websocket.ConnectionRequest
    :members:

.. autoclass:: autobahn.websocket.ConnectionResponse
    :members:

.. autoclass:: autobahn.websocket.ConnectionAccept
    :members:

.. autoclass:: autobahn.websocket.ConnectionDeny
    :members:


WebSocket Compression Negotiation
---------------------------------

Objects of the following classes are used during negotiation of WebSocket compression in the initial WebSocket opening handshake.

.. autoclass:: autobahn.websocket.PerMessageDeflateOffer
    :members:

.. autoclass:: autobahn.websocket.PerMessageDeflateOfferAccept
    :members:

.. autoclass:: autobahn.websocket.PerMessageDeflateResponse
    :members:

.. autoclass:: autobahn.websocket.PerMessageDeflateResponseAccept
    :members:


WebSocket URL Helpers
---------------------

The following helper functions can be used to assembled and parse proper WebSocket URLs.

.. autofunction:: autobahn.websocket.create_url

.. autofunction:: autobahn.websocket.parse_url
