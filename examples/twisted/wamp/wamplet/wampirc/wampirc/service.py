###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from __future__ import absolute_import

from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import clientFromString
from twisted.words.protocols import irc

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError

from wampirc.client import IRCClientFactory


class Bot:

    """
    Tracks currently running bot instances.
    """

    def __init__(self, id, factory, client):
        self.id = id
        self.factory = factory
        self.client = client


class IRCComponent(ApplicationSession):

    """
    IRC bot services component.
    """

    def __init__(self, config):
        ApplicationSession.__init__(self)
        self.config = config
        self._bots = {}
        self._bot_no = 0

    @wamp.register('com.myapp.start_bot')
    def start_bot(self, nick, channels):
        self._bot_no += 1
        id = self._bot_no
        factory = IRCClientFactory(self, nick, channels)

        from twisted.internet import reactor
        client = clientFromString(reactor, self.config.extra['server'])
        d = client.connect(factory)

        def onconnect(res):
            self._bots[id] = Bot(id, factory, client)
            return id
        d.addCallback(onconnect)

        return d

    @wamp.register('com.myapp.stop_bot')
    def stop_bot(self, id):
        if id in self._bots:
            f = self._bots[id].factory
            if f.proto:
                f.proto.transport.loseConnection()
            f.stopFactory()
            del self._bots[id]
        else:
            raise ApplicationError('com.myapp.error.no_such_bot')

    @inlineCallbacks
    def onJoin(self, details):
        try:
            regs = yield self.register(self)
            print("Ok, registered {} procedures.".format(len(regs)))
        except Exception as e:
            print("Failed to register procedures: {}".format(e))

        print("IRC Bot Backend ready!")

    def onDisconnect(self):
        reactor.stop()


def make(config):
    if config:
        return IRCComponent(config)
    else:
        # if no config given, return a description of this WAMPlet ..
        return {'label': 'An IRC bot service component',
                'description': 'This component provides IRC bot services via WAMP.'}


if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner

    extra = {
        "server": "tcp:irc.freenode.net:6667"
    }

    # test drive the component during development ..
    runner = ApplicationRunner(
        url="ws://127.0.0.1:8080/ws",
        realm="realm1",
        extra=extra,
        debug=False,  # low-level WebSocket debugging
        debug_wamp=False,  # WAMP protocol-level debugging
        debug_app=True)  # app-level debugging

    runner.run(make)
