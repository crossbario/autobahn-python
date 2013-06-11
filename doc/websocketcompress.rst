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

.. autoclass:: autobahn.compress.PerMessageDeflateAccept
   :members: __init__, __json__, __repr__

|


Per-Message Bzip2 Compression
-----------------------------

The following classes provide the API to the `permessage-bzip2` WebSocket extension functionality of AutobahnPython.

|

.. autoclass:: autobahn.compress.PerMessageBzip2Offer
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageBzip2Accept
   :members: __init__, __json__, __repr__

|


Per-Message Snappy Compression
------------------------------

The following classes provide the API to the `permessage-snappy` WebSocket extension functionality of AutobahnPython.

|

.. autoclass:: autobahn.compress.PerMessageSnappyOffer
   :members: __init__, __json__, __repr__

|

.. autoclass:: autobahn.compress.PerMessageSnappyAccept
   :members: __init__, __json__, __repr__

|
