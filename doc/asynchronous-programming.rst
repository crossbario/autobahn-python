.. _async_programming:

Asynchronous Programming
========================

We cannot give a complete introduction to asynchronous programming, Twisted or asyncio. Instead, you might have a look at the following resources for **Twisted**

* `Jessica McKellar - Architecting an event-driven networking engine: Twisted Python <https://www.youtube.com/watch?v=3R4gP6Egh5M>`__
* `Twisted Introduction <http://krondo.com/?page_id=1327>`__

and **asyncio**

* `Guido van Rossum's Keynote at PyCon US 2013 <http://pyvideo.org/video/1667/keynote-1>`__
* `Tulip: Async I/O for Python 3 <http://www.youtube.com/watch?v=1coLC-MUCJc>`__
* `Python 3.4 docs - asyncio <http://docs.python.org/3.4/library/asyncio.html>`__
* `PEP-3156 - Asynchronous IO Support Rebooted <http://www.python.org/dev/peps/pep-3156/>`__

However, we quickly introduce core asynchronous programming primitives provided by `Twisted <https://twistedmatrix.com/>`__ and `asyncio <https://docs.python.org/3.4/library/asyncio.html>`__:

* `Twisted Deferreds <https://twistedmatrix.com/documents/current/core/howto/defer.html>`__ and `Twisted inlineCallbacks <http://twistedmatrix.com/documents/current/api/twisted.internet.defer.html#inlineCallbacks>`__
* `asyncio Futures <https://docs.python.org/3.4/library/asyncio-task.html#future>`__ and `asyncio coroutines <http://docs.python.org/3.4/library/asyncio-task.html#coroutines>`_

Useful resources in the context of the latter are

* `Alex Martelli - Don't call us, we'll call you: callback patterns and idioms <https://www.youtube.com/watch?v=LCZRJStwkKM>`__
* `Wikipedia on Promises <http://en.wikipedia.org/wiki/Promise_%28programming%29>`__


Asynchronous Programming Primitives
-----------------------------------

Twisted Deferreds and inlineCallbacks
.....................................

Programming with Twisted Deferreds involves attaching *callbacks* to Deferreds which get called when the Deferred finally either resolves successfully or fails with an error

.. code-block:: python

   d = some_function() # returns a Twisted Deferred ..

   def on_success(res):
      print("result: {}".format(res))

   def on_error(err):
      print("error: {}".format(err))

   d.addCallbacks(on_success, on_error)


Using Deferreds offers the greatest flexibility since you are able to pass around Deferreds freely and can run code concurrently.

However, using plain Deferreds comes at a price: code in this style looks very different from synchronous/blocking code and the code can become hard to follow.

Now, `Twisted inlineCallbacks <http://twistedmatrix.com/documents/current/api/twisted.internet.defer.html#inlineCallbacks>`__ let you write code in a sequential looking manner that nevertheless executes asynchronously and non-blocking under the hood.

So converting above snipped to ``inlineCallbacks`` the code will look like

.. code-block:: python

   try:
      res = yield some_function()
      print("result: {}".format(res))
   except Exception as err:
      print("error: {}".format(err))

As you can see, this code looks very similar to regular synchronous/blocking Python code. The only difference (on surface) is the use of ``yield`` when calling a function that runs asynchronously. Otherwise, you process success result values and exceptions exactly as with regular code.

.. note::
   We'll only show basic usage here - for a more basic and complete introduction, please have a look at `this chapter <http://krondo.com/?p=2441>`__ from `this tutorial <http://krondo.com/?page_id=1327>`__.

--------

**Example**

The following demonstrates basic usage of ``inlineCallbacks`` in a complete example you can run.

First, consider this program using Deferreds. We simulate calling a slow function by sleeping (without blocking) inside the function ``slow_square``

.. code-block:: python
   :linenos:
   :emphasize-lines: 5,7,8,10,11

   from twisted.internet import reactor
   from twisted.internet.defer import Deferred

   def slow_square(x):
      d = Deferred()

      def resolve():
         d.callback(x * x)

      reactor.callLater(1, resolve)
      return d

   def test():
      d = slow_square(3)

      def on_success(res):
         print(res)
         reactor.stop()

      d.addCallback(on_success)

   test()
   reactor.run()

This is just regular Twisted code - nothing exciting here:

1. We create a ``Deferred`` to be returned by our ``slow_square`` function (line 5)
2. We create a function ``resolve`` (a closure) in which we resolve the previously created Deferred with the result (lines 7-8)
3. Then we ask the Twisted reactor to call ``resolve`` after 1 second (line 10)
4. And we return the previously created Deferred to the caller (line 11)

What you can see even with this trivial example already is that the code looks quite differently from synchronous/blocking code. It needs some practice until such code becomes natural to read.

