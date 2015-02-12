###############################################################################
##
# Copyright 2012 Tavendo GmbH
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

import os
import pkg_resources

from twisted.python import log
from twisted.internet import reactor
from twisted.application import service

from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from autobahn.resource import WebSocketResource, \
    HTTPChannelHixie76Aware


class EchoServerProtocol(WebSocketServerProtocol):

    def onMessage(self, msg, binary):
        self.sendMessage(msg, binary)


class EchoService(service.Service):

    """
    WebSocket Echo service - this runs a Twisted Web site with a WebSocket
    echo server running under path "/ws".
    """

    def __init__(self, port=8080, debug=False):
        self.port = port
        self.debug = debug

    def startService(self):

        factory = WebSocketServerFactory("ws://localhost:%d" % self.port, debug=self.debug)

        factory.protocol = EchoServerProtocol
        factory.setProtocolOptions(allowHixie76=True)  # needed if Hixie76 is to be supported

        # FIXME: Site.start/stopFactory should start/stop factories wrapped as Resources
        factory.startFactory()

        resource = WebSocketResource(factory)

        # we server static files under "/" ..
        webdir = os.path.abspath(pkg_resources.resource_filename("echows", "web"))
        root = File(webdir)

        # and our WebSocket server under "/ws"
        root.putChild("ws", resource)

        # both under one Twisted Web Site
        site = Site(root)
        site.protocol = HTTPChannelHixie76Aware  # needed if Hixie76 is to be supported

        self.site = site
        self.factory = factory

        self.listener = reactor.listenTCP(self.port, site)

    def stopService(self):
        self.factory.stopFactory()
        self.site.stopFactory()
        self.listener.stopListening()
