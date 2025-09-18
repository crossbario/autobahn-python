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

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol


class EchoServerProtocol(WebSocketServerProtocol):
    """
    Example WebSocket server protocol. This is where you define your application
    specific protocol and logic.
    """

    def onMessage(self, payload, isBinary):
        # just echo any WebSocket message received back to client
        ##
        self.sendMessage(payload, isBinary)


class EchoServerFactory(WebSocketServerFactory):
    """
    Example WebSocket server factory. This creates new instances of our protocol
    for each client connecting.
    """

    protocol = EchoServerProtocol


if __name__ == "__main__":
    import argparse
    import sys

    from twisted.internet.endpoints import serverFromString
    from twisted.python import log

    # parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output."
    )

    parser.add_argument(
        "--websocket",
        default="tcp:9000",
        help='WebSocket server Twisted endpoint descriptor, e.g. "tcp:9000" or "unix:/tmp/mywebsocket".',
    )

    parser.add_argument(
        "--wsurl",
        default="ws://127.0.0.1:9000",
        help="WebSocket URL (must suit the endpoint), e.g. ws://127.0.0.1:9000.",
    )

    parser.add_argument(
        "--web",
        default="tcp:8080",
        help='Web server endpoint descriptor, e.g. "tcp:8080".',
    )

    args = parser.parse_args()

    # start Twisted logging to stdout
    log.startLogging(sys.stdout)

    # we use an Autobahn utility to install the "best" available Twisted reactor
    from autobahn.twisted.choosereactor import install_reactor

    reactor = install_reactor()
    print("Running on reactor {}".format(reactor))

    # start a WebSocket server
    wsfactory = EchoServerFactory(args.wsurl)
    wsserver = serverFromString(reactor, args.websocket)
    wsserver.listen(wsfactory)

    # start a Web server
    if args.web != "":
        from twisted.web.server import Site
        from twisted.web.static import File

        webfactory = Site(File("."))
        webserver = serverFromString(reactor, args.web)
        webserver.listen(webfactory)

    # now enter the Twisted reactor loop
    reactor.run()
