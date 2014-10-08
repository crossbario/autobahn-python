# Auto Reconnecting WebSocket Client

This example demonstrates a WebSocket client that automatically retries connecting when the server connection is lost (or could not be established in the first place).

The reconnection schedule is doing proper exponential backoff. Please see Twisted documentation for [ReconnectingClientFactory](http://twistedmatrix.com/documents/current/api/twisted.internet.protocol.ReconnectingClientFactory.html)

## Running

Start the server in a first terminal:

	python server.py

Now start the client in a second terminal:

	python client.py

Then stop the server. The client looses the connection. Restart the server. The client will automatically reconnect to the server.

You can also start the client before starting the server. The client will connect when the server comes up (upon next reconnection schedule).

