This example demonstrates how to access an app session instance from outside - via the session factory.

It runs an application component as a client connected to a WAMP router.

Start a WAMP router:

	python ../../server.py

Start the backend component (which will run inside a client connecting to the router):

	python client.py

Open `frontend.html` in your browser.