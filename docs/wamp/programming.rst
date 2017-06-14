==================
 WAMP Programming
==================

This guide gives an introduction to programming with `WAMP <http://wamp.ws>`__ in Python using |Ab|. (Go straight to :ref:`wamp_examples`)

WAMP provides two communication patterns for application components to talk to each other

* :ref:`remote-procedure-calls`
* :ref:`publish-and-subscribe`

and we will cover all four interactions involved in above patterns

1. :ref:`registering-procedures` for remote calling
2. :ref:`calling-procedures` remotely
3. :ref:`subscribing-to-topics` for receiving events
4. :ref:`publishing-events` to topics

Note that WAMP is a "routed" protocol, and defines a Dealer and Broker role. Practically speaking, this means that any WAMP client needs a WAMP Router to talk to. We provide an open-source one called `Crossbar <http://crossbar.io>`_ (there are `other routers <http://wamp.ws/implementations/#routers>`_ available). See also `the WAMP specification <http://wamp.ws/spec/>`_ for more details

.. tip::
   If you are new to WAMP or want to learn more about the design principles behind WAMP, we have a longer text `here <http://wamp.ws/why/>`__.

------

Application Components
======================

WAMP is all about creating systems from loosely coupled *application components*. These application components are where your application-specific code runs.

A WAMP-based system consists of potentially many application components, which all connect to a WAMP router. The router is *generic*, which means, it does *not* run any application code, but only provides routing of events and calls.

These components use either Remote Procedure Calls (RPC) or Publish/Subscribe (PubSub) to communicate. Each component can do any mix of: register, call, subscribe or publish.

For RPC, an application component registers a callable method at a URI ("endpoint"), and other components call it via that endpoint.

In the Publish/Subscribe model, interested components subscribe to an event URI and when a publish to that URI happens, the event payload is routed to all subscribers:

Hence, to create a WAMP application, you:

1. write application components
2. connect the components to a router

Note that each component can do any mix of registering, calling, subscribing and publishing -- it is entirely up to you to logically group functionality as suits your problem space.


.. _creating-components:

Creating Components
-------------------

You create an application component by deriving from a base class provided by |ab|.

When using **Twisted**, you derive from :class:`autobahn.twisted.wamp.ApplicationSession`

.. code-block:: python
   :emphasize-lines: 1

   from autobahn.twisted.wamp import ApplicationSession

   class MyComponent(ApplicationSession):
      def onJoin(self, details):
         print("session ready")

whereas when you are using **asyncio**, you derive from :class:`autobahn.asyncio.wamp.ApplicationSession`

.. code-block:: python
   :emphasize-lines: 1

   from autobahn.asyncio.wamp import ApplicationSession

   class MyComponent(ApplicationSession):
      def onJoin(self, details):
         print("session ready")

As can be seen, the only difference between Twisted and asyncio is the import (line 1). The rest of the code is identical.

Also, |ab| will invoke callbacks on your application component when certain events happen. For example, :func:`ISession.onJoin <autobahn.wamp.interfaces.ISession.onJoin>` is triggered when the WAMP session has connected to a router and joined a realm. We'll come back to this topic later.


.. _running-components:

Running Components
------------------

To actually make use of an application components, the component needs to connect to a WAMP router.
|Ab| includes a *runner* that does the heavy lifting for you.

Here is how you use :class:`autobahn.twisted.wamp.ApplicationRunner` with **Twisted**

.. code-block:: python
   :emphasize-lines: 1

   from autobahn.twisted.wamp import ApplicationRunner

   runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1")
   runner.run(MyComponent)

and here is how you use :class:`autobahn.asyncio.wamp.ApplicationRunner` with **asyncio**

.. code-block:: python
   :emphasize-lines: 1

   from autobahn.asyncio.wamp import ApplicationRunner

   runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1")
   runner.run(MyComponent)

As can be seen, the only difference between Twisted and asyncio is the import (line 1). The rest of the code is identical.

There are two mandatory arguments to ``ApplicationRunner``:

1. ``url``: the WebSocket URL of the WAMP router (for WAMP-over-WebSocket)
2. ``realm``: the *Realm* the component should join on that router

