



@coroutine
def main(reactor, transport, config):
    session = ApplicationSession(config)
    yield session.join(transport)


def main1(reactor, session):
    pass

def main2(reactor, session):
    pass


if __name__ == '__main__':

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

    services = [main1, main2]

    client = Client(services, transports)
    react(client.run)
