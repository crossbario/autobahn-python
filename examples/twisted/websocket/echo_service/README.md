WebSocket Echo Service
======================

This example shows how to:

 1. package up Autobahn-based servers (and clients) as Twisted services
 2. provide an application as a Twisted plugin (for `twistd`)
 3. include static files into a package and access those in services


Resources
---------

  * http://twistedmatrix.com/documents/current/core/howto/application.html
  * http://twistedmatrix.com/documents/current/core/howto/plugin.html
  * http://twistedmatrix.com/documents/current/core/howto/tap.html


Running
-------

Run the server by doing

    twistd echows

and open

    http://localhost:8080/

in your browser.

This will show up all WebSocket messages exchanged between clients and server.