.. tip::
   A *Realm* is a routing namespace and an administrative domain for WAMP. For example, a single WAMP router can manage multiple *Realms*, and those realms are completely separate: an event published to topic T on a Realm R1 is NOT received by a subscribe to T on Realm R2.


Here are quick templates for you to copy/paste for creating and running a WAMP component.

**Twisted**:

.. code-block:: python
    :emphasize-lines: 2

    from twisted.internet.defer import inlineCallbacks
    from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

    class MyComponent(ApplicationSession):

        @inlineCallbacks
        def onJoin(self, details):
            print("session joined")
            # can do subscribes, registers here e.g.:
            # yield self.subscribe(...)
            # yield self.register(...)

    if __name__ == '__main__':
        runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1")
        runner.run(MyComponent)


**asyncio**:

.. code-block:: python
    :emphasize-lines: 1

    from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

    class MyComponent(ApplicationSession):
        async def onJoin(self, details):
            print("session joined")
            # can do subscribes, registers here e.g.:
            # await self.subscribe(...)
            # await self.register(...)

    if __name__ == '__main__':
        runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1")
        runner.run(MyComponent)


Running a WAMP Router
=====================

The component we've created attempts to connect to a **WAMP router** running locally which accepts connections on port ``8080``, and for a realm ``realm1``.

Our suggested way is to use `Crossbar.io <http://crossbar.io>`_ as your WAMP router. There are `other WAMP routers <http://wamp.ws/implementations#routers>`_ besides Crossbar.io as well.

Once you've `installed Crossbar.io <http://crossbar.io/docs/Quick-Start/>`_, initialize an instance of it with the default settings, which will accept WAMP (over WebSocket) connections on ``ws://<hostname>:8080/ws`` and has a ``realm1`` pre-configured.

To do this, do

.. code-block:: sh

   crossbar init

This will create the default Crossbar.io node configuration ``./.crossbar/config.json``. You can then start Crossbar.io by doing:

.. code-block:: sh

   crossbar start


.. _remote-procedure-calls:

Remote Procedure Calls
======================

**Remote Procedure Call (RPC)** is a messaging pattern involving peers of three roles:

* *Caller*
* *Callee*
* *Dealer*

A *Caller* issues calls to remote procedures by providing the procedure URI and any arguments for the call. The *Callee* will execute the procedure using the supplied arguments to the call and return the result of the call to the Caller.

*Callees* register procedures they provide with *Dealers*. *Callers* initiate procedure calls first to *Dealers*. *Dealers* route calls incoming from *Callers* to *Callees* implementing the procedure called, and route call results back from *Callees* to *Callers*.

The *Caller* and *Callee* will usually run application code, while the *Dealer* works as a generic router for remote procedure calls decoupling *Callers* and *Callees*. Thus, the *Caller* can be in a separate process (even a separate implementation language) from the *Callee*.


.. _registering-procedures:


Registering Procedures
----------------------

To make a procedure available for remote calling, the procedure needs to be *registered*. Registering a procedure is done by calling :meth:`ICallee.register <autobahn.wamp.interfaces.ICallee.register>` from a session.

Here is an example using **Twisted**

.. code-block:: python
    :linenos:
    :emphasize-lines: 14

    from autobahn.twisted.wamp import ApplicationSession
    from twisted.internet.defer import inlineCallbacks


    class MyComponent(ApplicationSession):
        @inlineCallbacks
        def onJoin(self, details):
            print("session ready")

            def add2(x, y):
                return x + y

            try:
                yield self.register(add2, u'com.myapp.add2')
                print("procedure registered")
            except Exception as e:
                print("could not register procedure: {0}".format(e))

The procedure ``add2`` is registered (line 14) under the URI ``u"com.myapp.add2"`` immediately in the ``onJoin`` callback which fires when the session has connected to a *Router* and joined a *Realm*.

.. tip::

   You can register *local* functions like in above example, *global* functions as well as *methods* on class instances. Further, procedures can also be automatically registered using *decorators*.

When the registration succeeds, authorized callers will immediately be able to call the procedure (see :ref:`calling-procedures`) using the URI under which it was registered (``u"com.myapp.add2"``).

