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


class MessageBasedHashServerProtocol(WebSocketServerProtocol):
    """
    Message-based WebSockets server that computes a SHA-256 for every
    message it receives and sends back the computed digest.
    """

    def onMessage(self, payload, isBinary):
        sha256 = hashlib.sha256()
        sha256.update(payload)
        digest = sha256.hexdigest()
        self.sendMessage(digest.encode("utf8"))
        print("Sent digest for message: {}".format(digest))


if __name__ == "__main__":
    factory = WebSocketServerFactory("ws://127.0.0.1:9000")
    factory.protocol = MessageBasedHashServerProtocol
    listenWS(factory)
    reactor.run()
