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

from twisted.python import log
from twisted.internet import protocol
from twisted.words.protocols import irc


class IRCClientProtocol(irc.IRCClient):

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        print "connected"

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        print "lost", reason

    def signedOn(self):
        print "signedon"
        for channel in self.channels:
            print "joining", channel
            self.join(channel)

    def joined(self, channel):
        print "joined", channel

    def privmsg(self, user, channel, msg):
        # privmsg oberstet!~vanaland@89.204.139.245 #autobahn bot23: test
        print "privmsg", user, channel, msg
        self.factory.session.publish('com.myapp.on_privmsg', user, channel, msg)

    def action(self, user, channel, msg):
        print "action", user, channel, msg


class IRCClientFactory(protocol.ClientFactory):

    def __init__(self, session, nickname, channels):
        self.session = session
        self.proto = None
        self.nickname = str(nickname)
        self.channels = [str(c) for c in channels]

    def buildProtocol(self, addr):
        assert(not self.proto)
        self.proto = IRCClientProtocol()
        self.proto.factory = self
        self.proto.nickname = self.nickname
        self.proto.channels = self.channels
        return self.proto

    def clientConnectionLost(self, connector, reason):
        # connector.connect()
        self.proto = None

    def clientConnectionFailed(self, connector, reason):
        # from twisted.internet import reactor
        # reactor.stop()
        self.proto = None