A registration may also fail, e.g. when a procedure is already registered under the given URI or when the session is not authorized to register procedures.

Using **asyncio**, the example looks like this:

.. code-block:: python
    :linenos:
    :emphasize-lines: 11

    from autobahn.asyncio.wamp import ApplicationSession

    class MyComponent(ApplicationSession):
        async def onJoin(self, details):
            print("session ready")

            def add2(x, y):
                return x + y

            try:
                await self.register(add2, u'com.myapp.add2')
                print("procedure registered")
            except Exception as e:
                print("could not register procedure: {0}".format(e))

The differences compared with the Twisted variant are:

* the ``import`` of ``ApplicationSession``
* the use of ``async`` keyword to declare co-routines
* the use of ``await`` instead of ``yield``


.. _calling-procedures:

Calling Procedures
------------------

Calling a procedure (that has been previously registered) is done using :func:`autobahn.wamp.interfaces.ICaller.call`.

Here is how you would call the procedure ``add2`` that we registered in :ref:`registering-procedures` under URI ``com.myapp.add2`` in **Twisted**

.. code-block:: python
    :linenos:
    :emphasize-lines: 11

    from autobahn.twisted.wamp import ApplicationSession
    from twisted.internet.defer import inlineCallbacks


    class MyComponent(ApplicationSession):
        @inlineCallbacks
        def onJoin(self, details):
            print("session ready")

            try:
                res = yield self.call(u'com.myapp.add2', 2, 3)
                print("call result: {}".format(res))
            except Exception as e:
                print("call error: {0}".format(e))

And here is the same done on **asyncio**

.. code-block:: python
    :linenos:
    :emphasize-lines: 9

    from autobahn.asyncio.wamp import ApplicationSession


    class MyComponent(ApplicationSession):
        async def onJoin(self, details):
            print("session ready")

            try:
                res = await self.call(u'com.myapp.add2', 2, 3)
                print("call result: {}".format(res))
            except Exception as e:
                print("call error: {0}".format(e))


.. _publish-and-subscribe:

Publish & Subscribe
===================

**Publish & Subscribe (PubSub)** is a messaging pattern involving peers of three roles:

* *Publisher*
* *Subscriber*
* *Broker*

A *Publisher* publishes events to topics by providing the topic URI and any payload for the event. Subscribers of the topic will receive the event together with the event payload.

*Subscribers* subscribe to topics they are interested in with *Brokers*. *Publishers* initiate publication first at a *Broker*. *Brokers* route events incoming from *Publishers* to *Subscribers* that are subscribed to respective topics.

The *Publisher* and *Subscriber* will usually run application code, while the *Broker* works as a generic router for events thus decoupling *Publishers* from *Subscribers*. That is, there can be many *Subscribers* written in different languages on different machines which can all receive a single event published by an independant *Publisher*.


.. _subscribing-to-topics:

Subscribing to Topics
---------------------

