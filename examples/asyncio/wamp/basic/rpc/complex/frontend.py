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

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

from autobahn.wamp.types import CallResult
from autobahn.asyncio.wamp import ApplicationSession


class Component(ApplicationSession):

    """
    Application component that calls procedures which
    produce complex results and showing how to access those.
    """

    @asyncio.coroutine
    def onJoin(self, details):

        res = yield from self.call('com.myapp.add_complex', 2, 3, 4, 5)
        print("Result: {} + {}i".format(res.kwresults['c'], res.kwresults['ci']))

        res = yield from self.call('com.myapp.split_name', 'Homer Simpson')
        print("Forname: {}, Surname: {}".format(res.results[0], res.results[1]))

        self.leave()

    def onDisconnect(self):
        asyncio.get_event_loop().stop()
