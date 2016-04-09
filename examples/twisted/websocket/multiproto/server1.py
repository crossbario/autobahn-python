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

import txaio

from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

from autobahn.websocket.types import ConnectionDeny


class BaseService:

    """
    Simple base for our services.
    """

    def __init__(self, proto):
        self.proto = proto
        self.is_closed = False

    def onOpen(self):
        pass

    def onClose(self, wasClean, code, reason):
        pass

    def onMessage(self, payload, isBinary):
        pass


class Echo1Service(BaseService):

    """
    Awesome Echo Service 1.
    """

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = "Echo 1 - {}".format(payload.decode('utf8'))
            print(msg)
            self.proto.sendMessage(msg.encode('utf8'))


class Echo2Service(BaseService):

    """
    Awesome Echo Service 2.
    """

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = "Echo 2 - {}".format(payload.decode('utf8'))
            print(msg)
            self.proto.sendMessage(msg.encode('utf8'))


class ServiceServerProtocol(WebSocketServerProtocol):

    SERVICEMAP = {'/echo1': Echo1Service,
                  '/echo2': Echo2Service}

    def __init__(self):
        self.service = None
        self.is_closed = txaio.create_future()

    def onConnect(self, request):
        # request has all the information from the initial
        # WebSocket opening handshake ..
        print(request.peer)
        print(request.headers)
        print(request.host)
        print(request.path)
        print(request.params)
        print(request.version)
        print(request.origin)
        print(request.protocols)
        print(request.extensions)

        # We map to services based on path component of the URL the
        # WebSocket client requested. This is just an example. We could
        # use other information from request, such has HTTP headers,
        # WebSocket subprotocol, WebSocket origin etc etc
        ##
        if request.path in self.SERVICEMAP:
            cls = self.SERVICEMAP[request.path]
            self.service = cls(self)
        else:
            err = "No service under %s" % request.path
            print(err)
            raise ConnectionDeny(404, unicode(err))

    def onOpen(self):
        if self.service:
            self.service.onOpen()

    def onMessage(self, payload, isBinary):
        if self.service:
            self.service.onMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        if self.service:
            self.service.onClose(wasClean, code, reason)


if __name__ == '__main__':

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = ServiceServerProtocol
    listenWS(factory)

    reactor.run()
