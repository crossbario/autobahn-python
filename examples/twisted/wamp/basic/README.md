# WAMP v2 Examples

The examples in this folder serve to illustrate **[WAMP version 2](https://github.com/tavendo/WAMP/blob/master/spec/README.md)** on [**Autobahn**|Python](http://autobahn.ws/):

* WAMP **RPC** and **PubSub** features for application use
* example WAMP **application components** and **routers**

# Application Component Deployment

**[WAMP v2](https://github.com/tavendo/WAMP/blob/master/spec/README.md)** on [**Autobahn**|Python](http://autobahn.ws/) allows to run application components in different deployment configurations without any changes to application code:

![Application Code Deployment Options](app_code_depl_options.png)

## Running the Demos

All demos use the same two example application routers to host the application components for a demo:

 * [A WAMP/WebSocket server container](server.py)
 * [A WAMP/WebSocket client container](client.py)

The application components of the demos are separate from the example application routres, and each application component demonstrates a different RPC or PubSub feature.

### Router with embedded application backend component

Run the example application router on a WebSocket transport server and start a demo "backend" application component inside the router:

	python server.py --component "rpc.timeservice.TimeServiceBackend"

Run the demo "frontend" application component over a WebSocket transport client:

	python client.py --component "rpc.timeservice.TimeServiceFrontend"


### Application backend component in client

Run the example application router on a WebSocket transport server:

	python server.py

Run the demo "backend" application component over a WebSocket transport client:

	python client.py --component "rpc.timeservice.TimeServiceBackend"

Run the demo "frontend" application component over a WebSocket transport client:

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


### Session

#### Series of Sessions

Demonstrates how multiple sessions can exist during the lifetime of the underlying transport.

 * `session.series.SeriesTestBackend`
 * `session.series.SeriesTestFrontend`


## AutobahnJS-based Demos

In addition, the demo front- and backends are available as AutobahnJS-based versions to run in browsers and NodeJS.

For example, run the example application router on a WebSocket transport server and start a demo "backend" application component inside the router:

	python server.py --component "rpc.timeservice.TimeServiceBackend"

Then, open the JavaScript frontend in a browser:

    rpc/timeservice_frontend.html

To run the frontend from NodeJS, install AutobahnJS

	npm install autobahn
	npm install when

and then

	node rpc/timeservice_frontend.js

To run the backend in NodeJS, run the plain router

	python server.py

and then start the backend:

	node rpc/timeservice_backend.js
