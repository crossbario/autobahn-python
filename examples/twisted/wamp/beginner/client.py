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

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import clientFromString

from autobahn.twisted import wamp, websocket
from autobahn.wamp import types


class MyFrontendComponent(wamp.ApplicationSession):

    """
    Application code goes here. This is an example component that calls
    a remote procedure on a WAMP peer, subscribes to a topic to receive
    events, and then stops the world after some events.
    """

    @inlineCallbacks
    def onJoin(self, details):

        # call a remote procedure
        #
        try:
            now = yield self.call(u'com.timeservice.now')
        except Exception as e:
            print("Error: {}".format(e))
        else:
            print("Current time from time service: {}".format(now))

        # subscribe to a topic
        #
        self.received = 0

        def on_event(i):
            print("Got event: {}".format(i))
            self.received += 1
            if self.received > 5:
                self.leave()

        sub = yield self.subscribe(on_event, u'com.myapp.topic1')
        print("Subscribed with subscription ID {}".format(sub.id))

    def onDisconnect(self):
        reactor.stop()


if __name__ == '__main__':

    # 0) start logging to console
    log.startLogging(sys.stdout)

    # 1) create a WAMP application session factory
    component_config = types.ComponentConfig(realm="realm1")
    session_factory = wamp.ApplicationSessionFactory(config=component_config)
    session_factory.session = MyFrontendComponent

    # optional: use specific set of serializers
    if False:
        serializers = None
    else:
        from autobahn.wamp.serializer import *
        serializers = []
        # serializers.append(JsonSerializer(batched = True))
        # serializers.append(MsgPackSerializer(batched = True))
        serializers.append(JsonSerializer())
        # serializers.append(MsgPackSerializer())

    # 2) create a WAMP-over-WebSocket transport client factory
    transport_factory = websocket.WampWebSocketClientFactory(session_factory,
                                                             serializers=serializers, debug=False, debug_wamp=False)

    # 3) start the client from a Twisted endpoint
    client = clientFromString(reactor, "tcp:127.0.0.1:8080")
    client.connect(transport_factory)

    # 4) now enter the Twisted reactor loop
    reactor.run()
