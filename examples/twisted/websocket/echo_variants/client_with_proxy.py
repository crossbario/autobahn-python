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

import sys

from twisted.internet import reactor
from twisted.python import log

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS


class EchoClientProtocol(WebSocketClientProtocol):

    def sendHello(self):
        self.sendMessage("Hello, world!".encode('utf8'))

    def onOpen(self):
        self.sendHello()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("Text message received: {}".format(payload.decode('utf8')))
        reactor.callLater(1, self.sendHello)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Need the WebSocket server address, i.e. ws://localhost:9000")
        sys.exit(1)

    if len(sys.argv) < 3:
        print("Need the Proxy, i.e. 192.168.1.100:8050")
        sys.exit(1)

    proxyHost, proxyPort = sys.argv[2].split(":")
    proxy = {'host': proxyHost, 'port': int(proxyPort)}

    if len(sys.argv) > 3 and sys.argv[3] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    factory = WebSocketClientFactory(sys.argv[1],
                                     proxy=proxy,
                                     debug=debug,
                                     debugCodePaths=debug)

    # uncomment to use Hixie-76 protocol
    # factory.setProtocolOptions(allowHixie76 = True, version = 0)
    factory.protocol = EchoClientProtocol
    connectWS(factory)

    reactor.run()
