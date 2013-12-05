# Publish and Subscribe with Autobahn

This example shows a very basic Publish & Subscriber WAMP server in Python and clients both in Python and JavaScript.

To start the server:

	python server.py

Now open

	http://localhost:8080

in one or more browser tabs, windows or different browsers (like Firefox, Chrome or IE10+).

Run the Python client:

	python client.py

or do

	python client.py ws://192.168.1.130:9000

to connect to the server running on a different host like `192.168.1.130`.
