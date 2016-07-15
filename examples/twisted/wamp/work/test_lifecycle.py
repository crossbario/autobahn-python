import txaio
txaio.use_twisted()

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.application.internet import ClientService

from autobahn.wamp.types import ComponentConfig
from autobahn.twisted.wamp import ApplicationSession, WampWebSocketClientFactory


class MyComponent(ApplicationSession):

    def onConnect(self):
        self.log.info('transport connected')
        self.join(self.config.realm)

    def onChallenge(self, challenge):
        self.log.info('authentication challenge received')

    def onJoin(self, details):
        self.log.info('session joined: {}'.format(details))

    def onLeave(self, details):
        self.log.info('session left: {}'.format(details))

    def onDisconnect(self):
        self.log.info('transport disconnected')


if __name__ == '__main__':
    txaio.start_logging(level='info')

    session = MyComponent(ComponentConfig(u'realm1', {}))
    transport = WampWebSocketClientFactory(session, url=u'ws://localhost:8080/ws')
    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 8080)
    service = ClientService(endpoint, transport)
    service.startService()
    reactor.run()
