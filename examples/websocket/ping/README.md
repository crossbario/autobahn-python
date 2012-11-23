WebSocket Ping Server and Client
================================

This example runs a WebSocket server that pings any connected WebSocket
client every second (via WebSocket Ping frames).

Included is a HTML and a Python client.


Running
-------

Run the server by doing

    python server.py

and open

    http://localhost:8080/

in your browser.

To run the Python client, do

    python client.py ws://localhost:9000

For both server and client you can add `debug` to the command line to **activate wire logging** of all sent and received WebSocket messages.



