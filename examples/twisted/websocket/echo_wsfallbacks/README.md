WebSocket Echo Server with Fallbacks
====================================

This example has the broadest browser support currently possible with Autobahn.

It supports native WebSocket protocol variants Hybi-10+ and RFC6455.

On IE6-9 it uses [Google Chrome Frame](http://www.google.com/chromeframe) when available.

On IE8,9 it can use a [Flash-based WebSocket implementation](https://github.com/gimite/web-socket-js). This requires Adobe Flash 10+.

> The Flash implementation can also be used on older Android devices without Chrome Mobile, but with Flash. You need to remove the conditional comments around the Flash file includes though in this case from the `index.html`.
>

Running
-------

Run the server by doing

    python server.py

and open

    http://localhost:8080/

in your browser. Open the JS console to see if the WebSocket connection was successful.


Here is a typical browser log when the Flash implementation kicks in:

    [WebSocket] debug enabled
    [WebSocket] policy file: xmlsocket://127.0.0.1:843
    [WebSocket] connected

    [WebSocket] request header:
    GET / HTTP/1.1
    Host: 127.0.0.1:9000
    Upgrade: websocket
    Connection: Upgrade
    Sec-WebSocket-Key: Ol4WMQosGk0SBHIGTBQMAQ==
    Origin: http://127.0.0.1:8080
    Sec-WebSocket-Version: 13

    [WebSocket] response header:
    HTTP/1.1 101 Switching Protocols
    Server: AutobahnPython/0.6.0
    Upgrade: WebSocket
    Connection: Upgrade
    Sec-WebSocket-Accept: 4wHBJpfr8P419FMUv8sJ/rT0x/4=

    Connected!
