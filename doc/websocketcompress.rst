*********************
WebSocket Compression
*********************

Autobahn|Python supports the following WebSocket extensions for compression:

  * `permessage-deflate <http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression>`_
  * permessage-bzip2
  * permessage-snappy

You can find a complete example `here <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/echo_compressed>`_.

|


Per-Message Deflate
===================

The following classes provide the API to the **permessage-deflate** WebSocket extension functionality of AutobahnPython.

|

.. autoclass:: autobahn.websocket.compress.PerMessageDeflateOffer
   :show-inheritance:
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.websocket.compress.PerMessageDeflateOfferAccept
   :show-inheritance:
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.websocket.compress.PerMessageDeflateResponse
   :show-inheritance:
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.websocket.compress.PerMessageDeflateResponseAccept
   :show-inheritance:
   :members: __init__, __json__, __repr__

|


Per-Message Bzip2
=================

The following classes provide the API to the (non-standard) **permessage-bzip2** WebSocket extension functionality of Autobahn|Python.

|

.. autoclass:: autobahn.websocket.compress.PerMessageBzip2Offer
   :show-inheritance:
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.websocket.compress.PerMessageBzip2OfferAccept
   :show-inheritance:
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.websocket.compress.PerMessageBzip2Response
   :show-inheritance:
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.websocket.compress.PerMessageBzip2ResponseAccept
   :show-inheritance:
   :members: __init__, __json__, __repr__

|


Per-Message Snappy
==================

The following classes provide the API to the (non-standard) **permessage-snappy** WebSocket extension functionality of Autobahn|Python.

|

.. autoclass:: autobahn.websocket.compress.PerMessageSnappyOffer
   :show-inheritance:
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.websocket.compress.PerMessageSnappyOfferAccept
   :show-inheritance:
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.websocket.compress.PerMessageSnappyResponse
   :show-inheritance:
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.websocket.compress.PerMessageSnappyResponseAccept
   :show-inheritance:
   :members: __init__, __json__, __repr__

|
