###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################


if __name__ == '__main__':

   import sys, argparse

   from twisted.python import log
   from twisted.internet.endpoints import serverFromString


   ## parse command line arguments
   ##
   parser = argparse.ArgumentParser()

   parser.add_argument("-d", "--debug", action = "store_true",
                       help = "Enable debug output.")

   parser.add_argument("-c", "--component", type = str, default = None,
                       help = "Start WAMP-WebSocket server with this application component, e.g. 'timeservice.TimeServiceBackend', or None.")

   parser.add_argument("--websocket", type = str, default = "tcp:9000",
                       help = 'WebSocket server Twisted endpoint descriptor, e.g. "tcp:9000" or "unix:/tmp/mywebsocket".')

   parser.add_argument("--wsurl", type = str, default = "ws://localhost:9000",
                       help = 'WebSocket URL (must suit the endpoint), e.g. "ws://localhost:9000".')

   args = parser.parse_args()


   ## start Twisted logging to stdout
   ##
   if args.debug:
      log.startLogging(sys.stdout)


   ## we use an Autobahn utility to install the "best" available Twisted reactor
   ##
   from autobahn.twisted.choosereactor import install_reactor
   reactor = install_reactor()
   if args.debug:
      print("Running on reactor {}".format(reactor))


   ## create a WAMP router session factory
   ##
   from autobahn.twisted.wamp import WampRouterFactory
   session_factory = WampRouterFactory()


   ## if asked to start an embedded application component ..
   ##
   if args.component:
      ## dynamically load the application component ..
      ##
      import importlib
      c = args.component.split('.')
      mod, klass = '.'.join(c[:-1]), c[-1]
      app = importlib.import_module(mod)
      SessionKlass = getattr(app, klass)

      ## .. and create and add an app WAMP session to the router
      ##
      session_factory.add(SessionKlass())


   ## run WAMP over WebSocket
   ##
   from autobahn.twisted.websocket import WampWebSocketServerFactory
   transport_factory = WampWebSocketServerFactory(session_factory, args.wsurl, debug = args.debug)
   transport_factory.setProtocolOptions(failByDrop = False)


   ## start the WebSocket server from an endpoint
   ##
   server = serverFromString(reactor, args.websocket)
   server.listen(transport_factory)


   ## now enter the Twisted reactor loop
   ##
   reactor.run()
