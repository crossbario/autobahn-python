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

from twisted.internet.protocol import Protocol


class HelloServerProtocol(Protocol):

    def connectionMade(self):
        print("connectionMade", self.transport.getHost(), self.transport.getPeer())
        self.transport.write('how are you?' * 100)

    def dataReceived(self, data):
        print("dataReceived: {}".format(data))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor
    from twisted.internet.protocol import Factory

    from autobahn.twisted.websocket import WrappingWebSocketServerFactory

    log.startLogging(sys.stdout)

    wrappedFactory = Factory.forProtocol(HelloServerProtocol)
    factory = WrappingWebSocketServerFactory(wrappedFactory,
                                             u"ws://127.0.0.1:9000",
                                             debug=False,
                                             enableCompression=False,
                                             autoFragmentSize=1024)

    reactor.listenTCP(9000, factory)
    reactor.run()
