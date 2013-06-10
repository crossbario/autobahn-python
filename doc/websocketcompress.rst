Compression
===========

The classes :class:`autobahn.wamp.WampClientProtocol` and
:class:`autobahn.wamp.WampClientFactory` are the base classes
you derive from to implement WAMP clients.


.. autoclass:: autobahn.compress.PerMessageCompress


.. autoclass:: autobahn.compress.PerMessageBzip2Mixin
   :members: EXTENSION_NAME


Per-Message Bzip2 Compression
-----------------------------

.. autoclass:: autobahn.compress.PerMessageBzip2Offer
   :members: EXTENSION_NAME,
             __init__,
             getExtensionString,
             parse,
             __json__,
             __repr__

.. autoclass:: autobahn.compress.PerMessageBzip2Accept
   :members: EXTENSION_NAME,
             __init__,
             __json__,
             __repr__

.. autoclass:: autobahn.compress.PerMessageBzip2
   :members: EXTENSION_NAME,
             __init__,
             __json__,
             __repr__,
             getExtensionString,
             startCompressMessage,
             compressMessageData,
             endCompressMessage,
             startDecompressMessage,
             decompressMessageData,
             endDecompressMessage
