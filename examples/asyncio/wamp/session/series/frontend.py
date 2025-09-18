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
import datetime

from autobahn.asyncio.wamp import ApplicationSession


class Component(ApplicationSession):
    """
    An application component using the time service
    during 3 subsequent WAMP sessions, while the
    underlying transport continues to exist.
    """

    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        self.count = 0

    async def onJoin(self, details):
        print("Realm joined (WAMP session started).")

        try:
            now = await self.call("com.timeservice.now")
        except Exception as e:
            print("Error: {}".format(e))
        else:
            print("Current time from time service: {}".format(now))

        self.leave()

    def onLeave(self, details):
        print("Realm left (WAMP session ended).")
        self.count += 1
        if self.count < 3:
            self.join("realm1")
        else:
            self.disconnect()

    def onDisconnect(self):
        print("Transport disconnected.")
        asyncio.get_event_loop().stop()
