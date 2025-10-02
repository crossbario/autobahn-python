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

import argparse
import asyncio

import txaio

txaio.use_asyncio()

import autobahn
from autobahn.asyncio.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.websocket.compress import (
    PerMessageDeflateOffer,
    PerMessageDeflateOfferAccept,
)
from autobahn.websocket.util import parse_url

# FIXME: streaming mode API is currently incompatible with permessage-deflate!
USE_STREAMING_TESTEE = False


class TesteeServerProtocol(WebSocketServerProtocol):
    """
    A message-based WebSocket echo server.
    """

    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)


class StreamingTesteeServerProtocol(WebSocketServerProtocol):
    """
    A streaming WebSocket echo server.
    """

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
    log = txaio.make_logger()

    if USE_STREAMING_TESTEE:
        protocol = StreamingTesteeServerProtocol
    else:
        protocol = TesteeServerProtocol

    def __init__(self, url):
        testee_ident = autobahn.asyncio.__ident__
        self.log.info(
            "Testee identification: {testee_ident}", testee_ident=testee_ident
        )
        WebSocketServerFactory.__init__(self, url, server=testee_ident)

        self.setProtocolOptions(failByDrop=False)  # spec conformance
        # self.setProtocolOptions(utf8validateIncoming = False)

        if USE_STREAMING_TESTEE:
            self.setProtocolOptions(failByDrop=True)  # needed for streaming mode
        else:
            # enable permessage-deflate WebSocket protocol extension
            def accept(offers):
                for offer in offers:
                    if isinstance(offer, PerMessageDeflateOffer):
                        return PerMessageDeflateOfferAccept(offer)

            self.setProtocolOptions(perMessageCompressionAccept=accept)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autobahn Testee Server (Twisted)")
    parser.add_argument(
        "--url",
        dest="url",
        type=str,
        default="ws://127.0.0.1:9001",
        help="The WebSocket fuzzing server URL.",
    )
    parser.add_argument(
        "--loglevel",
        dest="loglevel",
        type=str,
        default="info",
        help='Log level, eg "info" or "debug".',
    )

    options = parser.parse_args()

    txaio.start_logging(level=options.loglevel)

    # Create and set event loop early for Python 3.14 compatibility
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    factory = TesteeServerFactory(options.url)

    _, _, port, _, _, _ = parse_url(options.url)
    coro = loop.create_server(factory, port=port)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
