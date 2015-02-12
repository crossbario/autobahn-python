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

import hashlib
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS


class MessageBasedHashServerProtocol(WebSocketServerProtocol):

    """
    Message-based WebSockets server that computes a SHA-256 for every
    message it receives and sends back the computed digest.
    """

    def onMessage(self, payload, isBinary):
        sha256 = hashlib.sha256()
        sha256.update(payload)
        digest = sha256.hexdigest()
        self.sendMessage(digest.encode('utf8'))
        print("Sent digest for message: {}".format(digest))


if __name__ == '__main__':
    factory = WebSocketServerFactory("ws://localhost:9000")
    factory.protocol = MessageBasedHashServerProtocol
    listenWS(factory)
    reactor.run()
