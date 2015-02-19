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

from autobahn.twisted.util import sleep
from autobahn.twisted import wamp, rawsocket
from autobahn.wamp import types


class MyFrontendComponent(wamp.ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):

        def on_event(i):
            print("Got event: {}".format(i))

        yield self.subscribe(on_event, 'com.myapp.topic1')

        counter = 0
        while True:
            self.publish('com.myapp.topic1', counter, options=types.PublishOptions(excludeMe=False))
            counter += 1
            yield sleep(1)


if __name__ == '__main__':

    log.startLogging(sys.stdout)

    session_factory = wamp.ApplicationSessionFactory(config=types.ComponentConfig(realm="realm1"))
    session_factory.session = MyFrontendComponent

    from autobahn.wamp.serializer import *
    # serializer = JsonSerializer(batched = True)
    # serializer = MsgPackSerializer(batched = True)
    serializer = JsonSerializer()
    # serializer = MsgPackSerializer()

    transport_factory = rawsocket.WampRawSocketClientFactory(session_factory,
                                                             serializer=serializer, debug=True)

    client = clientFromString(reactor, "tcp:127.0.0.1:9000")
    client.connect(transport_factory)

    reactor.run()
