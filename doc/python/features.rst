Features
========

WebSocket
---------

*AutobahnPython* provides an implementation of the WebSocket protocol
which can be used to create WebSocket clients and servers.

   * implements `RFC6455 <http://tools.ietf.org/html/rfc6455>`_ (and Draft Hybi-10 to -17)
   * framework for clients and servers
   * easy to use basic API
   * advanced API for frame-based/streaming processing
   * very good `standards conformance <http://autobahn.ws/testsuite>`_
   * fully asynchronous `Twisted-based <http://twistedmatrix.com>`_ implementation
   * supports secure WebSocket (TLS)
   * Open-source (Apache 2 license)


RPC & PubSub (WAMP)
-------------------

Additionally, *AutobahnPython* provides an implementation of the
`The WebSocket Application Messaging Protocol (WAMP) <http://wamp.ws>`_.

Building on WAMP, AutobahnPython can be used to create applications around the
**Remote Procedure Call** and **Publish & Subscribe** messaging patterns.

   * implements `WAMP <http://wamp.ws>`_
   * provides asynchronous RPC and PubSub messaging
   * fully compatible with AutobahnJS and AutobahnAndroid (other WAMP impl.)
   * simple and open protocol
   * built on *JSON* and *WebSocket*
   * usable for clients and servers
