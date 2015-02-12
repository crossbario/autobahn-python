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
