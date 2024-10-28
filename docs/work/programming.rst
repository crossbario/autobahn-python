
Calling Procedures
------------------

Standard Calls
..............

Calling remote procedure with WAMP and |Ab| is easy and probably quickest to introduce by giving examples.

For example, here is how you call a remote procedure that takes no arguments and returns a single result - the current time:

.. code-block:: python

   now = yield session.call("com.timeservice.now")
   print(now)


This is using `yield`, which assumes the context in that you run this code is a *co-routine* (something decorated with `defer.inlineDeferred` in Twisted or declared with `async def` in asyncio).

The same call using plain Twisted Deferreds would look like:

.. code-block:: python

   d = session.call("com.timeservice.now")
   d.addCallback(print)

> Note: This use of `print` relies on `print` being a real function in Python 3. If you are on Python 2, you need to do `from __future__ import print_function` at the very beginning of your Python source file.
>

Here are a couple of more idioms using Twisted `Deferreds`.

Process the result in a chain of functions:

.. code-block:: python

   d = session.call("com.timeservice.now")
   d.addCallback(lambda now: "Now: {}".format(now))
   d.addCallback(print)

Process the result in a callback function:

.. code-block:: python

   def success(now):
      print("Now: {}".format(now))

   d = session.call("com.timeservice.now")
   d.addCallback(success)

Here is how that works with asyncio:

.. code-block:: python

   def success(future):
      now = future.result()
      print("Now: {}".format(now))

   f = session.call("com.timeservice.now")
   f.add_done_callback(success)

Call a remote procedure with one positional argument and no result:

.. code-block:: python

   yield session.call("com.supervotes.vote", "cherrycream")

Call a remote procedure with no arguments and no result:

.. code-block:: python

   yield session.call("com.myapp.ping")

Call a remote procedure with multiple positional arguments:

.. code-block:: python

   result = yield session.call("com.myapp.add2", 2, 5)

Call a remote procedure with keyword arguments:

.. code-block:: python

   result = yield session.call("com.myapp.getuser", nick = "homer", stars = 5)

Call a remote procedure with positional and keyword arguments:

.. code-block:: python

   result = yield session.call("com.myapp.getorders", "product5", limit = 10)

Batching Calls
..............

If you have multi-step code running remote procedures where each step depends on the results of the previous call, it is natural, and inevitable to schedule the calls sequentially:

.. code-block:: python

   sales = yield session.call("com.myapp.sales_by_product", "product1")
   sales_sq = yield session.call("com.calculator.square", sales)
   print("Squared sales: {}".format(sales_sq))

In above, `com.calculator.square` could not be run before or even while `com.myapp.sales_by_product` is still running and has not yet returned, since the former depends on the result of the latter.

On the other hand, if you have code like the following

.. code-block:: python

   sales1 = yield session.call("com.myapp.sales_by_product", "product1")
   print("Sales 1: {}".format(sales1))
   sales2 = yield session.call("com.myapp.sales_by_product", "product2")
   print("Sales 2: {}".format(sales2))

then these calls do not depend on the result of the other. Hence, these calls could be executed concurrently. And doing so might speed up your program.

Now, above code does not leverage the asynchronous and concurrent abilities of WAMP. To do so, you need to restructure the code a little:

.. code-block:: python

   d1 = session.call("com.myapp.sales_by_product", "product1")
   d2 = session.call("com.myapp.sales_by_product", "product2")
   sales1 = yield d1
   print("Sales 1: {}".format(sales1))
   sales2 = yield d2
   print("Sales 2: {}".format(sales2))

This way, you get both calls running simultaneously, but you wait on the results as they come in.

There is still one catch: if the call result for "Sales 1" comes in after the result for "Sales 2", the result of the former will not be printed until the result for the latter comes in.

Say you want to run the calls concurrently **and** print each result as soon as it comes in, without any waiting for others - neither for issuing calls, nor for printing results.

This is how you could approach that:

.. code-block:: python

   def print_sales(sales, product):
      print("Sales {}: {}".format(product, sales))

   d1 = session.call("com.myapp.sales_by_product", "product1")
   d2 = session.call("com.myapp.sales_by_product", "product2")
   d1.addCallback(print_sales, 1)
   d2.addCallback(print_sales, 2)

Notice the order of arguments in `print_sales`. The `sales` parameter comes first, since a Deferreds callback will always get the Deferreds result as the first positional argument. Additional callback arguments can be forwarded to the callback from `addCallback`. Twisted lets you forward both (additional) positional arguments, and keyword arguments.

