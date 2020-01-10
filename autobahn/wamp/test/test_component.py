###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
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

import os

if os.environ.get('USE_TWISTED', False):
    from autobahn.twisted.util import sleep
    from autobahn.twisted import wamp

    from twisted.trial import unittest
    from twisted.internet import defer
    from twisted.application import service

    class CaseComponent(wamp.ApplicationSession):
        """
        Application code goes here. This is an example component that calls
        a remote procedure on a WAMP peer, subscribes to a topic to receive
        events, and then stops the world after some events.
        """

        def __init__(self, config):
            wamp.ApplicationSession.__init__(self, config)
            self.test = config.extra['test']
            self.stop = False
            self._logline = 1
            self.finished = False

        def log(self, *args):
            if len(args) > 1:
                sargs = ", ".join(str(s) for s in args)
            elif len(args) == 1:
                sargs = args[0]
            else:
                sargs = "-"

            msg = '= : {0:>3} : {1:<20} : {2}'.format(self._logline, self.__class__.__name__, sargs)
            self._logline += 1
            print(msg)

        def finish(self):
            if not self.finished:
                self.test.deferred.callback(None)
                self.finished = True
            else:
                print("already finished")

    class Case1_Backend(CaseComponent):

        @defer.inlineCallbacks
        def onJoin(self, details):

            self.log("joined")

            def add2(x, y):
                self.log("add2 invoked: {0}, {1}".format(x, y))
                return x + y

            yield self.register(add2, 'com.mathservice.add2')
            self.log("add2 registered")

            self.finish()

    class Case1_Frontend(CaseComponent):

        @defer.inlineCallbacks
        def onJoin(self, details):

            self.log("joined")

            try:
                res = yield self.call('com.mathservice.add2', 2, 3)
            except Exception as e:
                self.log("call error: {0}".format(e))
            else:
                self.log("call result: {0}".format(res))

            self.finish()

    class Case2_Backend(CaseComponent):

        @defer.inlineCallbacks
        def onJoin(self, details):

            self.log("joined")

            def ping():
                self.log("ping() is invoked")
                return

            def add2(a, b):
                self.log("add2() is invoked", a, b)
                return a + b

            def stars(nick="somebody", stars=0):
                self.log("stars() is invoked", nick, stars)
                return "{0} starred {1}x".format(nick, stars)

            def orders(product, limit=5):
                self.log("orders() is invoked", product, limit)
                return ["Product {0}".format(i) for i in range(50)][:limit]

            def arglen(*args, **kwargs):
                self.log("arglen() is invoked", args, kwargs)
                return [len(args), len(kwargs)]

            yield self.register(ping, 'com.arguments.ping')
            yield self.register(add2, 'com.arguments.add2')
            yield self.register(stars, 'com.arguments.stars')
            yield self.register(orders, 'com.arguments.orders')
            yield self.register(arglen, 'com.arguments.arglen')

            self.log("procedures registered")

    class Case2_Frontend(CaseComponent):

        @defer.inlineCallbacks
        def onJoin(self, details):

            self.log("joined")

            yield sleep(1)

            yield self.call('com.arguments.ping')
            self.log("Pinged!")

            res = yield self.call('com.arguments.add2', 2, 3)
            self.log("Add2: {0}".format(res))

            starred = yield self.call('com.arguments.stars')
            self.log("Starred 1: {0}".format(starred))

            starred = yield self.call('com.arguments.stars', nick='Homer')
            self.log("Starred 2: {0}".format(starred))

            starred = yield self.call('com.arguments.stars', stars=5)
            self.log("Starred 3: {0}".format(starred))

            starred = yield self.call('com.arguments.stars', nick='Homer', stars=5)
            self.log("Starred 4: {0}".format(starred))

            orders = yield self.call('com.arguments.orders', 'coffee')
            self.log("Orders 1: {0}".format(orders))

            orders = yield self.call('com.arguments.orders', 'coffee', limit=10)
            self.log("Orders 2: {0}".format(orders))

            arglengths = yield self.call('com.arguments.arglen')
            self.log("Arglen 1: {0}".format(arglengths))

            arglengths = yield self.call('com.arguments.arglen', 1, 2, 3)
            self.log("Arglen 1: {0}".format(arglengths))

            arglengths = yield self.call('com.arguments.arglen', a=1, b=2, c=3)
            self.log("Arglen 2: {0}".format(arglengths))

            arglengths = yield self.call('com.arguments.arglen', 1, 2, 3, a=1, b=2, c=3)
            self.log("Arglen 3: {0}".format(arglengths))

            self.log("finishing")

            self.finish()

    class TestRpc(unittest.TestCase):

        if os.environ.get("WAMP_ROUTER_URL") is None:
            skip = ("Please provide WAMP_ROUTER_URL environment with url to "
                    "WAMP router to run WAMP integration tests")

        def setUp(self):
            self.url = os.environ.get("WAMP_ROUTER_URL")
            self.realm = "realm1"

        @defer.inlineCallbacks
        def runOneTest(self, components):
            self.deferred = defer.Deferred()
            app = service.MultiService()
            for component in components:
                c = wamp.Service(
                    url=self.url,
                    extra=dict(test=self),
                    realm=self.realm,
                    make=component,
                )
                c.setServiceParent(app)

            app.startService()
            yield self.deferred
            app.stopService()

        @defer.inlineCallbacks
        def test_case1(self):
            yield self.runOneTest([Case1_Backend, Case1_Frontend])

        @defer.inlineCallbacks
        def test_case2(self):
            yield self.runOneTest([Case2_Backend, Case2_Frontend])
