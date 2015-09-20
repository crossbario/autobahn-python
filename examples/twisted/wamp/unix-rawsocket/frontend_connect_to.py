#
# this version of frontend shows the highest-level API, ApplicationSession
#

from __future__ import print_function

from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet.defer import inlineCallbacks, Deferred
from twisted.internet.task import react

from autobahn.twisted.wamp import connect_to
from autobahn.wamp.types import ComponentConfig

# the example ApplicationSession subclass
from clientsession import ClientSession


@inlineCallbacks
def main(reactor):
    # we can use "real" Twisted endpoint objects (or even just a
    # string, which gets passed to clientFromString)
    rawsocket_unix_transport = {
        "type": "rawsocket",
        "endpoint": UNIXClientEndpoint(reactor, '/tmp/cb-raw'),
        # "endpoint": "unix:path=/tmp/cb-raw",
    }

    done = Deferred()
    session = ClientSession(ComponentConfig(u"realm1", None))
    session.on.disconnect(done.callback)

    connection = yield connect_to(reactor, rawsocket_unix_transport, session)
    print("Connection: {}".format(connection))

    yield done


if __name__ == '__main__':
    # "Twisted native" and other "lower-level" usage
    react(main)
    print("exiting.")
