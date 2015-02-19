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

    parser.add_argument("-c", "--component", type=str,
                        help="Start WAMP client with this application component, e.g. 'timeservice.TimeServiceFrontend'")

    parser.add_argument("-r", "--realm", type=str, default="realm1",
                        help="The WAMP realm to start the component in (if any).")

    parser.add_argument("--host", type=str, default="127.0.0.1",
                        help='IP or hostname to connect to.')

    parser.add_argument("--port", type=int, default=8080,
                        help='TCP port to connect to.')

    parser.add_argument("--transport", choices=['websocket', 'rawsocket-json', 'rawsocket-msgpack'], default="websocket",
                        help='WAMP transport type')

    parser.add_argument("--url", type=str, default=None,
                        help='The WebSocket URL to connect to, e.g. ws://127.0.0.1:8080/ws.')

    args = parser.parse_args()

    # create a WAMP application session factory
    ##
    from autobahn.asyncio.wamp import ApplicationSessionFactory
    from autobahn.wamp import types
    session_factory = ApplicationSessionFactory(types.ComponentConfig(realm=args.realm))

    # dynamically load the application component ..
    ##
    import importlib
    c = args.component.split('.')
    mod, klass = '.'.join(c[:-1]), c[-1]
    app = importlib.import_module(mod)

    # .. and set the session class on the factory
    ##
    session_factory.session = getattr(app, klass)

    if args.transport == "websocket":

        # create a WAMP-over-WebSocket transport client factory
        ##
        from autobahn.asyncio.websocket import WampWebSocketClientFactory
        transport_factory = WampWebSocketClientFactory(session_factory, url=args.url, debug_wamp=args.debug)
        transport_factory.setProtocolOptions(failByDrop=False)

    elif args.transport in ['rawsocket-json', 'rawsocket-msgpack']:

        # create a WAMP-over-RawSocket transport client factory
        ##
        if args.transport == 'rawsocket-msgpack':
            from autobahn.wamp.serializer import MsgPackSerializer
            serializer = MsgPackSerializer()
        elif args.transport == 'rawsocket-json':
            from autobahn.wamp.serializer import JsonSerializer
            serializer = JsonSerializer()
        else:
            raise Exception("should not arrive here")

        from autobahn.asyncio.rawsocket import WampRawSocketClientFactory
        transport_factory = WampRawSocketClientFactory(session_factory, serializer, debug=args.debug)

    else:
        raise Exception("logic error")

    # start the client
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(transport_factory, args.host, args.port)
    loop.run_until_complete(coro)

    # now enter the asyncio event loop
    loop.run_forever()
    loop.close()
