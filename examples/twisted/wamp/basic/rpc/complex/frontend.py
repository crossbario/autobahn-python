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

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession


class Component(ApplicationSession):

    """
    Application component that calls procedures which
    produce complex results and showing how to access those.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")

        res = yield self.call('com.myapp.add_complex', 2, 3, 4, 5)
        print("Result: {} + {}i".format(res.kwresults['c'], res.kwresults['ci']))

        res = yield self.call('com.myapp.split_name', 'Homer Simpson')
        print("Forname: {}, Surname: {}".format(res.results[0], res.results[1]))

        self.leave()

    def onDisconnect(self):
        print("disconnected")
        reactor.stop()


if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
