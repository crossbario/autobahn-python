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
from zope.interface import implementer

from autobahn.twisted.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
    connectWS,
)
from twisted.internet import interfaces, reactor

# 2^63 - This is the maximum imposed by the WS protocol
FRAME_SIZE = 0x7FFFFFFFFFFFFFFF


@implementer(interfaces.IPushProducer)
class RandomByteStreamProducer:
    """
    A Twisted Push Producer generating a stream of random octets sending out data
    in a WebSockets message frame.
    """

    def __init__(self, proto):
        self.proto = proto
        self.started = False
        self.paused = False

    def pauseProducing(self):
        self.paused = True

    def resumeProducing(self):
        self.paused = False

        if not self.started:
            self.proto.beginMessage(isBinary=True)
            self.proto.beginMessageFrame(FRAME_SIZE)
            self.started = True

        while not self.paused:
            data = randomByteString(1024)
            if self.proto.sendMessageFrameData(data) <= 0:
                self.proto.beginMessageFrame(FRAME_SIZE)
                print("new frame started!")

    def stopProducing(self):
        pass


class StreamingProducerHashClientProtocol(WebSocketClientProtocol):
    """
    Streaming WebSockets client that generates stream of random octets
    sent to streaming WebSockets server, which computes a running SHA-256,
    which it will send every BATCH_SIZE octets back to us. This example
    uses a Twisted producer to produce the byte stream as fast as the
    receiver can consume, but not faster. Therefor, we don't need the
    application-level flow control as with the other examples.
    """

    def onOpen(self):
        self.count = 0
        producer = RandomByteStreamProducer(self)
        self.registerProducer(producer, True)
        producer.resumeProducing()

    def onMessage(self, payload, isBinary):
        print(
            "Digest for batch {} computed by server: {}".format(
                self.count, payload.decode("utf8")
            )
        )
        self.count += 1


if __name__ == "__main__":
    factory = WebSocketClientFactory("ws://127.0.0.1:9000")
    factory.protocol = StreamingProducerHashClientProtocol
    connectWS(factory)
    reactor.run()
