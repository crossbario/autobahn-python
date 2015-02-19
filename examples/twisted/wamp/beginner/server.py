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
import six
import datetime

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import serverFromString

from autobahn.wamp import types
from autobahn.twisted.util import sleep
from autobahn.twisted import wamp, websocket


class MyBackendComponent(wamp.ApplicationSession):

    """
    Application code goes here. This is an example component that provides
    a simple procedure which can be called remotely from any WAMP peer.
    It also publishes an event every second to some topic.
    """

    @inlineCallbacks
    def onJoin(self, details):

        # register a procedure for remote calling
        ##
        def utcnow():
            print("Someone is calling me;)")
            now = datetime.datetime.utcnow()
            return six.u(now.strftime("%Y-%m-%dT%H:%M:%SZ"))

        reg = yield self.register(utcnow, u'com.timeservice.now')
        print("Registered procedure with ID {}".format(reg.id))

        # publish events to a topic
        ##
        counter = 0
        while True:
            self.publish(u'com.myapp.topic1', counter)
            print("Published event.")
            counter += 1
            yield sleep(1)


if __name__ == '__main__':

    # 0) start logging to console
    log.startLogging(sys.stdout)

    # 1) create a WAMP router factory
    router_factory = wamp.RouterFactory()

    # 2) create a WAMP router session factory
    session_factory = wamp.RouterSessionFactory(router_factory)

    # 3) Optionally, add embedded WAMP application sessions to the router
    component_config = types.ComponentConfig(realm="realm1")
    component_session = MyBackendComponent(component_config)
    session_factory.add(component_session)

    # 4) create a WAMP-over-WebSocket transport server factory
    transport_factory = websocket.WampWebSocketServerFactory(session_factory,
                                                             debug=False,
                                                             debug_wamp=False)

    # 5) start the server from a Twisted endpoint
    server = serverFromString(reactor, "tcp:8080")
    server.listen(transport_factory)

    # 6) now enter the Twisted reactor loop
    reactor.run()
