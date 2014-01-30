# WAMP v2 Demos

The examples in this folder serve to illustrate

* basic WAMP features applications can use
* deployment flexibility provided by Autobahn

WAMP on Autobahn allows to run application components in different deployment configurations:

![Application Code Deployment Options](app_code_depl_options.png)

## Running the Demos

All demos below use the same two example application containers:

 * [A WAMP/WebSocket server container](server.py)
 * [A WAMP/WebSocket client container](client.py)

The application code (the demos) is separate from above.

This allows to run all demos in different deployment configuration, as illustrated above.


### Router with embedded application backend component

Run the WAMP router/dealer on a WebSocket transport server, and start the embedded application backend:

	python server.py --component "rpc.timeservice.TimeServiceBackend"

Run the WAMP application frontend over a WebSocket transport client:

	python client.py --component "rpc.timeservice.TimeServiceFrontend"


### Application backend component in client

Run the WAMP router/dealer on a WebSocket transport server:

	python server.py

Run the WAMP application backend over a WebSocket transport client:

	python client.py --component "rpc.timeservice.TimeServiceBackend"

Run the WAMP application frontend over a WebSocket transport client:

	python client.py --component "rpc.timeservice.TimeServiceFrontend"


## Available Demos

### Remote Procedure Calls

#### Time Service

A trivial time service - demonstrates basic remote procedure feature.

 * `rpc.timeservice.TimeServiceBackend`
 * `rpc.timeservice.TimeServiceFrontend`

#### Procedure Arguments

Demonstrates all variants of call arguments.

 * `rpc.arguments.ArgumentsBackend`
 * `rpc.arguments.ArgumentsFrontend`

#### Complex Results

Demonstrates complex call results (call results with more than one positional or keyword results).

 * `rpc.complex.ComplexBackend`
 * `rpc.complex.ComplexFrontend` 

#### Handling Errors

Demonstrates error raising and catching over remote procedures.

 * `rpc.errors.ErrorsTestBackend`
 * `rpc.errors.ErrorsTestFrontend` 

#### Progressive Results

Demonstrates calling remote procedures that produce progressive results.

 * `rpc.progress.ProgressiveBackend`
 * `rpc.progress.ProgressiveFrontend` 

#### RPC Options

Using options with RPC.

 * `rpc.rpcoptions.RpcOptionsBackend`
 * `rpc.rpcoptions.RpcOptionsFrontend` 


### Publish & Subscribe

#### Time Service

Demonstrates basic publish and subscribe.

 * `pubsub.pubsub.PubSubTestBackend`
 * `pubsub.pubsub.PubSubTestFrontend`

#### Complex Events

Demonstrates publish and subscribe with complex events.

 * `pubsub.complex.ComplexEventTestBackend`
 * `pubsub.complex.ComplexEventTestFrontend`

#### PubSub Options

Using options with PubSub.

 * `pubsub.pubsuboptions.PubSubOptionsTestBackend`
 * `pubsub.pubsuboptions.PubSubOptionsTestFrontend`

#### Unsubscribing

Shows how to unsubscribe.

 * `pubsub.unsubscribe.UnsubscribeTestBackend`
 * `pubsub.unsubscribe.UnsubscribeTestFrontend`