Now lets say you want to gather the total sales for a whole list of products:

.. code-block:: python

   sales = []
   for product in ["product2", "product3", "product5"]:
      sales.append(yield session.call("com.myapp.sales_by_product", product))
   print("Sales: {}".format(sales))

Since above uses `yield` again, it will call the remote procedure `com.myapp.sales_by_product` three times, but one after the other. That is, it won't call the procedure for `product3` until the result (or an error) has been received for the call for `product2`.

Now, probably you want to speed up things like we did before and leverage the asynchronous and concurrent capabilities of WAMP. You could do:

.. code-block:: python

   dl = []
   for product in ["product2", "product3", "product5"]:
      dl.append(session.call("com.myapp.sales_by_product", product))
   sales = yield gatherResults(dl)
   print("Sales: {}".format(sales))

This will fire off all three calls essentially immediately, and then wait asynchronously until all three results have arrived. Doing so will - if the endpoint implementing `com.myapp.sales_by_product` is able to run concurrently - execute the three calls in parallel, and the result might be available faster.

Doing away with waiting before printing could be done like this:

.. code-block:: python

   def print_sales(sales, product):
      print("Sales {}: {}".format(product, sales))

   for product in ["product2", "product3", "product5"]:
      d = session.call("com.myapp.sales_by_product", product)
      d.addCallback(print_sales, product)

The direct asyncio equivalent of above would be:

.. code-block:: python

   import functools

   async def print_sales(product, future):
      sales = future.result()
      print("Sales {}: {}".format(product, sales))

   fl = []
   for product in ["product2", "product3", "product5"]:
      f = session.call("com.myapp.sales_by_product", product)
      f.add_done_callback(functools.partial(print_sales, product))
      fl.append(f)
   await asyncio.gather(*fl)

> Note: Part of the verbosity stems from the fact that, different from Twisted's `addCallback`, asyncio's `add_done_callback` sadly does not take and forward `args` and `kwargs` to the callback added.
>

However, there is a better way, if we restructure the code a little:

.. code-block:: python

   async def get_and_print_sales(product):
      sales = await session.call("com.myapp.sales_by_product", product)
      print("Sales {}: {}".format(product, sales))

   tasks = [get_and_print_sales(product) for product in ["product2", "product3", "product5"]]
   await asyncio.wait(tasks)

Calls with complex results
..........................

In Python, a function has always exactly one (positional) result. In WAMP, procedures can also have multiple positional and/or keyword results.

If a WAMP procedure call has such a result, the result is wrapped into an instance of `autobahn.wamp.types.CallResult` to fit the Python host language.

Call with more than multiple positional results:

.. code-block:: python

   c = yield session.call("com.math.complex.add", 5, 8, 2, 3)
   print("Result: {} + {}i".format(c.results[0], c.results[1]))

Call with keyword results:

