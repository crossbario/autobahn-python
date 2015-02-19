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
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.wamp import types
from autobahn.twisted.util import sleep

from autobahn.twisted import wamp, websocket
from autobahn.twisted.resource import WebSocketResource
from autobahn.twisted.longpoll import WampLongPollResource


class MyBackendComponent(wamp.ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):

        counter = 0
        while True:
            self.publish(u'com.myapp.topic1', counter)
            print("Published event.")
            counter += 1
            yield sleep(2)


if __name__ == '__main__':

    log.startLogging(sys.stdout)

    router_factory = wamp.RouterFactory()
    session_factory = wamp.RouterSessionFactory(router_factory)

    component_config = types.ComponentConfig(realm="realm1")
    component_session = MyBackendComponent(component_config)
    session_factory.add(component_session)

    ws_factory = websocket.WampWebSocketServerFactory(session_factory,
                                                      debug=False,
                                                      debug_wamp=False)
    ws_factory.startFactory()

    ws_resource = WebSocketResource(ws_factory)
    lp_resource = WampLongPollResource(session_factory, debug=True, debug_transport_id="kjmd3sBLOUnb3Fyr")

    root = File(".")
    root.putChild("ws", ws_resource)
    root.putChild("lp", lp_resource)

    web_factory = Site(root)
    web_factory.noisy = False

    server = serverFromString(reactor, "tcp:8080")
    server.listen(web_factory)

    reactor.run()
