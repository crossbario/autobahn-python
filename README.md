# Autobahn|Python

[![Build Status](https://travis-ci.org/tavendo/AutobahnPython.png?branch=master)](https://travis-ci.org/tavendo/AutobahnPython)
&nbsp; ![Version](https://pypip.in/v/autobahn/badge.png)
&nbsp; ![Downloads](https://pypip.in/d/autobahn/badge.png)

**Autobahn**|Python is a subproject of [Autobahn](http://autobahn.ws/) and provides open-source implementations of

* **[The WebSocket Protocol](http://tools.ietf.org/html/rfc6455)**
* **[The Web Application Messaging Protocol (WAMP)](http://wamp.ws/)**

in Python running on [**Twisted**](http://twistedmatrix.com/) and [**asyncio**](http://docs.python.org/3.4/library/asyncio.html).

You can use **Autobahn**|Python to create clients and servers in Python speaking just plain WebSocket or WAMP.

WebSocket allows [bidirectional real-time messaging on the Web](http://tavendo.com/blog/post/websocket-why-what-can-i-use-it/) and WAMP adds asynchronous *Remote Procedure Calls* and *Publish & Subscribe* on top of WebSocket.

WAMP provides asynchronous **Remote Procedure Calls** and **Publish & Subscribe** for applications in *one* protocol running over [WebSocket](http://tools.ietf.org/html/rfc6455) (and fallback transports for old browsers).

It is ideal for distributed, multi-client and server applications, such as multi-user database-drive business applications, sensor networks (IoT), instant messaging or MMOGs (massively multi-player online games) .

WAMP enables application architectures with application code distributed freely across processes and devices according to functional aspects. Since WAMP implementations exist for multiple languages, WAMP applications can be polyglott. Application components can be implemented in a language and run on a device which best fit the particular use case.


## Features

* framework for [WebSocket](http://tools.ietf.org/html/rfc6455) / [WAMP](http://wamp.ws/) clients and servers
* compatible with Python 2.6, 2.7, 3.3 and 3.4
* runs on [CPython](http://python.org/), [PyPy](http://pypy.org/) and [Jython](http://jython.org/)
* runs under [Twisted](http://twistedmatrix.com/) and [asyncio](http://docs.python.org/3.4/library/asyncio.html)
* implements WebSocket [RFC6455](http://tools.ietf.org/html/rfc6455), Draft Hybi-10+, Hixie-76
* implements [WebSocket compression](http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression)
* implements [WAMPv1](http://wamp.ws/spec/) and [WAMPv2](https://github.com/tavendo/WAMP/blob/master/spec/README.md) (*upcoming*)
* high-performance, fully asynchronous implementation
* best-in-class standards conformance (100% strict passes with [Autobahn Testsuite](http://autobahn.ws/testsuite))
* message-, frame- and streaming-APIs for WebSocket
* supports TLS (secure WebSocket) and proxies
* Open-source (Apache 2 [license](https://github.com/tavendo/AutobahnPython/blob/master/LICENSE))


## More Information

For more information, take a look at the [project documentation](http://autobahn.ws/python). This provides:

* [installation instructions](http://autobahn.ws/python/installation)
* [a list of all examples in this repo](http://autobahn.ws/python/examples)
* [an introduction to WebSocket programming](http://autobahn.ws/python/websocketprogramming)
* [an introduction to WAMP programming](http://autobahn.ws/python/wampprogramming)
* [a full API reference](http://autobahn.ws/python/reference)


## Get in touch

Get in touch on IRC `#autobahn` on `chat.freenode.net`, follow us on [Twitter](https://twitter.com/autobahnws) or join the [mailing list](http://groups.google.com/group/autobahnws).
