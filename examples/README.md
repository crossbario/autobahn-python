# Autobahn|Python Examples

This folder contains complete working code examples that demonstrate various features of **Autobahn**|Python:

 1. **Twisted**-based Examples
   * [WebSocket](twisted/websocket/README.md)
   * [WAMP](twisted/wamp/README.md)

2. **asyncio**-based Examples
   * [WebSocket](asyncio/websocket/README.md)
   * [WAMP](asyncio/wamp/README.md)

If you are new to Autobahn and WAMP, you should start with the following if you're going to use Twisted:

 * twisted/wamp/pubsub/basic/
 * twisted/wamp/rpc/arguments/

...whereas if you prefer asyncio:

 * asyncio/wamp/pubsub/basic/
 * asyncio/wamp/rpc/arguments/

Note that many of the examples use the same URIs for topics or RPC endpoints, so you can mix and match which `backend` or `frontend` script (whether Python or JavaScript) you use. For example, a Web browser tab could load a `backend.html` page that does publishes while you run a Python `frontend.py` that subscribes to those topics.

[Set up locally to run the examples](running-the-examples.md).
