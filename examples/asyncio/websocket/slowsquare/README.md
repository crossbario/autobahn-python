# WebSocket "Slow-Square" (Asyncio-based)

This example shows a WebSocket server that will receive a JSON encode float over WebSocket, slowly compute the square, and send back the result.

This example is intended to demonstrate how to use coroutines inside WebSocket handlers.

> This example uses the Asyncio integration of **Autobahn**|Python. You can find the corresponding example using the Twisted integration [here](https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/slowsquare).
> 

## Running

Run the server (Python 3)

    python server.py

or (Python 2)

    python server_py2.py

To run the Python client (both Python 3 and 2)

    python client.py
