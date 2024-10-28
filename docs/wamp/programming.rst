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

There are two ways to create components using |ab|. One is based on deriving from a particular class and overriding methods and the other is based on functions and decorators. The latter is the recommended approach (but note that many examples and existing code use the subclassing approach). Both are fine and end up calling the same code under the hood.

For both approaches you get to decide if you prefer to use **Twisted** or **asyncio** and express this through ``import``. This is :mod:`autobahn.twisted.*` versus :mod:`autobahn.asyncio.*`

When using **Twisted** you import from ``autobahn.twisted.component``:

.. code-block:: python
    :emphasize-lines: 1

    from autobahn.twisted.component import Component

    comp = Component(...)

    @comp.on_join
    def joined(session, details):
        print("session ready")


whereas when you are using **asyncio**:

.. code-block:: python
   :emphasize-lines: 1

    from autobahn.asyncio.component import Component

    comp = Component(...)

    @comp.on_join
    def joined(session, details):
        print("session ready")

As can be seen, the only difference between Twisted and asyncio is the import (line 1). The rest of the code is identical. For Twisted, you can use ``@inlineCallbacks`` or return ``Deferred`` from methods decorated with ``on_join``; in Python 3 (with asyncio or Twisted) you would use coroutines (``async def``).

There are four "life cycle" events that |ab| will trigger on your components: ``connect``, ``join``, ``leave``, and ``disconnect``. These all have corresponding decorators (or you can use code like ``comp.on('join', the_callback)`` if you prefer). We go over these events later.


.. _running-components:

Running Components
------------------

To actually make use of an application components, the component needs to connect to a WAMP router.
|Ab| includes a :func:`run` function that does the heavy lifting for you.

.. code-block:: python
   :emphasize-lines: 1-2

    from autobahn.twisted.component import Component
    from autobahn.twisted.component import run

    comp = Component(
        transports=u"ws://localhost:8080/ws",
        realm=u"realm1",
    )

    @comp.on_join
    def joined(session, details):
        print("session ready")

    if __name__ == "__main__":
        run([comp])

and with **asyncio**:

.. code-block:: python
   :emphasize-lines: 1-2

    from autobahn.asyncio.component import Component
    from autobahn.asyncio.component import run

    comp = Component(
        transports=u"ws://localhost:8080/ws",
        realm=u"realm1",
    )

    @comp.on_join
    async def joined(session, details):
        print("session ready")

    if __name__ == "__main__":
        run([comp])

As can be seen, the only difference between Twisted and asyncio is the import (line 1 and 2). The rest of the code is identical.

The configuration of the component is specified when you construct it; the above is the bare minimum -- you can specify many transports (which will be tried and re-tried in order) as well as authentication options, the realm to join, re-connection parameters, etcetera. See :ref:`component_config` for details. A single Python program can run many different ``Component`` instances at once and you can interconnect these as you see fit -- so a single program can have multiple WAMP connections (e.g. to different Realms or different WAMP routers) at once.

.. tip::
   A *Realm* is a routing namespace and an administrative domain for WAMP. For example, a single WAMP router can manage multiple *Realms*, and those realms are completely separate: an event published to topic T on a Realm R1 is NOT received by a subscribe to T on Realm R2.


Running Subclass-Style Components
---------------------------------

You can use the same "component" APIs to run a component based on subclassing `ApplicationSession`. In older code it's common to see :class:`autobahn.twisted.wamp.ApplicationRunner` or :class:`autobahn.asyncio.wamp.ApplicationRunner`. This runner lacks many of the options of the :func:`autobahn.twisted.component.run` or :func:`autobahn.asyncio.component.run` functions, so although it can still be useful you likely want to upgrade to :func:`run`.

All you need to do is set the `session_factory` of a :class:`autobahn.twisted.component.Component` instance to your :class:`autobahn.twisted.wamp.ApplicationSession` subclass (or pass it as a ``kwarg`` when creating the :class:`Component`)

.. code-block:: python

    comp = Component(
        session_factory=MyApplicationSession,
    )


Patterns for More Complicated Applications
------------------------------------------

Many of the examples in this documentation use a decorator style with fixed, static WAMP URIs for registrations and subscriptions. If you have a more complex application, you might want to create URIs at run-time or link several :class:`Component` instances together.

