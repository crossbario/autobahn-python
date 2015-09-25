from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted.connection import Connection


@coroutine
def main(reactor, connection):

    transport = yield connection.connect()
    session = yield transport.join(u'realm1')
    result = yield session.call(u'com.example.add2', 2, 3)
    yield session.leave()
    yield transport.disconnect()
    yield connection.close()


if __name__ == '__main__':
    connection = Connection()
    connection.on('start', main)

    react(connection.start)
