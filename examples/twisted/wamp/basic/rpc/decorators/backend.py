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

from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession


class MyService1:

    @wamp.register('com.mathservice.add2')
    def add2(self, x, y):
        return x + y

    @wamp.register('com.mathservice.mul2')
    def mul2(self, x, y):
        return x * y


class Component(ApplicationSession):

    """
    An application component registering RPC endpoints using decorators.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")

        # register all methods on this object decorated with "@wamp.register"
        # as a RPC endpoint
        ##
        svc1 = MyService1()

        for obj in [self, svc1]:
            results = yield self.register(obj)
            for success, res in results:
                if success:
                    # res is an Registration instance
                    print("Ok, registered procedure on {} with registration ID {}".format(obj, res.id))
                else:
                    # res is an Failure instance
                    print("Failed to register procedure: {}".format(res.value))

    @wamp.register('com.mathservice.square2')
    def square2(self, x, y):
        return x * x + y * y

    @wamp.register('com.mathservice.div2')
    def div2(self, x, y):
        if y:
            return float(x) / float(y)
        else:
            return 0


if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
