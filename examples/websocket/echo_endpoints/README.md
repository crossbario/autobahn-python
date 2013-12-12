# Using Twisted Endpoints with WebSocket

[Twisted Endpoints](http://twistedmatrix.com/documents/current/core/howto/endpoints.html) allow for creation of stream-oriented connections completely decoupled from creation of factories and protocols.

Using endpoints, you can create connections from [server descriptor strings](http://twistedmatrix.com/documents/13.2.0/api/twisted.internet.endpoints.serverFromString.html) or [client descriptor strings](http://twistedmatrix.com/documents/13.2.0/api/twisted.internet.endpoints.clientFromString.html) which can be provided via command line arguments.

Autobahn now support Twisted endpoints, and this allows you to e.g. speak WebSocket not only over TCPv4, TCPv6 and TLS, but also over Unix domain sockets (and possible other endpoints).

This is nifty and flexible.

## Running

### TCP

To run the echo server on TCP:

	python server.py --websocket "tcp:9000"

To run the echo client over TCP:

	python client.py --websocket "tcp:localhost:9000"

### Unix Domain Sockets

To run the echo server on a Unix domain socket:

	python server.py --websocket "unix:/tmp/mywebsocket"

To run the echo client over the Unix domain socket:

	python client.py --websocket "unix:path=/tmp/mywebsocket"
