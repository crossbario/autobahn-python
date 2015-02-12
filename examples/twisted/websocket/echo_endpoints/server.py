###############################################################################
##
# Copyright (C) 2013 Tavendo GmbH
##
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
##
# http://www.apache.org/licenses/LICENSE-2.0
##
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##
###############################################################################


from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol


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


if __name__ == '__main__':

    import sys
    import argparse

    from twisted.python import log
    from twisted.internet.endpoints import serverFromString

    # parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug output.")

    parser.add_argument("--websocket", default="tcp:9000",
                        help='WebSocket server Twisted endpoint descriptor, e.g. "tcp:9000" or "unix:/tmp/mywebsocket".')

    parser.add_argument("--wsurl", default="ws://localhost:9000",
                        help='WebSocket URL (must suit the endpoint), e.g. "ws://localhost:9000".')

    parser.add_argument("--web", default="tcp:8080",
                        help='Web server endpoint descriptor, e.g. "tcp:8080".')

    args = parser.parse_args()

    # start Twisted logging to stdout
    ##
    log.startLogging(sys.stdout)

    # we use an Autobahn utility to install the "best" available Twisted reactor
    ##
    from autobahn.choosereactor import install_reactor
    reactor = install_reactor()
    print("Running on reactor {}".format(reactor))

    # start a WebSocket server
    ##
    wsfactory = EchoServerFactory(args.wsurl, debug=args.debug)
    wsserver = serverFromString(reactor, args.websocket)
    wsserver.listen(wsfactory)

    # start a Web server
    ##
    if args.web != "":
        from twisted.web.server import Site
        from twisted.web.static import File

        webfactory = Site(File("."))
        webserver = serverFromString(reactor, args.web)
        webserver.listen(webfactory)

    # now enter the Twisted reactor loop
    ##
    reactor.run()
