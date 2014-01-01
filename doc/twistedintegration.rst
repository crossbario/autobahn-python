*******************
Twisted Integration
*******************

Autobahn|Python provides the following functions and classes for further Twisted integration.



Connect & Listen
================

.. autofunction:: autobahn.twisted.websocket.connectWS

.. autofunction:: autobahn.twisted.websocket.listenWS

|

Twisted Reactor
===============

.. autofunction:: autobahn.twisted.choosereactor.install_optimal_reactor

.. autofunction:: autobahn.twisted.choosereactor.install_reactor

|

Wrapping Factory & Protocol
===========================

You can find a complete example `here <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/wrapping>`_


.. autoclass:: autobahn.twisted.websocket.WrappingWebSocketServerFactory
   :show-inheritance:
   :members: __init__

.. autoclass:: autobahn.twisted.websocket.WrappingWebSocketClientFactory
   :show-inheritance:
   :members: __init__

|

Twisted Endpoints
=================

You can find a complete example `here <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/echo_endpoints>`_

|

Twisted Web & WSGI
==================

AutobahnPython provides integration with Twisted Web via a special `WebSocketResource` that can be added to Twisted Web resource hierarchies.

You can find a complete example `here <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/echo_site>`_

.. autoclass:: autobahn.twisted.resource.WebSocketResource
   :members: __init__,
             getChildWithDefault,
             putChild,
             render

.. autoclass:: autobahn.twisted.resource.HTTPChannelHixie76Aware

|

The Twisted Web support of AutobahnPython also allows you add WebSocket as part of a WSGI application that runs under Twisted.

You can find a complete example `here <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/echo_wsgi>`_

.. autoclass:: autobahn.twisted.resource.WSGIRootResource
   :members: __init__

|

Flash Policy Server
===================

You can find a complete example `here <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/echo_wsfallbacks>`_


.. autoclass:: autobahn.twisted.flashpolicy.FlashPolicyProtocol
   :members: __init__

.. autoclass:: autobahn.twisted.flashpolicy.FlashPolicyFactory
   :members: __init__
