from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.connection import Connection


def main(reactor, connection):

    def on_join(session, details):
        print("on_join", details)
        try:
            res = yield self.call(u'com.example.add2', [2, 3])
            print(res)
        except Exception as e:
            print(e)
        self.leave()

    connection.on('join', on_join)


if __name__ == '__main__':

    connection = Connection()
    react(connection.start, [main])
