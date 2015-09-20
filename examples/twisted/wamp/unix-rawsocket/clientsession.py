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

from __future__ import print_function

from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep


class ClientSession(ApplicationSession):
    """
    An example ApplicationSession shared by the different
    frontend_*.py variants.

    The only complicated thing this does is leave() and re-join the
    WAMP session without disconnecting the underlying transport.
    """

    #: how many times we wish to (re-) join before disconnecting
    joins = 2

    @inlineCallbacks
    def onJoin(self, details):
        print("onJoin:", details)
        self.joins = self.joins - 1
        sub = yield self.subscribe(self.subscription, "test.sub")
        print("subscribed:", sub)

        if False:
            # enabling this will cause the 'ready' event to fire much
            # sooner, and doesn't do the re-joining.
            self.joins = 0
            from twisted.internet import reactor
            print(".disconnect()-ing in 4 seconds")
            reactor.callLater(4, self.disconnect)
            return

        wait = 6
        while wait > 0:
            print("leaving in {} seconds".format(wait))
            wait -= 1
            yield sleep(1)
        print("leave()-ing")
        self.leave()

    def onLeave(self, details):
        print("onLeave:", details)
        if self.joins > 0:
            print("re-joining in 2 seconds")
            from twisted.internet import reactor
            reactor.callLater(2, self.join, self.config.realm)

        else:
            print("disconnecting.")
            self.disconnect()

    def onDisconnect(self):
        print("onDisconnect")

    def subscription(self, *args, **kw):
        print("sub:", args, kw)

    def __repr__(self):
        return '<ClientSession id={}>'.format(self._session_id)
