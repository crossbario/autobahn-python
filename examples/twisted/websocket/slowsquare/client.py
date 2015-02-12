###############################################################################
##
# Copyright (C) 2014 Tavendo GmbH
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

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

import json
import random


class SlowSquareClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        x = 10. * random.random()
        self.sendMessage(json.dumps(x).encode('utf8'))
        print("Request to square {} sent.".format(x))

    def onMessage(self, payload, isBinary):
        if not isBinary:
            res = json.loads(payload.decode('utf8'))
            print("Result received: {}".format(res))
            self.sendClose()

    def onClose(self, wasClean, code, reason):
        if reason:
            print(reason)
        reactor.stop()


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketClientFactory("ws://localhost:9000", debug=False)
    factory.protocol = SlowSquareClientProtocol

    reactor.connectTCP("127.0.0.1", 9000, factory)
    reactor.run()
