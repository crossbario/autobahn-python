*******************
Twisted Integration
*******************

Autobahn|Python provides the following functions and classes for further Twisted integration.



Connect & Listen
================

* :func:`autobahn.twisted.websocket.connectWS`
* :func:`autobahn.twisted.websocket.listenWS`

|

Twisted Reactor
===============

* :func:`autobahn.twisted.choosereactor.install_optimal_reactor`
* :func:`autobahn.twisted.choosereactor.install_reactor`

|

Wrapping Factory & Protocol
===========================

You can find a complete example `here <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/wrapping>`__


* :class:`autobahn.twisted.websocket.WrappingWebSocketServerFactory`
* :class:`autobahn.twisted.websocket.WrappingWebSocketClientFactory`

|

Twisted Endpoints
=================

You can find a complete example `here <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_endpoints>`__

|

Twisted Web & WSGI
==================

AutobahnPython provides integration with Twisted Web via a special `WebSocketResource` that can be added to Twisted Web resource hierarchies.

You can find a complete example `here <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_site>`__

* :class:`autobahn.twisted.resource.WebSocketResource`
* :class:`autobahn.twisted.resource.HTTPChannelHixie76Aware`

|

The Twisted Web support of AutobahnPython also allows you add WebSocket as part of a WSGI application that runs under Twisted.

You can find a complete example `here <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_wsgi>`__

* :class:`autobahn.twisted.resource.WSGIRootResource`

|

Flash Policy Server
===================

You can find a complete example `here <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_wsfallbacks>`__


* :class:`autobahn.twisted.flashpolicy.FlashPolicyProtocol`
* :class:`autobahn.twisted.flashpolicy.FlashPolicyFactory`
