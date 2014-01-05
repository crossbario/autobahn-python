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

### Call with progressive results

Call a remote procedure which produces interim, progressive results:

```python
def deletedSoFar(n):
   print("{} items deleted so far ..".format(n))

total = yield session.call("com.myapp.log.delete", options = CallOptions(onProgress = deletedSoFar))
print("{} items deleted in total.".format(total))
```
