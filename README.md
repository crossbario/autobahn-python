Autobahn WebSockets
===================

Autobahn WebSockets for Python provides an implementation of the WebSockets
protocol which can be used to build WebSockets clients and servers.

   * supports RFC 6455 and Hybi-10+ protocol versions
   * usable for clients and servers
   * easy to use basic API
   * advanced API for frame-based/streaming processing
   * very good standards conformance
   * fully asynchronous Twisted-based implementation
   * supports secure WebSockets (TLS)
   * Open-source (Apache 2 license)


Browser Support
---------------

   native support:
      * Google Chrome 14+
      * Mozilla Firefox 7+
      * Microsoft Internet Explorer 10+

   support via Adobe Flash 10+ (see below):
      * Microsoft Internet Explorer 8, 9
      * Safari 5


RPC/PubSub
----------

Autobahn WebSockets also provides an implementation of the

   WebSocket Application Messaging Protocol (WAMP)
   http://www.tavendo.de/autobahn/protocol.html

which can be used to build applications around Remote Procedure Call and
Publish & Subscribe messaging patterns.

   * provides RPC and PubSub messaging
   * built on JSON and WebSockets
   * simple and open protocol
   * usable for clients and servers
   * companion client libraries for jQuery and Android


Testsuite
---------

Autobahn WebSockets also includes a WebSockets test suite which can used to
test client and server implementations for protocol conformance.
The test suite includes nearly 300 test cases and has broad protocol coverage.


Using WebSocket Flash bridge
----------------------------

To use Autobahn with older browsers lacking WebSockets native support
(or only supporting an old protocol version), but having Adobe Flash 10+
installed, you will need to host the following 3 files from

   https://github.com/gimite/web-socket-js

   WebSocketMain.swf
   swfobject.js
   web_socket.js

on your web server (serving the HTML/JS opening the WebSocket connection)
and include the following (in this order!) in the HTML head element:

   <script type="text/javascript">
     WEB_SOCKET_SWF_LOCATION = "/path/to/WebSocketMain.swf";
   </script>

   <script src="/path/to/autobahn.js"></script>
   <script src="/path/to/swfobject.js"></script>
   <script src="/path/to/web_socket.js"></script>


Where to go
-----------

For more information, please visit: http://autobahn.ws
