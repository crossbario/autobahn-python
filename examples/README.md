# Autobahn|Python Examples

This folder contains complete working code examples that demonstrate various features of **Autobahn**|Python:

 1. **Twisted**-based Examples
   * [WebSocket](twisted/websocket)
   * [WAMP](twisted/wamp)

2. **asyncio**-based Examples
   * [WebSocket](asyncio/websocket)
   * [WAMP](asyncio/wamp)

If you are new to Autobahn and WAMP, you should start with the following if you're going to use Twisted:

 * twisted/wamp/basic/pubsub/basic/*
 * twisted/wamp/basic/rpc/basic/*

...whereas if you prefer asyncio:

 * asyncio/wamp/basic/pubsub/basic/*
 * asycnio/wamp/basic/rpc/basic/*

Note that many of the examples use the same URIs for topics or RPC endpoints, so you can mix and match which `backend` or `frontend` script (whether Python or JavaScript) you use. For example, a Web browser tab could load a `backend.html` page that does publishes while you run a Python `frontend.py` that subscribes to those topics.

[Set up locally to run the examples](running-the-examples.md).
