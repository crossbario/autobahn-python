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
# this version of frontend shows the highest-level API, ApplicationSession
#

from __future__ import print_function

from autobahn.twisted.wamp import Connection, run

# the example ApplicationSession subclass
from clientsession import ClientSession

do_tls = False
if do_tls:
    from twisted.internet._sslverify import OpenSSLCertificateAuthorities
    from twisted.internet.ssl import CertificateOptions
    from OpenSSL import crypto
    cert = crypto.load_certificate(
        crypto.FILETYPE_PEM,
        unicode(open('../pubsub/tls/server.crt', 'r').read())
    )
    tls_options = CertificateOptions(
        trustRoot=OpenSSLCertificateAuthorities([cert]),
    )

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
if do_tls:
    websocket_tcp_transport['url'] = u"wss://localhost:9983/ws"
    websocket_tcp_transport['endpoint']['port'] = 9983
    websocket_tcp_transport['endpoint']['tls'] = tls_options
    print("\nConfigured for TLS; server should be on {url}\n".format(**websocket_tcp_transport))

if __name__ == '__main__':
    connection = Connection(
        transports=[websocket_tcp_transport],
        realm=u"realm1",
        session_factory=ClientSession,
    )
    run(connection, log_level='debug')

