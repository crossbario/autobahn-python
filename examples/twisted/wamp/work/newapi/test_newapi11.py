@coroutine
def main1(reactor, connection):
    with yield connection.open() as transport:
        with yield transport.join(connection.config.realm) as session:
            result = yield session.call(u'com.example.add2', 2, 3)
            print('result={}'.format(result))

if __name__ == '__main__':
    connection = Connection(main1)
    react(connection.start)



@coroutine
def main2(reactor, connection):
    # create a new transport from the connection
    transport = yield connection.open()

    # create a new session running on the transport
    session = yield transport.join(connection.config.realm)

    # now register a procedure
    def add2(a, b):
        return a + b

    yield session.register(u'com.example.add2', add2)

    # and call the procedure
    result = yield session.call(u'com.example.add2', 2, 3)
    print('result={}'.format(result))

    # now leave the realm, which frees the underlying transport
    # but freeze the session
    yield session.leave(freeze=True)

    # .. sleep, but not too long, otherwise router finally kills the session.
    yield sleep(60)

    # create a second, new transport from the connection
    # this might be a 2nd TCP connection or a 2nd logical WAMP transport running
    # over a single, multiplexed connection
    transport2 = yield connection.open()

    # now resume the session on the new transport. using the session token mechanism,
    # the router will resume the session and deliver buffered events/calls to the
    # resumed session
    yield session.resume(transport2)

    # create a 2nd session running over the 1st transport
    session2 = transport.join(connection.config.realm)

    # call the procedure registered on the (resumed) session running on transport2
    result = yield session.call(u'com.example.add2', 2, 3)
    print('result={}'.format(result))

    # if the transport supports multiplexing, multiple session can run
    # concurrently over the underlying transport
    if transport.is_multiplexed:
        session3 = yield transport.join(connection.config.realm)

    # now finally leave sessions ..
    yield session.leave()
    yield session2.leave()

    # .. and close the transports
    yield transport.close()
    yield transport2.close()


if __name__ == '__main__':

    transports = [
        {
            'type': 'rawsocket',
            'serializer': 'msgpack',
            'endpoint': {
                'type': 'unix',
                'path': '/tmp/cb1.sock'
            }
        }
    ]
    config = Config(realm=u'myrealm1')
    connection = Connection(main, transports=transports, config=config)
    react(connection.start)
