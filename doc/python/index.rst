Autobahn WebSockets for Python Documentation
============================================

WebSockets Features
-------------------

*Autobahn WebSockets for Python* provides an implementation of the WebSockets protocol
which can be used to build WebSockets clients and servers.

   * supports Hybi-10 - Hybi-17 protocol versions
   * usable for clients and servers
   * easy to use basic API
   * advanced API for frame-based/streaming processing
   * very good `standards conformance <http://www.tavendo.de/autobahn/testsuite.html>`_
   * fully asynchronous `Twisted-based <http://twistedmatrix.com>`_ implementation
   * supports secure WebSockets (TLS)
   * Open-source (Apache 2 license)



RPC/PubSub Features
-------------------

Additionally, *Autobahn WebSockets for Python* provides an implementation of the
`WebSocket Application Messaging Protocol (WAMP) <http://www.tavendo.de/autobahn/protocol.html>`_ protocol.

Building on WAMP, Autobahn WebSockets can be used to create applications around
**Remote Procedure Call** and **Publish & Subscribe** messaging patterns.

   * includes Autobahn RPC/PubSub, an implementation of `WAMP <http://www.tavendo.de/autobahn/protocol.html>`_
   * simple and open protocol
   * built on *JSON* and *WebSockets*
   * provides RPC and PubSub messaging
   * usable for clients and servers
   * companion client libraries for jQuery and Android


Contents
--------

.. toctree::
   :maxdepth: 2

   websocketintro
   websocketprotocol
   websocketclient
   websocketserver
   wamp


Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
