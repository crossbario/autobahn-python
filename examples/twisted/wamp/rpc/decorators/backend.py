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

from os import environ
from twisted.internet.defer import inlineCallbacks
from twisted.python.failure import Failure

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner


class MyService1(object):
    @wamp.register(u'com.mathservice.add2')
    def add2(self, x, y):
        return x + y

    @wamp.register(u'com.mathservice.mul2')
    def mul2(self, x, y):
        return x * y


class Component(ApplicationSession):

    """
    An application component registering RPC endpoints using decorators.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")

        # to use this session to register all the @register decorated
        # methods, we call register with the object; so here we create
        # a MyService1 instance and register all the methods on it and
        # on ourselves

        results = []
        svc1 = MyService1()

        # register all @register-decorated methods from "svc1":
        res = yield self.register(svc1)
        results.extend(res)

        # register all our own @register-decorated methods:
        res = yield self.register(self)
        results.extend(res)

        for res in results:
            if isinstance(res, Failure):
                print("Failed to register procedure: {}".format(res.value))
            else:
                print("registration ID {}: {}".format(res.id, res.procedure))

    @wamp.register(u'com.mathservice.square2')
    def square2(self, x, y):
        return x * x + y * y

    @wamp.register(u'com.mathservice.div2')
    def div2(self, x, y):
        if y:
            return float(x) / float(y)
        else:
            return 0


if __name__ == '__main__':
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws"),
        u"crossbardemo",
    )
    runner.run(Component)