To receive events published to a topic, a session needs to first subscribe to the topic. Subscribing to a topic is done by calling :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`.

Here is a **Twisted** example:

.. code-block:: python
    :linenos:
    :emphasize-lines: 14

    from autobahn.twisted.wamp import ApplicationSession
    from twisted.internet.defer import inlineCallbacks


    class MyComponent(ApplicationSession):
        @inlineCallbacks
        def onJoin(self, details):
            print("session ready")

            def oncounter(count):
                print("event received: {0}", count)

            try:
                yield self.subscribe(oncounter, u'com.myapp.oncounter')
                print("subscribed to topic")
            except Exception as e:
                print("could not subscribe to topic: {0}".format(e))

We create an event handler function ``oncounter`` (you can name that as you like) which will get called whenever an event for the topic is received.

To subscribe (line 15), we provide the event handler function (``oncounter``) and the URI of the topic to which we want to subscribe (``u'com.myapp.oncounter'``).

When the subscription succeeds, we will receive any events published to ``u'com.myapp.oncounter'``. Note that we won't receive events published *before* the subscription succeeds.

The corresponding **asyncio** code looks like this

.. code-block:: python
    :linenos:
    :emphasize-lines: 12

    from autobahn.asyncio.wamp import ApplicationSession


    class MyComponent(ApplicationSession):
       async def onJoin(self, details):
           print("session ready")

           def oncounter(count):
               print("event received: {0}", count)

           try:
               await self.subscribe(oncounter, u'com.myapp.oncounter')
               print("subscribed to topic")
           except Exception as e:
               print("could not subscribe to topic: {0}".format(e))

Again, nearly identical to Twisted.


.. _publishing-events:

Publishing Events
-----------------

Publishing an event to a topic is done by calling :func:`autobahn.wamp.interfaces.IPublisher.publish`.

Events can carry arbitrary positional and keyword based payload -- as long as the payload is serializable in JSON.

Here is a **Twisted** example that will publish an event to topic ``u'com.myapp.oncounter'`` with a single (positional) payload being a counter that is incremented for each publish:

.. code-block:: python
    :linenos:
    :emphasize-lines: 13

    from autobahn.twisted.wamp import ApplicationSession
    from autobahn.twisted.util import sleep
    from twisted.internet.defer import inlineCallbacks


    class MyComponent(ApplicationSession):
        @inlineCallbacks
        def onJoin(self, details):
            print("session ready")

            counter = 0
            while True:
                self.publish(u'com.myapp.oncounter', counter)
                counter += 1
                yield sleep(1)

The corresponding **asyncio** code looks like this

.. code-block:: python
    :linenos:
    :emphasize-lines: 11

    from autobahn.asyncio.wamp import ApplicationSession
    from asyncio import sleep


    class MyComponent(ApplicationSession):
        async def onJoin(self, details):
            print("session ready")

            counter = 0
            while True:
                self.publish(u'com.myapp.oncounter', counter)
                counter += 1
                await sleep(1)

When publishing, you can pass an `options=` kwarg which is an instance of :class:`PublishOptions <autobahn.wamp.types.PublishOptions>`. Many of the options require support from the router.

 - whitelisting and blacklisting (all the `eligible*` and `exclude*` options) can affect which subscribers receive the publish; see `crossbar documentation <http://crossbar.io/docs/Subscriber-Black-and-Whitelisting/>`_ for more information;
 - `retain=` asks the router to retain the message;
 - `acknowledge=` asks the router to notify you it received the publish (note that this does *not* wait for every subscriber to have received the publish).

.. tip::
   By default, a publisher will not receive an event it publishes even when the publisher is *itself* subscribed to the topic subscribed to. This behavior can be overridden; see :class:`PublishOptions <autobahn.wamp.types.PublishOptions>` and ``exclude_me=False``.

.. tip::
   By default, publications are *unacknowledged*. This means, a ``publish()`` may fail *silently* (like when the session is not authorized to publish to the given topic). This behavior can be overridden; see :class:`PublishOptions <autobahn.wamp.types.PublishOptions>` and ``acknowledge=True``.


.. _session_lifecycle:

Session Lifecycle
=================

A WAMP application component has this lifecycle:

1. component created
2. transport connected (:meth:`ISession.onConnect <autobahn.wamp.interfaces.ISession.onConnect>` called)
3. authentication challenge received (only for authenticated WAMP sessions, :meth:`ISession.onChallenge <autobahn.wamp.interfaces.ISession.onChallenge>` called)
4. session established (realm joined, :meth:`ISession.onJoin <autobahn.wamp.interfaces.ISession.onJoin>` called)
5. session closed (realm left, :meth:`ISession.onLeave <autobahn.wamp.interfaces.ISession.onLeave>` called)
6. transport disconnected (:meth:`ISession.onDisconnect <autobahn.wamp.interfaces.ISession.onDisconnect>` called)

The :class:`ApplicationSession <autobahn.twisted.wamp.ApplicationSession>` will fire the following events which you can handle by overriding the respective method (see :class:`ISession <autobahn.wamp.interfaces.ISession>` for more information):

.. code-block:: python

    class MyComponent(ApplicationSession):
        def __init__(self, config=None):
            ApplicationSession.__init__(self, config)
            print("component created")

        def onConnect(self):
            print("transport connected")
            self.join(self.config.realm)

        def onChallenge(self, challenge):
            print("authentication challenge received")

        def onJoin(self, details):
            print("session joined")

        def onLeave(self, details):
            print("session left")

        def onDisconnect(self):
            print("transport disconnected")


