###############################################################################
##
# Copyright (C) 2014 Tavendo GmbH
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

from __future__ import absolute_import
from __future__ import print_function
try:
    from twisted.trial import unittest
except ImportError:
    unittest = None

import os

if unittest is not None:
    from autobahn.twisted.util import sleep
    from autobahn.twisted import wamp

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

            msg = u'= : {0:>3} : {1:<20} : {2}'.format(self._logline, self.__class__.__name__, sargs)
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
                return u"{0} starred {1}x".format(nick, stars)

            def orders(product, limit=5):
                self.log("orders() is invoked", product, limit)
                return [u"Product {0}".format(i) for i in range(50)][:limit]

            def arglen(*args, **kwargs):
                self.log("arglen() is invoked", args, kwargs)
                return [len(args), len(kwargs)]

            yield self.register(ping, u'com.arguments.ping')
            yield self.register(add2, u'com.arguments.add2')
            yield self.register(stars, u'com.arguments.stars')
            yield self.register(orders, u'com.arguments.orders')
            yield self.register(arglen, u'com.arguments.arglen')

            self.log("procedures registered")

    class Case2_Frontend(CaseComponent):
        test_running = False

        @defer.inlineCallbacks
        def onJoin(self, details):
            if self.test_running:
                return

            self.test_running = True
            self.log("joined")

            yield sleep(1)

            yield self.call(u'com.arguments.ping')
            self.log("Pinged!")

            res = yield self.call(u'com.arguments.add2', 2, 3)
            self.log("Add2: {0}".format(res))

            starred = yield self.call(u'com.arguments.stars')
            self.log("Starred 1: {0}".format(starred))

            starred = yield self.call(u'com.arguments.stars', nick=u'Homer')
            self.log("Starred 2: {0}".format(starred))

            starred = yield self.call(u'com.arguments.stars', stars=5)
            self.log("Starred 3: {0}".format(starred))

            starred = yield self.call(u'com.arguments.stars', nick=u'Homer', stars=5)
            self.log("Starred 4: {0}".format(starred))

            orders = yield self.call(u'com.arguments.orders', u'coffee')
            self.log("Orders 1: {0}".format(orders))

            orders = yield self.call(u'com.arguments.orders', u'coffee', limit=10)
            self.log("Orders 2: {0}".format(orders))

            arglengths = yield self.call(u'com.arguments.arglen')
            self.log("Arglen 1: {0}".format(arglengths))

            arglengths = yield self.call(u'com.arguments.arglen', 1, 2, 3)
            self.log("Arglen 1: {0}".format(arglengths))

            arglengths = yield self.call(u'com.arguments.arglen', a=1, b=2, c=3)
            self.log("Arglen 2: {0}".format(arglengths))

            arglengths = yield self.call(u'com.arguments.arglen', 1, 2, 3, a=1, b=2, c=3)
            self.log("Arglen 3: {0}".format(arglengths))

            while os.environ.get("TEST_DISCONNECTION", False):
                try:
                    arglengths = yield self.call(u'com.arguments.arglen', 1, 2, 3, a=1, b=2, c=3)
                except Exception as e:
                    print(e)
                self.log("Arglen 3: {0}".format(arglengths))
                yield sleep(1)

            self.log("finishing")

            self.finish()

    class TestRpc(unittest.TestCase):

        def setUp(self):
            self.debug = False
            self.url = os.environ.get("WAMP_ROUTER_URL")
            self.realm = u"realm1"
            if self.url is None:
                raise unittest.SkipTest("Please provide WAMP_ROUTER_URL environment with url to wamp router to run wamp integration tests")

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
                    debug=bool(os.environ.get('debug_websocket', False)),
                    debug_wamp=bool(os.environ.get('debug_lowlevel', False)),
                    debug_app=bool(os.environ.get('debug_app', False))
                )
                c.setServiceParent(app)

            app.startService()
            yield self.deferred
            yield app.stopService()

        @defer.inlineCallbacks
        def test_case1(self):
            yield self.runOneTest([Case1_Backend, Case1_Frontend])

        @defer.inlineCallbacks
        def test_case2(self):
            yield self.runOneTest([Case2_Backend, Case2_Frontend])
