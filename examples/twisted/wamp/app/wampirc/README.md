# WAMP IRC

WAMPlet that provides IRC bot services to applications.

The component bridges IRC and [WAMP](http://wamp.ws). It exposes IRC to WAMP, e.g. there are RPC endpoints for starting a bot, joining channels, listening for activity, and publishing IRC activity as WAMP PubSub events.

It is written as a WAMPlet, a reusable WAMP-based application component, that can be run connecting to any WAMP router (e.g. [**Crossbar**.io](https://github.com/crossbario/crossbar/wiki)). The component can be started directly, or WAMP routers capable of *hosting* WAMPlets can run the component under supervision.

## Try it

Start up a WAMP router in a first terminal - e.g. **Crossbar**.io:

```shell
crossbar init
crossbar start
```

Run the WAMPlet from the local directory:

```shell
PYTHONPATH="." python wampirc/service.py
```

Open the test console `test/index.html` in your browser to control the component.
