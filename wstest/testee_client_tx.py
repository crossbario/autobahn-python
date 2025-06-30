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

import txaio

txaio.use_twisted()

from twisted.internet import reactor

import autobahn

from autobahn.websocket.protocol import WebSocketProtocol
from autobahn.twisted.websocket import (
    connectWS,
    WebSocketClientFactory,
    WebSocketClientProtocol,
)

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


class TesteeClientFactory(WebSocketClientFactory):

    protocol = TesteeClientProtocol

    def __init__(self, url):
        self.agent = autobahn.twisted.__ident__
        WebSocketClientFactory.__init__(self, url, useragent=self.agent)

        self.setProtocolOptions(failByDrop=False)  # spec conformance

        # enable permessage-deflate WebSocket protocol extension
        offers = [PerMessageDeflateOffer()]
        self.setProtocolOptions(perMessageCompressionOffers=offers)

        def accept(response):
            if isinstance(response, PerMessageDeflateResponse):
                return PerMessageDeflateResponseAccept(response)

        self.setProtocolOptions(perMessageCompressionAccept=accept)

        # setup client testee stuff
        self.endCaseId = None
        self.currentCaseId = 0
        self.updateReports = True
        self.resource = "/getCaseCount"

    def clientConnectionLost(self, connector, reason):
        self.currentCaseId += 1
        if self.currentCaseId <= self.endCaseId:
            self.resource = "/runCase?case={}&agent={}".format(
                self.currentCaseId, self.agent
            )
            connector.connect()
        elif self.updateReports:
            self.resource = "/updateReports?agent={}".format(self.agent)
            self.updateReports = False
            connector.connect()
        else:
            reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        self.log.info(
            "Connection to {url} failed: {error_message}",
            url=self.url,
            error_message=reason.getErrorMessage(),
        )
        reactor.stop()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Autobahn Testee Client (Twisted)")
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

    factory = TesteeClientFactory(options.url)

    connectWS(factory)
    reactor.run()
