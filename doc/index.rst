.. _Autobahn: http://autobahn.ws
.. _AutobahnJS: http://autobahn.ws/js
.. _AutobahnPython: **Autobahn**\|Python
.. _WebSocket: http://tools.ietf.org/html/rfc6455
.. _RFC6455: http://tools.ietf.org/html/rfc6455
.. _WAMP: http://wamp.ws/
.. _Twisted: http://twistedmatrix.com/
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _CPython: http://python.org/
.. _PyPy: http://pypy.org/
.. _Jython: http://jython.org/
.. _WAMPv1: http://wamp.ws/spec/wamp1/
.. _WAMPv2: https://github.com/tavendo/WAMP/blob/master/spec/README.md
.. _AutobahnTestsuite: http://autobahn.ws/testsuite


|ab| Reference
==============

Release v\ |version|. (:ref:`Changelog`)


|ab| is a subproject of `Autobahn`_ and provides open-source implementations of

* `The WebSocket Protocol <http://tools.ietf.org/html/rfc6455>`_
* `The Web Application Messaging Protocol (WAMP) <http://wamp.ws/>`_

in Python 2 and 3, running on `Twisted`_ and `asyncio`_.

WebSocket allows `bidirectional real-time messaging on the Web <http://tavendo.com/blog/post/websocket-why-what-can-i-use-it/>`_ and WAMP adds `asynchronous Remote Procedure Calls and Publish & Subscribe on top of WebSocket <http://wamp.ws/why/>`_.

.. note:: Currently, only WebSocket is implemented on both `Twisted`_ and `asyncio`_. WAMP is currently only implemented on `Twisted`_. WAMP on `asyncio`_ is planned, but we can't guarantee a specific timeframe.


Show me some code
-----------------

Using |ab| you can create both clients and servers in Python speaking just plain WebSocket or WAMP.

WebSocket
+++++++++

A sample WebSocket server:

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


WAMP
++++

A sample WAMP application component:


.. code-block:: python

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


.. note::

   * WAMP application components can be run in servers and clients without any modification to your component class.

   * While |ab| supports both `Twisted`_ and `asyncio`_ for WebSocket code, WAMP is currently only supported on Twisted.

   * `AutobahnJS`_ allows you to write WAMP application components in JavaScript which run in browsers and Nodejs. Here is how above example `looks like <https://github.com/tavendo/AutobahnJS/#show-me-some-code>`_ in JavaScript.


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
* Open-source (Apache 2 `license <https://github.com/tavendo/AutobahnPython/blob/master/LICENSE>`_)


Get it now
----------

Install from the Python package index:

::

    $ pip install -U autobahn


Check the installation:

.. doctest::

   >>> from autobahn import __version__
   >>> print __version__
   0.8.5


Where to go from here
---------------------

:doc:`websockettoc` explains all you need to know about using |ab| as a WebSocket library, and includes a full reference for the relevant parts of the API.

:doc:`wamp2` is the API reference for the WAMP v2 implementation contained in |ab|.

:doc:`wampprogramming` gives an introduction for programming with WAMP (v2) in Python using |ab|.

:doc:`wamp1toc` contains the API reference for the WAMP v1 implementation in |ab|.

:doc:`examples` lists code examples covering a broader range of uses cases and advanced WAMP features.

.. toctree::
   :maxdepth: 3
   :hidden:

   websockettoc
   wamp2
   wampprogramming
   wamp1toc
   changelog
   table_of_contents


