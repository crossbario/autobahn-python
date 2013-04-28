WebSocket Echo Server and Client
================================

This example shows how to set and get custom HTTP headers for using during the initial WebSocket opening handshake.


Running
-------

Run the server by doing

    python server.py debug

Run the client by doing

    python client.py ws://127.0.0.1:9000 debug

The client will send a custom HTTP header `MyCustomClientHeader` during the initial WebSocket opening handshake:

        User-Agent: AutobahnPython/0.6.0
        Host: 127.0.0.1:9000
        Upgrade: WebSocket
        Connection: Upgrade
        Pragma: no-cache
        Cache-Control: no-cache
        MyCustomClientHeader: Bazbar
        Sec-WebSocket-Key: tI9KmKOGOAGTxgWfVn13zg==
        Sec-WebSocket-Version: 13

The server will respond with custom HTTP headers 

        HTTP/1.1 101 Switching Protocols
        Server: AutobahnPython/0.6.0
        Upgrade: WebSocket
        Connection: Upgrade
        MyCustomServerHeader: Foobar
        MyCustomDynamicServerHeader1: Hello
        MyCustomDynamicServerHeader2: Bazbar
        Sec-WebSocket-Accept: pQklbTbzxoUDuSDHpiYJThfd4vo=

where `MyCustomServerHeader` is a custom header sent to any connecting client (defined on the `WebSocketServerFactory`) and `MyCustomDynamicServerHeader1` and `MyCustomDynamicServerHeader2` are custom headers which values can be specific to the connecting client (and set within `onConnect`).
