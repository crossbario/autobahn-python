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

import asyncio
import argparse

import txaio

txaio.use_asyncio()

import autobahn

from autobahn.websocket.util import parse_url

from autobahn.websocket.protocol import WebSocketProtocol
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

from autobahn.websocket.compress import (
    PerMessageDeflateOffer,
    PerMessageDeflateResponse,
    PerMessageDeflateResponseAccept,
)


class TesteeClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        if self.factory.endCaseId is None:
            self.log.info("Getting case count ..")
        elif self.factory.currentCaseId <= self.factory.endCaseId:
            self.log.info(
                "Running test case {case_id}/{last_case_id} as user agent {agent} on peer {peer}",
                case_id=self.factory.currentCaseId,
                last_case_id=self.factory.endCaseId,
                agent=self.factory.agent,
                peer=self.peer,
            )

    def onMessage(self, msg, binary):
        if self.factory.endCaseId is None:
            self.factory.endCaseId = int(msg)
            self.log.info(
                "Ok, will run {case_count} cases", case_count=self.factory.endCaseId
            )
        else:
            if self.state == WebSocketProtocol.STATE_OPEN:
                self.sendMessage(msg, binary)

    def onClose(self, wasClean, code, reason):
        txaio.resolve(self.factory._done, None)


class TesteeClientFactory(WebSocketClientFactory):

    protocol = TesteeClientProtocol

    def __init__(self, url, agent):
        self.agent = agent
        WebSocketClientFactory.__init__(self, url, useragent=agent)

        self.setProtocolOptions(failByDrop=False)  # spec conformance

        # enable permessage-deflate WebSocket protocol extension
        offers = [PerMessageDeflateOffer()]
        self.setProtocolOptions(perMessageCompressionOffers=offers)

        def accept(response):
            if isinstance(response, PerMessageDeflateResponse):
                return PerMessageDeflateResponseAccept(response)

        self.setProtocolOptions(perMessageCompressionAccept=accept)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Autobahn Testee Client (asyncio)")
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

    factory = TesteeClientFactory(options.url, autobahn.asyncio.__ident__)

    _, host, port, _, _, _ = parse_url(options.url)

    loop = asyncio.get_event_loop()

    factory.resource = "/getCaseCount"
    factory.endCaseId = None
    factory.currentCaseId = 0
    factory.updateReports = True

    while True:

        factory._done = txaio.create_future()
        coro = loop.create_connection(factory, host, port)
        loop.run_until_complete(coro)
        loop.run_until_complete(factory._done)

        factory.currentCaseId += 1
        if factory.currentCaseId <= factory.endCaseId:
            factory.resource = "/runCase?case={}&agent={}".format(
                factory.currentCaseId, factory.agent
            )
        elif factory.updateReports:
            factory.resource = "/updateReports?agent={}".format(factory.agent)
            factory.updateReports = False
        else:
            break

    loop.close()
