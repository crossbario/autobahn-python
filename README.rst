Autobahn\|Python
================

WebSocket & WAMP for Python on Twisted and asyncio.

| |Version|  |CI Test Status|  |CI Deploy Status|  |CI Docker Status|  |CI EXE Status|  |Coverage|  |Docs|  |Docker Images|  |EXE Download|

--------------

| **Quick Links**: `Source Code <https://github.com/crossbario/autobahn-python>`__ - `Documentation <https://autobahn.readthedocs.io/en/latest/>`__ - `WebSocket Examples <https://autobahn.readthedocs.io/en/latest/websocket/examples.html>`__ - `WAMP Examples <https://autobahn.readthedocs.io/en/latest/wamp/examples.html>`__
| **Community**: `Forum <https://gitter.im/crossbario/public>`__ - `StackOverflow <https://stackoverflow.com/questions/tagged/autobahn>`__ - `Twitter <https://twitter.com/autobahnws>`__ - `IRC #autobahn/chat.freenode.net <https://webchat.freenode.net/>`__
| **Companion Projects**: `Autobahn|JS <https://github.com/crossbario/autobahn-js/>`__ - `Autobahn|Cpp <https://github.com/crossbario/autobahn-cpp>`__ - `Autobahn|Testsuite <https://github.com/crossbario/autobahn-testsuite>`__ - `Crossbar.io <https://crossbar.io>`__ - `WAMP <https://wamp-proto.org>`__

Introduction
------------

**Autobahn\|Python** is a subproject of `Autobahn <https://crossbar.io/autobahn>`__ and provides open-source
implementations of

-  `The WebSocket Protocol <https://tools.ietf.org/html/rfc6455>`__
-  `The Web Application Messaging Protocol (WAMP) <https://wamp-proto.org/>`__

for Python 3.7+ and running on `Twisted <https://twistedmatrix.com/>`__ and `asyncio <https://docs.python.org/3/library/asyncio.html>`__.

You can use **Autobahn\|Python** to create clients and servers in Python speaking just plain WebSocket or WAMP.

**WebSocket** allows `bidirectional real-time messaging on the Web <https://crossbario.com/blog/post/websocket-why-what-can-i-use-it/>`__ and beyond, while `WAMP <https://wamp-proto.org/>`__ adds real-time application communication on top of WebSocket.

**WAMP** provides asynchronous **Remote Procedure Calls** and **Publish & Subscribe** for applications in *one* protocol running over `WebSocket <https://tools.ietf.org/html/rfc6455>`__. WAMP is a *routed* protocol, so you need a **WAMP Router** to connect your **Autobahn\|Python** based clients. We provide `Crossbar.io <https://crossbar.io>`__, but there are `other options <https://wamp-proto.org/implementations.html#routers>`__ as well.

.. note::

    **Autobahn\|Python** up to version v19.11.2 supported Python 2 and 3.4+,
    and up to version v20.7.1 supported Python 3.5+,
    and up to version v21.2.1 supported Python 3.6+.

Features
--------

-  framework for `WebSocket <https://tools.ietf.org/html/rfc6455>`__ and `WAMP <https://wamp-proto.org/>`__ clients and servers
-  runs on `CPython <https://python.org/>`__ and `PyPy <https://pypy.org/>`
-  runs under `Twisted <https://twistedmatrix.com/>`__ and `asyncio <https://docs.python.org/3/library/asyncio.html>`__ - implements WebSocket
   `RFC6455 <https://tools.ietf.org/html/rfc6455>`__ and Draft Hybi-10+
-  implements `WebSocket compression <https://tools.ietf.org/html/draft-ietf-hybi-permessage-compression>`__
-  implements `WAMP <https://wamp-proto.org/>`__, the Web Application Messaging Protocol
-  high-performance, fully asynchronous implementation
-  best-in-class standards conformance (100% strict passes with `Autobahn Testsuite <https://crossbar.io/autobahn#testsuite>`__: `Client <https://autobahn.ws/testsuite/reports/clients/index.html>`__ `Server <https://autobahn.ws/testsuite/reports/servers/index.html>`__)
-  message-, frame- and streaming-APIs for WebSocket
-  supports TLS (secure WebSocket) and proxies
-  Open-source (`MIT license <https://github.com/crossbario/autobahn-python/blob/master/LICENSE>`__)

-----

Show me some code
-----------------

To give you a first impression, here are two examples. We have lot more `in the repo <https://github.com/crossbario/autobahn-python/tree/master/examples>`__.

WebSocket Echo Server
~~~~~~~~~~~~~~~~~~~~~

Here is a simple WebSocket Echo Server that will echo back any WebSocket
message received:

.. code:: python

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

To actually run above server protocol, you need some lines of `boilerplate <https://autobahn.readthedocs.io/en/latest/websocket/programming.html#running-a-server>`__.

WAMP Application Component
~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is a WAMP Application Component that performs all four types of
actions that WAMP provides:

#. **subscribe** to a topic
#. **publish** an event
#. **register** a procedure
#. **call** a procedure

