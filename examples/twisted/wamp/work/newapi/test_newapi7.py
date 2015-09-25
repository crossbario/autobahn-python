from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted.wamp import Connection

session = ApplicationSession()

@session.on_join
def on_join(session):
    print("Session {} has joined".format(session.id))

@session.on_leave
def on_leave(session, details):
    print("Session {} has left: {}".format(session.id, details.reason))

@session.register(u'com.myapp.add2')  # registering in on_join
def add2(a, b):
    return a + b

@coroutine
def main(transport):
    yield session.join(transport, u'myrealm1')
    result = yield session.call(u'com.myapp.add2', 2, 3)
    print("Result: {}".format(result))
    yield session.leave()
    yield transport.close()

if __name__ == '__main__':
    connection = Connection(main)
    react(connection.start)
