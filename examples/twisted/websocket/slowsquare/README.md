# WebSocket "Slow-Square" (Twisted-based)

This example shows a WebSocket server that will receive a JSON encode float over WebSocket, slowly compute the square, and send back the result.

This example is intended to demonstrate how to use coroutines inside WebSocket handlers.

> This example uses the Twisted integration of **Autobahn**|Python. You can find the corresponding example using the Asyncio integration [here](https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/websocket/slowsquare).
> 

## Running

Run the server

    python server.py

To run the Python client

    python client.py
