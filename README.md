# Autobahn|Python

## Introduction

**Autobahn**|Python is a subproject of [Autobahn](http://autobahn.ws/) and provides open-source implementations of

* **[The WebSocket Protocol](http://tools.ietf.org/html/rfc6455)**
* **[The Web Application Messaging Protocol (WAMP)](http://wamp.ws/)**

WebSocket allows [bidirectional real-time messaging on the Web](http://tavendo.com/blog/post/websocket-why-what-can-i-use-it/) and WAMP adds asynchronous *Remote Procedure Calls* and *Publish & Subscribe* on top of WebSocket. 

You can use **Autobahn**|Python to create clients and servers in Python speaking just plain WebSocket or WAMP.


**Autobahn**|Python features:

* framework for [WebSocket](http://tools.ietf.org/html/rfc6455) / [WAMP](http://wamp.ws/) clients and servers
* compatible with Python 2.6, 2.7, 3.3 and 3.4
* runs on [CPython](http://python.org/), [PyPy](http://pypy.org/) and [Jython](http://jython.org/)
* runs under [Twisted](http://twistedmatrix.com/) and [asyncio](http://docs.python.org/3.4/library/asyncio.html)
* implements WebSocket [RFC6455](http://tools.ietf.org/html/rfc6455), Draft Hybi-10+, Hixie-76
* implements [WebSocket compression](http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression)
* implements [WAMPv1](http://wamp.ws/spec/) and [WAMPv2](https://github.com/tavendo/WAMP/blob/master/spec/README.md) (*upcoming*)

and more

* high-performance, fully asynchronous implementation
* best-in-class standards conformance (100% strict passes with [Autobahn Testsuite](http://autobahn.ws/testsuite))
* message-, frame- and streaming-APIs for WebSocket
* supports TLS (secure WebSocket) and proxies
* Open-source (Apache 2 [license](https://github.com/tavendo/AutobahnPython/blob/master/LICENSE))

## Getting Started

Autobahn comes with lots of [examples](https://github.com/tavendo/AutobahnPython/tree/master/examples) with ready-to-run code. The "Hello, world!" of WebSocket is probably the "WebSocket Echo":

 * [WebSocket Echo (Twisted-based)](https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/echo)
 * [WebSocket Echo (Asyncio-based)](https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/websocket/echo)


Documentation
-------------

To get started quickly, check out the [examples](https://github.com/tavendo/AutobahnPython/tree/master/examples).
For complete API documentation, please consult the [reference documentation](https://autobahnpython.readthedocs.org/).


Where to go
-----------

For more information, including getting started, tutorials and reference documentation, please visit the project's [homepage](http://autobahn.ws/python), or check out the examples in this repository.


Get in touch
------------

Get in touch on IRC #autobahn on chat.freenode.net or join the [mailing list](http://groups.google.com/group/autobahnws).
