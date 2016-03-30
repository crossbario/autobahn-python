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

import math
from os import environ

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.wamp.exception import ApplicationError
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner


@wamp.error(u"com.myapp.error1")
class AppError1(Exception):
    """
    An application specific exception that is decorated with a WAMP URI,
    and hence can be automapped by Autobahn.
    """


class Component(ApplicationSession):
    """
    Example WAMP application frontend that catches exceptions.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")

        # catching standard exceptions
        ##
        for x in [2, 0, -2]:
            try:
                res = yield self.call(u'com.myapp.sqrt', x)
            except Exception as e:
                print("Error: {} {}".format(e, e.args))
            else:
                print("Result: {}".format(res))

        # catching WAMP application exceptions
        ##
        for name in ['foo', 'a', '*' * 11, 'Hello']:
            try:
                res = yield self.call(u'com.myapp.checkname', name)
            except ApplicationError as e:
                print("Error: {} {} {} {}".format(e, e.error, e.args, e.kwargs))
            else:
                print("Result: {}".format(res))

        # defining and automapping WAMP application exceptions
        ##
        self.define(AppError1)

        try:
            yield self.call(u'com.myapp.compare', 3, 17)
        except AppError1 as e:
            print("Compare Error: {}".format(e))

        print("Exiting; we received only errors we expected.")
        self.leave()

    def onDisconnect(self):
        print("disconnected")
        reactor.stop()


if __name__ == '__main__':
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws"),
        u"crossbardemo",
    )
    runner.run(Component)
