# Running the Example

There are four pieces you need to start for the full demo (see below for explanation): a `netcat` or telnet daemon on port 23; a Web server; a WebSocket port-forwarder; and the browser frontend.

## netcat

In this demo, we forward a telnet session from a browser to a telnet server. So, we need to run he telnet server, which is easiest with "netcat": ``nc -l 23`` (as root, so you can listen on 23). Run this in its own terminal.


## Web server

To serve the Web content, we can use the built-in Web server from Twisted like so. Run this from the same directory as this README:

    twistd -n --pidfile=twistd-web.pid web --path=. --port=tcp:8080


## Port Forwarder

More details below, but Autobahn provides a `twistd` plugin to "unwrap" a protocol that's being forwarded over WebSocket and send it to any endpoint. Run this in yet another window:

	twistd -n --pidfile=twistd-pf.pid endpointforward --endpoint "autobahn:tcp\:9000:url=ws\://localhost\:9000" --dest_endpoint="tcp:127.0.0.1:23"

This says, "listen on tcp 9000 and forward encapulated protocol to localhost:23".


## Browser Frontend

You can now point your favourite browser at http://localhost:8080/telnet.html and see the Websockify project's telnet demo; clicking "connect" should cause the "terminal" in your browser to be connected to your `netcat` process.

That is, we've encapsulated telnet over WebSocket in your browser and then de-encapsulated it at your server and forwarded it to telnet; this can be done with any protocol.


# Stream-based Endpoints over WebSocket

**Autobahn**|Python provides facilities to wrap existing stream-based Twisted factories and protocols with WebSocket.
That means, you can run any stream-based protocol *over* WebSocket without any modification to the existing protocol and factory.

Why would you want to do that? For example, to create a VNC, SSH, IRC, IMAP, MQTT or other client for some existing protocol that runs on browsers, and connects to an *unmodified* server.

> This example is about running any stream-based Twisted endpoint over WebSocket.
> **Autobahn**|Python also supports running WebSocket over any stream-based Twisted endpoint. Please see [here](https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_endpoints).
>

## WebSocket Transport Scheme

**Autobahn**|Python follows the transport scheme established by [websockify](https://github.com/kanaka/websockify): a WebSocket subprotocol is negotiated, either `binary` or `base64`. Alternative binary compatible subprotocols may also be specified, such as the MQTT `mqttv3.1` protocol, by using the `subprotocol` endpoint descriptor.

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
 1. `"autobahn:tcp\:localhost\:9000:url=ws\:// localhost\:9000:autofrag=4096"`

*Example Server Endpoint Descriptors*

 1. `"autobahn:tcp\:9000:url=ws\://localhost\:9000"`
 1. `"autobahn:tcp\:9000:url=ws\://localhost\:9000:autofrag=4096"`
 1. `"autobahn:tcp\:9000\:interface\=0.0.0.0:url=ws\://localhost\:9000:compress=true"`


## Twistd

### Endpoint Forwarder

**Autobahn**|Python further includes a `twistd` (the Twisted Daemon) plugin that provides a generic **stream endpoint forwarder**.

The forwarder can listen on any stream-based server endpoint and forward traffic to any other stream-based client endpoint.

As an example, here is how you forward WebSocket to Telnet:

	twistd -n endpointforward --endpoint "autobahn:tcp\:9000:url=ws\://localhost\:9000" --dest_endpoint="tcp:127.0.0.1:23"

Included in this directory is a Terminal client written in JavaScript (this code is from the [websockify project](https://github.com/kanaka/websockify)).

Open `telnet.html` in your browser, provide the server IP and port (the one running `twistd`) and press connect.

As soon as the Process support for endpoints in Twisted is fully here, the forwarder will allow you to expose any program over WebSocket, by forwarding the program's `stdin` and `stdout`.

Another example is to create a WebSocket proxy in front of a MQTT broker. This makes use of the optional `subprotocol` input that allows the `mqttv3.1` binary compatible subprotocol to be accepted along with the default `binary` and `base64` subprotocols.

	twistd -n endpointforward --endpoint "autobahn:tcp\:9000:url=ws\://localhost\:9000:subprotocol=mqttv3.1" --dest_endpoint="tcp:127.0.0.1:1883"

Essentially, these features are equivalent of what the following two projects provide:

 * [websockify](https://github.com/kanaka/websockify)
 * [websocketd](https://github.com/joewalnes/websocketd)

But since Twisted endpoints are extensible, eg support for serial is coming, this will also allow you to expose serial devices directly over WebSocket!

### Manhole

Start manhole

	echo "admin:admin" > passwd
	twistd -n manhole --telnetPort "autobahn:tcp\:9000:url=ws\://localhost\:9000:compress=false:debug=true" --passwd ./passwd

It seems, login is possible, but then the JS Terminal seems to get confused by Manhole sending `fffc01`. I don't know what's going on.
