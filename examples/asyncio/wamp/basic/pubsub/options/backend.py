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

from autobahn.wamp.types import PublishOptions, EventDetails, SubscribeOptions
from autobahn.asyncio.wamp import ApplicationSession


class Component(ApplicationSession):

    """
    An application component that publishes an event every second.
    """

    @asyncio.coroutine
    def onJoin(self, details):

        def on_event(i):
            print("Got event: {}".format(i))

        yield from self.subscribe(on_event, 'com.myapp.topic1')

        counter = 0
        while True:
            publication = yield from self.publish('com.myapp.topic1', counter,
                                                  options=PublishOptions(acknowledge=True, discloseMe=True, excludeMe=False))
            print("Event published with publication ID {}".format(publication.id))
            counter += 1
            yield from asyncio.sleep(1)
