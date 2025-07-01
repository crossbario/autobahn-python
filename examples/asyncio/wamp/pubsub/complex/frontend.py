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
import random
from os import environ

from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession
from autobahn.wamp.types import SubscribeOptions


class Component(ApplicationSession):
    """
    An application component that subscribes and receives events of no
    payload and of complex payload, and stops after 5 seconds.
    """

    async def onJoin(self, details):
        self.received = 0

        def on_heartbeat(details=None):
            print("Got heartbeat (publication ID {})".format(details.publication))

        await self.subscribe(
            on_heartbeat,
            "com.myapp.heartbeat",
            options=SubscribeOptions(details_arg="details"),
        )

        def on_topic2(a, b, c=None, d=None):
            print("Got event: {} {} {} {}".format(a, b, c, d))

        await self.subscribe(on_topic2, "com.myapp.topic2")
        asyncio.get_event_loop().call_later(5, self.leave)

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == "__main__":
    url = environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/ws")
    realm = "crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
