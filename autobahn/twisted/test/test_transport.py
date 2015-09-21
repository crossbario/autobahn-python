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

from __future__ import absolute_import

from mock import patch

from autobahn.twisted.connection import _check_twisted_endpoint
from autobahn.wamp.connection import check_endpoint

from twisted.trial import unittest
from twisted.internet.endpoints import clientFromString, serverFromString
from twisted.internet import reactor

try:
    from twisted.internet.ssl import optionsForClientTLS, CertificateOptions
    _OLD_TWISTED = False
except ImportError:
    _OLD_TWISTED = True


class TestEndpointTwistedObjects(unittest.TestCase):
    """
    Confirms we can pass real Twisted objects into check_endpoint
    """
    def test_endpoint_string_client(self):
        with patch('autobahn.twisted.connection.clientFromString') as cfs:
            self.assertTrue(_check_twisted_endpoint("tcp:host=localhost:port=1234"))
            self.assertTrue(cfs.mock_called)

    def test_endpoint_string_client_invalid(self):
        # bonus points if we mock clientFromString to raise
        # instead of depending on badparser being a bad plugin name?
        self.assertRaises(Exception, _check_twisted_endpoint, "badparser:foo=bar")

    def test_istream_client(self):
        ep = clientFromString(reactor, "tcp:host=127.0.0.1:port=1234")
        self.assertTrue(_check_twisted_endpoint(ep))

    def test_istream_server_but_connect(self):
        ep = serverFromString(reactor, "tcp:port=1234")
        self.assertRaises(Exception, _check_twisted_endpoint, ep)

    def test_bogus_endpoint(self):
        self.assertRaises(Exception, _check_twisted_endpoint, object())

    def test_bogus_endpoint_from_api(self):
        self.assertRaises(
            Exception, check_endpoint, object(),
            check_native_endpoint=_check_twisted_endpoint,
        )

    def test_bogus_endpoint_from_api_no_checker(self):
        self.assertRaises(
            Exception, check_endpoint, object(),
            check_native_endpoint=None,
        )

    def test_missing_native_check_tls(self):
        # if we provide TLS, we *need* a native checker
        self.assertRaises(
            Exception, check_endpoint, dict(host="wamp.ws", tls=True),
            check_native_endpoint=None,
        )

    def test_non_tcp_endpoint_from_api(self):
        # should skip TLS-checking of non-TCP endpoints
        self.assertTrue(
            check_endpoint(
                {
                    "type": "unix",
                    "path": "/dev/null",
                },
                check_native_endpoint=_check_twisted_endpoint,
            )
        )

    def test_tcp_no_tls(self):
        # should skip TLS checking if we don't provide any TLS config
        # at all
        self.assertTrue(
            check_endpoint(
                {
                    "type": "tcp",
                    "host": "127.0.0.1",
                },
                check_native_endpoint=_check_twisted_endpoint,
            )
        )

    def test_tls_wrong_bool(self):
        self.assertRaises(
            Exception, _check_twisted_endpoint,
            {
                "host": "wamp.ws",
                "tls": False,
            },
        )

    def test_tls_bool(self):
        if _OLD_TWISTED:
            raise unittest.SkipTest()
        self.assertTrue(_check_twisted_endpoint({"tls": True}))

    def test_tls_certificate_options(self):
        if _OLD_TWISTED:
            raise unittest.SkipTest()
        co = CertificateOptions()
        self.assertTrue(_check_twisted_endpoint({"tls": co}))

    def test_tls_connection_creator(self):
        if _OLD_TWISTED:
            raise unittest.SkipTest()
        co = optionsForClientTLS(u"example.com")
        self.assertTrue(_check_twisted_endpoint({"tls": co}))
