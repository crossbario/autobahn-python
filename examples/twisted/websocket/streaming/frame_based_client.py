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
from ranstring import randomByteString

from twisted.internet import reactor

from autobahn.twisted.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
    connectWS,
)


FRAME_SIZE = 1 * 2**20
FRAME_COUNT = 10


class FrameBasedHashClientProtocol(WebSocketClientProtocol):
    """
    Message-based WebSockets client that generates stream of random octets
    sent to WebSockets server as a sequence of frames all in one message.
    The server will respond to us with the SHA-256 computed over frames.
    When we receive response, we repeat by sending a new frame.
    """

    def sendOneFrame(self):
        data = randomByteString(FRAME_SIZE)

        self.sha256.update(data)
        digest = self.sha256.hexdigest()
        print("Digest for frame {} computed by client: {}".format(self.count, digest))

        self.sendMessageFrame(data)

    def onOpen(self):
        self.count = 0
        self.finished = False
        self.beginMessage(isBinary=True)
        self.sha256 = hashlib.sha256()
        self.sendOneFrame()

    def onMessage(self, payload, isBinary):
        print(
            "Digest for frame {} computed by server: {}".format(
                self.count, payload.decode("utf8")
            )
        )
        self.count += 1

        if self.count < FRAME_COUNT:
            self.sendOneFrame()
        elif not self.finished:
            self.endMessage()
            self.finished = True

        if self.count >= FRAME_COUNT:
            self.sendClose()

    def onClose(self, wasClean, code, reason):
        reactor.stop()


if __name__ == "__main__":

    factory = WebSocketClientFactory("ws://127.0.0.1:9000")
    factory.protocol = FrameBasedHashClientProtocol

    enableCompression = False
    if enableCompression:
        from autobahn.websocket.compress import (
            PerMessageDeflateOffer,
            PerMessageDeflateResponse,
            PerMessageDeflateResponseAccept,
        )

        # The extensions offered to the server ..
        offers = [PerMessageDeflateOffer()]
        factory.setProtocolOptions(perMessageCompressionOffers=offers)

        # Function to accept responses from the server ..
        def accept(response):
            if isinstance(response, PerMessageDeflateResponse):
                return PerMessageDeflateResponseAccept(response)

        factory.setProtocolOptions(perMessageCompressionAccept=accept)

    connectWS(factory)
    reactor.run()
