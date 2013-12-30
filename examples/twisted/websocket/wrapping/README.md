# Stream-based Transport over WebSocket

**Autobahn**|Python provides facilities to wrap existing stream-based Twisted factories and protocols with WebSocket. 
That means, you can run any stream-based protocol *over* WebSocket without any modification to the existing protocol and factory.

Why would you want to do that? For example, to create a VNC, SSH, IRC, IMAP or other client for some existing protocol that runs on browsers, and connects to an *unmodified* server.

## WebSocket Transport Scheme

**Autobahn**|Python follows the transport scheme established by [websockify](https://github.com/kanaka/websockify): a WebSocket subprotocol is negotiated, either `binary` or `base64`.

With the `binary` WebSocket subprotocol, any data is simply sent as payload of WebSocket binary messages. With the `base64` WebSocket subprotocol, any data is first Base64 encoded before being sent as the payload of WebSocket text messages.

Since **Autobahn**|Python implements WebSocket compression, traffic is automatically compressed ("permessage-deflate"). This can be turned off if you want.

> Currently the only browser with support for WebSocket compression is Chrome 32+.
> 

## Wrapping Factories and Protocols

Here is how you wrap an existing Twisted client protocol `HelloClientProtocol`:

```python
from autobahn.twisted.websocket import WrappingWebSocketClientFactory

wrappedFactory = Factory.forProtocol(HelloClientProtocol)
factory = WrappingWebSocketClientFactory(wrappedFactory, "ws://localhost:9000")
```

The only required parameter to `WrappingWebSocketClientFactory` besides the wrapped factory is the WebSocket URL of the server the wrapping factory will connect to.

There are a couple of optional arguments to `WrappingWebSocketClientFactory` for controlling it's WebSocket level behavior:

 * `enableCompression` can be used to enable/disable WebSocket compression ("permessage-deflate")
 * `autoFragmentSize` can be used to automatically fragment the stream data into WebSocket frames of at most this size
 * `debug` enables/disables debug log output

You can find a complete example for both client and server in these files:

 1. [client.py](client.py)
 2. [server.py](server.py)


## Wrapping Endpoints

Twisted provides a flexible machinery for creating clients and server from [**Endpoints**](http://twistedmatrix.com/documents/current/core/howto/endpoints.html) and **Autobahn**|Python includes a Twisted Plugin for both client and server stream endpoints.

This allows you to run any stream-based, endpoint-using program over the WebSocket transport **Autobahn**|Python, without even referencing Autobahn at all:

```python
wrappedFactory = Factory.forProtocol(HelloClientProtocol)

endpoint = clientFromString(reactor, "autobahn:tcp\:localhost\:9000:url=ws\:// localhost\:9000")
endpoint.connect(wrappedFactory)
```

You can find a complete example for both client and server in these files:

 1. [client_endpoint.py](client_endpoint.py)
 2. [server_endpoint.py](server_endpoint.py)


*Example Client Endpoint Descriptors*

 1. `"autobahn:tcp\:localhost\:9000:url=ws\:// localhost\:9000"`
 1. `"autobahn:tcp\:localhost\:9000:url=ws\:// localhost\:9000:compress=false"`
 1. `"autobahn:tcp\:localhost\:9000:url=ws\:// localhost\:9000:autofrag=4096:debug=true"`

*Example Server Endpoint Descriptors*

 1. `"autobahn:tcp\:9000:url=ws\://localhost\:9000"`
 1. `"autobahn:tcp\:9000:url=ws\://localhost\:9000:autofrag=4096:debug=true"`
 1. `"autobahn:tcp\:9000\:interface\=0.0.0.0:url=ws\://localhost\:9000:compress=true"`
