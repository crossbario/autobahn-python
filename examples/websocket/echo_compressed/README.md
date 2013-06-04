WebSocket Echo Server and Client
================================

This example demonstrates how to activate and use the WebSocket compression extension ([`permessage-deflate`](http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression-09)).

Running
-------

Run the server by doing

    python server.py

and open

    http://localhost:8080/

in your browser.

> Note: Currently (06/04/2013), the only browsers implementing WebSocket `permessage-deflate` are [Chrome Canary](https://www.google.com/intl/en/chrome/browser/canary.html) and [Chromium (Dev Channel)](http://www.chromium.org/getting-involved/dev-channel).
> 

To activate debug output on the server, start it

    python server.py debug

To run the Python client, do

    python client.py ws://127.0.0.1:9000

To activate debug output on the client, start it

    python client.py ws://127.0.0.1:9000 debug
