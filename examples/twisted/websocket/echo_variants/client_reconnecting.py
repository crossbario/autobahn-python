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

from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS


class EchoClientProtocol(WebSocketClientProtocol):

    def sendHello(self):
        self.sendMessage("Hello, world!".encode('utf8'))

    def onOpen(self):
        self.sendHello()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("Text message received: {}".format(payload.decode('utf8')))
        reactor.callLater(1, self.sendHello)


class EchoClientFactory(ReconnectingClientFactory, WebSocketClientFactory):

    protocol = EchoClientProtocol

    # http://twistedmatrix.com/documents/current/api/twisted.internet.protocol.ReconnectingClientFactory.html
    #
    maxDelay = 10
    maxRetries = 5

    def startedConnecting(self, connector):
        print('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        print('Lost connection. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Need the WebSocket server address, i.e. ws://127.0.0.1:9000")
        sys.exit(1)

    log.startLogging(sys.stdout)

    factory = EchoClientFactory(sys.argv[1])
    connectWS(factory)

    reactor.run()
