WAMP Programming
================

This guide gives an introduction to programming with `WAMP <http://wamp.ws>`__ in Python using |Ab|.

WAMP provides two communication patterns for application components to talk to each other

* :ref:`remote-procedure-calls`
* :ref:`publish-and-subscribe`

and we will cover all four interactions involved in above patterns

1. :ref:`registering-procedures` for remote calling
2. :ref:`calling-procedures` remotely
3. :ref:`subscribing-to-topics` for receiving events
4. :ref:`publishing-events` to topics

.. tip::
   If you are new to WAMP or want to learn more about the design principles behind WAMP, we have a longer text `here <http://wamp.ws/why/>`__.

------

Application Components
----------------------

WAMP is all about creating systems from loosely coupled *application components*. It's application components where your application specific code runs.

A WAMP based system consists of potentially many application components, which all connect to a WAMP router. The router is *generic*, which means, it does *not* run any application code, but only provides routing of events and calls.

Hence, to create a WAMP application, you 

1. write application components
2. connect the components to a router


.. _creating-components:

Creating Components
...................

You create an application component by deriving from a base class provided by |ab|.

When using **Twisted**, you derive from :class:`autobahn.twisted.wamp.ApplicationSession`

.. code-block:: python
   :emphasize-lines: 1

   from autobahn.twisted.wamp import ApplicationSession

   class MyComponent(ApplicationSession):

      def onJoin(self, details):
         print("session established")

whereas when you are using **asyncio**, you derive from :class:`autobahn.asyncio.wamp.ApplicationSession`

.. code-block:: python
   :emphasize-lines: 1

   from autobahn.asyncio.wamp import ApplicationSession

   class MyComponent(ApplicationSession):

      def onJoin(self, details):
         print("session established")

As can be seen, the only difference between Twisted and asyncio is the import (line 1). The rest of the code is identical.

Also, |ab| will invoke callbacks on your application component when certain events happen. For example, :func:`autobahn.wamp.interfaces.ISession.onJoin` is triggered when the WAMP session has connected to a router and joined a realm. We'll come back to this topic later.


.. _running-components:

Running Components
..................

To actually make use of an application components, the component needs to connect to a WAMP router.
|Ab| includes a *runner* that does the heavy lifting for you.

Here is how you use :class:`autobahn.twisted.wamp.ApplicationRunner` with **Twisted**

.. code-block:: python
   :emphasize-lines: 1

   from autobahn.twisted.wamp import ApplicationRunner

   runner = ApplicationRunner(url = "ws://localhost:8080/ws", realm = "realm1")
   runner.run(MyComponent)

and here is how you use :class:`autobahn.asyncio.wamp.ApplicationRunner` with **asyncio**

.. code-block:: python
   :emphasize-lines: 1

   from autobahn.asyncio.wamp import ApplicationRunner

   runner = ApplicationRunner(url = "ws://localhost:8080/ws", realm = "realm1")
   runner.run(MyComponent)

As can be seen, the only difference between Twisted and asyncio is the import (line 1). The rest of the code is identical.

There are two mandatory arguments to ``ApplicationRunner``:

1. ``url``: the WebSocket URL of the WAMP router (for WAMP-over-WebSocket)
2. ``realm``: the *Realm* the component should join on that router

.. tip::
   A *Realm* is a routing namespace and an administrative domain for WAMP. For example, a single WAMP router can manage multiple *Realms*, and those realms are completely separate: an event published to topic T on a Realm R1 is NOT received by a subscribe to T on Realm R2.


.. _remote-procedure-calls:

Remote Procedure Calls
----------------------

**Remote Procedure Call (RPC)** is a messaging pattern involving peers of three roles:

* *Caller*
* *Callee*
* *Dealer*

A *Caller* issues calls to remote procedures by providing the procedure URI and any arguments for the call. The *Callee* will execute the procedure using the supplied arguments to the call and return the result of the call to the Caller.

*Callees* register procedures they provide with *Dealers*. *Callers* initiate procedure calls first to *Dealers*. *Dealers* route calls incoming from *Callers* to *Callees* implementing the procedure called, and route call results back from *Callees* to *Callers*.

The *Caller* and *Callee* will usually run application code, while the *Dealer* works as a generic router for remote procedure calls decoupling *Callers* and *Callees*.


.. _registering-procedures:

Registering Procedures
......................

:func:`autobahn.wamp.interfaces.ICallee.register`

Twisted

.. code-block:: python
   :linenos:
   :emphasize-lines: 14

   from autobahn.twisted.wamp import ApplicationSession
   from twisted.internet.defer import inlineCallbacks

   @inlineCallbacks
   class MyComponent(ApplicationSession):

      def onJoin(self, details):
         print("session established")

         def add2(x, y):
            return x + y

         try:
            yield self.register(add2, u'com.myapp.add2')
            print("procedure registered")
         except Exception as e:
            print("could not register procedure: {0}".format(e))


asyncio

.. code-block:: python
   :linenos:
   :emphasize-lines: 14

   from autobahn.asyncio.wamp import ApplicationSession
   from asyncio import coroutine

   @coroutine
   class MyComponent(ApplicationSession):

      def onJoin(self, details):
         print("session established")

         def add2(x, y):
            return x + y

         try:
            yield from self.register(add2, u'com.myapp.add2')
            print("procedure registered")
         except Exception as e:
            print("could not register procedure: {0}".format(e))


