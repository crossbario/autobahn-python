## Calling procedures

### Standard calls

```python
try:
   res = yield session.call("com.myapp.add2", 2, 5)
except ApplicationError as err:
   print("Error: {}".format(err))
else:
   print("Ok, got result: {}".format(res))
```