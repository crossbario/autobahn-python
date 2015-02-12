###############################################################################
##
# Copyright (C) 2011-2014 Tavendo GmbH
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
import os
import socket

from twisted.internet import tcp
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory


class CustomPort(tcp.Port):

    def __init__(self, port, factory, backlog=50, interface='', reactor=None, reuse=False):
        tcp.Port.__init__(self, port, factory, backlog, interface, reactor)
        self._reuse = reuse

    def createInternetSocket(self):
        s = tcp.Port.createInternetSocket(self)

        if self._reuse:
            #
            # reuse IP Port
            #
            if 'bsd' in sys.platform or \
                    sys.platform.startswith('linux') or \
                    sys.platform.startswith('darwin'):
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

            elif sys.platform == 'win32':
                # on Windows, REUSEADDR already implies REUSEPORT
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            else:
                raise Exception("don't know how to set SO_REUSEPORT on platform {}".format(sys.platform))

        return s


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0} on server PID {1}".format(request.peer, os.getpid()))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory("ws://127.0.0.1:9000", debug=False)
    factory.protocol = MyServerProtocol

    # reactor.listenTCP(9000, factory)

    p = CustomPort(9000, factory, reuse=True)
    p.startListening()
    print p

    reactor.run()
