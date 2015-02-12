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

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol


class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        self.factory.broadcast(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):

    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """
    protocol = BroadcastServerProtocol

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url, debug=False)
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            self.clients.append(client)
            print("registered client {}".format(client.peer))

    def unregister(self, client):
        if client in self.clients:
            self.clients.remove(client)
            print("unregistered client {}".format(client.peer))

    def broadcast(self, payload, isBinary):
        for c in self.clients:
            c.sendMessage(payload, isBinary)
        print("broadcasted message to {} clients".format(len(self.clients)))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = BroadcastServerFactory("ws://localhost:9000")

    reactor.listenTCP(9000, factory)
    reactor.run()
