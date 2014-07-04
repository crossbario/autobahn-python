## Flask/WAMP Application using Crochet

This example demonstrates combining a Flask Web application with Autobahn WAMP code using [Crochet](https://crochet.readthedocs.org/).

### Running the Example

Install dependencies:

```shell
pip install flask autobahn[twisted] crochet
```

Start the server: 


```shell
python server.py
```

Now open the WAMP Web client `client.html` in your browser, and then visit [http://localhost:8080](http://localhost:8080), reloading a couple of times.

You should see the Web client be notified in real-time of the new page visit count:

![](screenshot.png)
