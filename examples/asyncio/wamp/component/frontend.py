from autobahn.asyncio.component import Component, run
from autobahn.wamp.types import RegisterOptions
from autobahn.wamp.exception import ApplicationError


async def main(reactor, session):
    print("Client session={}".format(session))

    try:
        res = await session.register(lambda: None, "com.foo.private")
        print("\n\nregistering 'com.foo.private' should have failed\n\n")
    except ApplicationError as e:
        print("registering 'com.foo.private' failed as expected: {}".format(e.error))

    res = await session.register(
        lambda: None,
        "should.work",
        options=RegisterOptions(match="exact"),
    )
    print("registered 'should.work' with id {}".format(res.id))

    try:
        res = await session.register(
            lambda: None,
            "prefix.fail.",
            options=RegisterOptions(match="prefix"),
        )
        print("\n\nshould have failed\n\n")
    except ApplicationError as e:
        print("prefix-match 'prefix.fail.' failed as expected: {}".format(e.error))

    print("calling 'example.foo'")
    res = await session.call("example.foo")
    print("example.foo() = {}".format(res))

    print("done")


component = Component(
    transports="ws://localhost:8080/auth_ws",
    main=main,
    realm="crossbardemo",
    authentication={
        "wampcra": {
            "authid": "bob",
            "authrole": "dynamic_authed",
            "secret": "p4ssw0rd",
        }
    },
)


if __name__ == "__main__":
    run([component])
