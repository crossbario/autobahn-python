Authentication of WAMP Sessions
===============================

WAMP Challenge-Response-Authentication ("WAMP-CRA") is a WAMP v1 protocol feature
that provides in-band authentication of WAMP clients to servers.

It is based on HMAC-SHA256 and built into AutobahnPython, AutobahnJS and AutobahnAndroid.

This example shows how a AutobahnJS client can authenticate to a AutobahnPython based
server. The server grants RPC and PubSub permissions based on authentication.

Running
-------

Run the server by doing

    python server.py

and open

    http://localhost:8080/

in **2 tabs/windows** of your browser.


To activate debug output on the server, start it

    python server.py debug

This will show up all WAMP messages exchanged between clients and server.

To use the Python client, do

    python client.py