.. _calling-procedures:


Calling Procedures
..................

:func:`autobahn.wamp.interfaces.ICaller.call`

Twisted

.. code-block:: python
   :linenos:
   :emphasize-lines: 11

   from autobahn.twisted.wamp import ApplicationSession
   from twisted.internet.defer import inlineCallbacks

   @inlineCallbacks
   class MyComponent(ApplicationSession):

      def onJoin(self, details):
         print("session established")

         try:
            res = yield self.call(u'com.myapp.add2', 2, 3)
            print("call result: {}".format(res))
         except Exception as e:
            print("call error: {0}".format(e))


asyncio

.. code-block:: python
   :linenos:
   :emphasize-lines: 11

   from autobahn.asyncio.wamp import ApplicationSession
   from asyncio import coroutine

   @coroutine
   class MyComponent(ApplicationSession):

      def onJoin(self, details):
         print("session established")

         try:
            res = yield from self.call(u'com.myapp.add2', 2, 3)
            print("call result: {}".format(res))
         except Exception as e:
            print("call error: {0}".format(e))


.. _publish-and-subscribe:

Publish & Subscribe
-------------------

**Publish & Subscribe (PubSub)** is a messaging pattern involving peers of three roles:

* *Publisher*
* *Subscriber*
* *Broker*

A *Publishers* publishes events to topics by providing the topic URI and any payload for the event. Subscribers of the topic will receive the event together with the event payload.

*Subscribers* subscribe to topics they are interested in with *Brokers*. *Publishers* initiate publication first at *Brokers*. *Brokers* route events incoming from *Publishers* to *Subscribers* that are subscribed to respective topics.

The *Publisher* and *Subscriber* will usually run application code, while the *Broker* works as a generic router for events decoupling *Publishers* from *Subscribers*.


.. _subscribing-to-topics:

Subscribing to Topics
.....................

:func:`autobahn.wamp.interfaces.ISubscriber.subscribe`

Twisted

.. code-block:: python
   :linenos:
   :emphasize-lines: 14

   from autobahn.twisted.wamp import ApplicationSession
   from twisted.internet.defer import inlineCallbacks

   @inlineCallbacks
   class MyComponent(ApplicationSession):

      def onJoin(self, details):
         print("session established")

         def oncounter(count):
            print("event received: {0}", count)

         try:
            yield self.subscribe(oncounter, 'com.myapp.oncounter')
            print("subscribed to topic")
         except Exception as e:
            print("could not subscribe to topic: {0}".format(e))


asyncio

.. code-block:: python
   :linenos:
   :emphasize-lines: 14

   from autobahn.asyncio.wamp import ApplicationSession
   from asyncio import coroutine

   @coroutine
   class MyComponent(ApplicationSession):

      def onJoin(self, details):
         print("session established")

         def oncounter(count):
            print("event received: {0}", count)

         try:
            yield from self.subscribe(oncounter, 'com.myapp.oncounter')
            print("subscribed to topic")
         except Exception as e:
            print("could not subscribe to topic: {0}".format(e))


.. _publishing-events:

Publishing Events
.................

:func:`autobahn.wamp.interfaces.IPublisher.publish`

Twisted

.. code-block:: python
   :linenos:
   :emphasize-lines: 13

   from autobahn.twisted.wamp import ApplicationSession
   from autobahn.twisted.util import sleep
   from twisted.internet.defer import inlineCallbacks

   @inlineCallbacks
   class MyComponent(ApplicationSession):

      def onJoin(self, details):
         print("session established")

         counter = 0
         while True:
            self.publish('com.myapp.oncounter', counter)
            counter += 1
            yield sleep(1)

asyncio

.. code-block:: python
   :linenos:
   :emphasize-lines: 13

   from autobahn.asyncio.wamp import ApplicationSession
   from asyncio import sleep
   from asyncio import coroutine

   @coroutine
   class MyComponent(ApplicationSession):

      def onJoin(self, details):
         print("session established")

         counter = 0
         while True:
            self.publish('com.myapp.oncounter', counter)
            counter += 1
            yield from sleep(1)


.. tip::
   By default, a publisher will not receive an event it publishes even when the publisher is *itself* subscribed to the topic subscribed to. This behavior can be overridden.

.. tip::
   By default, publications are unacknowledged. This means, a ``publish()`` may fail without noticing (like when the session is not authorized to publish to the given topic). This behavior can be overridden.


Upgrading
---------

From < 0.8.0
............

Starting with release 0.8.0, |Ab| now supports WAMP v2, and also support both Twisted and asyncio. This required changing module naming for WAMP v1 (which is Twisted only).

Hence, WAMP v1 code for |ab| **< 0.8.0**

.. code-block:: python

   from autobahn.wamp import WampServerFactory

should be modified for |ab| **>= 0.8.0** for (using Twisted)

.. code-block:: python

   from autobahn.wamp1.protocol import WampServerFactory

.. warning:: WAMP v1 will be deprecated with the 0.9 release of |Ab| which is expected in Q4 2014.
