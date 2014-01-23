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
   from twisted.internet.endpoints import clientFromString


   ## parse command line arguments
   ##
   parser = argparse.ArgumentParser()

   parser.add_argument("-d", "--debug", action = "store_true",
                       help = "Enable debug output.")

   parser.add_argument("-b", "--backend", action = "store_true",
                       help = "Start client providing application backend.")

   parser.add_argument("--websocket", default = "tcp:localhost:9000",
                       help = 'WebSocket client Twisted endpoint descriptor, e.g. "tcp:localhost:9000" or "unix:/tmp/mywebsocket".')

   parser.add_argument("--wsurl", default = "ws://localhost:9000",
                       help = 'WebSocket URL (must suit the endpoint), e.g. "ws://localhost:9000".')

   args = parser.parse_args()


   ## start Twisted logging to stdout
   ##
   log.startLogging(sys.stdout)


   ## we use an Autobahn utility to import the "best" available Twisted reactor
   ##
   from autobahn.twisted.choosereactor import install_reactor
   reactor = install_reactor()
   print("Running on reactor {}".format(reactor))


   from autobahn.wamp.protocol import WampAppFactory
   sessionFactory = WampAppFactory()

   if args.backend:
      from app import MyAppBackendSession
      sessionFactory.session = MyAppBackendSession
   else:
      from app import MyAppFrontendSession
      sessionFactory.session = MyAppFrontendSession

   ## run WAMP over WebSocket
   ##
   from autobahn.twisted.websocket import WampWebSocketClientFactory
   transportFactory = WampWebSocketClientFactory(sessionFactory, args.wsurl, debug = args.debug)
   transportFactory.setProtocolOptions(failByDrop = False)


   ## start a WebSocket client
   ##
   wsclient = clientFromString(reactor, args.websocket)
   wsclient.connect(transportFactory)


   ## now enter the Twisted reactor loop
   ##
   reactor.run()
