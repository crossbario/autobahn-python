Directory Watcher
=================

This example includes a directory watcher that publishes WAMP events whenever a file is changed, created or deleted on a given filesystem directory. Events are received in a HTML frontend.

This example consists of 3 parts:

 * `dirwatch.py`: directory watcher and WAMP client
 * `server.py`: a trivial WAMP server
 * `index.html`: the HTML/JS client 


Running
-------

Run the server by doing

    python server.py debug

and open

    http://<Server IP>:8080/

in your browser.

Open a terminal on a Linux desktop and

	python dirwatch.py

Then trigger some filesystem change (modify, create, delete file) within the example folder.