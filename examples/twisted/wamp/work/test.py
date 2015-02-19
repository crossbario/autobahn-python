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

import sys

from autobahn.websocket import WebSocketProtocol, HttpException, Timings
from autobahn.websocket import WebSocketClientProtocol, WebSocketClientFactory
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol

from autobahn.httpstatus import HTTP_STATUS_CODE_BAD_REQUEST
from autobahn.util import utcnow, newid

import autobahn.wamp2

from autobahn.wamp2.dealer import Dealer, exportRpc
from autobahn.wamp2.broker import Broker
from autobahn.wamp2.protocol import WampServerProtocol, \
    WampServerFactory, \
    WampClientProtocol, \
    WampClientFactory

from autobahn.wamp2.serializer import JsonSerializer, MsgPackSerializer

from twisted.python import log
from twisted.internet import reactor

from autobahn.websocket import connectWS, listenWS


def test1():

    serializer = JsonDefaultSerializer()

    wampSerializer = WampSerializer(serializer)

    # wampMsg = WampMessageSubscribe("http://myapp.com/topic1", match = WampMessageSubscribe.MATCH_PREFIX)
    # wampMsg = WampMessageUnsubscribe("http://myapp.com/topic1", match = WampMessageSubscribe.MATCH_PREFIX)
    wampMsg = WampMessagePublish("http://myapp.com/topic1", "Hello, world!")

    bytes = wampSerializer.serialize(wampMsg)

    print bytes

    wampMsg2 = wampSerializer.unserialize(bytes)

    print wampMsg2.__class__
    print wampMsg2


class Calculator:

    def __init__(self):
        self._sum = 0

    @exportRpc
    def add(self, a, b):
        return a + b

    @exportRpc
    def accumulate(self, value):
        self._sum += value

    @exportRpc
    def getValue(self):
        return self._sum


# http://myapp.com/getRevenue

# When multiple endpoints are registered under the same URI
# with a dealer, it is under the dealer's policy what happens:
#
# - ignore any but first
# - overwrite
# - accumulate
#
# make subscribe return a (ephemeral) subscription id (on success)
# make event contain that subscription id
# make unsubscribe contain that subscription id
#
# make provide return a (ephemeral) provisioning id (on success)
# make call contain that provisioning id
# make unprovide contain that provisioning id
#

# call _all_ implementing endpoints and get accumulated result
# call _all_ implementing endpoints, receive progressive results and final result empty
# call a random implementing endpoint and receive result
# call the implementing endpoint with given session ID
# call any implementing endpoint (let the dealer choose, e.g. nearest)


def test_server(wsuri, wsuri2=None):

    dealer = Dealer()

    if wsuri2 is None:
        calculator = Calculator()
        dealer.register("http://myapp.com/", calculator)

    broker = Broker()

    class MyPubSubServerProtocol(WampServerProtocol):

        def onSessionOpen(self):
            self.setBroker(broker)
            self.setDealer(dealer)

    wampFactory = WampServerFactory(wsuri)
    wampFactory.protocol = MyPubSubServerProtocol
    listenWS(wampFactory)

    if wsuri2:
        class MyPubSubClientProtocol(WampClientProtocol):

            def onSessionOpen(self):
                self.setBroker(broker)
                self.setDealer(dealer)

        factory = WampClientFactory(wsuri2)
        factory.protocol = MyPubSubClientProtocol
        connectWS(factory)


def test_client(wsuri, dopub):

    dorpc = False

    class MyPubSubClientProtocol(WampClientProtocol):

        def onSessionOpen(self):

            print "Connected!"

            def onMyEvent1(topic, event):
                print "Received event", topic, event

            d = self.subscribe("http://example.com/myEvent1", onMyEvent1)

            def subscribeSuccess(subscriptionid):
                print "Subscribe Success", subscriptionid

            def subscribeError(error):
                print "Subscribe Error", error

            d.addCallbacks(subscribeSuccess, subscribeError)

            self.counter = 0

            def sendMyEvent1():
                self.counter += 1
                self.publish("http://example.com/myEvent1",
                             {
                                 "msg": "Hello from Python!",
                                 "counter": self.counter
                             }
                             )
                reactor.callLater(2, sendMyEvent1)

            if dopub:
                sendMyEvent1()

            if dorpc:
                def writeln(res):
                    print res

                d = self.call("http://myapp.com/add", 23, 7)
                d.addBoth(writeln)

                d = self.call("http://myapp2.com/add", 40, 2)
                d.addBoth(writeln)

        def onClose(self, wasClean, code, reason):
            print "Connection closed", reason
            reactor.stop()

    factory = WampClientFactory(wsuri)
    factory.protocol = MyPubSubClientProtocol
    connectWS(factory)


def test_client2(wsuri):

    class MyPubSubClientProtocol(WampClientProtocol):

        def onSessionOpen(self):

            print "Connected!"
            calculator = Calculator()

            dealer = Dealer()
            dealer.register("http://myapp2.com/", calculator)

            self.setDealer(dealer)

        def onClose(self, wasClean, code, reason):
            print "Connection closed", reason
            reactor.stop()

    factory = WampClientFactory(wsuri)
    factory.protocol = MyPubSubClientProtocol
    connectWS(factory)

# python test.py server ws://127.0.0.1:9000
# python test.py server ws://127.0.0.1:9001 ws://127.0.0.1:9000
# python test.py client ws://127.0.0.1:9000 pub


# python test.py server ws://127.0.0.1:9000
# python test.py server ws://127.0.0.1:9001 ws://127.0.0.1:9000
# python test.py client2 ws://127.0.0.1:9001
# python test.py client ws://127.0.0.1:9000


if __name__ == '__main__':

    log.startLogging(sys.stdout)

    mode = sys.argv[1]
    wsuri = sys.argv[2]

    if mode == 'server' and len(sys.argv) > 3:
        wsuri2 = sys.argv[3]
    else:
        wsuri2 = None

    if mode == 'client' and len(sys.argv) > 3:
        dopub = sys.argv[3] == "pub"
    else:
        dopub = False

    if mode == 'client':
        test_client(wsuri, dopub)
    elif mode == 'client2':
        test_client2(wsuri)
    elif mode == 'server':
        test_server(wsuri, wsuri2)
    else:
        raise Exception("illegal mode")

    # test1()

    reactor.run()
