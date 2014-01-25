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

A trivial time service - demonstrates basic remote procedure feature.

 * `timeservice.TimeServiceBackend`
 * `timeservice.TimeServiceFrontend`

### Procedure Arguments

Demonstrates all variants of call arguments.

 * `arguments.ArgumentsBackend`
 * `arguments.ArgumentsFrontend`

### Complex Results

Demonstrates complex call results (call results with more than one positional or keyword results).

 * `complex.ComplexBackend`
 * `complex.ComplexFrontend` 

### Handling Errors

Demonstrates error raising and catching over remote procedures.

 * `errors.ErrorsTestBackend`
 * `errors.ErrorsTestFrontend` 

### Progressive Results

Demonstrates calling remote procedures that produce progressive results.

 * `progress.ProgressiveBackend`
 * `progress.ProgressiveFrontend` 
