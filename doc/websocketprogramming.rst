Programming with WebSocekt
==========================

.. note:: Content will be added to this section in the near future. For now, please take a look at the :ref:`WebSocket Examples <websocket_examples>` and the :ref:`WebSocket Reference <websocket_reference>`.


Upgrading from Autobahn < 0.7.0
-------------------------------

Starting with release 0.7.0, |ab| now supports both Twisted and asyncio as the underlying network library. This required changing module naming, e.g.

|ab| **< 0.7.0**:

     from autobahn.websocket import WebSocketServerProtocol

|ab| **>= 0.7.0**:

     from autobahn.twisted.websocket import WebSocketServerProtocol

or

     from autobahn.asyncio.websocket import WebSocketServerProtocol

Two more small changes (also see the `interface definition <https://github.com/tavendo/AutobahnPython/blob/master/autobahn/autobahn/websocket/interfaces.py>`_ now available):

 1. ``WebSocketProtocol.sendMessage``: renaming of parameter ``binary`` to ``isBinary`` (for consistency with `onMessage`)
 2. ``ConnectionRequest`` no longer provides ``peerstr``, but only ``peer``, and the latter is a plain, descriptive string (this was needed since we now support both Twisted and asyncio, and also non-TCP transports)
