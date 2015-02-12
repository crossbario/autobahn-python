###############################################################################
##
# Copyright (C) 2014 Tavendo GmbH
##
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
##
# http://www.apache.org/licenses/LICENSE-2.0
##
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##
###############################################################################

import datetime

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

from autobahn import wamp
from autobahn.asyncio.wamp import ApplicationSession


class Component(ApplicationSession):

    """
    An application component registering RPC endpoints using decorators.
    """

    @asyncio.coroutine
    def onJoin(self, details):

        # register all methods on this object decorated with "@wamp.register"
        # as a RPC endpoint
        ##
        results = yield from self.register(self)
        for res in results:
            if isinstance(res, wamp.protocol.Registration):
                # res is an Registration instance
                print("Ok, registered procedure with registration ID {}".format(res.id))
            else:
                # res is an Failure instance
                print("Failed to register procedure: {}".format(res))

    @wamp.register('com.mathservice.add2')
    def add2(self, x, y):
        return x + y

    @wamp.register('com.mathservice.mul2')
    def mul2(self, x, y):
        return x * y

    @wamp.register('com.mathservice.div2')
    def square(self, x, y):
        if y:
            return float(x) / float(y)
        else:
            return 0
