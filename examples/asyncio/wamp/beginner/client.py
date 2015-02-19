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

import sys

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

from autobahn.asyncio import wamp, websocket


class MyFrontendComponent(wamp.ApplicationSession):

    """
    Application code goes here. This is an example component that calls
    a remote procedure on a WAMP peer, subscribes to a topic to receive
    events, and then stops the world after some events.
    """

    def onConnect(self):
        self.join(u"realm1")

    @asyncio.coroutine
    def onJoin(self, details):

        # call a remote procedure
        ##
        try:
            now = yield from self.call(u'com.timeservice.now')
        except Exception as e:
            print("Error: {}".format(e))
        else:
            print("Current time from time service: {}".format(now))

        # subscribe to a topic
        ##
        self.received = 0

        def on_event(i):
            print("Got event: {}".format(i))
            self.received += 1
            if self.received > 5:
                self.leave()

        sub = yield from self.subscribe(on_event, u'com.myapp.topic1')
        print("Subscribed with subscription ID {}".format(sub.id))

    def onLeave(self, details):
        self.disconnect()

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == '__main__':

    # 1) create a WAMP application session factory
    session_factory = wamp.ApplicationSessionFactory()
    session_factory.session = MyFrontendComponent

    # 2) create a WAMP-over-WebSocket transport client factory
    transport_factory = websocket.WampWebSocketClientFactory(session_factory,
                                                             debug=False,
                                                             debug_wamp=False)

    # 3) start the client
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(transport_factory, '127.0.0.1', 8080)
    loop.run_until_complete(coro)

    # 4) now enter the asyncio event loop
    loop.run_forever()
    loop.close()
