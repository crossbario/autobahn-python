

from autobahn.twisted.component import Component, run
from autobahn.wamp.types import RegisterOptions
from autobahn.wamp.exception import ApplicationError
from twisted.internet.defer import inlineCallbacks


@inlineCallbacks
def main(reactor, session):
    print("Client session={}".format(session))

    try:
        res = yield session.register(lambda: None, u"com.foo.private")
        print("\n\nregistering 'com.foo.private' should have failed\n\n")
    except ApplicationError as e:
        print("registering 'com.foo.private' failed as expected: {}".format(e.error))

    res = yield session.register(
        lambda: None, u"should.work",
        options=RegisterOptions(match=u'exact'),
    )
    print("registered 'should.work' with id {}".format(res.id))

    try:
        res = yield session.register(
            lambda: None, u"prefix.fail.",
            options=RegisterOptions(match=u'prefix'),
        )
        print("\n\nshould have failed\n\n")
    except ApplicationError as e:
        print("prefix-match 'prefix.fail.' failed as expected: {}".format(e.error))

    print("calling 'example.foo'")
    res = yield session.call(u"example.foo")
    print("example.foo() = {}".format(res))

    print("done")


component = Component(
    transports=u"ws://localhost:8080/auth_ws",
    main=main,
    realm=u"crossbardemo",
    authentication={
        u"wampcra": {
            u"authid": u"bob",
            u"authrole": u"dynamic_authed",
            u"secret": u"p4ssw0rd",
        }
    }
)


if __name__ == "__main__":
    run([component])
