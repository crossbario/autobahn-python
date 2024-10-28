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

### Clients

The following examples show two alternative ways of connecting a WAMP client to a WAMP router. This code is also a good starting point for own apps.

 * [WAMP clients using AppRunner](client_using_apprunner.py)
 * [WAMP clients using Twisted ClientService](client_using_clientservice.py)

### Overview Examples
 * [LoopingCall](overview): shows an alternative way of publishing periodically

### RPC Examples

  * [Arguments](rpc/arguments): different types of argument-passing
  * [Complex](rpc/complex): complex return types
  * [Decorators](rpc/decorators): register RPC methods using decorators
  * [Errors](rpc/errors): map custom error classes to WAMP URIs
  * [Options](rpc/options): show some RegistrationOptions and CallOptions use
  * [Progress](rpc/progress): progressive results for long-running operations
  * [Slow Square](rpc/slowsquare): an RPC call that takes some time
  * [Time Service](rpc/timeservice): XXX delete?

### PubSub Examples

  * [Basic](pubsub/basic): publish to a topic once per second
  * [Complex](pubsub/complex): demonstrates different payload arguments
  * [Decorators](pubsub/decorators): doing subscriptions with decorators
  * [Options](pubsub/options): use of PublishOptions and SubscribeOptions
  * [Unsubscribe](pubsub/unsubscribe): listen to events for a limited time

### App Examples

_We still need to explain these. For starters, here's the list:_

  * [Calculator](app/calculator): _to be explained..._
  * [Crochet](app/crochet): _to be explained..._
  * [DBus](app/dbus): _to be explained..._
  * [Hello](app/hello): _to be explained..._
  * [Keyvalue](app/keyvalue): _to be explained..._
  * [Klein](app/klein): _to be explained..._
  * [Serial2ws](app/serial2ws): _to be explained..._
  * [Subscribe upon call](app/subscribe_upon_call): _to be explained..._

## How to run

See [Running the Examples](../../running-the-examples.md)
