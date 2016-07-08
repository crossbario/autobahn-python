WebSocket TLS Echo Server as Twisted Web Resource
=================================================

This is a variant of a basic WebSocket Echo server that is running as a *Twisted Web Resource* and under TLS (that is HTTPS for Web, and WSS for WebSocket).

Running
-------

Run the server by doing

    python server.py

and open

    https://localhost:8080/

in your browser.

This will show up all WebSocket messages exchanged between clients and server.
