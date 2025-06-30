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

import hashlib
from twisted.internet import reactor

from autobahn.twisted.websocket import (
    WebSocketServerFactory,
    WebSocketServerProtocol,
    listenWS,
)


class FrameBasedHashServerProtocol(WebSocketServerProtocol):
    """
    Frame-based WebSockets server that computes a running SHA-256 for message
    data received. It will respond after every frame received with the digest
    computed up to that point. It can receive messages of unlimited number
    of frames. Digest is reset upon new message.
    """

    def onMessageBegin(self, isBinary):
        WebSocketServerProtocol.onMessageBegin(self, isBinary)
        self.sha256 = hashlib.sha256()

    def onMessageFrame(self, payload):
        l = 0
        for data in payload:
            l += len(data)
            self.sha256.update(data)
        digest = self.sha256.hexdigest()
        print(
            "Received frame with payload length {}, compute digest: {}".format(
                l, digest
            )
        )
        self.sendMessage(digest.encode("utf8"))

    def onMessageEnd(self):
        self.sha256 = None


if __name__ == "__main__":

    factory = WebSocketServerFactory("ws://127.0.0.1:9000")
    factory.protocol = FrameBasedHashServerProtocol

    enableCompression = False
    if enableCompression:
        from autobahn.websocket.compress import (
            PerMessageDeflateOffer,
            PerMessageDeflateOfferAccept,
        )

        # Function to accept offers from the client ..

        def accept(offers):
            for offer in offers:
                if isinstance(offer, PerMessageDeflateOffer):
                    return PerMessageDeflateOfferAccept(offer)

        factory.setProtocolOptions(perMessageCompressionAccept=accept)

    listenWS(factory)
    reactor.run()
