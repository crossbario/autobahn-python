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

# t.i.reactor doesn't exist until we've imported it once, but we
# need it to exist so we can @patch it out in the tests ...
from twisted.internet import reactor  # noqa
from unittest.mock import patch, Mock

from twisted.internet.defer import inlineCallbacks, succeed
from twisted.trial import unittest

from autobahn.twisted.wamp import ApplicationRunner


def raise_error(*args, **kw):
    raise RuntimeError("we always fail")


class TestApplicationRunner(unittest.TestCase):
    @patch('twisted.internet.reactor')
    def test_runner_default(self, fakereactor):
        fakereactor.connectTCP = Mock(side_effect=raise_error)
        runner = ApplicationRunner('ws://fake:1234/ws', 'dummy realm')

        # we should get "our" RuntimeError when we call run
        self.assertRaises(RuntimeError, runner.run, raise_error)

        # both reactor.run and reactor.stop should have been called
        self.assertEqual(fakereactor.run.call_count, 1)
        self.assertEqual(fakereactor.stop.call_count, 1)

    @patch('twisted.internet.reactor')
    @inlineCallbacks
    def test_runner_no_run(self, fakereactor):
        fakereactor.connectTCP = Mock(side_effect=raise_error)
        runner = ApplicationRunner('ws://fake:1234/ws', 'dummy realm')

        try:
            yield runner.run(raise_error, start_reactor=False)
            self.fail()  # should have raise an exception, via Deferred

        except RuntimeError as e:
            # make sure it's "our" exception
            self.assertEqual(e.args[0], "we always fail")

        # neither reactor.run() NOR reactor.stop() should have been called
        # (just connectTCP() will have been called)
        self.assertEqual(fakereactor.run.call_count, 0)
        self.assertEqual(fakereactor.stop.call_count, 0)

    @patch('twisted.internet.reactor')
    def test_runner_no_run_happypath(self, fakereactor):
        proto = Mock()
        fakereactor.connectTCP = Mock(return_value=succeed(proto))
        runner = ApplicationRunner('ws://fake:1234/ws', 'dummy realm')

        d = runner.run(Mock(), start_reactor=False)

        # shouldn't have actually connected to anything
        # successfully, and the run() call shouldn't have inserted
        # any of its own call/errbacks. (except the cleanup handler)
        self.assertFalse(d.called)
        self.assertEqual(1, len(d.callbacks))

        # neither reactor.run() NOR reactor.stop() should have been called
        # (just connectTCP() will have been called)
        self.assertEqual(fakereactor.run.call_count, 0)
        self.assertEqual(fakereactor.stop.call_count, 0)

    @patch('twisted.internet.reactor')
    def test_runner_bad_proxy(self, fakereactor):
        proxy = 'myproxy'

        self.assertRaises(
            AssertionError,
            ApplicationRunner,
            'ws://fake:1234/ws', 'dummy realm',
            proxy=proxy
        )

    @patch('twisted.internet.reactor')
    def test_runner_proxy(self, fakereactor):
        proto = Mock()
        fakereactor.connectTCP = Mock(return_value=succeed(proto))

        proxy = {'host': 'myproxy', 'port': 3128}

        runner = ApplicationRunner('ws://fake:1234/ws', 'dummy realm', proxy=proxy)

        d = runner.run(Mock(), start_reactor=False)

        # shouldn't have actually connected to anything
        # successfully, and the run() call shouldn't have inserted
        # any of its own call/errbacks. (except the cleanup handler)
        self.assertFalse(d.called)
        self.assertEqual(1, len(d.callbacks))

        # neither reactor.run() NOR reactor.stop() should have been called
        # (just connectTCP() will have been called)
        self.assertEqual(fakereactor.run.call_count, 0)
        self.assertEqual(fakereactor.stop.call_count, 0)
