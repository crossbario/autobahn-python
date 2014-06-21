# WAMP Programming Examples

## Examples

1. RPC
  * [Arguments](rpc/arguments)
  * Complex
  * Decorators
  * Errors
  * Options
  * Progress
  * Slow Square
  * Time Service
2. PubSub
  * Basic
  * Complex
  * Decorators
  * Options
  * Unsubscribe


## How to run

To run the following examples, you need a WAMP router.

For example, you can use the included basic WAMP router by doing

```shell
python basicrouter.py
```

Or you can use [Crossbar.io](http://crossbar.io):

```shell
mkdir mynode
cd mynode
crossbar init
crossbar start
```

The examples usually contain two components:

 * frontend
 * backend

Each component is provided in two languages:

 * Python
 * JavaScript

The JavaScript version can run on the browser or in NodeJS.

To run an example, you can have three terminal sessions open with:

 1. router
 2. frontend
 3. backend

E.g. the Python examples can be run

```shell
cd pubsub/basic
python backend.py
```
