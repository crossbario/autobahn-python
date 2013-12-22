WebSocket Echo Server as Twisted Web Resource plus WSGI/Flask
=============================================================

This is a variant of a basic WebSocket Echo server that is running as a *Twisted Web Resource*.

Running
-------

Run the server by doing

    python server.py

and open

    http://localhost:8080/

in your browser.

To activate debug output on the server, start it

    python server.py debug

This will show up all WebSocket messages exchanged between clients and server.
