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

import txaio

from autobahn.twisted.websocket import (
    WebSocketServerFactory,
    WebSocketServerProtocol,
    listenWS,
)
from twisted.internet import reactor, ssl
from twisted.web.server import Site
from twisted.web.static import File


class EchoServerProtocol(WebSocketServerProtocol):
    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)


if __name__ == "__main__":
    txaio.start_logging(level="debug")

    # SSL server context: load server key and certificate
    # We use this for both WS and Web!
    contextFactory = ssl.DefaultOpenSSLContextFactory(
        "keys/server.key", "keys/server.crt"
    )

    factory = WebSocketServerFactory("wss://127.0.0.1:9000")
    # by default, allowedOrigins is "*" and will work fine out of the
    # box, but we can do better and be more-explicit about what we
    # allow. We are serving the Web content on 8080, but our WebSocket
    # listener is on 9000 so the Origin sent by the browser will be
    # from port 8080...
    factory.setProtocolOptions(
        allowedOrigins=[
            "https://127.0.0.1:8080",
            "https://localhost:8080",
        ]
    )

    factory.protocol = EchoServerProtocol
    listenWS(factory, contextFactory)

    webdir = File(".")
    webdir.contentTypes[".crt"] = "application/x-x509-ca-cert"
    web = Site(webdir)
    reactor.listenSSL(8080, web, contextFactory)
    # reactor.listenTCP(8080, web)

    reactor.run()
