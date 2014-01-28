RPCs with AutobahnPython
========================

The examples introduce Remote Procedure Calls ("RPCs") programming with AutobahnPython.

Included are servers which provide methods exported for RPC ("remoted methods"),
JavaScript clients using AutobahnJS and a Python clients using AutobahnPython.

Further, since AutobahnPython provides standard WAMP RPC services, any WAMP client
can use the service. You can access it i.e. from a native Android app via AutobahnAndroid.

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
