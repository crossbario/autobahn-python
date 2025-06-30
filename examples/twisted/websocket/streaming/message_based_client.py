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

MESSAGE_SIZE = 1 * 2**20


class MessageBasedHashClientProtocol(WebSocketClientProtocol):
    """
    Message-based WebSockets client that generates stream of random octets
    sent to WebSockets server as a sequence of messages. The server will
    respond to us with the SHA-256 computed over each message. When
    we receive response, we repeat by sending a new message.
    """

    def sendOneMessage(self):
        data = randomByteString(MESSAGE_SIZE)
        self.sendMessage(data, isBinary=True)

    def onOpen(self):
        self.count = 0
        self.sendOneMessage()

    def onMessage(self, payload, isBinary):
        print(
            "Digest for message {} computed by server: {}".format(
                self.count, payload.decode("utf8")
            )
        )
        self.count += 1
        self.sendOneMessage()


if __name__ == "__main__":

    factory = WebSocketClientFactory("ws://127.0.0.1:9000")
    factory.protocol = MessageBasedHashClientProtocol
    connectWS(factory)
    reactor.run()
