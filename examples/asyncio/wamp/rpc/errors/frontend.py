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

from os import environ
import math

import asyncio
from autobahn import wamp
from autobahn.wamp.exception import ApplicationError
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


@wamp.error("com.myapp.error1")
class AppError1(Exception):
    """
    An application specific exception that is decorated with a WAMP URI,
    and hence can be automapped by Autobahn.
    """


class Component(ApplicationSession):
    """
    Example WAMP application frontend that catches exceptions.
    """

    async def onJoin(self, details):

        # catching standard exceptions
        ##
        for x in [2, 0, -2]:
            try:
                res = await self.call("com.myapp.sqrt", x)
            except Exception as e:
                print("Error: {} {}".format(e, e.args))
            else:
                print("Result: {}".format(res))

        # catching WAMP application exceptions
        ##
        for name in ["foo", "a", "*" * 11, "Hello"]:
            try:
                res = await self.call("com.myapp.checkname", name)
            except ApplicationError as e:
                print("Error: {} {} {} {}".format(e, e.error, e.args, e.kwargs))
            else:
                print("Result: {}".format(res))

        # defining and automapping WAMP application exceptions
        ##
        self.define(AppError1)

        try:
            await self.call("com.myapp.compare", 3, 17)
        except AppError1 as e:
            print("Compare Error: {}".format(e))

        await self.leave()

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == "__main__":
    url = environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/ws")
    realm = "crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
