Authentication of WAMP Sessions
===============================

WAMP Challenge-Response-Authentication ("WAMP-CRA") is a WAMP v1 protocol feature
that provides in-band authentication of WAMP clients to servers.

It is based on HMAC-SHA256 and built into AutobahnPython, AutobahnJS and AutobahnAndroid.

This example shows how a AutobahnJS client can authenticate to a AutobahnPython based
server. The server grants RPC and PubSub permissions based on authentication.
