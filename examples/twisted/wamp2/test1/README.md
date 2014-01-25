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

### Time Service

 * `timeservice.TimeServiceBackend`
 * `timeservice.TimeServiceFrontend`

### Procedure Arguments

 * `arguments.ArgumentsBackend`
 * `arguments.ArgumentsFrontend`

### Complex Results

 * `complex.ComplexBackend`
 * `complex.ComplexFrontend` 

### Handling Errors

 * `errors.ErrorsTestBackend`
 * `errors.ErrorsTestFrontend` 

### Progressive Results

 * `progress.ProgressiveBackend`
 * `progress.ProgressiveFrontend` 
