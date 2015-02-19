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
