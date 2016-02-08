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

import shelve

from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession


class KeyValueStore(ApplicationSession):

    """
    Simple, persistent key-value store.
    """

    @inlineCallbacks
    def onJoin(self, details):
        self.store = shelve.open("keyvalue", flag='c', writeback=False)
        yield self.register(self)
        print("Ok, keyvalue-store procedures registered!")

    @wamp.register(u"com.example.keyvalue.set")
    def set(self, key=None, value=None):
        if key is not None:
            k = str(key)
            if value is not None:
                self.store[k] = value
            else:
                if k in self.store:
                    del self.store[k]
        else:
            self.store.clear()
        self.store.sync()

    @wamp.register(u"com.example.keyvalue.get")
    def get(self, key=None):
        if key is None:
            res = {}
            for key, value in self.store.items():
                res[key] = value
            return res
        else:
            return self.store.get(str(key), None)

    @wamp.register(u"com.example.keyvalue.keys")
    def keys(self):
        return self.store.keys()


if __name__ == '__main__':

    import sys
    import argparse

    # parse command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("--web", type=int, default=8080,
                        help='Web port to use for embedded Web server. Use 0 to disable.')

    parser.add_argument("--router", type=str, default=None,
                        help='If given, connect to this WAMP router. Else run an embedded router on 9000.')

    args = parser.parse_args()

    from twisted.python import log
    log.startLogging(sys.stdout)

    # import Twisted reactor
    from twisted.internet import reactor
    print("Using Twisted reactor {0}".format(reactor.__class__))

    # create embedded web server for static files
    if args.web:
        from twisted.web.server import Site
        from twisted.web.static import File
        reactor.listenTCP(args.web, Site(File(".")))

    # run WAMP application component
    from autobahn.twisted.wamp import ApplicationRunner
    router = args.router or u'ws://127.0.0.1:9000'

    runner = ApplicationRunner(router, u"realm1", standalone=not args.router)

    # start the component and the Twisted reactor ..
    runner.run(KeyValueStore)
