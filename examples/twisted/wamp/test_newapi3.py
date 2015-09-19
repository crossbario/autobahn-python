from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted.connection import Connection


def main(reactor, connection):

    @coroutine
    def on_join(session, details):
        print("on_join: {}".format(details))

        def add2(a, b):
            return a + b

        yield self.register(add2, u'com.example.add2')

        try:
            res = yield self.call(u'com.example.add2', 2, 3)
            print("result: {}".format(res))
        except Exception as e:
            print("error: {}".format(e))
        finally:
            self.leave()

    connection.on('join', on_join)


if __name__ == '__main__':

    connection = Connection()
    react(connection.start, [main])
