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
from twisted.internet.task import LoopingCall
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
# or: from autobahn.asyncio.wamp import ApplicationSession


class MyComponent(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):
        # publish an event every second. The event payloads can be
        # anything JSON- and msgpack- serializable
        def publish():
            return self.publish(u'com.myapp.hello', 'Hello, world!')
        LoopingCall(publish).start(1)

        # a remote procedure; see frontend.py for a Python front-end
        # that calls this. Any language with WAMP bindings can now call
        # this procedure if its connected to the same router and realm.
        def add2(x, y):
            return x + y
        yield self.register(add2, u'com.myapp.add2')


if __name__ == '__main__':
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws"),
        u"crossbardemo",
    )
    runner.run(MyComponent)
