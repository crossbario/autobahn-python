from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted import Client


@coroutine
def on_join(session):
    try:
        res = yield session.call(u'com.example.add2', 2, 3)
        print("Result: {}".format(res))
    except Exception as e:
        print("Error: {}".format(e))
    finally:
        session.leave()


if __name__ == '__main__':
    # this is Client, a high-level API above Connection and Session
    # it's a what is nowerdays ApplicationRunner, but with a better
    # name and a listener based interface
    client = Client()

    # "on_join" is a Session event that bubbled up via Connection
    # to Client here. this works since Connection/Session have default
    # implementations that by using WAMP defaults
    client.on_join(on_join)

    # now make it run ..
    client.run()
