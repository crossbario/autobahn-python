PubSub with AutobahnPython
==========================

This example show how to do Publish & Subscribe ("PubSub") with AutobahnPython.

It includes a server which registers some PubSub topics,
a JavaScript client using AutobahnJS and a Python client using AutobahnPython
both doing publish and subscribe.

Further, since it's a standard WAMP service, any WAMP client can use
the service. You could access it i.e. from a native Android app via AutobahnAndroid.

Also see the companion [AutobahnAndroid example](https://github.com/tavendo/AutobahnAndroid/tree/master/Demo/SimplePubSub).	

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
