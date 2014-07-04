## Flask/WAMP Application using Crochet

This example demonstrates combining a [Klein](https://github.com/twisted/klein) Web application with a Autobahn WAMP application.

> Klein essentially is Flask for Twisted Web.

### What we do

1. The app will run a Klein-based Web server.
2. Our Web code will receive HTML form data via a plain old HTTP/POST.
3. Upon receiving the HTTP/POST, the request handler will perform an asynchronous call to a WAMP procedure before returning
4. The WAMP procedure called is running as a WAMP component connected to a WAMP router
5. The Web app is also connected to the same router, so it can call the procedure

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