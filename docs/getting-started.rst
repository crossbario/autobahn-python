Getting Started
===============

This guide will help you get started with **Autobahn|Python** quickly.

Prerequisites
-------------

* Python 3.9 or later
* pip (Python package installer)

Quick Installation
------------------

.. code-block:: bash

    # For asyncio
    pip install autobahn

    # For Twisted
    pip install autobahn[twisted]

WebSocket Quick Start
---------------------

Here's a simple WebSocket echo server using asyncio:

.. code-block:: python

    import asyncio
    from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

    class MyServerProtocol(WebSocketServerProtocol):
        def onMessage(self, payload, isBinary):
            # Echo back the message
            self.sendMessage(payload, isBinary)

    async def main():
        factory = WebSocketServerFactory("ws://127.0.0.1:9000")
        factory.protocol = MyServerProtocol

        loop = asyncio.get_event_loop()
        server = await loop.create_server(factory, '127.0.0.1', 9000)
        print("WebSocket server running on ws://127.0.0.1:9000")
        await server.serve_forever()

    asyncio.run(main())

And a client to connect to it:

.. code-block:: python

    import asyncio
    from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

    class MyClientProtocol(WebSocketClientProtocol):
        def onOpen(self):
            self.sendMessage(b"Hello, WebSocket!")

        def onMessage(self, payload, isBinary):
            print(f"Received: {payload.decode('utf8')}")
            self.sendClose()

    async def main():
        factory = WebSocketClientFactory("ws://127.0.0.1:9000")
        factory.protocol = MyClientProtocol

        loop = asyncio.get_event_loop()
        transport, protocol = await loop.create_connection(factory, '127.0.0.1', 9000)

    asyncio.run(main())

WAMP Quick Start
----------------

Here's a simple WAMP component that registers a procedure and subscribes to a topic:

.. code-block:: python

    from autobahn.asyncio.component import Component, run

    component = Component(
        transports="ws://127.0.0.1:8080/ws",
        realm="realm1",
    )

    @component.register("com.example.add")
    async def add(a, b):
        return a + b

    @component.subscribe("com.example.topic")
    async def on_event(msg):
        print(f"Received event: {msg}")

    @component.on_join
    async def joined(session, details):
        print("Joined realm!")
        # Call our own procedure
        result = await session.call("com.example.add", 2, 3)
        print(f"2 + 3 = {result}")

    run([component])

.. note::

    WAMP requires a router like `Crossbar.io <https://crossbar.io>`__ to be
    running. See the Crossbar.io documentation for setup instructions.

Using with Twisted
------------------

The same code works with Twisted by changing the imports:

.. code-block:: python

    # Instead of:
    from autobahn.asyncio.websocket import WebSocketServerProtocol

    # Use:
    from autobahn.twisted.websocket import WebSocketServerProtocol

Next Steps
----------

* :doc:`installation` - Detailed installation options
* :doc:`programming-guide/index` - Comprehensive programming guides
* :doc:`programming-guide/websocket/index` - WebSocket programming
* :doc:`programming-guide/wamp/index` - WAMP programming
