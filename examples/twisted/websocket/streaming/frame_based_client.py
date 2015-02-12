###############################################################################
##
# Copyright (C) 2011-2013 Tavendo GmbH
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

import hashlib
from pprint import pprint
from ranstring import randomByteString

from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS


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
        print("Digest for frame {} computed by server: {}".format(self.count, payload.decode('utf8')))
        # pprint(self.trafficStats.__json__())
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


if __name__ == '__main__':

    factory = WebSocketClientFactory("ws://localhost:9000")
    factory.protocol = FrameBasedHashClientProtocol

    enableCompression = False
    if enableCompression:
        from autobahn.websocket.compress import PerMessageDeflateOffer, \
            PerMessageDeflateResponse, \
            PerMessageDeflateResponseAccept

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
