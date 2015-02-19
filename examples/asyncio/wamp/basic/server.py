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

if __name__ == '__main__':

    import sys
    import argparse

    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        import trollius as asyncio

    # parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug output.")

    parser.add_argument("-c", "--component", type=str, default=None,
                        help="Start WAMP server with this application component, e.g. 'timeservice.TimeServiceBackend', or None.")

    parser.add_argument("-r", "--realm", type=str, default="realm1",
                        help="The WAMP realm to start the component in (if any).")

    parser.add_argument("--interface", type=str, default="127.0.0.1",
                        help='IP of interface to listen on.')

    parser.add_argument("--port", type=int, default=8080,
                        help='TCP port to listen on.')

    parser.add_argument("--transport", choices=['websocket', 'rawsocket-json', 'rawsocket-msgpack'], default="websocket",
                        help='WAMP transport type')

    args = parser.parse_args()

    # create a WAMP router factory
    ##
    from autobahn.asyncio.wamp import RouterFactory
    router_factory = RouterFactory()

    # create a WAMP router session factory
    ##
    from autobahn.asyncio.wamp import RouterSessionFactory
    session_factory = RouterSessionFactory(router_factory)

    # if asked to start an embedded application component ..
    ##
    if args.component:
        # dynamically load the application component ..
        ##
        import importlib
        c = args.component.split('.')
        mod, klass = '.'.join(c[:-1]), c[-1]
        app = importlib.import_module(mod)
        SessionKlass = getattr(app, klass)

        # .. and create and add an WAMP application session to
        # run next to the router
        ##
        from autobahn.wamp import types
        session_factory.add(SessionKlass(types.ComponentConfig(realm=args.realm)))

    if args.transport == "websocket":

        # create a WAMP-over-WebSocket transport server factory
        ##
        from autobahn.asyncio.websocket import WampWebSocketServerFactory
        transport_factory = WampWebSocketServerFactory(session_factory, debug_wamp=args.debug)
        transport_factory.setProtocolOptions(failByDrop=False)

    elif args.transport in ['rawsocket-json', 'rawsocket-msgpack']:

        # create a WAMP-over-RawSocket transport server factory
        ##
        if args.transport == 'rawsocket-msgpack':
            from autobahn.wamp.serializer import MsgPackSerializer
            serializer = MsgPackSerializer()
        elif args.transport == 'rawsocket-json':
            from autobahn.wamp.serializer import JsonSerializer
            serializer = JsonSerializer()
        else:
            raise Exception("should not arrive here")

        from autobahn.asyncio.rawsocket import WampRawSocketServerFactory
        transport_factory = WampRawSocketServerFactory(session_factory, serializer, debug=args.debug)

    else:
        raise Exception("should not arrive here")

    # start the server from an endpoint
    ##
    loop = asyncio.get_event_loop()
    coro = loop.create_server(transport_factory, args.interface, args.port)
    server = loop.run_until_complete(coro)

    try:
        # now enter the asyncio event loop
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
