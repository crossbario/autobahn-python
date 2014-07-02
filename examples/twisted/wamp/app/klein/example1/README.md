## WAMP-Klein Application

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
pip install autobahn[twisted] klein
```

Start our WAMP application component (together with a development WAMP router): 


```shell
python server_wamp.py
```

You can test the WAMP application component from your browser by opening `test_wamp.html`.

Now, start our Klein-based Web server (which will connect to above WAMP router): 

```shell
python server_web.py
```

Open `test_web.html` in your browser.
