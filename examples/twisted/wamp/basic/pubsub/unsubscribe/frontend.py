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

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession


class Component(ApplicationSession):

    """
    An application component that subscribes and receives events.
    After receiving 5 events, it unsubscribes, sleeps and then
    resubscribes for another run. Then it stops.
    """

    @inlineCallbacks
    def test(self):

        self.received = 0

        @inlineCallbacks
        def on_event(i):
            print("Got event: {}".format(i))
            self.received += 1
            if self.received > 5:
                self.runs += 1
                if self.runs > 1:
                    self.leave()
                else:
                    yield self.subscription.unsubscribe()
                    print("Unsubscribed .. continue in 2s ..")
                    reactor.callLater(2, self.test)

        self.subscription = yield self.subscribe(on_event, 'com.myapp.topic1')
        print("Subscribed with subscription ID {}".format(self.subscription.id))

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")

        self.runs = 0
        yield self.test()

    def onDisconnect(self):
        print("disconnected")
        reactor.stop()


if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
