@coroutine
def component1_setup(reactor, session):
    # the session is joined and ready for use.
    def shutdown():
        print('backend component shutting down ..')
        session.leave()

    yield session.subscribe(u'com.example.shutdown', shutdown)

    def add2(a, b):
        print('backend component: add2()')
        return a + b

    yield session.register(u'com.example.add2', add2)

    print('backend component ready.')

    # as we exit, this signals we are ready! the session must be kept.


@coroutine
def component2_main(reactor, session):
    # the session is joined and ready
    result = yield session.call(u'com.example.add2', 2, 3)
    print('result={}'.format(result))

    session.publish(u'com.example.shutdown')

    # as we exit, this signals we are done with the session! the session
    # can be recycled


if __name__ == '__main__':
    from autobahn.twisted.wamp import Component, run

    components = [
        Component(setup=component1_setup),
        Component(main=component2_main)
    ]
    run(components)
