# WebSocket over Stream-based Endpoints

[Twisted Endpoints](http://twistedmatrix.com/documents/current/core/howto/endpoints.html) allow for creation of stream-oriented connections completely decoupled from creation of factories and protocols.

Using endpoints, you can create connections from [server descriptor strings](http://twistedmatrix.com/documents/13.2.0/api/twisted.internet.endpoints.serverFromString.html) or [client descriptor strings](http://twistedmatrix.com/documents/13.2.0/api/twisted.internet.endpoints.clientFromString.html) which can be provided via command line arguments.

**Autobahn**|Python now supports Twisted endpoints, and this allows you to speak WebSocket not only over

 * TCPv4,
 * TCPv6 and
 * TLS,

but also over

 * Unix domain sockets
 * Pipes to talk to Processes (modulo [this](https://twistedmatrix.com/trac/ticket/5813))
 * Serial (modulo [this](https://twistedmatrix.com/trac/ticket/4847))

and possible other endpoints. This is nifty and flexible.

> This example is about running WebSocket over different stream-based Twisted endpoints.
> **Autobahn**|Python also supports running any stream-based Twisted endpoint over WebSocket (which in turn runs over any stream-based underlying Twisted endpoint). Please see [here](https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/wrapping).
> 

## Running WebSocket over TCP

To run the echo server on TCP:

	python server.py --websocket "tcp:9000"

To run the echo client over TCP:

	python client.py --websocket "tcp:localhost:9000"

## Running WebSocket over Unix Domain Sockets

To run the echo server on a Unix domain socket:

	python server.py --websocket "unix:/tmp/mywebsocket"

To run the echo client over the Unix domain socket:

	python client.py --websocket "unix:path=/tmp/mywebsocket"
