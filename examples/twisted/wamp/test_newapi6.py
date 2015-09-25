from __future__ import print_function

from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks, DeferredList

from autobahn.twisted.connection import Connection
from datetime import datetime

class UserCode(object):
    def add(self, *args):
        return sum(args)

    def subtract(self, *args):
        return sum([-x for x in args])


# could be an AB-provided helper?
def register_object(session, prefix, obj):
    """
    yield register_object(session, u"com.example.datetime.", datetime.datetime)
    """
    methods = [f for f in dir(obj) if not f.startswith('_')]
    print("registering", methods, "of", obj.__class__.__name__)

    return DeferredList(
        [session.register(getattr(obj, m), prefix + m) for m in methods]
    )

@inlineCallbacks
def main(reactor, session):
    details = yield session.join(u'crossbardemo')
    print("joined: {}".format(details))
    api = UserCode()
    yield register_object(session, u"com.example.math.", api)
    yield register_object(session, u"com.example.dt.", datetime.now())

    # now call them
    x = yield session.call(u"com.example.math.add", 1, 2, 3)
    print("x =", x)
    y = yield session.call(u"com.example.math.subtract", 6, 2, 1)
    print("y =", y)
    z = yield session.call(u"com.example.dt.isoformat")
    print("z =", z)
    yield session.leave()
    yield session.disconnect()


if __name__ == '__main__':
    import txaio
    txaio.start_logging(level='info')
    connection = Connection(transports=u'ws://127.0.0.1:8080/ws', main=main)
    react(connection.start)
