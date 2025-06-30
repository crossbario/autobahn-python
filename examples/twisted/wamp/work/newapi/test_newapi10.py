# run multiple WAMP sessions over the same underlying WAMP transport

session1 = ApplicationSession()
session2 = ApplicationSession()


def main(reactor, transport):
    transport1 = yield transport.split()
    session = yield transport.join()
    yield session1.join(transport, "myrealm1")
    yield session2.join(transport, "myrealm1")


def main1(reactor, transport):
    yield session1.join(transport, "myrealm1")


def main2(reactor, transport):
    yield session2.join(transport, "myrealm1")


if __name__ == "__main__":
    transports = [
        {
            "type": "rawsocket",
            "serializer": "msgpack",
            "endpoint": {"type": "unix", "path": "/tmp/cb1.sock"},
        }
    ]

    realm = "myrealm1"

    extra = {"foo": 23, "bar": "baz"}

    client = Client([main1, main2])
    react(connection.start)
