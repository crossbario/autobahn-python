# WebSocket Echo (Asyncio-based)

This example shows a WebSocket echo server that will echo back any WebSocket message it receives to the client that sent the message.

It also includes a WebSocket client that will send a WebSocket message every second to the server it connected to. The Python client is available in two variants.

Lastly, a HTML5 client is also included.

This example uses the Asyncio integration of **Autobahn**|Python. You can find the corresponding example using the Twisted integration [here](https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo).

## Running

Run the server:

    python server.py

and open

    client.html

in your browser.

To run the Python client

    python client.py ws://127.0.0.1:9000

or (Python 3)

    python client_coroutines.py ws://127.0.0.1:9000

or (Python 2)

    python client_coroutines_py2.py ws://127.0.0.1:9000
