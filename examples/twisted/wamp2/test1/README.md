# WAMP v2 Demos

## Running the Demos

### Router with embedded application backend component

Run the WAMP router/dealer on a WebSocket transport server, and start the embedded application backend:

	server.py --component "timeservice.TimeServiceBackend"

Run the WAMP application frontend over a WebSocket transport client:

	client.py --component "timeservice.TimeServiceFrontend"


### Application backend component in client

Run the WAMP router/dealer on a WebSocket transport server:

	python server.py

Run the WAMP application backend over a WebSocket transport client:

	client.py --component "timeservice.TimeServiceBackend"

Run the WAMP application frontend over a WebSocket transport client:

	client.py --component "timeservice.TimeServiceFrontend"


## Available Demos


 1. `timeservice.TimeServiceBackend` and `timeservice.TimeServiceFrontend`
 2. `arguments.ArgumentsBackend` and `arguments.ArgumentsFrontend`
 3. `progress.ProgressiveBackend` and `progress.ProgressiveFrontend` 

