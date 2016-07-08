Broadcasting with WebSocket
===========================

This example provides a WebSocket server that will broadcast any message it receives
to all connected WebSocket clients. Additionally, it will broadcast a "tick" message
to all connected clients every second.

Clients are provided for AutobahnJS and AutobahnPython.

There is also a companion [example](https://github.com/crossbario/autobahn-android/tree/master/Demo/BroadcastClient) using AutobahnAndroid.


Running
-------

Run the server by doing

    python server.py

and open

    http://localhost:8080/

in your browser.

To use the Python client, do

    python client.py