.. code-block:: python

   c = yield session.call("com.math.complex.add", a = (5, 8), b = (2, 3))
   print("Result: {} + {}i".format(c.kwresults["real"], c.kwresults["imag"])

Handling errors
...............

Using Twisted coroutines (`twisted.internet.defer.inlineDeferred`):

.. code-block:: python

   try:
      res = yield session.call("com.calculator.sqrt", -1)
   except ApplicationError as err:
      print("Error: {}".format(err))
   else:
      print("Result: {}".format(res))

Using asyncio coroutines (`asyncio.coroutine`):

.. code-block:: python

   try:
      res = await session.call("com.calculator.sqrt", -1)
   except ApplicationError as err:
      print("Error: {}".format(err))
   else:
      print("Result: {}".format(res))

Using Twisted Deferreds (`twisted.internet.defer.Deferred`):

.. code-block:: python

   def success(res):
      print("Result: {}".format(res))

   def failed(failure):
      err = failure.value
      print("Error: {}".format(err))

   d = session.call("com.calculator.sqrt", -1)
   d.addCallbacks(success, failed)

Using asyncio Futures (`asyncio.Future`):

.. code-block:: python

   def done(future):
      try:
         res = future.result()
      except Exception as err:
         print("Error: {}".format(err))
      else:
         print("Result: {}".format(res))

   f = session.call("com.calculator.sqrt", -1)
   f.add_done_callback(done)

Canceling calls
...............

Canceling of calls results in a `autobahn.wamp.error.CanceledError` exception being raised:

.. code-block:: python

   def done(res):
      print("Alrighty.")

   def nope(err):
      if isinstance(err, CanceledError):
         print("Canceled.")
      else:
         print("Error: {}".format(err))

   d = session.call("com.myapp.longop")
   d.addCallbacks(done, nope)

   d.cancel()

Call timeout
............

Call a procedure, but automatically timeout the call after given time:

.. code-block:: python

   try:
      total = yield session.call("com.myapp.longop",
                              options = CallOptions(timeout = 10))
   except TimeoutError:
      print("Giving up.")
   except Exception as err:
      print("Error: {}".format(err))

Call with progressive results
.............................

Call a remote procedure which produces interim, progressive results:

.. code-block:: python

   def deletedSoFar(n):
      print("{} items deleted so far ..".format(n))

   total = yield session.call("com.myapp.log.delete",
                              options = CallOptions(on_progress = deletedSoFar))
   print("{} items deleted in total.".format(total))

Distributed calls
.................

.. code-block:: python

   result = yield session.call("com.myapp.customer.count", options = CallOptions(runAt = "all"))

.. code-block:: python

   yield session.call("com.myapp.pageview.log",
                        page = "http://www.myapp.com/page1.html",
   						   options = CallOptions(runAt = "any"))

.. code-block:: python

   result = yield session.call("com.myapp.order.place",
                            order = {...},
   								 options = CallOptions(runAt = "partition", pkey = 2391))

Registering endpoints
---------------------

Basic registration
..................

*Callees* can register any Python callable (such as functions, methods or objects that provide `__call__`) for remote calling via WAMP:

.. code-block:: python

   def hello(msg):
      return "You said {}. I say hello!".format(msg)

   try:
      yield session.register("com.myapp.hello", hello)
   except ApplicationError as err:
      print("Registration failed: {}".format(err))
   else:
      print("Ok, endpoint registered!")

Upon success, `session.register` will return a *registration* - an opaque handle that may be used later to unregister the endpoint. A registered callable is then called an *endpoint*.

You could then call above endpoint from another WAMP session:

.. code-block:: python

   try:
      res = yield session.call("com.myapp.hello", "foooo")
   except ApplicationError as err:
      print("Error: {}".format(err))
   else:
      print(res)

As another example, here is how you would register two methods on an object:

.. code-block:: python

   class Calculator:
      def add(self, a, b):
         return a + b

      def square(self, x):
         return x * x

   calc = Calculator()

   try:
      yield session.register("com.calculator.add", calc.add)
      yield session.register("com.calculator.square", calc.square)
   except ApplicationError as err:
      print("Registration failed: {}".format(err))
   else:
      print("Ok, object endpoints registered!")

Since above example uses `yield`, the registrations run sequentially. The second registration will not be executed until the first registration returns.

Further, should the first registration fail, the second won't be executed, and if the first succeeds, but the second fails, the first registration will nevertheless be in place though the second fails.

Each endpoint registration "stands on it's own". There is no way of registering multiple endpoints atomically.

If you want to leverage the asynchronous nature of WAMP and issue registrations in parallel ("batching"), you can do:

.. code-block:: python

   try:
      dl = []
      dl.append(session.register("com.calculator.add", calc.add))
      dl.append(session.register("com.calculator.square", calc.square))
      regs = yield gatherResults(dl)
   except ApplicationError as err:
      print("Registration failed: {}".format(err))
   else:
      print("Ok, {} object endpoints registered!".format(len(regs)))

Above will run the registrations in parallel ("batched").


Registrations via decorators
............................

Endpoints can also be defined by using Python decorators:

.. code-block:: python

   from autobahn import wamp

   @wamp.procedure("com.myapp.hello")
   def hello(msg):
      return "You said {}. I say hello!".format(msg)

   try:
      yield session.register(hello)
   except ApplicationError as err:
      print("Registration failed: {}".format(err))
   else:
      print("Ok, endpoint registered!")

This also works for whole objects with decorated methods at once:

.. code-block:: python

   from autobahn import wamp

   class Calculator:

      @wamp.procedure("com.calculator.add")
      def add(self, a, b):
         return a + b

      @wamp.procedure("com.calculator.square")
      def square(self, x):
         return x * x

   calc = Calculator()

   try:
      registrations = yield defer.gatherResults(session.register(calc))
   except ApplicationError as err:
      print("Registration failed: {}".format(err))
   else:
      print("Ok, {} object endpoints registered!".format(len(registrations)))

Above will register all methods of `Calculator` which have been decorated using `@wamp.procedure`.

In asyncio, use

.. code-block:: python

   registrations = await asyncio.gather(*session.register(calc))

to yield a list of registrations.


Unregistering
.............

The following will unregister a previously registered endpoint from a *Callee*:

.. code-block:: python

   registration = yield session.register("com.myapp.hello", hello)

   try:
      yield session.unregister(registration)
   except ApplicationError as err:
      print("Unregistration failed: {}".format(err))
   else:
      print("Ok, endpoint unregistered!")

Producing progressive results in invocations
............................................

The following endpoint will produce progressive call results:

.. code-block:: python

   def longop(n, invocation = Invocation):
      for i in range(n):
         invocation.progress(i)
         yield sleep(1)
      return n

   yield session.register("com.myapp.longop", longop)

and can be called like this

.. code-block:: python

   def processedSoFar(i):
      print("{} items processed so far ..".format(i))

   total = yield session.call("com.myapp.longop", 10,
                              options = CallOptions(on_progress = processedSoFar))
   print("{} items deleted in total.".format(total))

Registration with invocation details
....................................

For an endpoint to receive invocation details during invocation, the callable registered for the endpoint must consume a keyword argument with a default value of type `autobahn.wamp.types.Invocation`:

.. code-block:: python

   def deleteTask(taskId, invocation = Invocation):
      # delete "task" ..
      db.deleteTask(taskId)
      # .. and notify all but the caller
      session.publish("com.myapp.task.on_delete", taskId,
   				   PublishOptions(exclude = [invocation.caller])

   yield session.register("com.myapp.task.delete", deleteTask)

Note that the default value must be of `class` type (not an instance of `autobahn.wamp.types.Invocation`).

This endpoint can now be called

.. code-block:: python

   yield session.call("com.myapp.task.delete", "t130")

Pattern-based registrations
...........................

.. code-block:: python

   def deleteTask(invocation = Invocation):
      # retrieve wildcard component from procedure URI
      taskId = invocation.procedure.split('.')[3]
      # delete "task" ..
      db.deleteTask(taskId)
      # .. and notify all
      session.publish("com.myapp.task.{}.on_delete".format(taskId))

   yield session.register("com.myapp.task..delete", deleteTask,
   					options = RegisterOptions(match = "wildcard"))

This endpoint can now be called

.. code-block:: python

   yield session.call("com.myapp.task.t130.delete")

Registering via decorators:

.. code-block:: python

   from autobahn import wamp

   @wamp.procedure("com.myapp.task.<taskId>.delete")
   def deleteTask(taskId):
      # delete "task" ..
      db.deleteTask(taskId)
      # .. and notify all
      session.publish("com.myapp.task.{}.on_delete".format(taskId))

   yield session.register(deleteTask,
   				options = RegisterOptions(match = "wildcard"))

.. code-block:: python

   @wamp.procedure("com.myapp.item.<int:id>.get_name")
   def get_item_name(id):
      return db.get_item_name(id)

.. code-block:: python

   @wamp.procedure("com.myapp.<string:obj_type>.<int:id>.get_name")
   def get_object_name(obj_type, id):
      if obj_type == "item":
         return db.get_item_name(id)
      elif obj_type == "user":
         return db.get_user_name(id)
      else:
         raise ApplicationError("com.myapp.error.no_such_object_type")

.. code-block:: python

   @wamp.procedure("com.myapp.<suffix:path>")
   def generic_proc(path):
      if path == "proc.echo":
         ...

Distributed endpoints
.....................

Publish & Subscribe
-------------------

### Subscribing event handlers

Event handlers are callables subscribed on topics to receive events published to that topic.

To subscribe a callable (and hence make it an event handler):

.. code-block:: python

   def on_product_create(id, label, price):
      printf("New product created: {} ({})".format(label, id))

   try:
      yield session.subscribe("com.myapp.product.on_create", on_product_create)
   except ApplicationError as err:
      print("Subscription failed: {}".format(err))
   else:
      print("Ok, event handler subscribed!")

Above event handler will then receive events published from another WAMP session:

.. code-block:: python

   try:
      yield session.publish("com.myapp.product.on_create", 103, "PyJacket", 50.3)
   except ApplicationError as err:
      print("Publication failed: {}".format(err))
   else:
      print("Ok, event published!")

Subscriptions via decorators
............................

Event handlers can also be defined using Python decorators:

.. code-block:: python

   from autobahn import wamp

   @wamp.topic("com.myapp.product.on_create")
   def on_product_create(id, label, price):
      print("New product created: {} ({})".format(label, id))

   try:
      yield session.subscribe(on_product_create)
   except ApplicationError as err:
      print("Subscription failed: {}".format(err))
   else:
      print("Ok, event handler subscribed!")

Pattern-based Subscriptions
...........................

Decorators can also be used to setup event handlers for pattern-based subscriptions. Patterns can be:
 * prefix-patterns
 * wildcard-patterns


**Wildcard Subscriptions**

Here is how you subscribe to a topic wildcard-pattern:

.. code-block:: python

   from autobahn import wamp

   @wamp.topic("com.myapp.<country>.<state>.<city>.on_concert")
   def on_concert_pulse(country, state, city, title, date):
      print("Concert {} in {}, {}/{} on {}".format(title, city, state, country, date)

   try:
      yield session.subscribe(on_concert_pulse)
   except ApplicationError as err:
      print("Subscription failed: {}".format(err))
   else:
      print("Ok, event handler subscribed!")

Above handler matches topics like

 * `com.myapp.us.montana.billings.on_concert`
 * `com.myapp.us.newmexico.albuquerque.on_concert`

and the event handler parameters `country`, `state` and `city` will be automatically
bound to the matched components of the topic upon receiving an event for a topic
that matches the pattern.

It would *not* match topics like

 * `com.myapp.de.bavaria.munich.on_concert`
 * `com.myapp.us.montana.billings`
 * `com.myapp.us.montana.billings.on_challenge`
 * `com.myapp.us.newmexico.albuquerque.citycenter.on_concert`

You could publish events to be received and processed by above handler like this:

.. code-block:: python

   try:
      state = "newmexico"
      city = "albuquerque"
      yield session.publish("com.myapp.us.{}.{}.on_concert".format(state, city),
                            "Powerhour with Ali Spagnola", "2014-02-04")
   except ApplicationError as err:
      print("Publication failed: {}".format(err))
   else:
      print("Ok, event published!")

The parameters `title` and `date` in the event handler will be bound from the
published payload.

If you are only interested in a subset of events, that works like this

.. code-block:: python

   @wamp.topic("com.myapp.us.montana.<city>.on_concert")
   def on_concert_us_montana_pulse(city, title, date):
      ## only concerts in the US, Montana

Above handler will match topics like

 * `com.myapp.us.montana.billings.on_concert`
 * `com.myapp.us.montana.helena.on_concert`

but not

 * `com.myapp.us.newmexico.albuquerque.on_concert`

Or

.. code-block:: python

   @wamp.topic("com.myapp.us.<state>.<city>.on_concert")
   def on_concert_us_montana_pulse(state, city, title, date):
      ## only concerts in the US

Above handler will match topics like

 * `com.myapp.us.montana.billings.on_concert`
 * `com.myapp.us.montana.helena.on_concert`
 * `com.myapp.us.newmexico.albuquerque.on_concert`

but not

 * `com.myapp.us.montana.billings.on_challenge`
 * `com.myapp.us.newmexico.albuquerque.citycenter.on_concert`
 * `com.myapp.de.bavaria.munich.on_concert`


**Prefix Subscriptions**

Besides wildcard, you can also match by prefix (the variable part being then a suffix):

.. code-block:: python

   @wamp.topic("com.myapp.us.<suffix:path>")
   def on_us_event(path, title, date):
      ## handle any U.S. event ..
      parts = path.split('.')
      if parts[-1] == 'on_concert':
         ## do something with concert
      elif parts[-1] == 'on_challenge':
         ## do something with challenge
      ...

This will match any of

 * `com.myapp.us.montana.billings`
 * `com.myapp.us.montana.billings.on_concert`
 * `com.myapp.us.montana.billings.on_challenge`
 * `com.myapp.us.newmexico.albuquerque.on_concert`
 * `com.myapp.us.newmexico.albuquerque.citycenter.on_concert`

It will *not* match topics like

 * `com.myapp.de.bavaria.munich.on_concert`

On matching, the event handler parameter `path` will be bound to the complete,
remaining suffix after removing the matching prefix.

E.g. publishing to `com.myapp.us.newmexico.albuquerque.citycenter.on_concert` would bind
`path` to `"newmexico.albuquerque.citycenter.on_concert"`.



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

.. note:: WAMPv1 will be deprecated with the 0.9.0 release.
