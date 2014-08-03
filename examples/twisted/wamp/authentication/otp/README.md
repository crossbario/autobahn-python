# WAMP One-Time-Password Authentication

Run this demo by starting the server

	python server.py

and opening `http://127.0.0.1:8080` in your browser. Open the JavaScript console to watch output.

When asked to enter the "current code", start a [TOTP](http://en.wikipedia.org/wiki/Time-based_One-time_Password_Algorithm) application like [Google Authenticator](http://en.wikipedia.org/wiki/Google_Authenticator), create an account with secret

	MFRGGZDFMZTWQ2LK

and enter the code currently shown for that account.

> The secret as well as the username are hard-coded into the example program.

