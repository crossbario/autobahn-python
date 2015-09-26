from autobahn.wamp import Api


api = Api()

@api.register(u'com.example.add2')
def add2(a, b):
    return a + b

@api.subscribe(u'com.example.on-hello', details=True)
def on_hello(msg, details=None):
    print(u'Someone said: {}'.format(msg))
    details.session.leave()

@coroutine
def component1(reactor, session):
    yield session.add_api(api)

@coroutine
def component2(reactor, session):
    result = yield session.call(u'com.example.add2', 2, 3)
    session.publish(u'com.example.on-hello', u'result={}'.format(result))


if __name__ == '__main__':
    from autobahn.twisted.component import Component, run

    components = [
        Component(setup=component1),
        Component(main=component2)
    ]

    run(components)
