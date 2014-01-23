# WAMP v2 Demo

## WAMP Router with embedded application backend

Run the WAMP router/dealer on a WebSocket transport server, and start the embedded application backend:

	python server.py --backend

Run the WAMP application frontend over a WebSocket transport client:

	python client.py


## WAMP Router with application backend on client

Run the WAMP router/dealer on a WebSocket transport server:

	python server.py

Run the WAMP application backend over a WebSocket transport client:

	python client.py --backend

Run the WAMP application frontend over a WebSocket transport client:

	python client.py

