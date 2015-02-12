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

from autobahn.twisted.wamp import Application


app = Application()


def onEvent(msg):
    print("got event: {}".format(msg))


@app.register('com.example.triggersubscribe')
def triggerSubscribe():
    print("triggersubscribe() called")
    yield app.session.subscribe(onEvent, 'com.example.topic1')


@app.signal('onjoined')
def onjoined():
    print("realm joined!")


if __name__ == "__main__":
    app.run("ws://localhost:8080/ws", "realm1", standalone=True)
