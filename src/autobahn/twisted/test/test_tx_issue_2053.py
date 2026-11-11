###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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

"""
Regression tests for autobahn-python#2053 (Twisted): ApplicationRunner.run()
with start_reactor=False and an endpoint, but no reactor.
"""

# t.i.reactor doesn't exist until we've imported it once, but we
# need it to exist so we can @patch it out in the tests ...
from twisted.internet import reactor  # noqa
from unittest.mock import Mock, patch

from twisted.internet.defer import inlineCallbacks, succeed
from twisted.trial import unittest

from autobahn.twisted.wamp import ApplicationRunner, ApplicationSession


class _ConnectedEndpoint:
    """
    An endpoint whose connect() succeeds right away.
    """

    def __init__(self, proto):
        self.proto = proto

    def connect(self, factory):
        return succeed(self.proto)


class TestRunnerEndpointWithoutReactor(unittest.TestCase):
    @patch("twisted.internet.reactor")
    @inlineCallbacks
    def test_connect_with_endpoint_and_no_reactor(self, fakereactor):
        # The connect Deferred used to fail with AttributeError: the shutdown
        # cleanup was registered on reactor=None. It now uses the global reactor.
        proto = Mock()
        runner = ApplicationRunner("ws://127.0.0.1:1/ws", "realm1")
        res = yield runner.run(
            ApplicationSession,
            start_reactor=False,
            endpoint=_ConnectedEndpoint(proto),
        )
        self.assertIs(res, proto)
        fakereactor.addSystemEventTrigger.assert_called_once()
        args = fakereactor.addSystemEventTrigger.call_args[0]
        self.assertEqual(args[:2], ("before", "shutdown"))
        self.assertIs(args[3], proto)
        # not started, not stopped: the caller runs the reactor
        self.assertEqual(fakereactor.run.call_count, 0)
        self.assertEqual(fakereactor.stop.call_count, 0)

    @inlineCallbacks
    def test_connect_with_endpoint_and_reactor(self):
        # a reactor passed in is the one used
        proto = Mock()
        myreactor = Mock()
        runner = ApplicationRunner("ws://127.0.0.1:1/ws", "realm1")
        res = yield runner.run(
            ApplicationSession,
            start_reactor=False,
            endpoint=_ConnectedEndpoint(proto),
            reactor=myreactor,
        )
        self.assertIs(res, proto)
        myreactor.addSystemEventTrigger.assert_called_once()
