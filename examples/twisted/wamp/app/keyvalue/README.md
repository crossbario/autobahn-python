Key-Value Store Service
=======================

This example implements a AutobahnPython based WAMP server with RPC
endpoints providing a persistent key-value store.

The example also demonstrates how to run the WAMP server and a
Twisted Web based web server under one port/service.

A browser based UI is included which uses AutobahnJS to access
the decimal calculator service.

A AutobahnPython based client is also included.

Further, since it's a standard WAMP service, any WAMP client can use
the service. You could access it i.e. from a native
Android app via AutobahnAndroid.


Running
-------

Run the server by doing

    python server.py

and open

    http://localhost:8080/

in your browser.

This will show up all WAMP messages exchanged between clients and server.


Perspective
-----------

**Persistence**


The service uses the standard Python **shelve** module for persistence.

You can easily adapt that to store data instead in something like
*sqlite*, *PostgreSQL*, *memcached*, *Riak*, .. whatever.


**Change Notification**


You can also easily extend the example to provide PubSub events for automatic change notification.

Upon creating, updating or deleting data for a key, just *dispatch* a PubSub event server-side.

Clients can subscribe to *keys*, and will get notified when data changes.
