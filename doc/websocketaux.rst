Auxiliary
=========

The classes and functions here provide auxiliary and supporting
functionality to the WebSocket implementation.


Connect & Listen
----------------

.. autofunction:: autobahn.websocket.connectWS

.. autofunction:: autobahn.websocket.listenWS


URL Handling
------------

.. autofunction:: autobahn.websocket.createWsUrl

.. autofunction:: autobahn.websocket.parseWsUrl


Opening Handshake
-----------------

.. autoclass:: autobahn.websocket.ConnectionRequest
   :members: __init__

.. autoclass:: autobahn.websocket.ConnectionResponse
   :members: __init__

.. autoclass:: autobahn.websocket.HttpException
   :members: __init__


Twisted Web Integration
-----------------------

.. autoclass:: autobahn.resource.WebSocketResource
   :members: __init__,
             getChildWithDefault,
             putChild,
             render

.. autoclass:: autobahn.resource.WSGIRootResource
   :members: __init__

.. autoclass:: autobahn.resource.HTTPChannelHixie76Aware


Flash Policy File Server
------------------------

.. autoclass:: autobahn.flashpolicy.FlashPolicyProtocol
   :members: __init__

.. autoclass:: autobahn.flashpolicy.FlashPolicyFactory
   :members: __init__


Misc
----

.. autofunction:: autobahn.useragent.lookupWsSupport

.. autoclass:: autobahn.websocket.Timings
   :members: __init__,
             track,
             diff
