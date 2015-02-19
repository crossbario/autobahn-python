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

from twisted.python import log
from twisted.internet.endpoints import clientFromString

from autobahn.twisted.choosereactor import install_reactor
from autobahn.twisted.websocket import WampWebSocketClientFactory
from autobahn.twisted.wamp import ApplicationSessionFactory
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp import types


class MySession(ApplicationSession):

    def onJoin(self, details):
        print("Session attached to realm!")


log.startLogging(sys.stdout)

reactor = install_reactor()

print("Running on reactor {}".format(reactor))

session_factory = ApplicationSessionFactory(types.ComponentConfig(realm=u"realm1"))
session_factory.session = MySession

transport_factory = WampWebSocketClientFactory(session_factory, url="ws://localhost", debug=True)

client = clientFromString(reactor, "unix:/tmp/cbsocket")
client.connect(transport_factory)
reactor.run()
