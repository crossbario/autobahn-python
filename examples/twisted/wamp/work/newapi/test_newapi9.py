from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted.wamp import Connection

# A single session can freeze and resume over different transports

# sessions have a lifecycle independent of Connection/Transport
session = ApplicationSession()


def add2(a, b):
    return a + b


@coroutine
def main(transport):
    # join a realm and try to resume the session
    details = yield session.join(transport, "myrealm1", resume=True)

    if not details.is_resumed:
        # if the session is fresh, register a procedure ..

        yield session.register("com.myapp.add2", add2)

        # and leave the realm, freezing the session
        yield session.leave(freeze=True)

    else:
        # if the session is resumed, our registration will have been
        # reestablished automatically

        result = yield session.call("com.myapp.add2", 2, 3)
        print("Result: {}", result)

        # leave the realm finally
        yield session.leave()

    yield transport.close()


@coroutine
def test():
    transports = [
        {
            "type": "rawsocket",
            "serializer": "msgpack",
            "endpoint": {"type": "unix", "path": "/tmp/cb1.sock"},
        },
        {
            "type": "websocket",
            "url": "ws://127.0.0.1:8080/ws",
            "endpoint": {"type": "tcp", "host": "127.0.0.1", "port": 8080},
        },
    ]

    connection1 = Connection(main1, transports=transports[0])
    yield react(connection1.start)

    connection2 = Connection(main2, transports=transports[1])
    yield react(connection2.start)


if __name__ == "__main__":
    test()