Logging
=======

Internally, |Ab| uses `txaio <https://github.com/crossbario/txaio>`_ as an abstraction layer over Twisted and asyncio APIs. `txaio`_ also provides an abstracted logging API, which is what both |Ab| and Crossbar_ use.

There is a `txaio Programming Guide <http://txaio.readthedocs.org/en/latest/programming-guide.html#logging>`_ which includes information on logging. If you are writing new code, you can choose the txaio_ APIs for maximum compatibility and runtime-efficiency (see below). If you prefer to write idiomatic logging code to "go with" the event-based frameword you've chosen, that's possible as well. For asyncio_ this is Python's built-in `logging <https://docs.python.org/3.5/library/logging.html>`_ module; for Twisted it is the `post-15.2.0 logging API <http://twistedmatrix.com/documents/current/core/howto/logger.html>`_. The logging system in `txaio`_ is able to interoperate with the legacy Twisted logging API as well.

The txaio_ API encourages a more structured approach while still achieving easily-rendered text logging messages. The basic idiom is to use new-style Python formatting strings and pass any "data" as kwargs. So a typical logging call might look like: ``self.log.info("Knob {frob.name} moved {degrees} right.", knob=an_obj, degrees=42)`` and if the "info" log level is not enabled, the string won't be "interpolated" (i.e. ``str()`` will not be invoked on any of the args, and a new string won't be produced). On top of that, logging observers may examine the ``kwargs`` and do things beyond "normal" logging. This is very much inspired by ``twisted.logger``; you can read the `Twisted logging documentation <http://twistedmatrix.com/documents/current/core/howto/logger.html>`_ for more insight.

Before any logging happens of course you must activate the logging system. There is a convenience method in `txaio`_ called ``txaio.start_logging``. This will use ``twisted.logger.globalLogBeginner`` on Twisted or ``logging.Logger.addHandler`` under asyncio and allows you to specify and output stream and/or a log level. Valid levels are the list of strings in ``txaio.interfaces.log_levels``.

If you have instead got your own log-starting code (e.g. ``twistd``) or Twisted/asyncio specific log handlers (``logging.Handler`` subclass on asyncio and ``ILogObserver`` implementer under Twisted) then you will still get |Ab| and `Crossbar`_ messages. Probably the formatting will be slightly different from what ``txaio.start_logging`` provides. In either case, **do not depend on the formatting** of the messages e.g. by "screen-scraping" the logs.

We very much **recommend using the ``txaio.start_logging()`` method** of activating the logging system, as we've gone to pains to ensure that over-level logs are a "no-op" and incur minimal runtime cost. We achieve this by re-binding all out-of-scope methods on any logger created by ``txaio.make_logger()`` to a do-nothing function (by saving weak-refs of all the loggers created); at least on `PyPy`_ this is very well optimized out. This allows us to be generous with ``.debug()`` or ``.trace()`` calls without incurring very much overhead. Your Milage May Vary using other methods. If you haven't called ``txaio.start_logging()`` this optimization is not activated.


Upgrading
=========

From < 0.8.0
------------

Starting with release 0.8.0, |Ab| now supports WAMP v2, and also support both Twisted and asyncio. This required changing module naming for WAMP v1 (which is Twisted only).

Hence, WAMP v1 code for |ab| **< 0.8.0**

.. code-block:: python

   from autobahn.wamp import WampServerFactory

should be modified for |ab| **>= 0.8.0** for (using Twisted)

.. code-block:: python

   from autobahn.wamp1.protocol import WampServerFactory

.. warning:: WAMP v1 will be deprecated with the 0.9 release of |Ab| which is expected in Q4 2014.


From < 0.9.4
------------

Starting with release 0.9.4, all WAMP router code in |Ab| has been split out and moved to `Crossbar.io <http://crossbar.io>`_. Please see the announcement `here <https://groups.google.com/d/msg/autobahnws/bCj7O2G2sxA/6-pioJZ_S_MJ>`__.
