###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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

import asyncio
from os import environ

from autobahn import wamp
from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession


class Component(ApplicationSession):
    """
    An application component that subscribes and receives events, and
    stop after having received 5 events.
    """

    async def onJoin(self, details):
        self.received = 0

        # subscribe all methods on this object decorated with "@wamp.subscribe"
        # as PubSub event handlers
        results = await self.subscribe(self)
        for res in results:
            if isinstance(res, wamp.protocol.Subscription):
                # res is an Subscription instance
                print("Ok, subscribed handler with subscription ID {}".format(res.id))
            else:
                # res is an Failure instance
                print("Failed to subscribe handler: {}".format(res))

    @wamp.subscribe("com.myapp.topic1")
    def onEvent1(self, i):
        print("Got event on topic1: {}".format(i))
        self.received += 1
        if self.received > 5:
            self.leave()

    @wamp.subscribe("com.myapp.topic2")
    def onEvent2(self, msg):
        print("Got event on topic2: {}".format(msg))

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == "__main__":
    url = environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/ws")
    realm = "crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
