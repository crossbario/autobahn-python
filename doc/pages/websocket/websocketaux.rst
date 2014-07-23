*******************
WebSocket Auxiliary
*******************

The classes and functions here provide auxiliary and supporting
functionality to the WebSocket implementation.


URL Handling
============

.. autofunction:: autobahn.websocket.protocol.createWsUrl

.. autofunction:: autobahn.websocket.protocol.parseWsUrl


User Agents
===========

.. autofunction:: autobahn.websocket.useragent.lookupWsSupport


Traffic Statistics
==================

.. autoclass:: autobahn.websocket.protocol.Timings
   :members: __init__,
             track,
             diff

.. autoclass:: autobahn.websocket.protocol.TrafficStats
   :members: __init__,
             reset,
             __json__
