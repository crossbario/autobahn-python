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

import sys
import os
import socket

from twisted.internet import tcp
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory


class CustomPort(tcp.Port):

    def __init__(
        self, port, factory, backlog=50, interface="", reactor=None, reuse=False
    ):
        tcp.Port.__init__(self, port, factory, backlog, interface, reactor)
        self._reuse = reuse

    def createInternetSocket(self):
        s = tcp.Port.createInternetSocket(self)

        if self._reuse:
            #
            # reuse IP Port
            #
            if (
                "bsd" in sys.platform
                or sys.platform.startswith("linux")
                or sys.platform.startswith("darwin")
            ):
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

            elif sys.platform == "win32":
                # on Windows, REUSEADDR already implies REUSEPORT
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            else:
                raise Exception(
                    "don't know how to set SO_REUSEPORT on platform {}".format(
                        sys.platform
                    )
                )

        return s


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print(
            "Client connecting: {0} on server PID {1}".format(request.peer, os.getpid())
        )

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode("utf8")))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == "__main__":

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory("ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol

    # reactor.listenTCP(9000, factory)

    p = CustomPort(9000, factory, reuse=True)
    p.startListening()

    reactor.run()
