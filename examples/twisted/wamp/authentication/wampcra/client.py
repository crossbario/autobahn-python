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

import sys

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import clientFromString

from autobahn.twisted import wamp, websocket
from autobahn.wamp import types
from autobahn.wamp import auth


PASSWORDS = {
    u'peter': u'secret1',
    u'joe': u'secret2'
}

USER = u'peter'
# USER = u'joe'


class MyFrontendComponent(wamp.ApplicationSession):

    def onConnect(self):
        self.join(self.config.realm, [u"wampcra"], USER)

    def onChallenge(self, challenge):
        print challenge
        if challenge.method == u"wampcra":
            if u'salt' in challenge.extra:
                key = auth.derive_key(PASSWORDS[USER].encode('utf8'),
                                      challenge.extra['salt'].encode('utf8'),
                                      challenge.extra.get('iterations', None),
                                      challenge.extra.get('keylen', None))
            else:
                key = PASSWORDS[USER].encode('utf8')
            signature = auth.compute_wcs(key, challenge.extra['challenge'].encode('utf8'))
            return signature.decode('ascii')
        else:
            raise Exception("don't know how to compute challenge for authmethod {}".format(challenge.method))

    @inlineCallbacks
    def onJoin(self, details):

        # call a remote procedure
        ##
        try:
            now = yield self.call(u'com.timeservice.now')
        except Exception as e:
            print("Error: {}".format(e))
        else:
            print("Current time from time service: {}".format(now))

        self.leave()

    def onLeave(self, details):
        print("onLeave: {}".format(details))
        self.disconnect()

    def onDisconnect(self):
        reactor.stop()


if __name__ == '__main__':

    # 0) start logging to console
    log.startLogging(sys.stdout)

    # 1) create a WAMP application session factory
    component_config = types.ComponentConfig(realm="realm1")
    session_factory = wamp.ApplicationSessionFactory(config=component_config)
    session_factory.session = MyFrontendComponent

    # 2) create a WAMP-over-WebSocket transport client factory
    transport_factory = websocket.WampWebSocketClientFactory(session_factory,
                                                             url="ws://127.0.0.1:8080/ws", debug=False, debug_wamp=False)

    # 3) start the client from a Twisted endpoint
    client = clientFromString(reactor, "tcp:127.0.0.1:8080")
    client.connect(transport_factory)

    # 4) now enter the Twisted reactor loop
    reactor.run()
