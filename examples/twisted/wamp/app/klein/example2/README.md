## WAMP-Klein Application

This example demonstrates combining a [Klein](https://github.com/twisted/klein) Web application with a Autobahn WAMP application.

> Klein essentially is Flask for Twisted Web.

### Running the Example

Install dependencies:

```shell
pip install autobahn[twisted] jinja2 klein
```

Start the server side:


```shell
python server.py
```

Open [http://localhost:8080](http://localhost:8080) in your browser.
