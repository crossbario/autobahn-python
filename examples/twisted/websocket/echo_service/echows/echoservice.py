###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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

import os
import pkg_resources

from twisted.python import log
from twisted.internet import reactor
from twisted.application import service

from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol

from autobahn.resource import WebSocketResource


class EchoServerProtocol(WebSocketServerProtocol):

    def onMessage(self, msg, binary):
        self.sendMessage(msg, binary)


class EchoService(service.Service):
    """
    WebSocket Echo service - this runs a Twisted Web site with a WebSocket
    echo server running under path "/ws".
    """

    def __init__(self, port=8080):
        self.port = port

    def startService(self):

        factory = WebSocketServerFactory("ws://127.0.0.1:%d" % self.port)
        factory.protocol = EchoServerProtocol

        # FIXME: Site.start/stopFactory should start/stop factories wrapped as Resources
        factory.startFactory()

        resource = WebSocketResource(factory)

        # we server static files under "/" ..
        webdir = os.path.abspath(pkg_resources.resource_filename("echows", "web"))
        root = File(webdir)

        # and our WebSocket server under "/ws" (note that Twisted uses
        # bytes for URIs)
        root.putChild(b"ws", resource)

        # both under one Twisted Web Site
        site = Site(root)

        self.site = site
        self.factory = factory

        self.listener = reactor.listenTCP(self.port, site)

    def stopService(self):
        self.factory.stopFactory()
        self.site.stopFactory()
        self.listener.stopListening()
