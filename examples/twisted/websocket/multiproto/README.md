# Running multiple WebSocket services

This example demonstrates how to run multiple, different WebSocket services in one server on one port.


## Service Wrapper

This example shows how to choose the service to be used in `onConnect` of a wrapping `webSocketServerProtocol`.

This method has the advantage of being able to choose the service to be used using any information from the initial WebSocket opening handshake.

Run the server

	python server1.py

Run the client with different WebSocket URLs:

	python client.py ws://127.0.0.1:9000/echo1
	python client.py ws://127.0.0.1:9000/echo2


## Twisted Web

AutobahnPython based WebSocket servers can run under Twisted Web as a resource.

This is quite flexible and allows to mix different services like static file serving, WSGI servers (like Flask) and AutobahnPython-based WebSocket or WAMP servers all under one server and port.

Run the server

	python server2.py

Run the client with different WebSocket URLs:

	python client.py ws://127.0.0.1:9000/echo1
	python client.py ws://127.0.0.1:9000/echo2
	
This method has the disadvantage compared to the other option in that you cannot choose your service dependent on WebSocket specific details from the WebSocket opening handshake like i.e. WebSocket subprotocol.