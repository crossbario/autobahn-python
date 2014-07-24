Introduction
============

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

A sample WAMP application component implementing all client roles:

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


Complete example code:

 * **server**, which provides a remote procedure enpoint and publishes to a topic - `Twisted <https://github.com/tavendo/AutobahnPython/blob/master/examples/twisted/wamp/beginner/server.py>`__ - `asyncio <https://github.com/tavendo/AutobahnPython/blob/master/examples/asyncio/wamp/beginner/server.py>`__
 * **client**, which calls the procedure and subscribes to the topic - `Twisted <https://github.com/tavendo/AutobahnPython/blob/master/examples/twisted/wamp/beginner/client.py>`__ - `asyncio <https://github.com/tavendo/AutobahnPython/blob/master/examples/asyncio/wamp/beginner/client.py>`__

There are many more examples showing options and advanced features:

* :doc:`WebSocket Examples <websocket/examples>`.
* :doc:`WAMP Examples <wamp/examples>`.


.. note::

   * WAMP application components can be run in servers and clients without any modification to your component class.

   * `AutobahnJS`_ allows you to write WAMP application components in JavaScript which run in browsers and Nodejs. Here is how above example `looks like <https://github.com/tavendo/AutobahnJS/#show-me-some-code>`_ in JavaScript.
