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

from twisted.web.client import Agent
from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner


class Component1(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):

        from twisted.internet import reactor
        self._agent = Agent(reactor)

        yield self.register(self)
        print("Procedures registered")

    @wamp.register('com.myapp.httpget')
    def httpget(self, url):
        d = self._agent.request('GET', str(url))

        def cbResponse(_):
            return "got response"
        d.addCallback(cbResponse)

        return d


if __name__ == '__main__':

    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component1)
