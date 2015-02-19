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

from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession


class MyAppComponent(ApplicationSession):

    def onJoin(self, details):
        if not self.factory._myAppSession:
            self.factory._myAppSession = self

    def onLeave(self, details):
        if self.factory._myAppSession == self:
            self.factory._myAppSession = None


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet.endpoints import clientFromString
    log.startLogging(sys.stdout)

    # we use an Autobahn utility to import the "best" available Twisted reactor
    ##
    from autobahn.twisted.choosereactor import install_reactor
    reactor = install_reactor()
    print("Running on reactor {}".format(reactor))

    # create a WAMP application session factory
    ##
    from autobahn.twisted.wamp import ApplicationSessionFactory
    session_factory = ApplicationSessionFactory()

    # .. and set the session class on the factory
    ##
    session_factory.session = MyAppComponent

    # since we are running this component as a client, there
    # will be only 1 app session instance anyway. We'll store a
    # reference on the session factory, so we can access it
    # from "outside" the session instance later (see below)
    ##
    session_factory._myAppSession = None

    # create a WAMP-over-WebSocket transport client factory
    ##
    from autobahn.twisted.websocket import WampWebSocketClientFactory
    transport_factory = WampWebSocketClientFactory(session_factory, "ws://127.0.0.1:8080/ws")

    # start a WebSocket client from an endpoint
    ##
    client = clientFromString(reactor, "tcp:127.0.0.1:8080")
    client.connect(transport_factory)

    # publish an event every second from the (single) application session
    # that get created by the session factory
    ##
    @inlineCallbacks
    def pub():
        counter = 0
        while True:
            # here we can access the app session that was created ..
            ##
            if session_factory._myAppSession:
                session_factory._myAppSession.publish('com.myapp.topic123', counter)
                print("published event", counter)
            else:
                print("no session")
            counter += 1
            yield sleep(1)

    pub()

    # now enter the Twisted reactor loop
    ##
    reactor.run()
