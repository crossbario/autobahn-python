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

Call a remote procedure which produces interim, progressive results:

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

