###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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

from twisted.internet import reactor, ssl
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import (
    WebSocketServerFactory,
    WebSocketServerProtocol,
    listenWS,
)

from autobahn.twisted.resource import WebSocketResource


class PingServerProtocol(WebSocketServerProtocol):

    def doPing(self):
        if self.run:
            self.sendPing()
            self.factory.pingsSent[self.peer] += 1
            print(
                "Ping sent to {} - {}".format(
                    self.peer, self.factory.pingsSent[self.peer]
                )
            )
            reactor.callLater(1, self.doPing)

    def onPong(self, payload):
        self.factory.pongsReceived[self.peer] += 1
        print(
            "Pong received from {} - {}".format(
                self.peer, self.factory.pongsReceived[self.peer]
            )
        )

    def onOpen(self):
        self.factory.pingsSent[self.peer] = 0
        self.factory.pongsReceived[self.peer] = 0
        self.run = True
        self.doPing()

    def onClose(self, wasClean, code, reason):
        self.run = False


class PingServerFactory(WebSocketServerFactory):

    def __init__(self, uri):
        WebSocketServerFactory.__init__(self, uri)
        self.pingsSent = {}
        self.pongsReceived = {}


if __name__ == "__main__":

    log.startLogging(sys.stdout)

    contextFactory = ssl.DefaultOpenSSLContextFactory(
        "keys/server.key", "keys/server.crt"
    )

    factory = PingServerFactory("wss://127.0.0.1:9000")

    factory.protocol = PingServerProtocol
    listenWS(factory, contextFactory)

    resource = WebSocketResource(factory)

    root = File(".")
    # note that Twisted uses bytes for URLs, which mostly affects Python3
    root.putChild(b"ws", resource)
    site = Site(root)

    reactor.listenSSL(8080, site, contextFactory)
    # reactor.listenTCP(8080, site)

    reactor.run()
