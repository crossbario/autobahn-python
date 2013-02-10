AutobahnPython
==============

AutobahnPython implements **[The WebSocket Protocol](http://tools.ietf.org/html/rfc6455)** and **[The WebSocket Application Messaging Protocol (WAMP)](http://wamp.ws/)**:

* framework for WebSocket and WAMP clients and servers
* implements WebSocket RFC6455, Draft Hybi-10+, Hixie-76 and WAMP v1
* Twisted-based, runs on CPython and PyPy
* high-performance, fully asynchronous implementation
* best-in-class standards conformance (100% strict passes with *[Autobahn WebSocket Testsuite](http://autobahn.ws/testsuite)*)
* message-, frame- and streaming-APIs
* Deferred-based API for asynchronous RPC and PubSub (WAMP)
* supports TLS (secure WebSocket)
* session authentication (WAMP-CRA)
* Open-source (Apache 2 license)

You can use AutobahnPython to create clients and servers speaking either plain WebSocket or WAMP.

Using WAMP you can build applications around **asynchronous RPC** and **PubSub** messaging patterns.

Dependencies
------------

AutobahnPython is designed to work with [Python](http://www.python.org/) (latest versions of 2.6 or 2.7) and [PyPy](http://pypy.org/) (1.9 or later).
The only dependency is [Twisted](http://twistedmatrix.com) (11.1 or later).

Where to go
-----------

For more information, including getting started, tutorials and reference documentation, please visit the project's [homepage](http://autobahn.ws/python), or check out the examples in this repository.


Get in touch
------------

Get in touch on IRC #autobahn on chat.freenode.net or join the [mailing list](http://groups.google.com/group/autobahnws).
