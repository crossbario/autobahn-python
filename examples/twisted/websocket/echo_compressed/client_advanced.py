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

from autobahn.twisted.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
    connectWS,
)
from autobahn.websocket.compress import *
from twisted.internet import reactor
from twisted.python import log


class EchoClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("WebSocket extensions in use: %s" % response.extensions)

    def sendHello(self):
        self.sendMessage("Hello, world!" * 100)

    def onOpen(self):
        self.sendHello()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("Text message received: {}".format(payload.decode("utf8")))
        reactor.callLater(1, self.sendHello)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Need the WebSocket server address, i.e. ws://127.0.0.1:9000")
        sys.exit(1)

    log.startLogging(sys.stdout)

    factory = WebSocketClientFactory(sys.argv[1])

    factory.protocol = EchoClientProtocol

    # Advanced usage: specify exact list of offers ("PMCE") we announce to server.
    #
    # Examples:
    #

    # this is just what the default constructor for PerMessageDeflateOffer
    # creates anyway
    offers1 = [
        PerMessageDeflateOffer(
            acceptNoContextTakeover=True,
            acceptMaxWindowBits=True,
            requestNoContextTakeover=False,
            request_max_window_bits=0,
        )
    ]

    # request the server to use a sliding window of 2^8 bytes
    offers2 = [PerMessageDeflateOffer(True, True, False, 8)]

    # request the server to use a sliding window of 2^8 bytes, but let the
    # server fall back to "standard" if server does not support the setting
    offers3 = [
        PerMessageDeflateOffer(True, True, False, 8),
        PerMessageDeflateOffer(True, True, False, 0),
    ]

    # request "no context takeover", accept the same, but deny setting
    # a sliding window. no fallback!
    offers4 = [PerMessageDeflateOffer(True, False, True, 0)]

    # offer "permessage-snappy", "permessage-bzip2" and "permessage-deflate"
    # note that the first 2 are currently not even in an RFC draft
    #
    offers5 = []
    if "permessage-snappy" in PERMESSAGE_COMPRESSION_EXTENSION:
        # this require snappy to be installed
        offers5.append(PerMessageSnappyOffer())
    offers5.append(PerMessageBzip2Offer(True, 1))
    offers5.append(PerMessageDeflateOffer(True, True, False, 12))

    # factory.setProtocolOptions(perMessageCompressionOffers = offers1)
    # factory.setProtocolOptions(perMessageCompressionOffers = offers2)
    # factory.setProtocolOptions(perMessageCompressionOffers = offers3)
    # factory.setProtocolOptions(perMessageCompressionOffers = offers4)
    factory.setProtocolOptions(perMessageCompressionOffers=offers5)

    # factory.setProtocolOptions(autoFragmentSize = 4)

    def accept(response):
        if isinstance(response, PerMessageDeflateResponse):
            return PerMessageDeflateResponseAccept(response)

        elif isinstance(response, PerMessageBzip2Response):
            return PerMessageBzip2ResponseAccept(response)

        elif isinstance(response, PerMessageSnappyResponse):
            return PerMessageSnappyResponseAccept(response)

    factory.setProtocolOptions(perMessageCompressionAccept=accept)

    connectWS(factory)
    reactor.run()
