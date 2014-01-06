## Calling procedures

### Standard calls

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

### Handling errors

```python
try:
   res = yield session.call("com.myapp.sqrt", -1)
except ApplicationError as err:
   print("Error: {}".format(err))
```

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

A registered callable is then called an *endpoint*.

Upon success, `session.register` will return a *registration* - an opaque handle that may be used later to unregister the endpoint.

Here is how you would register two methods on an object:

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

total = yield session.call("com.myapp.longop", 10, options = CallOptions(onProgress = processedSoFar))
print("{} items deleted in total.".format(total))
```


### Registration with invocation details

For an endpoint to receive invocation details during invocation, the callable registered for the endpoint must consume a keyword argument of type `autobahn.wamp.types.Invocation`:

```python
def deleteTask(taskId, invocation = Invocation):
   # delete "task" ..
   db.deleteTask(taskId)
   # .. and notify all but the caller
   session.publish("com.myapp.task.on_delete", taskId, PublishOptions(exclude = [invocation.caller])

yield session.register("com.myapp.task.delete", deleteTask)
```

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
