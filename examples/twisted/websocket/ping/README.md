WebSocket Ping Server and Client
================================

This example runs a WebSocket server that pings any connected WebSocket
client every second (via WebSocket Ping frames).

Included is a HTML and a Python client.

*This example uses secure WebSocket (TLS).*


Running
-------

Run the server by doing

    python server.py

and open

    https://localhost:8080/

in your browser.

To run the Python client, do

    python client.py wss://localhost:9000
