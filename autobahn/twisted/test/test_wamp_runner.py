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

import unittest
from unittest.mock import patch

from zope.interface import implementer

from twisted.internet.interfaces import IReactorTime


@implementer(IReactorTime)
class FakeReactor(object):
    """
    This just fakes out enough reactor methods so .run() can work.
    """

    stop_called = False

    def __init__(self, to_raise):
        self.stop_called = False
        self.to_raise = to_raise
        self.delayed = []

    def run(self, *args, **kw):
        raise self.to_raise

    def stop(self):
        self.stop_called = True

    def callLater(self, delay, func, *args, **kwargs):
        self.delayed.append((delay, func, args, kwargs))

    def connectTCP(self, *args, **kw):
        raise RuntimeError("ConnectTCP shouldn't get called")


class TestWampTwistedRunner(unittest.TestCase):
    # XXX should figure out *why* but the test_protocol timeout
    # tests fail if we *don't* patch out this txaio stuff. So,
    # presumably it's messing up some global state that both tests
    # implicitly depend on ...

    @patch("txaio.use_twisted")
    @patch("txaio.start_logging")
    @patch("txaio.config")
    def test_connect_error(self, *args):
        """
        Ensure the runner doesn't swallow errors and that it exits the
        reactor properly if there is one.
        """
        try:
            from autobahn.twisted.wamp import ApplicationRunner

            # the 'reactor' member doesn't exist until we import it
            from twisted.internet import reactor  # noqa: F401
            from twisted.internet.error import ConnectionRefusedError
        except ImportError:
            raise unittest.SkipTest("No twisted")

        runner = ApplicationRunner("ws://localhost:1", "realm")
        exception = ConnectionRefusedError("It's a trap!")

        with patch("twisted.internet.reactor", FakeReactor(exception)) as mockreactor:
            self.assertRaises(
                ConnectionRefusedError,
                # pass a no-op session-creation method
                runner.run,
                lambda _: None,
                start_reactor=True,
            )
            self.assertTrue(mockreactor.stop_called)
