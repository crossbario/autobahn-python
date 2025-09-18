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

from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession


class Component(ApplicationSession):
    """
    An application component calling the different backend procedures.
    """

    async def onJoin(self, details):
        await self.call("com.arguments.ping")
        print("Pinged!")

        res = await self.call("com.arguments.add2", 2, 3)
        print("Add2: {}".format(res))

        starred = await self.call("com.arguments.stars")
        print("Starred 1: {}".format(starred))

        starred = await self.call("com.arguments.stars", nick="Homer")
        print("Starred 2: {}".format(starred))

        starred = await self.call("com.arguments.stars", stars=5)
        print("Starred 3: {}".format(starred))

        starred = await self.call("com.arguments.stars", nick="Homer", stars=5)
        print("Starred 4: {}".format(starred))

        orders = await self.call("com.arguments.orders", "coffee")
        print("Orders 1: {}".format(orders))

        orders = await self.call("com.arguments.orders", "coffee", limit=10)
        print("Orders 2: {}".format(orders))

        arglengths = await self.call("com.arguments.arglen")
        print("Arglen 1: {}".format(arglengths))

        arglengths = await self.call("com.arguments.arglen", 1, 2, 3)
        print("Arglen 1: {}".format(arglengths))

        arglengths = await self.call("com.arguments.arglen", a=1, b=2, c=3)
        print("Arglen 2: {}".format(arglengths))

        arglengths = await self.call("com.arguments.arglen", 1, 2, 3, a=1, b=2, c=3)
        print("Arglen 3: {}".format(arglengths))

        self.leave()

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == "__main__":
    url = environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/ws")
    realm = "crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
