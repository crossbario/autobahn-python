WebSocket & WAMP for Python on Twisted and asyncio
==================================================

**Autobahn|Python** is a subproject of `Autobahn <https://crossbar.io/autobahn>`__
and provides open-source implementations of:

* `The WebSocket Protocol <https://tools.ietf.org/html/rfc6455>`__
* `The Web Application Messaging Protocol (WAMP) <https://wamp-proto.org/>`__

for Python 3.9+, running on `Twisted <https://twisted.org/>`__ and `asyncio <https://docs.python.org/3/library/asyncio.html>`__.

You can use **Autobahn|Python** to create clients and servers in Python speaking
just plain WebSocket or WAMP.

WebSocket allows `bidirectional real-time messaging on the Web <https://crossbario.com/blog/post/websocket-why-what-can-i-use-it/>`__
while `WAMP <https://wamp-proto.org/>`__ provides applications with
`high-level communication abstractions <https://wamp-proto.org/comparison.html>`__
(remote procedure calling and publish/subscribe) in an open standard WebSocket-based protocol.

Contents
--------

.. toctree::
   :maxdepth: 3

   installation
   wheels-inventory
   asynchronous-programming
   websocket/programming
   websocket/examples
   websocket/conformance
   wamp/programming
   wamp/flatbuffers-schema
   wamp/message-design
   wamp/aio-repl
   wamp/examples
   environments/index
   OVERVIEW.md
   ai/index

Releases
--------

.. toctree::
   :maxdepth: 2

   release-notes
   changelog
