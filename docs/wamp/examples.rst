.. _wamp_examples:

WAMP Examples
=============

**NOTE** that for all examples you will **need to run a router**. We develop `Crossbar.io <http://crossbar.io/docs>`_ and there are `other routers <http://wamp.ws/implementations/#routers>`_ available as well. We include a working `Crossbar.io <http://crossbar.io/docs>`_ configuration in the `examples/router/ subdirectory <https://github.com/crossbario/autobahn-python/tree/master/examples/router>`_ as well as `instructions on how to run it <https://github.com/crossbario/autobahn-python/blob/master/examples/running-the-examples.md>`_.

Overview of Examples
++++++++++++++++++++

The examples are organized between `asyncio <https://docs.python.org/3.4/library/asyncio.html>`__ and `Twisted <https://www.twistedmatrix.com>`__ at the top-level, with similarly-named examples demonstrating the same functionality with the respective framework.

Each example typically includes four things:

- ``frontend.py``: the Caller or Subscriber, in Python
- ``backend.py``: the Callee or Publisher, in Python
- ``frontend.js``: JavaScript version of the frontend
- ``backend.js``: JavaScript version of the backend
- ``*.html``: boilerplate so a browser can run the JavaScript

So for each example, you start *one* backend and *one* frontend component (your choice). You can usually start multiple frontend components with no problem, but will get errors if you start two backends trying to register at the same procedure URI (for example).

Still, you are encouraged to  try playing with mixing and matching the frontend and backend components, starting multiple front-ends, etc. to explore Crossbar and Autobahn's behavior. Often the different examples use similar URIs for procedures and published events, so you can even try mixing between the examples.

The provided `Crossbar.io <http://crossbar.io/docs>`__ configuration will run a Web server that you can visit at `http://localhost:8080` and includes links to the frontend/backend HTML for the javascript versions. Usually these just use ``console.log()`` so you'll have to open up the JavaScript console in your browser to see it working.

.. _run_all_examples:

Automatically Run All Examples
++++++++++++++++++++++++++++++

There is a script (``./examples/run-all-examples.py``) which runs all the WAMP examples for 5 seconds each, `this asciicast
<https://asciinema.org/a/9cnar155zalie80c9725nvyk7>`__ shows you how (see comments for how to run it yourself):

.. raw:: html

    <script type="text/javascript" src="https://asciinema.org/a/9cnar155zalie80c9725nvyk7.js" id="asciicast-21588" async></script>



Publish & Subscribe (PubSub)
++++++++++++++++++++++++++++

* Basic `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/pubsub/basic>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/pubsub/basic>`__ - Demonstrates basic publish and subscribe.

* Complex `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/pubsub/complex>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/pubsub/complex>`__ - Demonstrates publish and subscribe with complex events.

* Options `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/pubsub/options>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/pubsub/options>`__ - Using options with PubSub.

* Unsubscribe `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/pubsub/unsubscribe>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/pubsub/unsubscribe>`__ - Cancel a subscription to a topic.


Remote Procedure Calls (RPC)
++++++++++++++++++++++++++++

* Time Service `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/rpc/timeservice>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/rpc/timeservice>`__ - A trivial time service - demonstrates basic remote procedure feature.

* Slow Square `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/rpc/slowsquare>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/rpc/slowsquare>`__ - Demonstrates procedures which return promises and return asynchronously.

* Arguments `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/rpc/arguments>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/rpc/arguments>`__ - Demonstrates all variants of call arguments.

* Complex Result `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/rpc/complex>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/rpc/complex>`__  - Demonstrates complex call results (call results with more than one positional or keyword results).

* Errors `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/rpc/errors>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/rpc/errors>`__ - Demonstrates error raising and catching over remote procedures.

* Progressive Results `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/rpc/progress>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/rpc/progress>`__ - Demonstrates calling remote procedures that produce progressive results.

* Options `Twisted <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/wamp/rpc/options>`__ - `asyncio <https://github.com/crossbario/autobahn-python/tree/master/examples/asyncio/wamp/rpc/options>`__ - Using options with RPC.


I'm Confused, Just Tell Me What To Run
++++++++++++++++++++++++++++++++++++++

If all that is too many options to consider, you want to do this:

1. Open 3 terminals
2. In terminal 1, `setup and run a local Crossbar <https://github.com/crossbario/autobahn-python/blob/master/examples/running-the-examples.md>`_ in the root of your Autobahn checkout.
3. In terminals 2 and 3, go to the root of your Autobahn checkout and activate the virtualenv from step 2 (``source venv-autobahn/bin/activate``)
4. In terminal 2 run ``python ./examples/twisted/wamp/rpc/arguments/backend.py``
5. In terminal 3 run ``python ./examples/twisted/wamp/rpc/arguments/frontend.py``

The above procedure is gone over in this `this asciicast <https://asciinema.org/a/2vl1eahfaxptoen9bnevd06lq>`_:

.. raw:: html

   <script type="text/javascript" src="https://asciinema.org/a/2vl1eahfaxptoen9bnevd06lq.js" id="asciicast-21580" async></script>
