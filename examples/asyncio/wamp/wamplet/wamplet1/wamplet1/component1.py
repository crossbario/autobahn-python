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

import datetime

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

from autobahn import wamp
from autobahn.asyncio.wamp import ApplicationSession

from calculator import Calculator


# WAMP application component with our app code.
##
class Component1(ApplicationSession):

    @asyncio.coroutine
    def onJoin(self, details):

        # register a function that can be called remotely
        ##
        def utcnow():
            now = datetime.datetime.utcnow()
            return now.strftime("%Y-%m-%dT%H:%M:%SZ")

        reg = yield from self.register(utcnow, 'com.timeservice.now')
        print("Procedure registered with ID {}".format(reg.id))

        # create an application object that exposes methods for remoting
        ##
        self.calculator = Calculator()

        # register all methods on the "calculator" decorated with "@wamp.register"
        ##
        results = yield from self.register(self.calculator)
        for res in results:
            if isinstance(res, wamp.protocol.Registration):
                print("Ok, registered procedure with registration ID {}".format(res.id))
            else:
                print("Failed to register procedure: {}".format(res))

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


def make(config):
    ##
    # This component factory creates instances of the
    # application component to run.
    ##
    # The function will get called either during development
    # using the ApplicationRunner below, or as  a plugin running
    # hosted in a WAMPlet container such as a Crossbar.io worker.
    ##
    if config:
        return Component1(config)
    else:
        # if no config given, return a description of this WAMPlet ..
        return {'label': 'Awesome WAMPlet 1',
                'description': 'This is just a test WAMPlet that provides some procedures to call.'}


if __name__ == '__main__':
    from autobahn.asyncio.wamp import ApplicationRunner

    # test drive the component during development ..
    runner = ApplicationRunner(
        url="ws://127.0.0.1:8080/ws",
        realm="realm1",
        debug=False,  # low-level WebSocket debugging
        debug_wamp=False,  # WAMP protocol-level debugging
        debug_app=True)  # app-level debugging

    runner.run(make)
