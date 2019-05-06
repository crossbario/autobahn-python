import txaio
txaio.use_twisted()

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import TCP4ClientEndpoint, UNIXClientEndpoint
from twisted.application.internet import ClientService

from autobahn.wamp.types import ComponentConfig
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

def add2(a, b):
    print('add2 called: {} {}'.format(a, b))
    return a + b


class MyAppSession(ApplicationSession):

    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self._countdown = 5

    def onConnect(self):
        self.log.info('transport connected')

        # lets join a realm .. normally, we would also specify
        # how we would like to authenticate here
        self.join(self.config.realm)

    def onChallenge(self, challenge):
        self.log.info('authentication challenge received')

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info('session joined: {}'.format(details))

        yield self.register(add2, u'com.example.add2')

        for i in range(10):
            res = yield self.call(u'com.example.add2', 23, i * self._countdown)
            self.log.info('result: {}'.format(res))

        yield self.leave()

    def onLeave(self, details):
        self.log.info('session left: {}'.format(details))
        self.disconnect()

    def onDisconnect(self):
        self.log.info('transport disconnected')
        # this is to clean up stuff. it is not our business to
        # possibly reconnect the underlying connection
        self._countdown -= 1
        if self._countdown <= 0:
            try:
                reactor.stop()
            except ReactorNotRunning:
                pass


if __name__ == '__main__':
    txaio.start_logging(level='debug')

    # create a WAMP session object. this is reused across multiple
    # reconnects (if automatically reconnected)
    session = MyAppSession(ComponentConfig(u'crossbardemo', {}))

    # use WAMP-over-RawSocket
    # runner = ApplicationRunner(u'rs://localhost:8080', u'crossbardemo')

    # alternatively, use WAMP-over-Unix-socket
    runner = ApplicationRunner(
        u'ws://localhost:8080',
        u'crossbardemo',
    )

    # alternatively, use WAMP-over-WebSocket plain (standalone, not hooked in under Twisted Web)
    #runner = ApplicationRunner(u'ws://localhost:8080/ws', u'crossbardemo')

    # alternatively, use WAMP-over-WebSocket running under Twisted Web (as a web resource)
    # runner = ApplicationRunner(u'ws://localhost:8080/twws', u'crossbardemo')

    runner.run(
        session,
        auto_reconnect=True,
        endpoint=UNIXClientEndpoint(
            reactor,
            "examples/router/.crossbar/unix_socket",
        )

    )
