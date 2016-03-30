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
    Example WAMP application backend that raised exceptions.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")

        # raising standard exceptions
        ##
        def sqrt(x):
            if x == 0:
                raise Exception("don't ask foolish questions;)")
            else:
                # this also will raise, if x < 0
                return math.sqrt(x)

        yield self.register(sqrt, u'com.myapp.sqrt')

        # raising WAMP application exceptions
        ##
        def checkname(name):
            if name in ['foo', 'bar']:
                raise ApplicationError(u"com.myapp.error.reserved")

            if name.lower() != name.upper():
                # forward positional arguments in exceptions
                raise ApplicationError(u"com.myapp.error.mixed_case", name.lower(), name.upper())

            if len(name) < 3 or len(name) > 10:
                # forward keyword arguments in exceptions
                raise ApplicationError(u"com.myapp.error.invalid_length", min=3, max=10)

        yield self.register(checkname, u'com.myapp.checkname')

        # defining and automapping WAMP application exceptions
        ##
        self.define(AppError1)

        def compare(a, b):
            if a < b:
                raise AppError1(b - a)

        yield self.register(compare, u'com.myapp.compare')

        print("procedures registered")


if __name__ == '__main__':
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws"),
        u"crossbardemo",
    )
    runner.run(Component)
