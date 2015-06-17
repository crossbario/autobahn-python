# WAMP Programming Examples

There are several very-similar examples that each follow a similar form and demonstrate several different ways of using WAMP under Autobahn. Each of these examples usually includes:

- backend.py: the logical "backend", in Python (registers procedures, publishes events)
- frontend.py: the logical "frontend", in Python (calls endpoints, receives events)
- frontend.js: similar version in JavaScript
- backend.js: similar version in JavaScript
- *.html: boilerplate to hold the .js

Note that any WAMP component can "do" all the roles (so a "backend" component can easily also call endpoints or listen for events) but we needed to separate things somehow. However, you can organize your components however you see fit.

For examples using RPC, you need to run the backend first, so that procedures are registered and available to call.

## The Examples

### RPC Examples

  * [Arguments](rpc/arguments): different types of argument-passing
  * [Complex](rpc/complex): complex return types
  * [Decorators](rpc/decorators): register RPC methods using decorators
  * [Errors](rpc/errors): map custom error classes to WAMP URIs
  * [Options](rpc/options): show some RegistrationOptions and CallOptions use
  * [Progress](rpc/progress): progressive results for long-running oprations
  * [Slow Square](rpc/slowsquare): an RPC call that takes some time
  * [Time Service](rpc/timeservice): XXX delete?

### PubSub Examples

  * [Basic](pubsub/basic): publish to a topic once per second
  * [Complex](pubsub/complex): demonstrates different payload arguments
  * [Decorators](pubsub/decorators): doing subscriptions with decorators
  * [Options](pubsub/options): use of PublishOptions and SubscribeOptions
  * [Unsubscribe](pubsub/unsubscribe): listen to events for a limited time

There also some larger examples, implemented as pluggable "WAMPlets". These can also serve as skeletons to base your own WAMPlets from, should you wish to package components like this.

### Vote Game

The [votegame](wamplet/votegame) example is a collaborative voting "game" to decide the most amazing fruit. Updates votes amongst all clients in realtime.

### IRC Bot

The [wampirc](wamplet/wampirc) example shows some simple bridging between IRC and WAMP, exporting private messages to the bot as WAMP publish()-es.


## How to run

See [Running the Examples](../../running-the-examples.md)
