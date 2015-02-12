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

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")

        counter = 0
        topics = ['com.myapp.topic1', 'com.foobar.topic2']
        while True:
            for topic in topics:
                try:
                    yield self.publish(topic, counter, options=PublishOptions(acknowledge=True))
                    print("Event published to {}".format(topic))
                except Exception as e:
                    print("Publication to {} failed: {}".format(topic, e))

            counter += 1
            yield sleep(1)


if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(Component)
