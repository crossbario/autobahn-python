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

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

from autobahn.websocket.compress import *


class EchoServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("WebSocket connection request by {}".format(request.peer))

    def onOpen(self):
        print("WebSocket extensions in use: {}".format(self.websocket_extensions_in_use))

    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)


if __name__ == '__main__':

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = EchoServerProtocol

#   factory.setProtocolOptions(autoFragmentSize = 4)

    # Enable WebSocket extension "permessage-deflate". This is all you
    # need to do (unless you know what you are doing .. see below)!
    def accept0(offers):
        for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
                return PerMessageDeflateOfferAccept(offer)

    # Enable experimental compression extensions "permessage-snappy"
    # and "permessage-bzip2"
    def accept1(offers):
        for offer in offers:
            if isinstance(offer, PerMessageSnappyOffer):
                return PerMessageSnappyOfferAccept(offer)

            elif isinstance(offer, PerMessageBzip2Offer):
                return PerMessageBzip2OfferAccept(offer)

            elif isinstance(offer, PerMessageDeflateOffer):
                return PerMessageDeflateOfferAccept(offer)

    # permessage-deflate, server requests the client to do no
    # context takeover
    def accept2(offers):
        for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
                if offer.acceptNoContextTakeover:
                    return PerMessageDeflateOfferAccept(offer, requestNoContextTakeover=True)

    # permessage-deflate, server requests the client to do no
    # context takeover, and does not context takeover also
    def accept3(offers):
        for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
                if offer.acceptNoContextTakeover:
                    return PerMessageDeflateOfferAccept(offer, requestNoContextTakeover=True, noContextTakeover=True)

    # permessage-deflate, server requests the client to do use
    # max window bits specified
    def accept4(offers):
        for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
                if offer.acceptMaxWindowBits:
                    return PerMessageDeflateOfferAccept(offer, requestMaxWindowBits=8)


#   factory.setProtocolOptions(perMessageCompressionAccept = accept0)
#   factory.setProtocolOptions(perMessageCompressionAccept = accept1)
#   factory.setProtocolOptions(perMessageCompressionAccept = accept2)
#   factory.setProtocolOptions(perMessageCompressionAccept = accept3)
    factory.setProtocolOptions(perMessageCompressionAccept=accept4)

    listenWS(factory)

    webdir = File(".")
    web = Site(webdir)
    reactor.listenTCP(8080, web)

    reactor.run()
