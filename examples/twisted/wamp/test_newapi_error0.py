from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted.wamp import Session
from autobahn.twisted.connection import Connection

# do we get decent errors if we have a completely wrong realm?
# (should see something, and it exits)

if __name__ == '__main__':
    connection = Connection(transports=u"ws://127.0.0.1:8080/ws", realm=u"bogus")
    react(connection.start)
