|AbL|
=====

*Open-source (MIT) real-time framework for Web, Mobile & Internet of Things.*

Latest release: v\ |version| (:ref:`changelog`)

.. ifconfig:: not no_network

   .. raw:: html

      <p>
         <a href="https://travis-ci.org/crossbario/autobahn-python">
            <img src="https://img.shields.io/pypi/v/autobahn.svg" alt="Build Status" />
         </a>
         <a href="https://pypi.python.org/pypi/autobahn">
            <img src="https://img.shields.io/pypi/dm/autobahn.svg" alt="Downloads" />
         </a>
      </p>

-----

|AbL| is part of the `Autobahn`_ project and provides open-source implementations of

* `The WebSocket Protocol <http://tools.ietf.org/html/rfc6455>`_
* `The Web Application Messaging Protocol (WAMP) <http://wamp.ws/>`_

in Python 2 and 3, running on `Twisted`_ **or** `asyncio`_.

Documentation Overview
----------------------

See :ref:`site_contents` for a full site-map. Top-level pages available:

.. toctree::
   :maxdepth: 1

   installation
   asynchronous-programming
   wamp/programming
   wamp/examples
   websocket/programming
   websocket/examples
   reference/autobahn
   contribute
   changelog

-----

Autobahn Features
-----------------

WebSocket allows `bidirectional real-time messaging <http://crossbario.com/blog/post/websocket-why-what-can-i-use-it/>`_ on the Web while `WAMP <http://wamp.ws/>`_ provides applications with `high-level communication abstractions <http://wamp.ws/why/>`_ (remote procedure calling and publish/subscribe) in an open standard WebSocket-based protocol.

|AbL| features:

* framework for `WebSocket`_ and `WAMP`_ clients
* compatible with Python 2.7 and 3.3+
* runs on `CPython`_, `PyPy`_ and `Jython`_
* runs under `Twisted`_ and `asyncio`_
* implements WebSocket `RFC6455`_ (and draft versions Hybi-10+)
* implements `WebSocket compression <http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression>`_
* implements `WAMP`_, the Web Application Messaging Protocol
* supports TLS (secure WebSocket) and proxies
* Open-source (`MIT license <https://github.com/crossbario/autobahn-python/blob/master/LICENSE>`_)

...and much more.

Further, |AbL| is written with these goals:

1. high-performance, fully asynchronous and scalable code
2. best-in-class standards conformance and security

We do take those design and implementation goals quite serious. For example, |AbL| has 100% strict passes with `AutobahnTestsuite`_, the quasi industry standard of WebSocket protocol test suites we originally created only to test |AbL| ;)

.. note::
   In the following, we will just refer to |Ab| instead of the
   more precise term |AbL| and there is no
   ambiguity.


What can I do with Autobahn?
----------------------------

WebSocket is great for apps like **chat**, **trading**, **multi-player games** or **real-time charts**. It allows you to **actively push information** to clients as it happens. (See also :ref:`run_all_examples`)

.. image:: _static/wamp-demos.png
    :alt: ascii-cast of all WAMP demos running
    :height: 443
    :width: 768
    :target: wamp/examples.html#run-all-examples
    :scale: 40%
    :align: right

Further, WebSocket allows you to real-time enable your Web user interfaces: **always current information** without reloads or polling. UIs no longer need to be a boring, static thing. Looking for the right communication technology for your next-generation Web apps? Enter WebSocket.

And WebSocket works great not only on the Web, but also as a protocol for wiring up the **Internet-of-Things (IoT)**. Connecting a sensor or actor to other application components in real-time over an efficient protocol. Plus: you are using the *same* protocol to connect frontends like Web browsers.

While WebSocket already is quite awesome, it is still low-level. Which is why we have WAMP. WAMP allows you to **compose your application from loosely coupled components** that talk in real-time with each other - using nice high-level communication patterns ("Remote Procedure Calls" and "Publish & Subscribe").

WAMP enables application architectures with application code **distributed freely across processes and devices** according to functional aspects. Since WAMP implementations exist for **multiple languages**, WAMP applications can be **polyglot**. Application components can be implemented in a language and run on a device which best fit the particular use case.

WAMP is a routed protocol, so you need a WAMP router. We suggest using `Crossbar.io <http://crossbar.io>`_, but there are also `other implementations <http://wamp.ws/implementations/>`_ available.

More:

* `WebSocket - Why, what, and - can I use it? <http://crossbario.com/blog/post/websocket-why-what-can-i-use-it/>`_
* `Why WAMP? <http://wamp.ws/why/>`_


Show me some code!
------------------

A sample **WebSocket server**:

.. code-block:: python

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

Complete example code:

* `WebSocket Echo (Twisted-based) <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo>`_
* `WebSocket Echo (Asyncio-based) <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/websocket/echo>`_

Introduction to WebSocket Programming with |ab|:

* :doc:`websocket/programming`

---------

A sample **WAMP application component** implementing all client roles:

.. code-block:: python

    from autobahn.twisted.wamp import ApplicationSession
    # or: from autobahn.asyncio.wamp import ApplicationSession
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

* `Twisted Example <https://github.com/crossbario/autobahn-python/blob/master/examples/twisted/wamp/overview/>`__
* `asyncio Example <https://github.com/crossbario/autobahn-python/blob/master/examples/asyncio/wamp/overview/>`__

Introduction to WAMP Programming with |ab|:

* :doc:`wamp/programming`

----------


Where to start
--------------

To get started, jump to :doc:`installation`.

For developers new to asynchronous programming, Twisted or asyncio, we've collected some useful pointers and information in :doc:`asynchronous-programming`.

For **WebSocket developers**, :doc:`websocket/programming` explains all you need to know about using |ab| as a WebSocket library, and includes a full reference for the relevant parts of the API.

:doc:`websocket/examples` lists WebSocket code examples covering a broader range of uses cases and advanced WebSocket features.

For **WAMP developers**, :doc:`wamp/programming` gives an introduction for programming with WAMP in Python using |ab|.

:doc:`wamp/examples` lists WAMP code examples covering all features of WAMP.


Community
---------

Development of |ab| takes place on the GitHub `source repository <https://github.com/crossbario/autobahn-python>`_.

.. note::
   We are open for contributions, whether that's code or documentation! Preferably via pull requests.

We also take **bug reports** at the `issue tracker <https://github.com/crossbario/autobahn-python/issues>`_.

The best place to **ask questions** is on the `mailing list <https://groups.google.com/forum/#!forum/autobahnws>`_. We'd also love to hear about your project and what you are using |ab| for!

Another option is `StackOverflow <http://stackoverflow.com>`_ where `questions <http://stackoverflow.com/questions/tagged/autobahn?sort=newest>`__ related to |ab| are tagged `"autobahn" <http://stackoverflow.com/tags/autobahn/info>`__ (or `"autobahnws" <http://stackoverflow.com/tags/autobahnws/info>`__).

The best way to **Search the Web** for related material is by using these (base) search terms:

* `"autobahnpython" <https://www.google.com/search?q=autobahnpython>`__
* `"autobahnws" <https://www.google.com/search?q=autobahnws>`__

You can also reach users and developers on **IRC** channel ``#autobahn`` at `freenode.net <http://www.freenode.net/>`__.

Finally, we are on `Twitter <https://twitter.com/autobahnws>`_.


.. toctree::
   :hidden:

   installation
   asynchronous-programming
   websocket/programming
   wamp/programming
   websocket/examples
   wamp/examples
   reference/autobahn
   contribute
   changelog
