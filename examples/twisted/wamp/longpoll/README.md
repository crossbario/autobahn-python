# WAMP-over-Longpoll

WAMP can run over Long-poll, a HTTP-bassed fallback for browsers lacking native WebSocket support.

The implementation in AutobahnPython follows the specification of the transport in the [WAMP Advanced Profile](https://github.com/tavendo/WAMP/blob/master/spec/advanced.md#long-poll-transport).

The example here includes a WAMP router running two services on a Web transport:

 * **/ws**: WAMP-over-WebSocket transport
 * **/lp**: WAMP-over-Long-poll transport

The Long-poll transport can be tested with **curl**.

Start the router in a first terminal:

```shell
make test
```

Run the following in a second terminal:

```shell
make open
make receive
```

Run the following in a thrid terminal, restarting the `make receive` command in the second terminal:

```shell
make hello
make subscribe
```

As you continue to restart `make receive`, WAMP events should be received.

