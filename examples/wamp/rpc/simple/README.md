RPCs with AutobahnPython
========================

This example show how to do Remote Procedure Calls ("RPCs") with AutobahnPython.

It includes a server which provides some methods exported for RPC ("remoted methods"),
a JavaScript client using AutobahnJS and a Python client using AutobahnPython.

Further, since it's a standard WAMP service, any WAMP client can use
the service. You can access it i.e. from a native Android app via AutobahnAndroid.

Also see the companion [AutobahnAndroid example](https://github.com/tavendo/AutobahnAndroid/tree/master/Demo/SimpleRpc).	


Running
-------

Run the server by doing

    python server.py

and open

    http://localhost:8080/

in your browser.

To activate debug output on the server, start it

    python server.py debug

This will show up all WAMP messages exchanged between clients and server.

To use the Python client, do

    python client.py


Inline Callbacks
----------------

The 

	client_icb.py

client shows how to program RPCs using *Twisted Inline Callbacks*, a variant coding
style for using *Twisted Deferreds*.
