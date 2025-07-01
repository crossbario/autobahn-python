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

import sys

from autobahn.twisted.resource import WebSocketResource
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import Data


class Echo1ServerProtocol(WebSocketServerProtocol):
    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = "Echo 1 - {}".format(payload.decode("utf8"))
            print(msg)
            self.sendMessage(msg.encode("utf8"))


class Echo2ServerProtocol(WebSocketServerProtocol):
    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = "Echo 2 - {}".format(payload.decode("utf8"))
            print(msg)
            self.sendMessage(msg.encode("utf8"))


if __name__ == "__main__":
    log.startLogging(sys.stdout)

    factory1 = WebSocketServerFactory()
    factory1.protocol = Echo1ServerProtocol
    factory1.startFactory()  # when wrapped as a Twisted Web resource, start the underlying factory manually
    resource1 = WebSocketResource(factory1)

    factory2 = WebSocketServerFactory()
    factory2.protocol = Echo2ServerProtocol
    factory2.startFactory()  # when wrapped as a Twisted Web resource, start the underlying factory manually
    resource2 = WebSocketResource(factory2)

    # Establish a dummy root resource
    root = Data("", "text/plain")

    # and our WebSocket servers under different paths .. (note that
    # Twisted uses bytes for URIs)
    root.putChild(b"echo1", resource1)
    root.putChild(b"echo2", resource2)

    # both under one Twisted Web Site
    site = Site(root)
    reactor.listenTCP(9000, site)

    reactor.run()
