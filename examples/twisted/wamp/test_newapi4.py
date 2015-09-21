from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted.wamp import Session
from autobahn.twisted.connection import Connection


def make_session(config):

    @coroutine
    def on_join(session, details):
        print("on_join: {}".format(details))

        def add2(a, b):
            return a + b

        yield session.register(add2, u'com.example.add2')

        try:
            res = yield session.call(u'com.example.add2', 2, 3)
            print("result: {}".format(res))
        except Exception as e:
            print("error: {}".format(e))
        finally:
            session.leave()

    session = Session(config=config)
    session.on('join', on_join)
    return session


if __name__ == '__main__':

    session = make_session()
    connection = Connection()
    react(connection.start, [session])
