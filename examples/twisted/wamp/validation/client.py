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

from autobahn.wamp.types import PublishOptions
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession


class Component(ApplicationSession):

    """
    An application component that publishes an event every second.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")

        def add2(a, b):
            return a + b

        yield self.register(add2, 'com.myapp.add2')

        def on_event(i):
            print("Got event: {}".format(i))

        yield self.subscribe(on_event, 'com.myapp.topic1')

        counter = 0
        while True:
            print(".")

            try:
                res = yield self.call('com.myapp.add2', counter, 7)
                print("Got call result: {}".format(res))
            except Exception as e:
                print("Call failed: {}".format(e))

            try:
                publication = yield self.publish('com.myapp.topic1', counter,
                                                 options=PublishOptions(acknowledge=True, discloseMe=True, excludeMe=False))
                print("Event published with publication ID {}".format(publication.id))
            except Exception as e:
                print("Publication failed: {}".format(e))

            counter += 1
            yield sleep(1)


if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
