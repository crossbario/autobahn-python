Autobahn WebSockets
===================

Features
--------

Autobahn WebSockets for Python provides an implementation of the WebSockets
protocol which can be used to build WebSockets clients and servers.

   * supports RFC 6455 and Hybi-10+ protocol versions
   * supports RPC/PubSub over WebSockets (WAMP - see below)
   * usable for clients and servers
   * easy to use basic API
   * advanced API for frame-based/streaming processing
   * very good standards conformance (see below)
   * fully asynchronous Twisted-based implementation
   * supports secure WebSockets (TLS)
   * Open-source (Apache 2 license)


Browser Support
---------------

Native support:

   * Google Chrome 14+
   * Mozilla Firefox 7+
   * Microsoft Internet Explorer 10+
   * Safari/WebKit Nightly (as of March 2012)

Support via Adobe Flash 10+:

   * Microsoft Internet Explorer 8, 9
   * Google Chrome 4 - 13
   * Mozilla Firefox 3 - 6
   * Safari 5+

Support via Google Chrome Frame:

   * Microsoft Internet Explorer 6 - 9


RPC/PubSub over WebSocket (WAMP)
--------------------------------

Autobahn WebSockets also provides an implementation of the

   WebSocket Application Messaging Protocol (WAMP)
   http://autobahn.ws/wamp

which can be used to build applications around Remote Procedure Call
and Publish & Subscribe messaging patterns.

   * provides RPC and PubSub messaging
   * built on JSON and WebSockets
   * simple and open protocol
   * usable for clients and servers
   * companion client libraries for jQuery and Android


Testsuite
---------

Autobahn WebSockets also includes a WebSockets test suite which can used to
test client and server implementations for protocol conformance.

The Autobahn WebSockets Test Suite executes nearly 300 automated test cases
and has an extensive test coverage.

For current test reports and a list of users (over 20 projects/companies),
please visit:

   http://autobahn.ws/testsuite


Where to go
-----------

For more information, please visit: http://autobahn.ws

Get in touch on IRC #autobahn on chat.freenode.net or join the mailing
list on http://groups.google.com/group/autobahnws.
