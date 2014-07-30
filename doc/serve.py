###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
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

if __name__ == "__main__":

   import sys
   import argparse
   import mimetypes

   from twisted.python import log
   from twisted.internet import reactor
   from twisted.web.server import Site
   from twisted.web.static import File
   from twisted.internet.endpoints import serverFromString

   mimetypes.add_type('image/svg+xml', '.svg')
   mimetypes.add_type('text/javascript', '.jgz')

   parser = argparse.ArgumentParser()

   parser.add_argument("--root", type = str, default = ".",
                       help = 'Web document root directory')

   parser.add_argument("--endpoint", type = str, default = "tcp:8080",
                       help = 'Twisted server endpoint descriptor, e.g. "tcp:8080" or "unix:/tmp/mywebsocket".')

   parser.add_argument("-s", "--silence", action = "store_true",
                       help = "Disable access logging.")

   args = parser.parse_args()
   log.startLogging(sys.stdout)

   factory = Site(File(args.root))
   if args.silence:
      factory.log = lambda _: None
      factory.noisy = False

   server = serverFromString(reactor, args.endpoint)
   server.listen(factory)

   reactor.run()
