Introduction
============

**Autobahn|Python** is a subproject of `Autobahn <https://crossbar.io/autobahn>`__
and provides open-source implementations of:

* `The WebSocket Protocol <https://tools.ietf.org/html/rfc6455>`__ (RFC 6455)
* `The Web Application Messaging Protocol (WAMP) <https://wamp-proto.org/>`__

for Python 3.9+, running on `Twisted <https://twisted.org/>`__ and
`asyncio <https://docs.python.org/3/library/asyncio.html>`__.

What is WebSocket?
------------------

`WebSocket <https://tools.ietf.org/html/rfc6455>`__ is a protocol for
creating bidirectional, real-time communication channels between browsers
(or other clients) and servers.

Unlike HTTP, which is request-response based, WebSocket provides:

* Full-duplex communication
* Low latency
* Persistent connections
* Efficient binary and text messaging

What is WAMP?
-------------

`WAMP <https://wamp-proto.org/>`__ (Web Application Messaging Protocol) is
an open standard protocol that provides two messaging patterns:

* **Remote Procedure Calls (RPC)** - Call procedures on remote peers
* **Publish/Subscribe (PubSub)** - Subscribe to topics and receive events

WAMP runs over WebSocket (and other transports) and provides:

* Unified application messaging
* Routed RPC and PubSub
* Built-in authentication and authorization
* Multiple serialization formats (JSON, MessagePack, CBOR, FlatBuffers)

Why Autobahn|Python?
--------------------

* **Dual Framework Support**: Works on both Twisted and asyncio
* **Complete Implementation**: Full WebSocket and WAMP support
* **Production Ready**: Used in production by many organizations
* **Well Tested**: Comprehensive test suite and conformance testing
* **Active Development**: Regular updates and improvements

Key Features
------------

WebSocket Features
~~~~~~~~~~~~~~~~~~

* Client and server implementations
* RFC 6455 compliant
* Per-message compression (permessage-deflate)
* Automatic ping/pong handling
* Binary and text message support

WAMP Features
~~~~~~~~~~~~~

* WAMP Basic Profile and Advanced Profile support
* Multiple serializers (JSON, MessagePack, CBOR, FlatBuffers, UBJSON)
* Authentication methods (Anonymous, Ticket, WAMP-CRA, WAMP-SCRAM, Cryptosign)
* End-to-end encryption
* Progressive call results
* Call cancellation
* Caller/publisher identification and disclosure

Next Steps
----------

* :doc:`installation` - How to install Autobahn|Python
* :doc:`getting-started` - Quick start guide
* :doc:`programming-guide/index` - Detailed programming guides