Now, when converted to ``inlineCallbacks``, the code becomes:

.. code-block:: python
   :linenos:
   :emphasize-lines: 5,7,8

   from twisted.internet import reactor
   from twisted.internet.defer import inlineCallbacks, returnValue
   from autobahn.twisted.util import sleep

   @inlineCallbacks
   def slow_square(x):
      yield sleep(1)
      returnValue(x * x)

   @inlineCallbacks
   def test():
      res = yield slow_square(3)
      print(res)
      reactor.stop()

   test()
   reactor.run()


Have a look at the highlighted lines - here is what we do:

1. Decorating our squaring function with ``inlineCallbacks`` (line 5). Doing so marks the function as a coroutine which allows us to use this sequential looking coding style.
2. Inside the function, we simulate the slow execution by sleeping for a second (line 7). However, we are sleeping in a non-blocking way (:func:`autobahn.twisted.util.sleep`). The ``yield`` will put the coroutine aside until the sleep returns.
3. To return values from Twisted coroutines, we need to use ``returnValue`` (line 8).

.. note::

   The reason ``returnValue`` is necessary goes deep into implementation details of Twisted and Python. In short: co-routines in Python 2 with Twisted are simulated using exceptions. Only Python 3.3+ has gotten native support for co-routines using the new yield from statement.

In above, we are using a little helper :func:`autobahn.twisted.util.sleep` for sleeping "inline". The helper is really trivial:

.. code-block:: python

   from twisted.internet import reactor
   from twisted.internet.defer import Deferred

   def sleep(delay):
      d = Deferred()
      reactor.callLater(delay, d.callback, None)
      return d

The rest of the program is just for driving our test function and running a Twisted reactor.



Asyncio Futures and Coroutines
..............................

`Asyncio Futures <http://docs.python.org/3.4/library/asyncio-task.html#future>`_ like Twisted Deferreds encapsulate the result of a future computation. At the time of creation, the result is (usually) not yet available, and will only be available eventually.

On the other hand, asyncio futures are quite different from Twisted Deferreds. One difference is that they have no builtin machinery for chaining.

`Asyncio Coroutines <http://docs.python.org/3.4/library/asyncio-task.html#coroutines>`_ are (on a certain level) quite similar to Twisted inline callbacks. Here is the code corresponding to our example above:


-------

**Example**

The following demonstrates basic usage of ``asyncio.coroutine`` in a complete example you can run.

First, consider this program using plain ``asyncio.Future``. We simulate calling a slow function by sleeping (without blocking) inside the function ``slow_square``

.. code-block:: python
   :linenos:
   :emphasize-lines: 4,6-7,10,12

   import asyncio

   def slow_square(x):
      f = asyncio.Future()

      def resolve():
         f.set_result(x * x)

      loop = asyncio.get_event_loop()
      loop.call_later(1, resolve)

      return f

   def test():
      f = slow_square(3)

      def done(f):
         res = f.result()
         print(res)

      f.add_done_callback(done)

      return f

   loop = asyncio.get_event_loop()
   loop.run_until_complete(test())
   loop.close()

Using asyncio in this way is probably uite unusual. This is becomes asyncio os opinionated towards using coroutines from the beginning. Anyway, here is what above code does:

1. We create a ``Future`` to be returned by our ``slow_square`` function (line 4)
2. We create a function ``resolve`` (a closure) in which we resolve the previously created Future with the result (lines 6-7)
3. Then we ask the asyncio event loop to call ``resolve`` after 1 second (line 10)
4. And we return the previously created Future to the caller (line 12)


What you can see even with this trivial example already is that the code looks quite differently from synchronous/blocking code. It needs some practice until such code becomes natural to read.

Now, when converted to ``asyncio.coroutine``, the code becomes:

.. code-block:: python
   :linenos:
   :emphasize-lines: 3,5,6

   import asyncio

   @asyncio.coroutine
   def slow_square(x):
      yield from asyncio.sleep(1)
      return x * x


   @asyncio.coroutine
   def test():
      res = yield from slow_square(3)
      print(res)

   loop = asyncio.get_event_loop()
   loop.run_until_complete(test())

The main differences (on surface) are:

1. The use of the decorator ``@asyncio.coroutine`` (line 3) in asyncio versus ``@defer.inlineCallbacks`` with Twisted
2. The use of ``defer.returnValue`` in Twisted for returning values whereas in asyncio, you can use plain returns (line 6)
3. The use of ``yield from`` in asyncio, versus plain ``yield`` in Twisted (line 5)
4. The auxiliary code to get the event loop started and stopped

Most of the examples that follow will show code for both Twisted and asyncio, unless the conversion is trivial.
