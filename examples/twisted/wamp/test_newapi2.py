from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.connection import Connection

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner


class MySession(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        print("on_join", details)
        try:
            res = yield self.call(u'com.example.add2', [2, 3])
            print(res)
        except Exception as e:
            print(e)
        self.leave()

    def onLeave(self, details):
        print("on_leave: {}".format(details))
        self.disconnect()


def main(reactor, connection):
    # called exactly once when this connection is started
    print('connection setup time!')

    def on_join(session):
        # called each time a transport was (re)connected and a session
        # was established. until we leave explicitly or stop reconnecting.
        print('session ready!')
        #session.leave()

    connection.on('join', on_join)


if __name__ == '__main__':

    if True:
        connection = Connection(main, realm=u'realm1', session_klass=MySession)
        react(connection.start)
    else:
        runner = ApplicationRunner(u"ws://127.0.0.1:8080/ws", u"realm1")
        runner.run(MySession)
