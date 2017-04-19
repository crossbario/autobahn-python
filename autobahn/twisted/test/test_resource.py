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

from __future__ import absolute_import, print_function

from twisted.trial import unittest
from twisted.internet.interfaces import IPushProducer
from zope.interface import implementer
from mock import Mock

from autobahn.twisted.resource import WebSocketResource



class TestResource(unittest.TestCase):

    def test_transport_wrong_interface(self):
        class FakeTransport(object):
            """
            I do not implement IPushProducer
            """
            def getPeer(self):
                return None

        transport = FakeTransport()
        request = Mock()
        request.transport = transport
        request.requestHeaders.getAllRawHeaders = Mock(return_value=dict())
        res = WebSocketResource(Mock())

        with self.assertRaises(RuntimeError) as expected_err:
            res.render(request)
        self.assertTrue("IPushProducer" in str(expected_err.exception))

    def test_transport_producer(self):
        @implementer(IPushProducer)
        class FakeTransport(object):
            called = False

            def getPeer(self):
                return None

            def resumeProducing(self, *args, **kw):
                self.called = True

        transport = FakeTransport()
        request = Mock()
        request.transport = transport
        request.requestHeaders.getAllRawHeaders = Mock(return_value=dict())
        res = WebSocketResource(Mock())
        res.render(request)

        # names of all the calls we made
        calls = [call[0] for call in request.mock_calls]
        self.assertTrue(transport.called)
