import txaio
from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks as coroutine
from autobahn.twisted.wamp import Session
from autobahn.twisted.connection import Connection

# should get a nice error on listening on a bogus event.

class Foo(Session):
    def on_join(self, details):
        print("on_join", details)
        self.on('foo', lambda: None)

if __name__ == '__main__':
    txaio.start_logging()
    connection = Connection(transports=u"ws://127.0.0.1:8080/ws", realm=u"crossbardemo")
    connection.session = Foo
    #connection.on('blam', lambda: None)
    react(connection.start)
