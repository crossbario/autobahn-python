.. _Autobahn: http://autobahn.ws
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


Autobahn|Python Reference
=========================

Release v\ |version|. (:ref:`Changelog`)


**Autobahn** Python is a subproject of `Autobahn`_ and provides open-source implementations of

* `The WebSocket Protocol <http://tools.ietf.org/html/rfc6455>`_
* `The Web Application Messaging Protocol (WAMP) <http://wamp.ws/>`_

in Python running on `Twisted`_ and `asyncio`_.

WebSocket allows `bidirectional real-time messaging on the Web <http://tavendo.com/blog/post/websocket-why-what-can-i-use-it/>`_ and WAMP adds asynchronous *Remote Procedure Calls* and *Publish & Subscribe* on top of WebSocket. 

You can use **Autobahn**|Python to create clients and servers in Python speaking just plain WebSocket or WAMP:



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




Features
--------

You can use **Autobahn**|Python to create clients and servers in Python speaking just plain WebSocket or WAMP:

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
::

    $ pip install -U autobahn


Contents
========

.. toctree::
   :maxdepth: 3

   websockettoc
   wamp1toc
   wamp2
   wamp2all


* :ref:`genindex`
* :ref:`search`
