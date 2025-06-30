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

from streaming_client import BATCH_SIZE


class StreamingHashServerProtocol(WebSocketServerProtocol):
    """
    Streaming WebSockets server that computes a running SHA-256 for data
    received. It will respond every BATCH_SIZE bytes with the digest
    up to that point. It can receive messages of unlimited number of frames
    and frames of unlimited length (actually, up to 2^63, which is the
    WebSockets protocol imposed limit on frame size). Digest is reset upon
    new message.
    """

    def onMessageBegin(self, isBinary):
        WebSocketServerProtocol.onMessageBegin(self, isBinary)
        self.sha256 = hashlib.sha256()
        self.count = 0
        self.received = 0
        self.next = BATCH_SIZE

    def onMessageFrameBegin(self, length):
        WebSocketServerProtocol.onMessageFrameBegin(self, length)

    def onMessageFrameData(self, payload):
        length = len(payload)
        self.received += length

        # when the data received exceeds the next BATCH_SIZE ..
        if self.received >= self.next:

            # update digest up to batch size
            rest = length - (self.received - self.next)
            self.sha256.update(payload[:rest])

            # send digest
            digest = self.sha256.hexdigest()
            self.sendMessage(digest.encode("utf8"))
            print("Sent digest for batch {} : {}".format(self.count, digest))

            # advance to next batch
            self.next += BATCH_SIZE
            self.count += 1

            # .. and update the digest for the rest
            self.sha256.update(payload[rest:])
        else:
            # otherwise we just update the digest for received data
            self.sha256.update(payload)

    def onMessageFrameEnd(self):
        pass

    def onMessageEnd(self):
        pass


if __name__ == "__main__":
    factory = WebSocketServerFactory("ws://127.0.0.1:9000")
    factory.protocol = StreamingHashServerProtocol
    listenWS(factory)
    reactor.run()
