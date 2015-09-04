# Autobahn|Python

[![Version](https://img.shields.io/pypi/v/autobahn.svg)](https://pypi.python.org/pypi/autobahn) &nbsp;
[![Status](https://img.shields.io/pypi/status/autobahn.svg)](https://pypi.python.org/pypi/autobahn) &nbsp;
[![License](https://img.shields.io/pypi/l/autobahn.svg)](https://pypi.python.org/pypi/autobahn) &nbsp;
[![Implementation](https://img.shields.io/pypi/implementation/autobahn.svg)](https://pypi.python.org/pypi/autobahn) &nbsp;
[![Python Versions](https://img.shields.io/pypi/pyversions/autobahn.svg)](https://pypi.python.org/pypi/autobahn) &nbsp;
[![Downloads](https://img.shields.io/pypi/dm/autobahn.svg)](https://pypi.python.org/pypi/autobahn) &nbsp;
[![Build Status](https://travis-ci.org/tavendo/AutobahnPython.svg?branch=master)](https://travis-ci.org/tavendo/AutobahnPython) &nbsp;
[![Coverage](https://img.shields.io/codecov/c/github/tavendo/AutobahnPython/master.svg)](https://codecov.io/github/tavendo/AutobahnPython) &nbsp;

**Autobahn**|Python is a subproject of [Autobahn](http://autobahn.ws/) and provides open-source implementations of

* **[The WebSocket Protocol](http://tools.ietf.org/html/rfc6455)**
* **[The Web Application Messaging Protocol (WAMP)](http://wamp.ws/)**

in Python running on [**Twisted**](http://twistedmatrix.com/) and [**asyncio**](http://docs.python.org/3.4/library/asyncio.html).

You can use **Autobahn**|Python to create clients and servers in Python speaking just plain WebSocket or WAMP.

WebSocket allows [bidirectional real-time messaging on the Web](http://tavendo.com/blog/post/websocket-why-what-can-i-use-it/) and WAMP adds asynchronous *Remote Procedure Calls* and *Publish & Subscribe* on top of WebSocket.

WAMP provides asynchronous **Remote Procedure Calls** and **Publish & Subscribe** for applications in *one* protocol running over [WebSocket](http://tools.ietf.org/html/rfc6455) (and fallback transports for old browsers).

It is ideal for distributed, multi-client and server applications, such as multi-user database-drive business applications, sensor networks (IoT), instant messaging or MMOGs (massively multi-player online games) .

WAMP enables application architectures with application code distributed freely across processes and devices according to functional aspects. Since WAMP implementations exist for multiple languages, WAMP applications can be polyglot. Application components can be implemented in a language and run on a device which best fit the particular use case.

**Note** that WAMP is a *routed* protocol, so you need to run something that plays the Broker and Dealer roles from the [WAMP Specification](http://wamp.ws/spec/). We provide [Crossbar.io](http://crossbar.io) but there are [other options](http://wamp.ws/implementations/#routers) as well.


## Show me some code

A simple WebSocket echo server:

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

      ## echo back message verbatim
      self.sendMessage(payload, isBinary)

   def onClose(self, wasClean, code, reason):
      print("WebSocket connection closed: {}".format(reason))
```

... and a sample WAMP application component:

```python
from autobahn.twisted.wamp import ApplicationSession
# or: from autobahn.asyncio.wamp import ApplicationSession

class MyComponent(ApplicationSession):

   def onConnect(self):
      self.join("realm1")


   @inlineCallbacks
   def onJoin(self, details):

      # 1) subscribe to a topic
      def onevent(msg):
         print("Got event: {}".format(msg))

      yield self.subscribe(onevent, 'com.myapp.hello')

      # 2) publish an event
      self.publish('com.myapp.hello', 'Hello, world!')

      # 3) register a procedure for remoting
      def add2(x, y):
         return x + y

      self.register(add2, 'com.myapp.add2');

      # 4) call a remote procedure
      res = yield self.call('com.myapp.add2', 2, 3)
      print("Got result: {}".format(res))
```

## Features

* framework for [WebSocket](http://tools.ietf.org/html/rfc6455) / [WAMP](http://wamp.ws/) clients and servers
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


## More Information

For more information, take a look at the [project documentation](http://autobahn.ws/python). This provides:

* [installation instructions](http://autobahn.ws/python/installation.html)
* [an introduction to WebSocket programming](http://autobahn.ws/python/websocket/programming.html)
* [an introduction to WAMP programming](http://autobahn.ws/python/wamp/programming.html)
* [a list of WebSocket examples in this repo](http://autobahn.ws/python/websocket/examples.html)
* [a list of WAMP examples in this repo](http://autobahn.ws/python/wamp/examples.html)
* [a full API reference](http://autobahn.ws/python/reference/autobahn.html)

> **WAMP Version 1**: Looking for WAMP version 1? The last version of AutobahnPython supporting WAMP1 was [0.8.15](https://pypi.python.org/pypi/autobahn/0.8.15). WAMP version 1 is fully deprecated now and no further development happens on AutobahnPython.


## Get in touch

Get in touch on IRC `#autobahn` on `chat.freenode.net`, follow us on [Twitter](https://twitter.com/autobahnws) or join the [mailing list](http://groups.google.com/group/autobahnws).
