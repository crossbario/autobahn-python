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

from ranstring import randomByteString
from twisted.internet import reactor

from autobahn.twisted.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
    connectWS,
)

BATCH_SIZE = 1 * 2**20


class StreamingHashClientProtocol(WebSocketClientProtocol):
    """
    Streaming WebSockets client that generates stream of random octets
    sent to WebSockets server as a sequence of batches in one frame, in
    one message. The server computes a running SHA-256, which it will send
    every BATCH_SIZE octets back to us. When we receive a response, we
    repeat by sending another batch of data.
    """

    def sendOneBatch(self):
        data = randomByteString(BATCH_SIZE)

        # Note, that this could complete the frame, when the frame length is
        # reached. Since the frame length here is 2^63, we don't bother, since
        # it'll take _very_ long to reach that.
        self.sendMessageFrameData(data)

    def onOpen(self):
        self.count = 0
        self.beginMessage(isBinary=True)
        # 2^63 - This is the maximum imposed by the WS protocol
        self.beginMessageFrame(0x7FFFFFFFFFFFFFFF)
        self.sendOneBatch()

    def onMessage(self, payload, isBinary):
        print(
            "Digest for batch {} computed by server: {}".format(
                self.count, payload.decode("utf8")
            )
        )
        self.count += 1
        self.sendOneBatch()


if __name__ == "__main__":

    factory = WebSocketClientFactory("ws://127.0.0.1:9000")
    factory.protocol = StreamingHashClientProtocol
    connectWS(factory)
    reactor.run()
