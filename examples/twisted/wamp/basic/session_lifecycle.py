from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner


class MySession(ApplicationSession):
    def __init__(self, config=None):
        ApplicationSession.__init__(self, config)
        self.log.info('session created')

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
    runner = ApplicationRunner(url=u'ws://localhost:8080/ws', realm=u'realm1')
    runner.run(MySession)
