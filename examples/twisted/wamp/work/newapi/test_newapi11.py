@coroutine
def main(reactor, session):
    # the session is joined and ready
    result = yield session.call("com.example.add2", 2, 3)
    print("result={}".format(result))
    # as we exit, this signals we are done with the session! the session
    # can be recycled


if __name__ == "__main__":
    client = Client(main=main)
    react(client.run)


@coroutine
def setup(reactor, session):
    # the session is joined and ready also!
    def add2(a, b):
        return a + b

    yield session.register("com.example.add2", add2)
    print("procedure registered")
    # as we exit, this signals we are ready! the session must be kept.


if __name__ == "__main__":
    client = Client(setup=setup)
    react(client.run)


@coroutine
def client_main(reactor, client):

    @coroutine
    def transport_main(reactor, transport):

        @coroutine
        def session_main(reactor, session):
            result = yield session.call("com.example.add2", 2, 3)
            print("result={}".format(result))

        # returns when the session_main has finished (!), the session
        # calls leave() or the underlying transport closes
        yield transport.join(session_main, transport)

    # returns when the transport_main won't reconnect
    yield client.connect(transport_main)


if __name__ == "__main__":
    client = Client(client_main=client_main)
    react(client.run)


@coroutine
def session_main(reactor, session):
    result = yield session.call("com.example.add2", 2, 3)
    print("result={}".format(result))


if __name__ == "__main__":
    client = Client(session_main=session_main)
    react(client.run)


@coroutine
def session_main(reactor, session):
    def add2(a, b):
        return a + b

    yield session.register("com.example.add2", add2)
    print("procedure registered")
    txaio.return_value(txaio.create_future())


if __name__ == "__main__":
    client = Client(session_main=session_main)
    react(client.run)


@coroutine
def main1(reactor, session, details):

    result = yield session.call("com.example.add2", 2, 3)
    print("result={}".format(result))

    yield session.leave()


if __name__ == "__main__":
    # hooking into on_join is the highest-level API -
    # the user callback will fire with a joined session ready to use
    # both the transport auto-reconnection logic and the session creation
    # defaults in Client are reused
    client = Client(on_join=main1)
    react(client.run)


@coroutine
def main1(reactor, transport, details):
    # transport.join() yields a joined session object when successful
    session = yield transport.join(details.config.realm)

    # the session is joined and can be used
    result = yield session.call("com.example.add2", 2, 3)
    print("result={}".format(result))

    yield session.leave()


if __name__ == "__main__":
    # hooking into on_connect is a medium-level API -
    # the user callback will fire with a connected transport which
    # can be used to create new sessions from. the auto-reconnection
    # logic in Client is reused. user code can reuse a transport while
    # joining/leaving multiple times. with a multiplexing capable transport,
    # user code may even create multiple concurrent sessions.
    client = Client(on_open=main1)
    react(client.run)


@coroutine
def main1(reactor, client, details):
    # client.open() yields a connected transport when successful
    transport = yield client.open()

    # create a session running over the transport
    session = yield transport.join(config.realm)
    result = yield session.call("com.example.add2", 2, 3)
    print("result={}".format(result))
    yield session.leave()
    yield transport.close()


if __name__ == "__main__":
    # hooking into on_create is a low-level API - the user callback
    # will fire with a created client, and the user code can
    # control the whole transport and session creation, connection and
    # reconnection process.
    client = Client(on_create=main1)
    react(client.run)


@coroutine
def main1(reactor, client, config):
    transport = yield client.open()
    session = yield transport.join(config.realm)
    result = yield session.call("com.example.add2", 2, 3)
    print("result={}".format(result))
    yield session.leave()
    yield transport.close()


if __name__ == "__main__":
    # hooking into on_create is a low-level API - the user callback
    # will fire with a created client, and the user code can
    # control the whole transport and session creation, connection and
    # reconnection process.
    client = Client(on_create=main1)
    react(client.run)


@coroutine
def main1(reactor, client, config):
    while True:
        delay = client.next_delay()
        if delay:
            yield sleep(delay)
        else:
            break
        try:
            pass
            # client.open() yields a connected WAMP transport
            # with yield client.open() as transport:
            #     try:
            #         with yield transport.join(config.realm) as session:
            #             result = yield session.call('com.example.add2', 2, 3)
            #             print('result={}'.format(result))
            #     except Exception as e:
            #         pass
        except Exception as e:
            pass


if __name__ == "__main__":
    # hooking into on_create is a low-level API - the user callback
    # will fire with a created client, and the user code can
    # control the whole transport and session creation, connection and
    # reconnection process.
    client = Client(on_create=main1)
    react(client.run)


@coroutine
def main2(reactor, connection):
    # create a new transport from the connection
    transport = yield connection.open()

    # create a new session running on the transport
    session = yield transport.join(connection.config.realm)

    # now register a procedure
    def add2(a, b):
        return a + b

    yield session.register("com.example.add2", add2)

    # and call the procedure
    result = yield session.call("com.example.add2", 2, 3)
    print("result={}".format(result))

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
    result = yield session.call("com.example.add2", 2, 3)
    print("result={}".format(result))

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


if __name__ == "__main__":

    transports = [
        {
            "type": "rawsocket",
            "serializer": "msgpack",
            "endpoint": {"type": "unix", "path": "/tmp/cb1.sock"},
        }
    ]
    config = Config(realm="myrealm1")
    connection = Connection(main, transports=transports, config=config)
    react(connection.start)
