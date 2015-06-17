.. _wamp_examples:

WAMP Examples
=============

**NOTE** that for all examples you will **need to run a router**. We develop `Crossbar.io <http://crossbar.io/docs>`_ and there are `other routers <http://wamp.ws/implementations/#routers>`_ available as well. We include a working `Crossbar.io <http://crossbar.io/docs>`_ configuration in the `examples/router/ subdirectory <https://github.com/tavendo/AutobahnPython/tree/master/examples/router>`_ as well as `instructions on how to run it <https://github.com/tavendo/AutobahnPython/blob/master/examples/running-the-examples.md>`_.

Overview of Examples
++++++++++++++++++++

The examples are organized between `asycio <https://docs.python.org/3.4/library/asyncio.html>`_ and `Twisted <https://www.twistedmatrix.com>`_ at the top-level, with similarly-named examples demonstrating the same functionality with the respective framework.

Each example typically includes four things:

- ``frontend.py``: the Caller or Subscriber, in Python
- ``backend.py``: the Callee or Publisher, in Python
- ``frontend.js``: JavaScript version of the frontend
- ``backend.js``: JavaScript version of the backend
- ``*.html``: boilerplate so a browser can run the JavaScript

So for each example, you start *one* backend and *one* frontend component (your choice). You can usually start multiple frontend components with no problem, but will get errors if you start two backends trying to register at the same procedure URI (for example).

Still, you are encouraged to  try playing with mixing and matching the frontend and backend components, starting multiple front-ends, etc. to explore Crossbar and Autobahn's behavior. Often the different examples use similar URIs for procedures and published events, so you can even try mixing between the examples.

The provided `Crossbar.io <http://crossbar.io/docs>`_ configuration will run a Web server that you can visit at `http://localhost:8080`_ and includes links to the frontend/backend HTML for the javascript versions. Usually these just use ``console.log()`` so you'll have to open up the JavaScript console in your browser to see it working.


Publish & Subscribe (PubSub)
++++++++++++++++++++++++++++

* Basic `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/pubsub/basic>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/pubsub/basic>`_ - Demonstrates basic publish and subscribe.

* Complex `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/pubsub/complex>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/pubsub/complex>`_ - Demonstrates publish and subscribe with complex events.

* Options `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/pubsub/options>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/pubsub/options>`_ - Using options with PubSub.

* Unsubscribe `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/pubsub/unsubscribe>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/pubsub/unsubscribe>`_ - Cancel a subscription to a topic.


Remote Procedure Calls (RPC)
++++++++++++++++++++++++++++

* Time Service `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/rpc/timeservice>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/rpc/timeservice>`_ - A trivial time service - demonstrates basic remote procedure feature.

* Slow Square `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/rpc/slowsquare>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/rpc/slowsquare>`_ - Demonstrates procedures which return promises and return asynchronously.

* Arguments `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/rpc/arguments>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/rpc/arguments>`_ - Demonstrates all variants of call arguments.

* Complex Result `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/rpc/complex>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/rpc/complex>`_  - Demonstrates complex call results (call results with more than one positional or keyword results).

* Errors `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/rpc/errors>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/rpc/errors>`_ - Demonstrates error raising and catching over remote procedures.

* Progressive Results `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/rpc/progress>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/rpc/progress>`_ - Demonstrates calling remote procedures that produce progressive results.

* Options `Twisted <https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/wamp/rpc/options>`_ - `asyncio <https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/rpc/options>`_ - Using options with RPC.


I'm Confused, Just Tell Me What To Run
++++++++++++++++++++++++++++++++++++++

If all that is too many options to consider, you want to do this:

1. Open 3 terminals
2. In terminal 1, `setup and run a local Crossbar <https://github.com/tavendo/AutobahnPython/blob/master/examples/running-the-examples.md>`_ in the root of your Autobahn checkout.
3. In terminals 2 and 3, go to the root of your Autobahn checkout and activate the virtualenv from step 2 (``source venv-autobahn/bin/activate``)
4. In terminal 2 run ``python ./examples/twisted/wamp/rpc/arguments/backend.py``
5. In terminal 3 run ``python ./examples/twisted/wamp/rpc/arguments/frontend.py``

The above procedure is gone over in this `this asciicast <https://asciinema.org/a/2vl1eahfaxptoen9bnevd06lq.png)](https://asciinema.org/a/2vl1eahfaxptoen9bnevd06lq>`_:

.. raw:: html

   <script type="text/javascript" src="https://asciinema.org/a/2vl1eahfaxptoen9bnevd06lq.js" id="asciicast-21580" async></script>
