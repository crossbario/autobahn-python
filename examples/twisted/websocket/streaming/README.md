Using Frame-/Streaming-based APIs in AutobahnPython
===================================================

The example here demonstrate how to use the (advanced) frame-based and streaming WebSocket APIs
of AutobahnPython.

They also show off how to do advanced flow-control via the Twisted producer-consumer pattern.

The example clients produce random data, send it to a server which computes SHA256 fingerprints over the received data and send back the fingerprint to the client.

Compared are 4 variants of above functionality:

 * message-based API
 * frame-based API
 * streaming API
 * streaming API with producer-consumer pattern


Message-based Processing
------------------------

This pair of client/server uses the standard *message-based WebSocket API* of AutobahnPython.

Run the server by doing

    python message_based_server.py

and the client

    python message_based_client.py


Frame-based Processing
-----------------------

This pair of client/server uses the *frame-based WebSocket API* of AutobahnPython.

Run the server by doing

    python frame_based_server.py

and the client

    python frame_based_client.py


Streaming Processing
--------------------

This pair of client/server uses the *streaming WebSocket API* of AutobahnPython.

Run the server by doing

    python streaming_server.py

and the client

    python streaming_client.py


Producer-Consumer Processing
----------------------------

This pair of client/server uses the *streaming WebSocket API* of AutobahnPython together with the *Producer-Consumer Pattern* of Twisted.

Run the server by doing

    python streaming_server.py

and the client

    python streaming_producer_client.py

