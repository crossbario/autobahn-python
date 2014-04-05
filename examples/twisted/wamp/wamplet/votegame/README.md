This example demonstrates the use of databases (e.g. SQLite or PostgreSQL) from WAMP application components. The example is a simple voting app packaged up as a **WAMPlet** application component.

A **WAMPlet** can be thought of a reusable application component that can be deployed dynamically as needed.

Get started by copying this folder and it's contents and begin by modifying a working base line.

## Try it

All the interesting bits with our application component are in [here](votegame/backend.py).

For development, start a locally running WAMP router, e.g. **Crossbar**.io:

```shell
cd $HOME
crossbar init
crossbar start
```

and in a second terminal run the file containing the application component:

```shell
python votegame/backend.py
```

In your browser, open the file `votegame/web/index.html`.

## Deploying

You can deploy your WAMPlet to a WAMPlet container for production.

Here is a configuration for [**Crossbar**.io](http://crossbar.io) which runs a WAMP router, loads the VoteGame backend component and serves static Web content from the VoteGame package:

```javascript
{
   "processes": [
      {
         "type": "router",
         "realms": {
            "realm1": {
               "permissions": {
                  "anonymous": {
                     "create": true,
                     "join": true,
                     "access": {
                        "*": {
                           "publish": true,
                           "subscribe": true,
                           "call": true,
                           "register": true
                        }
                     }
                  }
               },
               "components": [
                  {
                     "type": "wamplet",
                     "dist": "votegame",
                     "entry": "backend",
                     "extra": {
                        "dbfile": "votegame.db",
                        "items": ["banana", "lemon", "grapefruit"]
                     }
                  }
               ]
            }
         },
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
                     "module": "votegame",
                     "resource": "web"
                  },
                  "ws": {
                     "type": "websocket",
                     "url": "ws://localhost:8080/ws"
                  }
               }
            }
         ]
      }
   ]
}
```

