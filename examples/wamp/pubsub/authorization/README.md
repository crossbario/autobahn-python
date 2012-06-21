Writing custom PubSub handlers for Authorization
================================================

This example show how to write custom PubSub handlers and use that for
implementing fine-grained authorization.

It includes a server which register a custom PubSub handler for topics,
a JavaScript client using AutobahnJS and a Python client using AutobahnPython
both doing publish and subscribe.

Further, since it's a standard WAMP service, any WAMP client can use
the service. You could access it i.e. from a native Android app via AutobahnAndroid.

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


Perspective
-----------

Fine-grained authorization for topics is just one application of custom PubSub handlers.

Custom PubSub handlers allow you to hook into the AutobahnPython PubSub machinery
and do very flexible things.