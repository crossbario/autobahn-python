# Programming with WAMP

This document gives an introduction for pgroamming with WAMP in Python using **Autobahn**|Python.

We will cover:

1. Remote Procedure Calls
 * Calling Procedures
 * Registering Endpoints 
2. Publish & Subscribe
 * Publishing Events
 * Subscribing to Topics
 
## Calling Procedures

### Standard Calls

Call a remote procedure with no result:

```python
yield session.call("com.supervotes.vote", "cherrycream")
```

Call a remote procedure with no arguments:

```python
result = yield session.call("com.timeservice.now")
```

Call a remote procedure with positional arguments:

```python
result = yield session.call("com.myapp.add2", 2, 5)
```

Call a remote procedure with keyword arguments:

```python
result = yield session.call("com.myapp.getuser", nick = "homer")
```

Call a remote procedure with positional and keyword arguments:

```python
result = yield session.call("com.myapp.getorders", "product5", limit = 10)
```

### Batching Calls

Lets say you want to gather the total sales for three products:

```python
sales = []
for product in ["product2", "product3", "product5"]:
   sales.append(yield session.call("com.myapp.sales_by_product", product))
print("Sales: {}".format(sales))
```

Since above uses `yield`, it will call the remote procedure `com.myapp.sales_by_product` three times, but one after the other. That is, it won't call the procedure for `product3` until the result (or an error) has been received for the call for `product2`.

Now, probably you wan't to speed up things, and leverage the asynchronous and batching capabilities of WAMP. You could do:

```python
dl = []
for product in ["product2", "product3", "product5"]:
   dl.append(session.call("com.myapp.sales_by_product", product))
sales = yield gatherResults(dl)
print("Sales: {}".format(sales))
```

This will fire off all three calls essentially immediately, and then wait asynchronously until all three results have arrived. Doing so will - if the endpoint implementing `com.myapp.sales_by_product` is able to run concurrently - execute the three calls in parallel, and the result might be available faster.


### Calls with complex results

In Python, a function has always exactly one (positional) result. In WAMP, procedures can also have multiple positional and/or keyword results.

If a WAMP procedure call has such a result, the result is wrapped into an instance of `autobahn.wamp.types.CallResult` to fit the Python host language.

Call with more than multiple positional results:

```python
c = yield session.call("com.math.complex.add", 5, 8, 2, 3)
print("Result: {} + {}i".format(c.results[0], c.results[1]))
```

Call with keyword results:

```python
c = yield session.call("com.math.complex.add", a = (5, 8), b = (2, 3))
print("Result: {} + {}i".format(c.kwresults["real"], c.kwresults["imag"])
```

### Handling errors

```python
try:
   res = yield session.call("com.myapp.sqrt", -1)
except ApplicationError as err:
   print("Error: {}".format(err))
```

### Canceling calls

Canceling of calls results in a `autobahn.wamp.error.CanceledError` exception being raised:

```python
def done(res):
   print("Alrighty.")

def nope(err):
   if isinstance(err, CanceledError):
      print("Canceled.")
   else:
      print("Error: {}".format(err))

d = session.call("com.myapp.longop")
d.addCallbacks(done, nope)
...
d.cancel()
```

### Call timeouts

Call a procedure, but automatically timeout the call after given time:

```python
try:
   total = yield session.call("com.myapp.longop", options = CallOptions(timeout = 10))
except TimeoutError:
   print("Giving up.")
except Exception as err:
   print("Error: {}".format(err))
```

### Call with progressive results

Call a remote procedure which produces interim, progressive results:

```python
def deletedSoFar(n):
   print("{} items deleted so far ..".format(n))

total = yield session.call("com.myapp.log.delete", options = CallOptions(onProgress = deletedSoFar))
print("{} items deleted in total.".format(total))
```

### Distributed calls

```python
result = yield session.call("com.myapp.customer.count", options = CallOptions(runAt = "all"))
```

```python
yield session.call("com.myapp.pageview.log", page = "http://www.myapp.com/page1.html",
						options = CallOptions(runAt = "any"))
```

```python
result = yield session.call("com.myapp.order.place", order = {...},
								options = CallOptions(runAt = "partition", pkey = 2391))
```


## Registering endpoints

### Basic registration

*Callees* can register any Python callable (such as functions, methods or objects that provide `__call__`) for remote calling via WAMP:

```python
def hello(msg):
   return "You said {}. I say hello!".format(msg)

try:
   yield session.register("com.myapp.hello", hello)
except ApplicationError as err:
   print("Registration failed: {}".format(err))
else:
   print("Ok, endpoint registered!")
```

Upon success, `session.register` will return a *registration* - an opaque handle that may be used later to unregister the endpoint. A registered callable is then called an *endpoint*.

