###############################################################################
##
# Copyright (C) 2011-2013 Tavendo GmbH
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

from twisted.internet.protocol import Protocol


class HelloClientProtocol(Protocol):

    def connectionMade(self):
        print("connectionMade")
        self.transport.write('hello')

    def dataReceived(self, data):
        print("dataReceived: {}".format(data))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor
    from twisted.internet.protocol import Factory
    from twisted.internet.endpoints import clientFromString

    log.startLogging(sys.stdout)

    wrappedFactory = Factory.forProtocol(HelloClientProtocol)

    endpoint = clientFromString(reactor, "autobahn:tcp\:localhost\:9000:url=ws\://localhost\:9000")
    endpoint.connect(wrappedFactory)

    reactor.run()
