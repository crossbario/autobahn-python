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
