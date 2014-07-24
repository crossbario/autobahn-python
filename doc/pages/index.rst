|Ab|
====

Latest release: v\ |version| (:ref:`Changelog`)

.. raw:: html

   <p>
   <a href="https://travis-ci.org/tavendo/AutobahnPython"><img src="https://travis-ci.org/tavendo/AutobahnPython.png?branch=master" /></a>
   <a href="http://pypi.python.org/pypi/autobahn"><img src="https://pypip.in/d/autobahn/badge.png" /></a>
   </p>

|Ab| is a subproject of the `Autobahn`_ project and provides open-source implementations of

* `The WebSocket Protocol <http://tools.ietf.org/html/rfc6455>`_
* `The Web Application Messaging Protocol (WAMP) <http://wamp.ws/>`_

in Python 2 and 3, running on `Twisted`_ and `asyncio`_.

WebSocket allows `bidirectional real-time messaging <http://tavendo.com/blog/post/websocket-why-what-can-i-use-it/>`_ on the Web while `WAMP <http://wamp.ws/>`_ provides applications with `high-level communication abstractions <http://wamp.ws/why/>`_ in an open standard WebSocket based protocol.

|Ab| features

* framework for `WebSocket`_ / `WAMP`_ clients and servers
* compatible with Python 2.6, 2.7, 3.3 and 3.4
* runs on `CPython`_, `PyPy`_ and `Jython`_
* runs under `Twisted`_ and `asyncio`_
* implements WebSocket `RFC6455`_ (and older versions like Hybi-10+ and Hixie-76)
* implements `WebSocket compression <http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression>`_
* implements `WAMPv2`_ (and `WAMPv1`_)
* supports TLS (secure WebSocket) and proxies
* Open-source (`Apache 2 license <https://github.com/tavendo/AutobahnPython/blob/master/LICENSE>`_)

and much more.

Further, |Ab| is written with these goals

1. high-performance, fully asynchronous and scalable code
2. best-in-class standards conformance and security

We do take those design and implementation goals quite serious. For example, |Ab| has 100% strict passes with `AutobahnTestsuite`_, the quasi industry standard of WebSocket protocol test suites we originally created only to test |Ab|;)

.. note::

   We will refer to |Ab| simply by **Autobahn** when it is clear from the context
   which Autobahn subproject library is meant. In this documentation, this
   is |Ab| almost always.



What can I do with this stuff?
------------------------------

WAMP implements `two messaging patterns on top of WebSocket <http://wamp.ws/why/>`_:

* **Publish & Subscribe**: *Publishers* publish events to a topic, and *subscribers* to the topic receive these events. A *router* brokers these events.
* **Remote Procedure Calls**: A *callee* registers a remote procedure with a *router*. A *caller* makes a call for that procedure to the *router*. The *router* deals the call to the *callee* and returns the result to the *caller*.

Basic *router* functionality is provided by |ab|.

WAMP is ideal for distributed, multi-client and server applications, such as multi-user database-drive business applications, sensor networks (IoT), instant messaging or MMOGs (massively multi-player online games) .

WAMP enables application architectures with application code distributed freely across processes and devices according to functional aspects. Since WAMP implementations exist for multiple languages, WAMP applications can be polyglott. Application components can be implemented in a language and run on a device which best fit the particular use case.


Show me some code!
------------------

A sample **WebSocket server**:

.. code-block:: python

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

Complete example code:

* `WebSocket Echo (Twisted-based) <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/echo>`_
* `WebSocket Echo (Asyncio-based) <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/websocket/echo>`_

---------

A sample **WAMP application component** implementing all client roles:

.. code-block:: python

   class MyComponent(ApplicationSession):

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


Complete example code:

* **server**, which provides a remote procedure enpoint and publishes to a topic - `Twisted <https://github.com/tavendo/AutobahnPython/blob/master/examples/twisted/wamp/beginner/server.py>`__ - `asyncio <https://github.com/tavendo/AutobahnPython/blob/master/examples/asyncio/wamp/beginner/server.py>`__
* **client**, which calls the procedure and subscribes to the topic - `Twisted <https://github.com/tavendo/AutobahnPython/blob/master/examples/twisted/wamp/beginner/client.py>`__ - `asyncio <https://github.com/tavendo/AutobahnPython/blob/master/examples/asyncio/wamp/beginner/client.py>`__

----------


Where to start
==============

To get started, jump to :doc:`installation`.

For **WebSocket developers**, :doc:`websocket/websocketprogramming` explains all you need to know about using |ab| as a WebSocket library, and includes a full reference for the relevant parts of the API.

:doc:`websocket/examples` lists WebSocket code examples covering a broader range of uses cases and advanced WebSocket features.

For **WAMP developers**, :doc:`wamp/wampprogramming` gives an introduction for programming with WAMP in Python using |ab|.

:doc:`wamp/examples` lists WAMP code examples covering all features of WAMP.


Community
=========

Development of |ab| takes place on the Github `source repository <https://github.com/tavendo/AutobahnPython>`_. We are open for contributions, whether that's code or documentation! We also take bug reports at the `issue tracker <https://github.com/tavendo/AutobahnPython/issues>`_.

The best place to ask questions about |ab| is on the `mailing list <https://groups.google.com/forum/#!forum/autobahnws>`_ or on `StackOverflow <http://stackoverflow.com>`_. Questions on StackOverflow related to |ab| are tagged ``autobahn`` (or ``autobahnws``) and
can be found `here <http://stackoverflow.com/questions/tagged/autobahn?sort=newest>`_.

The best way to search the Web for |ab| related material is by using these search terms:

* ``autobahnpython`` (`try <https://www.google.com/search?q=autobahnpython>`_)
* ``autobahnws`` (`try <https://www.google.com/search?q=autobahnws>`_)

You can also reach users and developers on IRC channel ``autobahn`` at ``freenode.net``.

Finally, we are on `Twitter <https://twitter.com/autobahnws>`_.


.. toctree::
   :maxdepth: 2
   :hidden:

   installation
   websocket/websocketprogramming
   wamp/wampprogramming
   reference/autobahn
   changelog
