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

#
# this version of frontend shows the medium-level API, "Connection"
# along with the Twisted "react()" API.
#
# (For a higher-level/simpler example, see frontend_appsession.py)
#

from __future__ import print_function

import random

from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import react

from autobahn.twisted.wamp import Connection
from autobahn.wamp.types import ComponentConfig

# the example ApplicationSession subclass
from clientsession import ClientSession


# this transport has an invalid unix-socket path
bad_transport = {
    "type": "rawsocket",
    "endpoint": {
        "type": "unix",
        "path": "/tmp/cb-raw-foo",
    }
}

rawsocket_unix_transport = {
    "type": "rawsocket",
    "endpoint": {
        "type": "unix",
        "path": "/tmp/cb-raw",
    }
}

websocket_tcp_transport = {
    "type": "websocket",
    "url": u"ws://localhost:8080/ws",
    "endpoint": {
        "type": "tcp",
        "host": "127.0.0.1",
        "port": 8080,
    }
}


@inlineCallbacks
def main(reactor):
    # transports can be an iterable, or a list. Try enabling different
    # transports to see what happens.

    # you can use "native" Twisted endpoint objects
    native_object_transport = {
        "type": "websocket",
        "url": u"ws://localhost:8080/ws",
        "endpoint": UNIXClientEndpoint(reactor, '/tmp/cb-web')
    }

    # ...and also plain strings, which will be passed ultimately to
    # clientFromString
    endpoint_object_transport = {
        "type": "websocket",
        "url": u"ws://localhost:8080/ws",
        "endpoint": "unix:path=/tmp/cb-web",
    }

    transports = [
        # bad_transport,
        native_object_transport,
        endpoint_object_transport,
        rawsocket_unix_transport,
        websocket_tcp_transport,
        # {"just": "completely bogus"}
    ]

    def random_transports():
        while True:
            t = random.choice(transports)
            print("Returning transport: {}".format(t))
            yield t

    session = ClientSession(ComponentConfig(u"realm1"))
    connection = Connection(
        session,
        random_transports(),
        reactor,
    )

    # the 'ready' event means that we've joined a WAMP session
    # successfully, *and* the onJoin has *completed*; see
    # clientsession.py to enable different behavior that makes ready
    # fire sooner. These listeners should be hooked up before
    # connection.open() is called.
    def on_ready(session):
        print("Session ready:", session)
    session.on('ready', on_ready)

    print("Connection:", connection)
    yield connection.open()
    print("disconnected")


if __name__ == '__main__':
    react(main)
