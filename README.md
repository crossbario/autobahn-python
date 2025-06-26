# Autobahn|Python

WebSocket & WAMP for Python on Twisted and asyncio.

[![Version](https://img.shields.io/pypi/v/autobahn.svg)](https://pypi.python.org/pypi/autobahn)
[![CI Test Status](https://github.com/crossbario/autobahn-python/workflows/main/badge.svg)](https://github.com/crossbario/autobahn-python/actions?query=workflow%3Amain)
[![CI Deploy Status](https://github.com/crossbario/autobahn-python/workflows/deploy/badge.svg)](https://github.com/crossbario/autobahn-python/actions?query=workflow%3Adeploy)
[![CI Docker Status](https://github.com/crossbario/autobahn-python/workflows/docker/badge.svg)](https://github.com/crossbario/autobahn-python/actions?query=workflow%3Adocker)
[![CI EXE Status](https://github.com/crossbario/autobahn-python/workflows/pyinstaller/badge.svg)](https://github.com/crossbario/autobahn-python/actions?query=workflow%3Apyinstaller)
[![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)](https://autobahn.readthedocs.io/en/latest/)
[![Docker
Images](https://img.shields.io/badge/download-docker-blue.svg?style=flat)](https://hub.docker.com/r/crossbario/autobahn-python/)
[![EXE
Download](https://img.shields.io/badge/download-exe-blue.svg?style=flat)](https://download.crossbario.com/xbrnetwork/linux-amd64/xbrnetwork-latest)

---

**Quick Links**:
[Source Code](https://github.com/crossbario/autobahn-python) -
[Documentation](https://autobahn.readthedocs.io/en/latest/) -
[WebSocket Examples](https://autobahn.readthedocs.io/en/latest/websocket/examples.html) -
[WAMP Examples](https://autobahn.readthedocs.io/en/latest/wamp/examples.html)  
**Community**:
[Forum](https://crossbar.discourse.group/) -
[StackOverflow](https://stackoverflow.com/questions/tagged/autobahn) -
[Twitter](https://twitter.com/autobahnws) -
[IRC \#autobahn/chat.freenode.net](https://webchat.freenode.net/)  
**Companion
Projects**:
[Autobahn|JS](https://github.com/crossbario/autobahn-js/) -
[Autobahn|Cpp](https://github.com/crossbario/autobahn-cpp) -
[Autobahn|Testsuite](https://github.com/crossbario/autobahn-testsuite) -
[Crossbar.io](https://crossbar.io) -
[WAMP](https://wamp-proto.org)

## Introduction

**Autobahn|Python** is a subproject of
[Autobahn](https://crossbar.io/autobahn) and provides open-source
implementations of

- [The WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [The Web Application Messaging Protocol (WAMP)](https://wamp-proto.org/)

for Python 3.7+ and running on
[Twisted](https://twistedmatrix.com/) and
[asyncio](https://docs.python.org/3/library/asyncio.html).

You can use **Autobahn|Python** to create clients and servers in
Python speaking just plain WebSocket or WAMP.

**WebSocket** allows
[bidirectional real-time messaging on the Web](https://crossbario.com/blog/post/websocket-why-what-can-i-use-it/)
and beyond, while [WAMP](https://wamp-proto.org/) adds real-time
application communication on top of WebSocket.

**WAMP** provides asynchronous **Remote Procedure Calls** and
**Publish & Subscribe** for applications in _one_ protocol
running over [WebSocket](https://tools.ietf.org/html/rfc6455).
WAMP is a _routed_ protocol, so you need a **WAMP Router** to
connect your **Autobahn|Python** based clients. We provide
[Crossbar.io](https://crossbar.io), but there are
[other options](https://wamp-proto.org/implementations.html#routers)
as well.

Note

**Autobahn|Python** up to version v19.11.2 supported Python 2 and
3.4+, and up to version v20.7.1 supported Python 3.5+, and up to
version v21.2.1 supported Python 3.6+.

## Features

- framework for [WebSocket](https://tools.ietf.org/html/rfc6455)
  and [WAMP](https://wamp-proto.org/) clients and servers
- runs on [CPython](https://python.org/) and
  <span class="title-ref">PyPy &lt;https://pypy.org/&gt;</span>
- runs under [Twisted](https://twistedmatrix.com/) and
  [asyncio](https://docs.python.org/3/library/asyncio.html) -
  implements WebSocket
  [RFC6455](https://tools.ietf.org/html/rfc6455) and Draft
  Hybi-10+
- implements
  [WebSocket compression](https://tools.ietf.org/html/draft-ietf-hybi-permessage-compression)
- implements [WAMP](https://wamp-proto.org/), the Web Application
  Messaging Protocol
- high-performance, fully asynchronous implementation
- best-in-class standards conformance (100% strict passes with
  [Autobahn Testsuite](https://crossbar.io/autobahn#testsuite):
  [Client](https://autobahn.ws/testsuite/reports/clients/index.html)
  [Server](https://autobahn.ws/testsuite/reports/servers/index.html))
- message-, frame- and streaming-APIs for WebSocket
- supports TLS (secure WebSocket) and proxies
- Open-source
  ([MIT license](https://github.com/crossbario/autobahn-python/blob/master/LICENSE))

---

## AI Policy

Important

**A Note on Upcoming Policy Changes Regarding AI-Assisted
Content**

Up to and including version **v25.6.1**, this project contains no
code or documentation generated with the assistance of AI tools.
This version represents the final release under our historical
contribution policy.

Starting with future versions (after v25.6.1), our contribution
policy will change. Subsequent releases **MAY** contain code or
documentation created with AI assistance.

We urge all users and contributors to review our
[AI Policy](AI_POLICY.rst). This document details:

- The rules and warranties required for all future contributions.
- The potential intellectual property implications for the
  project and its users.

This policy was established following an open community
discussion, which you can review on
<span class="title-ref">GitHub issue \#1663
&lt;https://github.com/crossbario/autobahn-python/issues/1663&gt;</span>.

We are providing this transparent notice to enable you to make an
informed decision. If our new AI policy is incompatible with your
own (or your organization's) development practices or risk
tolerance, please take this into consideration when deciding
whether to upgrade beyond version v25.6.1.

## Show me some code

To give you a first impression, here are two examples. We have
lot more
[in the repo](https://github.com/crossbario/autobahn-python/tree/master/examples).

### WebSocket Echo Server

Here is a simple WebSocket Echo Server that will echo back any
WebSocket message received:

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

To actually run above server protocol, you need some lines of
[boilerplate](https://autobahn.readthedocs.io/en/latest/websocket/programming.html#running-a-server).

### WAMP Application Component

Here is a WAMP Application Component that performs all four types
of actions that WAMP provides:

1.  **subscribe** to a topic
2.  **publish** an event
3.  **register** a procedure
4.  **call** a procedure

<!-- -->

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

            self.register(add2, 'com.myapp.add2')

            # 4. call a remote procedure
            res = yield self.call('com.myapp.add2', 2, 3)
            print("Got result: {}".format(res))

Above code will work on Twisted and asyncio by changing a single
line (the base class of `MyComponent`). To actually run above
application component, you need some lines of
[boilerplate](https://autobahn.readthedocs.io/en/latest/wamp/programming.html#running-components)
and a
[WAMP Router](https://autobahn.readthedocs.io/en/latest/wamp/programming.html#running-a-wamp-router).

## Extensions

### Networking framework

Autobahn runs on both Twisted and asyncio. To select the
respective netoworking framework, install flavor:

- `asyncio`: Install asyncio (when on Python 2, otherwise it's
  included in the standard library already) and asyncio support
  in Autobahn
- `twisted`: Install Twisted and Twisted support in Autobahn

---

### WebSocket acceleration and compression

- `accelerate`: Install WebSocket acceleration - _Only use on
  CPython - not on PyPy (which is faster natively)_
- `compress`: Install (non-standard) WebSocket compressors
  **bzip2** and **snappy** (standard **deflate** based WebSocket
  compression is already included in the base install)

---

### Encryption and WAMP authentication

Autobahn supports running over TLS (for WebSocket and all WAMP
transports) as well as **WAMP-cryposign** authentication.

To install use this flavor:

- `encryption`: Installs TLS and WAMP-cryptosign dependencies

Autobahn also supports **WAMP-SCRAM** authentication. To install:

- `scram`: Installs WAMP-SCRAM dependencies

---

### XBR

Autobahn includes support for [XBR](https://xbr.network/). To
install use this flavor:

- `xbr`:

To install:

    pip install autobahn[xbr]

or (Twisted, with more bells an whistles)

    pip install autobahn[twisted,encryption,serialization,xbr]

or (asyncio, with more bells an whistles)

    pip install autobahn[asyncio,encryption,serialization,xbr]

---

### Native vector extensions (NVX)

&gt; This is NOT yet complete - ALPHA!

Autobahn contains **NVX**, a network accelerator library that
provides SIMD accelerated native vector code for WebSocket (XOR
masking) and UTF-8 validation.

> NVX lives in namespace
> <span class="title-ref">autobahn.nvx</span> and currently
> requires a x86-86 CPU with at least SSE2 and makes use of
> SSE4.1 if available. The code is written using vector
> instrinsics, should compile with both GCC and Clang,and
> interfaces with Python using CFFI, and hence runs fast on PyPy.

---

### WAMP Serializers

- `serialization`: To install additional WAMP serializers: CBOR,
  MessagePack, UBJSON and Flatbuffers

**Above is for advanced uses. In general we recommend to use CBOR
where you can, and JSON (from the standard library) otherwise.**

---

To install Autobahn with all available serializers:

    pip install autobahn[serializers]

or (development install)

    pip install -e .[serializers]

Further, to speed up JSON on CPython using `ujson`, set the
environment variable:

    AUTOBAHN_USE_UJSON=1

Warning

Using `ujson` (on both CPython and PyPy) will break the ability
of Autobahn to transport and translate binary application
payloads in WAMP transparently. This ability depends on features
of the regular JSON standard library module not available on
`ujson`.