You could then call above endpoint from another WAMP session:

```python
try:
   res = yield session.call("com.myapp.hello", "foooo")
except ApplicationError as err:
   print("Error: {}".format(err))
else:
   print(res)
```

As another example, here is how you would register two methods on an object:

```python
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
```

Since above example uses `yield`, the registrations run sequentially. The second registration will not be executed until the first registration returns.

Further, should the first registration fail, the second won't be executed, and if the first succeeds, but the second fails, the first registration will nevertheless be in place though the second fails.

Each endpoint registration "stands on it's own". There is no way of registering multiple endpoints atomically.

If you want to leverage the asynchronous nature of WAMP and issue registrations in parallel ("batching"), you can do:

```python
try:
   dl = []
   dl.append(session.register("com.calculator.add", calc.add))
   dl.append(session.register("com.calculator.square", calc.square))
   regs = yield gatherResults(dl)
except ApplicationError as err:
   print("Registration failed: {}".format(err))
else:
   print("Ok, {} object endpoints registered!".format(len(regs)))
```

Above will run the registrations in parallel ("batched").


### Registrations via decorators

Endpoints can also be defined by using Python decorators:

```python
from autobahn.wamp import export

@export("com.myapp.hello")
def hello(msg):
   return "You said {}. I say hello!".format(msg)

try:
   yield session.register(hello)
except ApplicationError as err:
   print("Registration failed: {}".format(err))
else:
   print("Ok, endpoint registered!")
```

This also works for whole objects with decorated methods at once:

```python
from autobahn.wamp import export

class Calculator:

   @export("com.calculator.add")
   def add(self, a, b):
      return a + b

   @export("com.calculator.square")
   def square(self, x):
      return x * x

calc = Calculator()

try:
   registrations = yield session.register(calc)
except ApplicationError as err:
   print("Registration failed: {}".format(err))
else:
   print("Ok, {} object endpoints registered!".format(len(registrations)))
```

Above will register all methods of `Calculator` which have been decorated using `export`.

In this case, `session.register`, will, upon success, return a list of registrations.


```python
@export("com.calculator")
class Calculator:

   @export("add")
   def add(self, a, b):
      return a + b

   @export
   def square(self, x):
      return x * x
```


### Unregistering

The following will unregister a previously registered endpoint from a *Callee*:

```python
registration = yield session.register("com.myapp.hello", hello)

try:
   yield session.unregister(registration)
except ApplicationError as err:
   print("Unregistration failed: {}".format(err))
else:
   print("Ok, endpoint unregistered!")
```


### Producing progressive results in invocations

The following endpoint will produce progressive call results:

```python
def longop(n, invocation = Invocation):
   for i in range(n):
      invocation.progress(i)
      yield sleep(1)
   return n

yield session.register("com.myapp.longop", longop)
```

and can be called like this

```python
def processedSoFar(i):
   print("{} items processed so far ..".format(i))

total = yield session.call("com.myapp.longop", 10,
                           options = CallOptions(onProgress = processedSoFar))
print("{} items deleted in total.".format(total))
```


### Registration with invocation details

For an endpoint to receive invocation details during invocation, the callable registered for the endpoint must consume a keyword argument with a default value of type `autobahn.wamp.types.Invocation`:

```python
def deleteTask(taskId, invocation = Invocation):
   # delete "task" ..
   db.deleteTask(taskId)
   # .. and notify all but the caller
   session.publish("com.myapp.task.on_delete", taskId,
				   PublishOptions(exclude = [invocation.caller])

yield session.register("com.myapp.task.delete", deleteTask)
```

Note that the default value must be of `class` type (not an instance of `autobahn.wamp.types.Invocation`).

This endpoint can now be called

```python
yield session.call("com.myapp.task.delete", "t130")
```

### Pattern-based registrations

```python
def deleteTask(invocation = Invocation):
   # retrieve wildcard component from procedure URI
   taskId = invocation.procedure.split('.')[3]
   # delete "task" ..
   db.deleteTask(taskId)
   # .. and notify all
   session.publish("com.myapp.task.{}.on_delete".format(taskId))

yield session.register("com.myapp.task..delete", deleteTask,
					   options = RegisterOptions(match = "wildcard"))
```

This endpoint can now be called

```python
yield session.call("com.myapp.task.t130.delete")
```

Registering via decorators:

```python
from autobahn.wamp import export

@export("com.myapp.task.<taskId>.delete")
def deleteTask(taskId):
   # delete "task" ..
   db.deleteTask(taskId)
   # .. and notify all
   session.publish("com.myapp.task.{}.on_delete".format(taskId))

yield session.register(deleteTask,
					   options = RegisterOptions(match = "wildcard"))
```


### Distributed endpoints
