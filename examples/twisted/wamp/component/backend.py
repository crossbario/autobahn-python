

from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from autobahn.wamp.types import RegisterOptions
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet._sslverify import OpenSSLCertificateAuthorities
from twisted.internet.ssl import CertificateOptions
from twisted.internet.ssl import optionsForClientTLS, Certificate
from OpenSSL import crypto
from os.path import join, split
import six


examples_dir = join(split(__file__)[0], '..', '..', '..')
cert_fname = join(examples_dir, 'router', '.crossbar', 'server.crt')
if False:
    cert = crypto.load_certificate(
        crypto.FILETYPE_PEM,
        six.u(open(cert_fname, 'r').read())
    )
    # tell Twisted to use just the one certificate we loaded to verify connections
    options = CertificateOptions(
        trustRoot=OpenSSLCertificateAuthorities([cert]),
    )
else:
    cert = Certificate.loadPEM(six.u(open(cert_fname, 'r').read()))
    options = optionsForClientTLS(
        hostname=u'localhost',
        trustRoot=cert,
    )

component = Component(
    transports=[
        {
            u"type": u"websocket",
            u"url": u"ws://localhost:8080/ws",
            u"endpoint": {
                u"type": u"tcp",
                u"host": u"localhost",
                u"port": 8080,
#                "tls": options,
#                "tls": {
#                    u"hostname": u"localhost",
#                    u"trust_root": cert_fname,
#                },
            },
            u"options": {
                u"open_handshake_timeout": 100,
            }
        },
    ],
    realm=u"crossbardemo",
)


@component.on_join
def join(session, details):
    print("joined {}: {}".format(session, details))


@component.register(
    u"example.foo",
    options=RegisterOptions(details_arg='details'),
)
@inlineCallbacks
def foo(*args, **kw):
    print("foo({}, {})".format(args, kw))
    for x in range(5, 0, -1):
        print("  returning in {}".format(x))
        yield sleep(1)
    print("returning '42'")
    returnValue(42)


if __name__ == "__main__":
    run([component])
