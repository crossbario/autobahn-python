import os

import txaio

from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import SSL4ClientEndpoint
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet.ssl import (
    optionsForClientTLS,
    trustRootFromCertificates,
    Certificate,
    CertificateOptions,
)
from twisted.internet import reactor

from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import Session

# This uses the new-api with various Twisted native objects. For the
# Unix socket things, yo'll have to add a transport to "config.json"
# like this:
#    {
#        "type": "websocket",
#        "endpoint": {
#            "type": "unix",
#            "path": "unix-websocket"
#        }
#    }
# ...then, the socket will appear in the .crossbar directory as
# "unix-websocket". Everything in here presumes yo're using the
# "example/router/.crossbar" with config.json linked to either
# "config-no-tls.json" or "config-tls.json"


class Foo(Session):
    def __init__(self, *args, **kw):
        1 / 0


@inlineCallbacks
def setup(reactor, session):
    print("bob created", session)

    def on_join(session, details):
        print("bob joined", session, details)

    session.on("join", on_join)
    yield sleep(5)
    print("bob done sleeping")


#    session.leave()


if __name__ == "__main__":
    cert_fname = os.path.join(
        os.path.split(__file__)[0],
        "..",
        "..",
        "..",
        "..",
        "router",
        ".crossbar",
        "ca.cert.pem",
    )
    inter_cert_fname = os.path.join(
        os.path.split(__file__)[0],
        "..",
        "..",
        "..",
        "..",
        "router",
        ".crossbar",
        "intermediate.cert.pem",
    )

    tls_transport = {
        "type": "websocket",
        "url": "wss://127.0.0.1:8083/ws",
        "endpoint": SSL4ClientEndpoint(
            reactor,
            "127.0.0.1",
            8083,
            optionsForClientTLS(
                "localhost",
                # XXX why do I need BOTH the intermediate and actual
                # cert? Did I create the CA/intermediate certificates
                # incorrectly?
                trustRoot=trustRootFromCertificates(
                    [
                        Certificate.loadPEM(open(cert_fname).read()),
                        Certificate.loadPEM(open(inter_cert_fname).read()),
                    ]
                ),
            ),
        ),
    }

    unix_transport = {
        "type": "websocket",
        "url": "ws://localhost/ws",
        "endpoint": UNIXClientEndpoint(
            reactor,
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..",
                "..",
                "..",
                "router",
                ".crossbar",
                "intermediate.cert.pem",
            ),
        ),
    }

    # this one should produce handshake errors etc, good for testing error-cases:
    tls_transport_untrusted = {
        "type": "websocket",
        "url": "wss://127.0.0.1:8083/ws",
        "endpoint": SSL4ClientEndpoint(
            reactor,
            "127.0.0.1",
            8080,
            optionsForClientTLS("localhost"),
        ),
    }

    clearnet_transport = {
        "type": "websocket",
        "url": "ws://127.0.0.1:8080/ws",
        "endpoint": TCP4ClientEndpoint(reactor, "localhost", 8080),
    }

    transports = [
        tls_transport_untrusted,
        tls_transport,
        clearnet_transport,
    ]

    # try main= vs. setup= to see different exit behavior
    component = Component(main=setup, transports=transports, realm="crossbardemo")
    # component = Component(setup=setup, transports=transports, realm='crossbardemo')

    # can add this confirm logging of more error-cases
    # component.session_factory = Foo
    txaio.start_logging(level="info")
    run(component)
