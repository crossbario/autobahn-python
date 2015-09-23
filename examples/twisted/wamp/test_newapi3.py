from __future__ import print_function

from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks as coroutine

from autobahn.twisted.connection import Connection


@coroutine
def main(reactor, session):
    details = yield session.join(u'crossbardemo')
    print("joined: {}".format(details))
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
        yield session.leave()


if __name__ == '__main__':
    if False:
        import txaio
        txaio.start_logging(level='debug')

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
    connection = Connection(transports=transports, main=main)
    react(connection.start)
