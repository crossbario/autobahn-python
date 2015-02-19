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

import autobahn

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from autobahn.websocket.compress import *


class TesteeServerProtocol(WebSocketServerProtocol):

    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)


class StreamingTesteeServerProtocol(WebSocketServerProtocol):

    def onMessageBegin(self, isBinary):
        WebSocketServerProtocol.onMessageBegin(self, isBinary)
        self.beginMessage(isBinary)

    def onMessageFrameBegin(self, length):
        WebSocketServerProtocol.onMessageFrameBegin(self, length)
        self.beginMessageFrame(length)

    def onMessageFrameData(self, payload):
        self.sendMessageFrameData(payload)

    def onMessageFrameEnd(self):
        pass

    def onMessageEnd(self):
        self.endMessage()


class TesteeServerFactory(WebSocketServerFactory):

    # protocol = TesteeServerProtocol
    protocol = StreamingTesteeServerProtocol

    def __init__(self, url, debug=False, ident=None):
        if ident is not None:
            server = ident
        else:
            server = "AutobahnPython-Asyncio/%s" % autobahn.version
        WebSocketServerFactory.__init__(self, url, debug=debug, debugCodePaths=debug, server=server)
        self.setProtocolOptions(failByDrop=False)  # spec conformance
        self.setProtocolOptions(failByDrop=True)  # needed for streaming mode
        # self.setProtocolOptions(utf8validateIncoming = False)

        # enable permessage-deflate
        ##
        def accept(offers):
            for offer in offers:
                if isinstance(offer, PerMessageDeflateOffer):
                    return PerMessageDeflateOfferAccept(offer)

        self.setProtocolOptions(perMessageCompressionAccept=accept)


if __name__ == '__main__':

    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        import trollius as asyncio

    factory = TesteeServerFactory("ws://localhost:9002", debug=False)

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, port=9002)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
