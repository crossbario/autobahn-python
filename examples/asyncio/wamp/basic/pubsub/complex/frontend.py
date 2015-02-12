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

import random

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

from autobahn.wamp.types import SubscribeOptions
from autobahn.asyncio.wamp import ApplicationSession


class Component(ApplicationSession):

    """
    An application component that subscribes and receives events
    of no payload and of complex payload, and stops after 5 seconds.
    """

    @asyncio.coroutine
    def onJoin(self, details):

        self.received = 0

        def on_heartbeat(details=None):
            print("Got heartbeat (publication ID {})".format(details.publication))

        yield from self.subscribe(on_heartbeat, 'com.myapp.heartbeat', options=SubscribeOptions(details_arg='details'))

        def on_topic2(a, b, c=None, d=None):
            print("Got event: {} {} {} {}".format(a, b, c, d))

        yield from self.subscribe(on_topic2, 'com.myapp.topic2')

        asyncio.get_event_loop().call_later(5, self.leave)

    def onDisconnect(self):
        asyncio.get_event_loop().stop()
