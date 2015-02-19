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

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

from autobahn.asyncio.wamp import ApplicationSession


class Component(ApplicationSession):

    """
    An application component that subscribes and receives events.
    After receiving 5 events, it unsubscribes, sleeps and then
    resubscribes for another run. Then it stops.
    """

    @asyncio.coroutine
    def test(self):

        self.received = 0

        # @asyncio.coroutine
        def on_event(i):
            print("Got event: {}".format(i))
            self.received += 1
            if self.received > 5:
                self.runs += 1
                if self.runs > 1:
                    self.leave()
                else:
                    self.subscription.unsubscribe()
                    # yield from self.subscription.unsubscribe()
                    print("Unsubscribed .. continue in 2s ..")

                    # FIXME
                    asyncio.get_event_loop().call_later(2, self.test)

        self.subscription = yield from self.subscribe(on_event, 'com.myapp.topic1')
        print("Subscribed with subscription ID {}".format(self.subscription.id))

    @asyncio.coroutine
    def onJoin(self, details):

        self.runs = 0
        yield from self.test()

    def onDisconnect(self):
        asyncio.get_event_loop().stop()
