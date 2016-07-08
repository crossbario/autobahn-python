*********************
WebSocket Compression
*********************

Autobahn|Python supports the following WebSocket extensions for compression:

* `permessage-deflate <http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression>`_
* permessage-bzip2
* permessage-snappy

You can find a complete example `here <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_compressed>`_.

|


Per-Message Deflate
===================

The following classes provide the API to the **permessage-deflate** WebSocket extension functionality of AutobahnPython.

* :class:`autobahn.websocket.compress.PerMessageDeflateOffer`
* :class:`autobahn.websocket.compress.PerMessageDeflateOfferAccept`
* :class:`autobahn.websocket.compress.PerMessageDeflateResponse`
* :class:`autobahn.websocket.compress.PerMessageDeflateResponseAccept`


Per-Message Bzip2
=================

The following classes provide the API to the (non-standard) **permessage-bzip2** WebSocket extension functionality of Autobahn|Python.

* :class:`autobahn.websocket.compress.PerMessageBzip2Offer`
* :class:`autobahn.websocket.compress.PerMessageBzip2OfferAccept`
* :class:`autobahn.websocket.compress.PerMessageBzip2Response`
* :class:`autobahn.websocket.compress.PerMessageBzip2ResponseAccept`


Per-Message Snappy
==================

The following classes provide the API to the (non-standard) **permessage-snappy** WebSocket extension functionality of Autobahn|Python.

* :class:`autobahn.websocket.compress.PerMessageSnappyOffer`
* :class:`autobahn.websocket.compress.PerMessageSnappyOfferAccept`
* :class:`autobahn.websocket.compress.PerMessageSnappyResponse`
* :class:`autobahn.websocket.compress.PerMessageSnappyResponseAccept`
