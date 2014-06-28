## Hello WAMP

This example demonstrates the use of `wamp.Application` objects, an alternative WAMP API to `ApplicationSession`.

`Application` objects provide a Flask-esque API to WAMP. You create an application object and then can e.g. register procedures using decorators:

```python
app = Application()

@app.register('com.example.add2')
def add2(a, b):
   return a + b
```

### Running the Example

Start the app component for development in a standalone router embedding the component:


```shell
python hello.py
```

Open `hello.html` in your browser.
