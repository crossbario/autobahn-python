Symmetric RPC
=============

RPC with WAMP works fully symmetric: clients can call procedures on servers and vice-versa.

This example demonstrates how to call endpoints on the client from the server.


Running
-------

Run the server by doing

    python server.py

To activate debug output on the server, start it

    python server.py debug

This will show up all WAMP messages exchanged between clients and server.

To run the Python client, do

    python client.py
