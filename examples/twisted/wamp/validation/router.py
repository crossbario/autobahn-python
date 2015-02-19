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

from autobahn.wamp.exception import ApplicationError
from autobahn.twisted.wamp import Router


class MyRouter(Router):

    def validate(self, payload_type, uri, args, kwargs):
        print("MyRouter.validate: {} {} {} {}".format(payload_type, uri, args, kwargs))

        if payload_type == 'event' and uri == 'com.myapp.topic1':
            if len(args) == 1 and isinstance(args[0], int) and args[0] % 2 == 0 and kwargs is None:
                print("event payload validated for {}".format(uri))
            else:
                raise ApplicationError(ApplicationError.INVALID_ARGUMENT, "invalid event payload for topic {} - must be a single integer".format(uri))


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

    parser.add_argument("--endpoint", type=str, default="tcp:8080",
                        help='Twisted server endpoint descriptor, e.g. "tcp:8080" or "unix:/tmp/mywebsocket".')

    args = parser.parse_args()
    log.startLogging(sys.stdout)

    # we use an Autobahn utility to install the "best" available Twisted reactor
    ##
    from autobahn.twisted.choosereactor import install_reactor
    reactor = install_reactor()
    print("Running on reactor {}".format(reactor))

    # create a WAMP router factory
    ##
    from autobahn.twisted.wamp import RouterFactory
    router_factory = RouterFactory()
    router_factory.router = MyRouter

    # create a WAMP router session factory
    ##
    from autobahn.twisted.wamp import RouterSessionFactory
    session_factory = RouterSessionFactory(router_factory)

    # create a WAMP-over-WebSocket transport server factory
    ##
    from autobahn.twisted.websocket import WampWebSocketServerFactory
    transport_factory = WampWebSocketServerFactory(session_factory, debug=args.debug)
    transport_factory.setProtocolOptions(failByDrop=False)

    # start the server from an endpoint
    ##
    server = serverFromString(reactor, args.endpoint)
    server.listen(transport_factory)

    # now enter the Twisted reactor loop
    ##
    reactor.run()
