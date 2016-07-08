.. _websocket_examples:

WebSocket Examples
==================

Basic Examples
--------------

.. note::
   The examples here demonstrate WebSocket programming with |ab| and are available in Twisted and asyncio-based variants respectively.

Echo
....

`Twisted <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo>`__  / `asyncio <https://github.com/crossbario/autobahn-python/blob/master/examples/asyncio/websocket/echo>`__

A simple WebSocket echo server and client.

Slow Square
............

`Twisted <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/slowsquare>`__  / `asyncio <https://github.com/crossbario/autobahn-python/blob/master/examples/asyncio/websocket/slowsquare>`__

This example shows a WebSocket server that will receive a JSON encode float over WebSocket, slowly compute the square, and send back the result.
The example is intended to demonstrate how to use co-routines inside WebSocket handlers.


Testee
......

`Twisted <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/testee>`__  / `asyncio <https://github.com/crossbario/autobahn-python/blob/master/examples/asyncio/websocket/testee>`__

The example implements a *testee* for testing against `Autobahn|Testsuite <http://crossbar.io/autobahn#testsuite>`_.

-----------


Additional Examples
-------------------

.. note::
   The examples here demonstrate various further features and aspects of WebSocket programming with |ab|. However, these examples are **currently only available for Twisted**.


Secure WebSocket
................

`Twisted <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_tls>`__

How to run WebSocket over TLS ("wss").


WebSocket and Twisted Web
.........................

`Twisted <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_site>`__

How to run WebSocket under Twisted Web. This is a very powerful feature, as it allows you to create a complete HTTP(S) resource hierarchy with different services like static file serving, REST and WebSocket combined under one server.


Twisted Web, WebSocket and WSGI
...............................

`Twisted <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_wsgi>`__

This example shows how to run Flask (or any other WSGI compliant Web thing) under Twisted Web and combine that with WebSocket.


Secure WebSocket and Twisted Web
................................

`Twisted <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_site_tls>`__

A variant of the previous example that runs a HTTPS server with secure WebSocket on a subpath.


WebSocket Ping-Pong
...................

`Twisted <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/ping>`__

The example demonstrates how to trigger and process WebSocket pings and pongs.


More
....

* `WebSocket Authentication with Mozilla Persona <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/auth_persona>`_
* `Broadcasting over WebSocket <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/broadcast>`_
* `WebSocket Compression <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_compressed>`_
* `WebSocket over Twisted Endpoints <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_endpoints>`_
* `Using HTTP Headers with WebSocket <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_httpheaders>`_
* `WebSocket on Multicore <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_multicore>`_
* `WebSocket as a Twisted Service <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_service>`_
* `WebSocket Echo Variants <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_variants>`_
* `WebSocket Fallbacks <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/echo_wsfallbacks>`_
* `Using multiple WebSocket Protocols <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/multiproto>`_
* `Streaming WebSocket <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/streaming>`_
* `Wrapping Twisted Protocol/Factories over WebSocket <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/websocket/wrapping>`_
* `Using wxPython with Autobahn <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/wxpython>`_
