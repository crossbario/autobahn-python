Compression
===========

AutobahnPython supports the following WebSocket extensions for compression:

  * `permessage-deflate`
  * `permessage-bzip2`
  * `permessage-snappy`

|


Per-Message Deflate Compression
-------------------------------

The following classes provide the API to the `permessage-deflate` WebSocket extension functionality of AutobahnPython.

|

.. autoclass:: autobahn.compress.PerMessageDeflateOffer
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageDeflateOfferAccept
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageDeflateResponse
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageDeflateResponseAccept
   :members: __init__, __json__, __repr__

|


Per-Message Bzip2 Compression
-----------------------------

The following classes provide the API to the `permessage-bzip2` WebSocket extension functionality of AutobahnPython.

|

.. autoclass:: autobahn.compress.PerMessageBzip2Offer
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageBzip2OfferAccept
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageBzip2Response
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageBzip2ResponseAccept
   :members: __init__, __json__, __repr__

|


Per-Message Snappy Compression
------------------------------

The following classes provide the API to the `permessage-snappy` WebSocket extension functionality of AutobahnPython.

|

.. autoclass:: autobahn.compress.PerMessageSnappyOffer
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageSnappyOfferAccept
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageSnappyResponse
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageSnappyResponseAccept
   :members: __init__, __json__, __repr__

|
