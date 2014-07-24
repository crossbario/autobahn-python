|ab|
====

Latest release: v\ |version|. (:ref:`Changelog`)

|ab| is a subproject of `Autobahn`_ and provides open-source implementations of

* `The WebSocket Protocol <http://tools.ietf.org/html/rfc6455>`_
* `The Web Application Messaging Protocol (WAMP) <http://wamp.ws/>`_

in Python 2 and 3, running on `Twisted`_ and `asyncio`_.

WebSocket allows `bidirectional real-time messaging on the Web <http://tavendo.com/blog/post/websocket-why-what-can-i-use-it/>`_.

WAMP implements `two messaging patterns on top of WebSocket <http://wamp.ws/why/>`_:

* **Publish & Subscribe**: *Publishers* publish events to a topic, and *subscribers* to the topic receive these events. A *router* brokers these events.
* **Remote Procedure Calls**: A *callee* registers a remote procedure with a *router*. A *caller* makes a call for that procedure to the *router*. The *router* deals the call to the *callee* and returns the result to the *caller*.

Basic *router* functionality is provided by |ab|.

WAMP is ideal for distributed, multi-client and server applications, such as multi-user database-drive business applications, sensor networks (IoT), instant messaging or MMOGs (massively multi-player online games) .

WAMP enables application architectures with application code distributed freely across processes and devices according to functional aspects. Since WAMP implementations exist for multiple languages, WAMP applications can be polyglott. Application components can be implemented in a language and run on a device which best fit the particular use case.


Features
--------

* framework for `WebSocket`_ / `WAMP`_ clients and servers
* compatible with Python 2.6, 2.7, 3.3 and 3.4
* runs on `CPython`_, `PyPy`_ and `Jython`_
* runs under `Twisted`_ and `asyncio`_
* implements WebSocket `RFC6455`_, Draft Hybi-10+ and Hixie-76
* implements `WebSocket compression <http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression>`_
* implements `WAMPv1`_ and `WAMPv2`_
* high-performance, fully asynchronous implementation
* best-in-class standards conformance (100% strict passes with `AutobahnTestsuite`_)
* message-, frame- and streaming-APIs for WebSocket
* supports TLS (secure WebSocket) and proxies
* Open-source (`Apache 2 license <https://github.com/tavendo/AutobahnPython/blob/master/LICENSE>`_)


Where to go from here
---------------------



:doc:`wamp/examples` lists code examples covering a broader range of uses cases and advanced WAMP features.

:doc:`websocket/websocketprogramming` explains all you need to know about using |ab| as a WebSocket library, and includes a full reference for the relevant parts of the API.

:doc:`wamp/wampprogramming` gives an introduction for programming with WAMP (v2) in Python using |ab|.


.. toctree::
   :maxdepth: 2

   introduction
   installation
   websocket/websocketprogramming
   wamp/wampprogramming
   changelog
