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

import time
from os import environ
import sys

from twisted.internet import reactor
from twisted.internet.defer import DeferredList

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.util import get_clock


class Component(ApplicationSession):
    """
    An application component using the time service.
    """

    def onJoin(self, details):
        print("session attached")

        def got(res, started, msg):
            duration = 1000. * (get_clock() - started)
            print("{}: {} in {}".format(msg, res, duration))

        t1 = get_clock()
        d1 = self.call(u'com.math.slowsquare', 3)
        d1.addCallback(got, t1, "Slow Square")

        t2 = get_clock()
        d2 = self.call(u'com.math.square', 3)
        d2.addCallback(got, t2, "Quick Square")

        def done(_):
            print("All finished.")
            self.leave()

        DeferredList([d1, d2]).addBoth(done)

    def onDisconnect(self):
        print("disconnected")
        reactor.stop()


if __name__ == '__main__':
    import six
    url = environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = u"crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