.. code:: python

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

Above code will work on Twisted and asyncio by changing a single line
(the base class of ``MyComponent``). To actually run above application component, you need some lines of `boilerplate <https://autobahn.readthedocs.io/en/latest/wamp/programming.html#running-components>`__ and a `WAMP Router <https://autobahn.readthedocs.io/en/latest/wamp/programming.html#running-a-wamp-router>`__.


Extensions
----------

Networking framework
~~~~~~~~~~~~~~~~~~~~

Autobahn runs on both Twisted and asyncio. To select the respective netoworking framework, install flavor:

* ``asyncio``: Install asyncio (when on Python 2, otherwise it's included in the standard library already) and asyncio support in Autobahn
* ``twisted``: Install Twisted and Twisted support in Autobahn

-----


WebSocket acceleration and compression
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``accelerate``: Install WebSocket acceleration - *Only use on CPython - not on PyPy (which is faster natively)*
* ``compress``: Install (non-standard) WebSocket compressors **bzip2** and **snappy** (standard **deflate** based WebSocket compression is already included in the base install)

-----


Encryption and WAMP authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Autobahn supports running over TLS (for WebSocket and all WAMP transports) as well as **WAMP-cryposign** authentication.

To install use this flavor:

* ``encryption``: Installs TLS and WAMP-cryptosign dependencies

Autobahn also supports **WAMP-SCRAM** authentication. To install:

* ``scram``: Installs WAMP-SCRAM dependencies

-----


XBR
~~~

Autobahn includes support for `XBR <https://xbr.network/>`__. To install use this flavor:

* ``xbr``:

To install:

.. code:: console

    pip install autobahn[xbr]

or (Twisted, with more bells an whistles)

.. code:: console

    pip install autobahn[twisted,encryption,serialization,xbr]

or (asyncio, with more bells an whistles)

.. code:: console

    pip install autobahn[asyncio,encryption,serialization,xbr]

-----


Native vector extensions (NVX)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

> This is NOT yet complete - ALPHA!

Autobahn contains **NVX**, a network accelerator library that provides SIMD accelerated native vector code for WebSocket (XOR masking) and UTF-8 validation.

.. note:

    NVX lives in namespace `autobahn.nvx` and currently requires a x86-86 CPU with at least SSE2 and makes use of SSE4.1 if available. The code is written using vector instrinsics, should compile with both GCC and Clang,and interfaces with Python using CFFI, and hence runs fast on PyPy.

-----


WAMP Serializers
~~~~~~~~~~~~~~~~

* ``serialization``: To install additional WAMP serializers: CBOR, MessagePack, UBJSON and Flatbuffers

**Above is for advanced uses. In general we recommend to use CBOR where you can,
and JSON (from the standard library) otherwise.**

-----

To install Autobahn with all available serializers:

.. code:: console

    pip install autobahn[serializers]

or (development install)

.. code:: console

    pip install -e .[serializers]

Further, to speed up JSON on CPython using ``ujson``, set the environment variable:

.. code:: console

    AUTOBAHN_USE_UJSON=1

.. warning::

    Using ``ujson`` (on both CPython and PyPy) will break the ability of Autobahn
    to transport and translate binary application payloads in WAMP transparently.
    This ability depends on features of the regular JSON standard library module
    not available on ``ujson``.


.. |Version| image:: https://img.shields.io/pypi/v/autobahn.svg
   :target: https://pypi.python.org/pypi/autobahn

.. |CI Test Status| image:: https://github.com/crossbario/autobahn-python/workflows/main/badge.svg
   :target: https://github.com/crossbario/autobahn-python/actions?query=workflow%3Amain
   :alt: CI Test Status

.. |CI Deploy Status| image:: https://github.com/crossbario/autobahn-python/workflows/deploy/badge.svg
   :target: https://github.com/crossbario/autobahn-python/actions?query=workflow%3Adeploy
   :alt: CI Deploy Status

.. |CI Docker Status| image:: https://github.com/crossbario/autobahn-python/workflows/docker/badge.svg
   :target: https://github.com/crossbario/autobahn-python/actions?query=workflow%3Adocker
   :alt: CI Docker Status

.. |CI EXE Status| image:: https://github.com/crossbario/autobahn-python/workflows/pyinstaller/badge.svg
   :target: https://github.com/crossbario/autobahn-python/actions?query=workflow%3Apyinstaller
   :alt: CI EXE Status

.. |Coverage| image:: https://img.shields.io/codecov/c/github/crossbario/autobahn-python/master.svg
   :target: https://codecov.io/github/crossbario/autobahn-python

.. |Docs| image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat
   :target: https://autobahn.readthedocs.io/en/latest/

.. |Docker Images| image:: https://img.shields.io/badge/download-docker-blue.svg?style=flat
   :target: https://hub.docker.com/r/crossbario/autobahn-python/

.. |EXE Download| image:: https://img.shields.io/badge/download-exe-blue.svg?style=flat
   :target: https://download.crossbario.com/xbrnetwork/linux-amd64/xbrnetwork-latest
