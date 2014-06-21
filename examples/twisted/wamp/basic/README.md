# WAMP Programming Examples

## Examples

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


## Hosting

Crossbar.io is a WAMP router that can also act as a host for WAMP application components. E.g. to let Crossbar.io host a backend application component, you can use a node configuration like this:

```javascript

{
   "controller": {
   },
   "workers": [
      {
         "type": "router",
         "options": {
            "pythonpath": ["f:\\scm\\tavendo\\autobahn\\AutobahnPython\\examples\\twisted\\wamp\\basic"]
         },
         "realms": [
            {
               "name": "realm1",
               "roles": [
                  {
                     "name": "anonymous",
                     "permissions": [
                        {
                           "uri": "*",
                           "publish": true,
                           "subscribe": true,
                           "call": true,
                           "register": true
                        }
                     ]
                  }
               ]
            }
         ],
         "components": [
            {
               "type": "class",
               "classname": "pubsub.complex.backend.Component",
               "realm": "realm1"
            }
         ],
         "transports": [
            {
               "type": "web",
               "endpoint": {
                  "type": "tcp",
                  "port": 8080
               },
               "paths": {
                  "/": {
                     "type": "static",
                     "directory": ".."
                  },
                  "ws": {
                     "type": "websocket"
                  }
               }
            }
         ]
      }
   ]
}
```