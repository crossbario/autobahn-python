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

from twisted.internet.defer import inlineCallbacks, returnValue

from autobahn.wamp.types import RegisterOptions
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession


class Component(ApplicationSession):

    """
    Application component that produces progressive results.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")

        @inlineCallbacks
        def longop(n, details=None):
            if details.progress:
                # caller can (and requested to) consume progressive results
                for i in range(n):
                    details.progress(i)
                    yield sleep(1)
            else:
                # process like a normal call (not producing progressive results)
                yield sleep(1 * n)
            returnValue(n)

        yield self.register(longop, 'com.myapp.longop', RegisterOptions(details_arg='details'))

        print("procedures registered")


if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
