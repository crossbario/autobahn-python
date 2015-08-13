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

from __future__ import print_function

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

from os import environ
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import ssl


class Component(ApplicationSession):
    """
    An application component that publishes an event every second.
    """

    @asyncio.coroutine
    def onJoin(self, details):
        counter = 0
        while True:
            print("publish: com.myapp.topic1", counter)
            self.publish('com.myapp.topic1', counter)
            counter += 1
            yield from asyncio.sleep(1)


if __name__ == '__main__':
    # see README; this way everything accesses same cert-files
    cert_path = '../../../../twisted/wamp/pubsub/tls/server.crt'
    print(cert_path)
    # create an ssl.Context using just our self-signed cert as the CA certificates
    options = ssl.create_default_context(cadata=open(cert_path, 'r').read())
    # ...which we pass as "ssl=" to ApplicationRunner (passed to loop.create_connection)
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", "wss://127.0.0.1:8083/ws"),
        u"crossbardemo",
        ssl=options,  # try removing this, but still use self-signed cert
        debug_wamp=False,  # optional; log many WAMP details
        debug=False,  # optional; log even more details
    )
    runner.run(Component)
