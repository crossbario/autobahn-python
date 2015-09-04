# Autobahn|Python

[![Version](https://img.shields.io/pypi/v/autobahn.svg)](https://pypi.python.org/pypi/autobahn)
[![Python Versions](https://img.shields.io/pypi/pyversions/autobahn.svg)](https://pypi.python.org/pypi/autobahn)
[![Downloads](https://img.shields.io/pypi/dm/autobahn.svg)](https://pypi.python.org/pypi/autobahn)
[![Build Status](https://travis-ci.org/tavendo/AutobahnPython.svg?branch=master)](https://travis-ci.org/tavendo/AutobahnPython)
[![Coverage](https://img.shields.io/codecov/c/github/tavendo/AutobahnPython/master.svg)](https://codecov.io/github/tavendo/AutobahnPython)

**Quick Links**: [Docs](http://autobahn.ws/python) - [WebSocket Examples](http://autobahn.ws/python/websocket/examples.html) - [WAMP Examples](http://autobahn.ws/python/wamp/examples.html) - [Crossbar.io](http://crossbar.io)

**Contact us**: [Mailing list](http://groups.google.com/group/autobahnws) - [Twitter](https://twitter.com/autobahnws) - IRC `#autobahn` at `chat.freenode.net`

---

## Introduction

**Autobahn|Python** is a subproject of [Autobahn](http://autobahn.ws/) and provides open-source implementations of

* **[The WebSocket Protocol](http://tools.ietf.org/html/rfc6455)**
* **[The Web Application Messaging Protocol (WAMP)](http://wamp.ws/)**

in Python running on [**Twisted**](http://twistedmatrix.com/) and [**asyncio**](http://docs.python.org/3.4/library/asyncio.html).

You can use **Autobahn|Python** to create clients and servers in Python speaking just plain WebSocket or WAMP.

**WebSocket** allows [bidirectional real-time messaging on the Web](http://tavendo.com/blog/post/websocket-why-what-can-i-use-it/) and [WAMP](http://wamp.ws/) adds real-time application messaging abstractions on top of WebSocket.

**WAMP** provides asynchronous **Remote Procedure Calls** and **Publish & Subscribe** for applications in *one* protocol running over [WebSocket](http://tools.ietf.org/html/rfc6455). WAMP is a *routed* protocol, so you need a **WAMP Router** to connect your **Autobahn|Python** based clients. We provide [Crossbar.io](http://crossbar.io), but there are [other options](http://wamp.ws/implementations/#routers) as well.

## Features

* framework for [WebSocket](http://tools.ietf.org/html/rfc6455) and [WAMP](http://wamp.ws/) clients and servers
* compatible with Python 2.6, 2.7, 3.3 and 3.4
* runs on [CPython](http://python.org/), [PyPy](http://pypy.org/) and [Jython](http://jython.org/)
* runs under [Twisted](http://twistedmatrix.com/) and [asyncio](http://docs.python.org/3.4/library/asyncio.html)
* implements WebSocket [RFC6455](http://tools.ietf.org/html/rfc6455), Draft Hybi-10+, Hixie-76
* implements [WebSocket compression](http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression)
* implements [WAMP](http://wamp.ws/), the Web Application Messaging Protocol
* high-performance, fully asynchronous implementation
* best-in-class standards conformance (100% strict passes with [Autobahn Testsuite](http://autobahn.ws/testsuite))
* message-, frame- and streaming-APIs for WebSocket
* supports TLS (secure WebSocket) and proxies
* Open-source ([MIT license](https://github.com/tavendo/AutobahnPython/blob/master/LICENSE))

## Show me some code

To give you a first impression, here are two examples. We have lot more [in the repo](https://github.com/tavendo/AutobahnPython/tree/master/examples).

### WebSocket Echo Server

Here is a simple WebSocket Echo Server that will echo back any WebSocket message received:

```python
from autobahn.twisted.websocket import WebSocketServerProtocol
# or: from autobahn.asyncio.websocket import WebSocketServerProtocol

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {} bytes".format(len(payload)))
        else:
            print("Text message received: {}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))
```

To actually run above server protocol, you need some lines of [boilerplate](http://autobahn.ws/python/websocket/programming.html#running-a-server).

### WAMP Application Component

Here is a WAMP Application Component that performs all four types of actions that WAMP provides:

1. **subscribe** to a topic
2. **publish** an event
3. **register** a procedure
4. **call** a procedure

```python
from autobahn.twisted.wamp import ApplicationSession
# or: from autobahn.asyncio.wamp import ApplicationSession

class MyComponent(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):

        # 1. subscribe to a topic so we receive events
        def onevent(msg):
            print("Got event: {}".format(msg))

        yield self.subscribe(onevent, 'com.myapp.hello')

        # 2. publish an event to a topic
        self.publish('com.myapp.hello', 'Hello, world!')

        # 3. register a procedure for remote calling
        def add2(x, y):
            return x + y

        self.register(add2, 'com.myapp.add2');

        # 4. call a remote procedure
        res = yield self.call('com.myapp.add2', 2, 3)
        print("Got result: {}".format(res))
```

Above code will work on Twisted and asyncio by changing a single line (the base class of `MyComponent`)!

To actually run above application component, you need some lines of [boilerplate](http://autobahn.ws/python/wamp/programming.html#running-components) and a [WAMP Router](http://crossbar.io).
