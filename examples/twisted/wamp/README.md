# WAMP Programming Examples

There are several very-similar examples that each follow a similar form and demonstrate several different ways of using WAMP under Autobahn. Each of these examples usually includes:

- backend.py: the logical "backend", in Python (registers procedures, publishes events)
- frontend.py: the logical "frontend", in Python (calls endpoints, receives events)
- frontend.js: similar version in JavaScript
- backend.js: similar version in JavaScript
- *.html: boilerplate to hold the .js

Note that any WAMP component can "do" all the roles (so a "backend" component can easily also call endpoints or listen for events) but we needed to separate things somehow. However, you can organize your components however you see fit.


## Simple Examples

1. RPC
  * [Arguments](rpc/arguments)
  * [Complex](rpc/complex)
  * [Decorators](rpc/decorators)
  * [Errors](rpc/errors)
  * [Options](rpc/options)
  * [Progress](rpc/progress)
  * [Slow Square](rpc/slowsquare)
  * [Time Service](rpc/timeservice)

2. PubSub
  * [Basic](pubsub/basic)
  * [Complex](pubsub/complex)
  * [Decorators](pubsub/decorators)
  * [Options](pubsub/options)
  * [Unsubscribe](pubsub/unsubscribe)

There also some more "real" examples, implemented as pluggable "WAMPlets". These also serve as skeletons to base your own WAMPlets from, should you wish to package components as illustrated.

3. Vote Game [votegame](wamplet/votegame)

A collaborative voting "game" to decide the most amazing fruit.

4. IRC Bot [wampirc](wamplet/wampirc)

Basically shows some simple bridging between IRC and WAMP, exporting private messages to the bot as WAMP publish()es.


## How to run

See [Running the Examples](../../running-the-examples.md)
