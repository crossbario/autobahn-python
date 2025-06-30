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

from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol


class EchoClientProtocol(WebSocketClientProtocol):
    """
    Example WebSocket client protocol. This is where you define your application
    specific protocol and logic.
    """

    def sendHello(self):
        self.sendMessage("Hello, world!".encode("utf8"))

    def onOpen(self):
        self.sendHello()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("Text message received: {}".format(payload.decode("utf8")))
        self.factory.reactor.callLater(1, self.sendHello)


class EchoClientFactory(WebSocketClientFactory):
    """
    Example WebSocket client factory. This creates a new instance of our protocol
    when the client connects to the server.
    """

    protocol = EchoClientProtocol


if __name__ == "__main__":
    import argparse
    import sys

    from twisted.internet.endpoints import clientFromString
    from twisted.python import log

    # parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output."
    )

    parser.add_argument(
        "--websocket",
        default="tcp:127.0.0.1:9000",
        help='WebSocket client Twisted endpoint descriptor, e.g. "tcp:127.0.0.1:9000" or "unix:/tmp/mywebsocket".',
    )

    parser.add_argument(
        "--wsurl",
        default="ws://127.0.0.1:9000",
        help="WebSocket URL (must suit the endpoint), e.g. ws://127.0.0.1:9000.",
    )

    args = parser.parse_args()

    # start Twisted logging to stdout
    log.startLogging(sys.stdout)

    # we use an Autobahn utility to import the "best" available Twisted reactor
    from autobahn.twisted.choosereactor import install_reactor

    reactor = install_reactor()
    print("Running on reactor {}".format(reactor))

    # start a WebSocket client
    wsfactory = EchoClientFactory(args.wsurl)
    wsclient = clientFromString(reactor, args.websocket)
    wsclient.connect(wsfactory)

    # now enter the Twisted reactor loop
    reactor.run()
