from twisted.internet.task import react
from autobahn.twisted.connection import Connection


def main(reactor, connection):
    # called exactly once when this connection is started
    print('connection setup time!')

    def on_join(session):
        # called each time a transport was (re)connected and a session
        # was established. until we leave explicitly or stop reconnecting.
        print('session ready!')
        #session.leave()

    connection.on('join', on_join)


if __name__ == '__main__':
    connection = Connection(main)
    react(connection.start)
