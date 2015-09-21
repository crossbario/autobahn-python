from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted.connection import Connection


def main(reactor, connection):

    @coroutine
    def on_join(session, details):
        print("on_join: {}".format(details))
        try:
            print(session._transport)
            print(session._transport.websocket_protocol_in_use)
        except Exception as e:
            pass

        def add2(a, b):
            print("add2() called", a, b)
            return a + b

        yield session.register(add2, u'com.example.add2')

        try:
            res = yield session.call(u'com.example.add2', 2, 3)
            print("result: {}".format(res))
        except Exception as e:
            print("error: {}".format(e))
        finally:
            print("leaving ..")
            session.leave()

    connection.on('join', on_join)


if __name__ == '__main__':
    #import txaio
    #txaio.use_twisted()
    #txaio.start_logging(level='debug')

    transports = [
        {
            'type': 'rawsocket',
            'serializer': 'msgpack',
            'endpoint': {
                'type': 'unix',
                'path': '/tmp/cb1.sock'
            }
        },
        {
            'type': 'websocket',
            'url': 'ws://127.0.0.1:8080/ws',
            'endpoint': {
                'type': 'tcp',
                'host': '127.0.0.1',
                'port': 8080
            }
        }
    ]
    connection = Connection(transports=transports)
    connection.on('start', main)

    react(connection.start)
