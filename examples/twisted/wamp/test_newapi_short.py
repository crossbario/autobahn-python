from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted import Runner


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
    # this is Runner, a high-level API above Connection and Session
    runner = Runner()

    # "on_join" is a Session event that bubbled up via Connection
    # to Runner here. this works since Connection/Session have default
    # implementations that work with WAMP defaults
    runner.on_join(on_join)
    runner.run()