It is important to remember that :class:`Component` handles re-connection  -- this implies there are times when your component is **not** connected. The `on_join` handlers are run whenever a fresh WAMP session is started, so this is the appropriate way to hook in "initialization"-style code (`on_leave` is where "un-initialization" code goes). Note that each new WAMP session will use a new instance of :class:`ApplicationSession`.

Here's a slightly more complex example that is a small `Klein`_ Web application that publishes to a WAMP session when a certain URL is requested (note that the Crossbario.io router supports `various REST-style integrations <https://crossbar.io/docs/HTTP-Bridge/>`_ already). Using a similar pattern, you could tie together two or more :class:`Component` instances (even connecting to two or more *different* WAMP routers).

.. _Klein: https://github.com/twisted/klein

.. literalinclude:: ../listings/webapp.py
   :language: python


Longer Example
--------------

Here is a more-complete example showing some of the options you can pass when setting up a `Component`. This example can be run against the Crossbar.io router configuration that comes with |ab| -- just run `crossbar start` in  `examples/router/` in your clone.

**Twisted**:

.. literalinclude:: ../listings/tx_complete.py
   :language: python


The Python3 / asyncio version of the same example is nearly identical except for some imports (and the use of `async def` instead of Twisted's decorators):

**asyncio**:

.. literalinclude:: ../listings/aio_complete.py
    :emphasize-lines: 1
    :language: python

.. _component_config:

Component Configuration Options
===============================

Most of the arguments given when creating a new :class:`Component` are a series of ``dict`` instances containing "configuration"-style information. These are documented in :class:`autobahn.wamp.component.Component` so we go through the most important ones here:

transports=
-----------

You may define any number of transports; these are tried in round-robin order when doing connections (and subsequent re-connections). If the ``is_fatal=`` predicate is used and returns ``True`` for any errors, that transport won't be used any more (and when no transports remain, the :class:`Component` has "failed").

Each transport is defined similarly to `"connecting transports" <https://crossbar.io/docs/WebSocket-Transport/#connecting-transports>`_ in Crossbar.io but as a simplification a plain unicode URI may be used, for example ``transports=u"ws://example.com/ws"`` or ``transports=[u"ws://example.com/ws"]``. If using a ``dict`` instead of a string you can specify the following keys:

- ``type``: ``"websocket"`` (default) or ``"rawsocket"``
- ``url``: the URL of the router to connect to (very often, this will be the same as the "endpoint" host but not always)
- ``endpoint``: (optional; can be inferred from above)
  - ``type``: ``"tcp"`` or ``"unix"``
  - ``host``, ``port``: only for ``type="tcp"``
  - ``path``: only for ``type="unix"``
  - ``tls``: bool (advanced Twisted users can pass :class:`CertificateOptions`); this is also inferred from a ``wss:`` scheme.

In addition, each transport may have some options related to re-connections:

- ``max_retries``: (default -1, "try forever") or a hard limit.
- ``max_retry_delay``: (default 300)
- ``initial_retry_delay``: (default 1.5) how long we wait to re-connect the first time
- ``retry_delay_growth``: (default 1.5) a multiplier expanding our delay each try (so the second re-connect we wait ``retry_delay_growth * initial_retry_delay`` seconds).
- ``retry_delay_jitter``: (default 0.1) percent of total retry delay to add/subtract as jitter

After a successful connection, all re-connection values are set back to their original values.


realm=
------

Each WAMP Session is associated with precisely one realm, and so is each `Component`. A "realm" is a logically separated WAMP URI space (and is isolated from all other realms that may exist on a WAMP router). You must pass a unicode string here.


session_factory=
----------------

Leaving this as ``None`` should be fine for most users. You may pass an :class:`ApplicationSession` subclass here (or even a callable that takes a single ``config`` argument and returns an instance implementing :class:`.IApplicationSession`) to create new session objects. This can be used by users of the "subclass"-style API who still want to take advantage of the configuration of :class:`Component` and :func:`run()`. The ``session`` argument passed in many of the callbacks will be an instance of this (see also :ref:`session_lifecycle`).


authentication=
---------------

This contains a ``dict`` mapping an authenticator name to its configuration. You do not have to have any authentication information, in which case ``anonymous`` will be used. Currently valid authenticators are: ``anonymous``, ``ticket``, ``wampcra``, ``cryptosign`` (experimental) and ``scram`` (experimental).

Typically the administrator of your WAMP router will decide which authentication methods are allowed. See for example `Crossbar.io's authentication documentation <https://crossbar.io/docs/Authentication/>`_ for some discussion of the various methods.

``anonymous`` accepts no options. Most methods accept options for:

  - ``authextra``: application-specific information
  - ``authid``: unicode username
  - ``authrole``: the desired role inside the realm

The other authentication methods take additional options as indicated
below:

  - **wampcra**: also accepts  ``secret`` (the password)
  - **cryptosign** (experimental): also accepts ``privkey``, the hex-encoded ed25519 private key
  - **scram** (experimental): also requires ``nonce`` (hex-encoded), ``kdf`` (``"argon2id-13"`` or ``"pbkdf2"``), ``salt`` (hex-encoded), ``iterations`` (integer) and optionally ``memory`` (integer) and ``channel_binding`` (currently ignored).
  - **ticket**: accepts only the ``ticket`` option


Running a WAMP Router
=====================

The component we've created attempts to connect to a **WAMP router** running locally which accepts connections on port ``8080``, and for a realm ``crossbardemo``.

Our suggested way is to use `Crossbar.io <http://crossbar.io>`_ as your WAMP router. There are `other WAMP routers <http://wamp.ws/implementations#routers>`_ besides Crossbar.io as well.

Once you've `installed Crossbar.io <http://crossbar.io/docs/Quick-Start/>`_, run the example configuration from ``examples/router`` in your |ab| clone. If you want to start fresh, you can instead do this:

.. code-block:: sh

   crossbar init

This will create the default Crossbar.io node configuration ``./.crossbar/config.json``. You can then start Crossbar.io by doing:

.. code-block:: sh

   crossbar start

**Note**: The defaults in the above will not work with the examples in the repository nor this documentation; please use the example router configuration that ships with |ab| (in ``examples/router/.crossbar/``).


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

Here is an example using **Twisted**; note that we've eliminated the configuration of the ``Component`` for clarity; see above for full example.

.. code-block:: python
    :linenos:
    :emphasize-lines: 14

    from autobahn.twisted.component import Component, run

    component = Component(...)

    @component.on_join
    @inlineCallbacks
    def joined(session, details):
        print("session ready")

        def add2(x, y):
            return x + y

        try:
            yield session.register(add2, u'com.myapp.add2')
            print("procedure registered")
        except Exception as e:
            print("could not register procedure: {0}".format(e))


The procedure ``add2`` is registered (line 14) under the URI ``u"com.myapp.add2"`` immediately in the ``on_join`` callback which fires when the session has connected to a *Router* and joined a *Realm*. Another way to arrange for procedures to be registered is with the ``@register`` decorator:

.. code-block:: python
    :linenos:
    :emphasize-lines: 5

    from autobahn.twisted.component import Component, run

    component = Component(...)

    @component.register
    def add2(x, y):
        return x + y


.. tip::

   You can register *local* functions like in above example, *global* functions as well as *methods* on class instances. Further, procedures can also be automatically registered using *decorators*.

When the registration succeeds, authorized callers will immediately be able to call the procedure (see :ref:`calling-procedures`) using the URI under which it was registered (``u"com.myapp.add2"``).

A registration may also fail, e.g. when a procedure is already registered under the given URI or when the session is not authorized to register procedures.

Using **asyncio**, the example looks identical except for the imports (note that ``add`` could be ``async def`` here if it needed to do other work).

.. code-block:: python
    :linenos:

    from autobahn.asyncio.component import Component, run

    component = Component(...)

    @component.register
    def add2(x, y):
        return x + y


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
    :emphasize-lines: 12


    from autobahn.twisted.component import Component, run
    from twisted.internet.defer import inlineCallbacks


    component = Component(...)

    @component.on_join
    @inlineCallbacks
    def joined(session, details):
        print("session ready")
        try:
            res = yield session.call(u'com.myapp.add2', 2, 3)
            print("call result: {}".format(res))
        except Exception as e:
            print("call error: {0}".format(e))


And here is the same done on **asyncio**

.. code-block:: python
    :linenos:
    :emphasize-lines: 10

    from autobahn.asyncio.component import Component, run


    component = Component(...)

    @component.on_join
    async def joined(session, details):
        print("session ready")
        try:
            res = await session.call(u'com.myapp.add2', 2, 3)
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

The *Publisher* and *Subscriber* will usually run application code, while the *Broker* works as a generic router for events thus decoupling *Publishers* from *Subscribers*. That is, there can be many *Subscribers* written in different languages on different machines which can all receive a single event published by an independent *Publisher*.


.. _subscribing-to-topics:

Subscribing to Topics
---------------------

To receive events published to a topic, a session needs to first subscribe to the topic. Subscribing to a topic is done by calling :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`.

Here is a **Twisted** example:

.. code-block:: python
    :linenos:
    :emphasize-lines: 16

    from autobahn.twisted.component import Component
    from twisted.internet.defer import inlineCallbacks


    component = Component(...)

    @component.on_join
    @inlineCallbacks
    def joined(session, details):
        print("session ready")

        def oncounter(count):
            print("event received: {0}", count)

        try:
            yield session.subscribe(oncounter, u'com.myapp.oncounter')
            print("subscribed to topic")
        except Exception as e:
            print("could not subscribe to topic: {0}".format(e))

We create an event handler function ``oncounter`` (you can name that as you like) which will get called whenever an event for the topic is received.

To subscribe (line 15), we provide the event handler function (``oncounter``) and the URI of the topic to which we want to subscribe (``u'com.myapp.oncounter'``).

When the subscription succeeds, we will receive any events published to ``u'com.myapp.oncounter'``. Note that we won't receive events published *before* the subscription succeeds.

The corresponding **asyncio** code looks like this

.. code-block:: python
    :linenos:
    :emphasize-lines: 14

    from autobahn.twisted.component import Component


    component = Component(...)

    @component.on_join
    async def joined(session, details):
        print("session ready")

        def oncounter(count):
            print("event received: {0}", count)

        try:
            yield session.subscribe(oncounter, u'com.myapp.oncounter')
            print("subscribed to topic")
        except Exception as e:
            print("could not subscribe to topic: {0}".format(e))

Again, nearly identical to Twisted. Note that when using the ``Component`` APIs we can use a shortcut to the above (e.g. perhaps there's nothing else to do in ``on_join``). This shortcut works similarly for Twisted, so we only show an **asyncio** example:

.. code-block:: python
    :linenos:
    :emphasize-lines: 6

    from autobahn.twisted.component import Component


    component = Component(...)

    @component.subscribe(u"com.myapp.oncounter")
    def oncounter(count):
        print("event received: {0}", count)


.. _publishing-events:

Publishing Events
-----------------

Publishing an event to a topic is done by calling :func:`autobahn.wamp.interfaces.IPublisher.publish`.

Events can carry arbitrary positional and keyword based payload -- as long as the payload is serializable in JSON.

Here is a **Twisted** example that will publish an event to topic ``u'com.myapp.oncounter'`` with a single (positional) payload being a counter that is incremented for each publish:

.. code-block:: python
    :linenos:
    :emphasize-lines: 17

    from autobahn.twisted.component import Component
    from autobahn.twisted.util import sleep
    from twisted.internet.defer import inlineCallbacks


    component = Component(...)


    @component.on_join
    @inlineCallbacks
    def joined(session, details):
        print("session ready")

        counter = 0
        while True:
            # publish() only returns a Deferred if we asked for an acknowledgement
            session.publish(u'com.myapp.oncounter', counter)
            counter += 1
            yield sleep(1)

The corresponding **asyncio** code looks like this

.. code-block:: python
    :linenos:
    :emphasize-lines: 15

    from autobahn.asyncio.component import Component
    from asyncio import sleep


    component = Component(...)


    @component.on_join
    async def joined(session, details):
        print("session ready")

        counter = 0
        while True:
            # publish() is only async if we asked for an acknowledgement
            session.publish(u'com.myapp.oncounter', counter)
            counter += 1
            await sleep(1)

When publishing, you can pass an `options=` kwarg which is an instance of :class:`PublishOptions <autobahn.wamp.types.PublishOptions>`. Many of the options require support from the router.

 - whitelisting and blacklisting (all the `eligible*` and `exclude*` options) can affect which subscribers receive the publish; see `crossbar documentation <http://crossbar.io/docs/Subscriber-Black-and-Whitelisting/>`_ for more information;
 - `retain=` asks the router to retain the message;
 - `acknowledge=` asks the router to notify you it received the publish (note that this does *not* wait for every subscriber to have received the publish) and causes ``publish()`` to return a Future/Deferred.

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

In the ``Component`` API, there are similar corresponding events. The biggest difference is the lack of "challenge" events (you pass authentication configuration instead) and the addition of a "ready" event. You can subscribe to these events directly using a "listener" style API or via decorators. The events are:

1. "connect": transport connected
2. "join": session has successfully joined a realm
3. "ready": indicates that the realm has been joined **and** all "join" handlers have completed (including async ones)
4. "leave": session has left a realm
5. "disconnect": transport has disconnected

You can use the method :meth:`autobahn.wamp.component.Component.on` to subscribe directly to events with a listener-function. For example, ``component.on('ready', my_ready_listener)``. Note that on a single ``Component`` instance these callbacks *can* happen multiple times (e.g. if the component is disconnected and then reconnects, its ``connect`` message will fire again after the ``disconnect``). However, they will always be in order (i.e. you can't ``join`` until after a ``connect`` and ``ready`` always comes after ``join``).

There is also still the older "subclassing" based API, which is still supported and can be used if you prefer. This API involves subclassing :class:`ApplicationSession <autobahn.twisted.wamp.ApplicationSession>` and overriding methods corresponding to the events (see :class:`ISession <autobahn.wamp.interfaces.ISession>` for more information):

.. code-block:: python

    class CustomSession(ApplicationSession):
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

There is a `txaio Programming Guide <http://txaio.readthedocs.org/en/latest/programming-guide.html#logging>`_ which includes information on logging. If you are writing new code, you can choose the txaio_ APIs for maximum compatibility and runtime-efficiency (see below). If you prefer to write idiomatic logging code to "go with" the event-based framework you've chosen, that's possible as well. For asyncio_ this is Python's built-in `logging <https://docs.python.org/3.5/library/logging.html>`_ module; for Twisted it is the `post-15.2.0 logging API <http://twistedmatrix.com/documents/current/core/howto/logger.html>`_. The logging system in `txaio`_ is able to interoperate with the legacy Twisted logging API as well.

The txaio_ API encourages a more structured approach while still achieving easily-rendered text logging messages. The basic idiom is to use new-style Python formatting strings and pass any "data" as kwargs. So a typical logging call might look like: ``self.log.info("Knob {frob.name} moved {degrees} right.", knob=an_obj, degrees=42)`` and if the "info" log level is not enabled, the string won't be "interpolated" (i.e. ``str()`` will not be invoked on any of the args, and a new string won't be produced). On top of that, logging observers may examine the ``kwargs`` and do things beyond "normal" logging. This is very much inspired by ``twisted.logger``; you can read the `Twisted logging documentation <http://twistedmatrix.com/documents/current/core/howto/logger.html>`_ for more insight.

Before any logging happens of course you must activate the logging system. There is a convenience method in `txaio`_ called ``txaio.start_logging``. This will use ``twisted.logger.globalLogBeginner`` on Twisted or ``logging.Logger.addHandler`` under asyncio and allows you to specify and output stream and/or a log level. Valid levels are the list of strings in ``txaio.interfaces.log_levels``. If you're using the high-level :func:`autobahn.twisted.component.run` or :func:`autobahn.asyncio.component.run` APIs, logging will be started for you.

If you have instead got your own log-starting code (e.g. ``twistd``) or Twisted/asyncio specific log handlers (``logging.Handler`` subclass on asyncio and ``ILogObserver`` implementer under Twisted) then you will still get |Ab| and `Crossbar`_ messages. Probably the formatting will be slightly different from what ``txaio.start_logging`` provides. In either case, **do not depend on the formatting** of the messages e.g. by "screen-scraping" the logs.

We very much **recommend using the ``txaio.start_logging()`` method** of activating the logging system, as we've gone to pains to ensure that over-level logs are a "no-op" and incur minimal runtime cost. We achieve this by re-binding all out-of-scope methods on any logger created by ``txaio.make_logger()`` to a do-nothing function (by saving weak-refs of all the loggers created); at least on `PyPy`_ this is very well optimized out. This allows us to be generous with ``.debug()`` or ``.trace()`` calls without incurring very much overhead. Your Mileage May Vary using other methods. If you haven't called ``txaio.start_logging()`` this optimization is not activated.


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
