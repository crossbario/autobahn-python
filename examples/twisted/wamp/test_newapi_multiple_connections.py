from twisted.internet import reactor
import txaio
from autobahn.twisted.wamp import Connection


def main1(connection):
    print('main1 created', connection)

    def on_join(session):
        print('main1 joined', session)
        session.leave()

    connection.on_join(on_join)


def main2(connection):
    print('main2 created', connection)

    def on_join(session):
        print('main2 joined', session)
        session.leave()

    connection.on_join(on_join)


def run(entry_points):

    transports = [
        {
            "type": "websocket",
            "url": "ws://127.0.0.1:8080/ws"
        }
    ]

    done = []

    for main in entry_points:
        connection = Connection(main, realm=u'public',
            transports=transports, reactor=reactor)
        done.append(connection.connect())

    # deferred that fires when all connections are done
    done = txaio.gather(done)

    def finish(res):
        print("all connections done", res)
        reactor.stop()

    done.addBoth(finish)

    reactor.run()


if __name__ == '__main__':
    return run([main1, main2])
