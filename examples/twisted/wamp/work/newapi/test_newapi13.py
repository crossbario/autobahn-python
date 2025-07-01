from autobahn.wamp import Api

# create an API object to use the decorator style
# register/subscribe WAMP actions
api = Api()


@api.register("com.example.add2")
def add2(a, b):
    return a + b


@api.subscribe("com.example.on-hello", details=True)
def on_hello(msg, details=None):
    print("Someone said: {}".format(msg))
    details.session.leave()


@coroutine
def component1(reactor, session):
    """
    A first component, which gets called "setup-like". When
    it returns, this signals that the component is ready for work.
    """
    # expose the API on the session
    yield session.expose(api)


@coroutine
def component2(reactor, session):
    """
    A second component, which gets called "main-like".
    When it returns, this will automatically close the session.
    """
    result = yield session.call("com.example.add2", 2, 3)
    session.publish("com.example.on-hello", "result={}".format(result))


if __name__ == "__main__":
    from autobahn.twisted.component import Component, run

    # Components wrap either a setup or main function and
    # can be configured with transports, authentication and so on.
    components = [Component(setup=component1), Component(main=component2)]

    # a convenience runner is provided which takes a list of
    # components and runs all of them
    run(components)
