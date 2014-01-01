Auxiliary
=========

The classes and functions here provide auxiliary and supporting
functionality to the WebSocket implementation.


Connect & Listen
----------------

.. autofunction:: autobahn.twisted.websocket.connectWS

.. autofunction:: autobahn.twisted.websocket.listenWS


URL Handling
------------

.. autofunction:: autobahn.websocket.protocol.createWsUrl

.. autofunction:: autobahn.websocket.protocol.parseWsUrl


Opening Handshake
-----------------

.. autoclass:: autobahn.websocket.http.HttpException
   :members: __init__


Twisted Web Integration
-----------------------

.. autoclass:: autobahn.twisted.resource.WebSocketResource
   :members: __init__,
             getChildWithDefault,
             putChild,
             render

.. autoclass:: autobahn.twisted.resource.WSGIRootResource
   :members: __init__

.. autoclass:: autobahn.twisted.resource.HTTPChannelHixie76Aware


Flash Policy File Server
------------------------

.. autoclass:: autobahn.twisted.flashpolicy.FlashPolicyProtocol
   :members: __init__

.. autoclass:: autobahn.twisted.flashpolicy.FlashPolicyFactory
   :members: __init__


Misc
----

.. autofunction:: autobahn.websocket.useragent.lookupWsSupport

.. autoclass:: autobahn.websocket.protocol.Timings
   :members: __init__,
             track,
             diff

.. autoclass:: autobahn.websocket.protocol.TrafficStats
   :members: __init__,
             reset,
             __json__
