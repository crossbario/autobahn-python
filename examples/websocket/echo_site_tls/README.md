WebSocket TLS Echo Server as Twisted Web Resource
=================================================

This is a variant of a basic WebSocket Echo server that is running as a *Twisted Web Resource* and under TLS (that is HTTPS for Web, and WSS for WebSocket).

*Note: This currently does NOT work! Need to investigate further.*

Running
-------

Run the server by doing

    python server.py

and open

    https://localhost:8080/

in your browser.

To activate debug output on the server, start it

    python server.py debug

This will show up all WebSocket messages exchanged between clients and server.
