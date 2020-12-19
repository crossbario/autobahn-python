###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
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

import os
import unittest
from txaio.testutil import replace_loop

if os.environ.get('USE_TWISTED', False):
    from unittest.mock import patch
    from zope.interface import implementer
    from twisted.internet.interfaces import IReactorTime

    @implementer(IReactorTime)
    class FakeReactor(object):
        '''
        This just fakes out enough reactor methods so .run() can work.
        '''
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

        @patch('txaio.use_twisted')
        @patch('txaio.start_logging')
        @patch('txaio.config')
        def test_connect_error(self, *args):
            '''
            Ensure the runner doesn't swallow errors and that it exits the
            reactor properly if there is one.
            '''
            try:
                from autobahn.twisted.wamp import ApplicationRunner
                from twisted.internet.error import ConnectionRefusedError
                # the 'reactor' member doesn't exist until we import it
                from twisted.internet import reactor  # noqa: F401
            except ImportError:
                raise unittest.SkipTest('No twisted')

            runner = ApplicationRunner('ws://localhost:1', 'realm')
            exception = ConnectionRefusedError("It's a trap!")

            with patch('twisted.internet.reactor', FakeReactor(exception)) as mockreactor:
                self.assertRaises(
                    ConnectionRefusedError,
                    # pass a no-op session-creation method
                    runner.run, lambda _: None, start_reactor=True
                )
                self.assertTrue(mockreactor.stop_called)
else:
    import asyncio
    from unittest.mock import patch, Mock

    from autobahn.asyncio.wamp import ApplicationRunner

    class TestApplicationRunner(unittest.TestCase):
        '''
        Test the autobahn.asyncio.wamp.ApplicationRunner class.
        '''
        def _assertRaisesRegex(self, exception, error, *args, **kw):
            try:
                self.assertRaisesRegex
            except AttributeError:
                f = self.assertRaisesRegexp
            else:
                f = self.assertRaisesRegex
            f(exception, error, *args, **kw)

        def test_explicit_SSLContext(self):
            '''
            Ensure that loop.create_connection is called with the exact SSL
            context object that is passed (as ssl) to the __init__ method of
            ApplicationRunner.
            '''
            with replace_loop(Mock()) as loop:
                with patch.object(asyncio, 'get_event_loop', return_value=loop):
                    loop.run_until_complete = Mock(return_value=(Mock(), Mock()))
                    ssl = {}
                    runner = ApplicationRunner('ws://127.0.0.1:8080/ws', 'realm',
                                               ssl=ssl)
                    runner.run('_unused_')
                    self.assertIs(ssl, loop.create_connection.call_args[1]['ssl'])

        def test_omitted_SSLContext_insecure(self):
            '''
            Ensure that loop.create_connection is called with ssl=False
            if no ssl argument is passed to the __init__ method of
            ApplicationRunner and the websocket URL starts with "ws:".
            '''
            with replace_loop(Mock()) as loop:
                with patch.object(asyncio, 'get_event_loop', return_value=loop):
                    loop.run_until_complete = Mock(return_value=(Mock(), Mock()))
                    runner = ApplicationRunner('ws://127.0.0.1:8080/ws', 'realm')
                    runner.run('_unused_')
                    self.assertIs(False, loop.create_connection.call_args[1]['ssl'])

        def test_omitted_SSLContext_secure(self):
            '''
            Ensure that loop.create_connection is called with ssl=True
            if no ssl argument is passed to the __init__ method of
            ApplicationRunner and the websocket URL starts with "wss:".
            '''
            with replace_loop(Mock()) as loop:
                with patch.object(asyncio, 'get_event_loop', return_value=loop):
                    loop.run_until_complete = Mock(return_value=(Mock(), Mock()))
                    runner = ApplicationRunner('wss://127.0.0.1:8080/wss', 'realm')
                    runner.run(self.fail)
                    self.assertIs(True, loop.create_connection.call_args[1]['ssl'])

        def test_conflict_SSL_True_with_ws_url(self):
            '''
            ApplicationRunner must raise an exception if given an ssl value of True
            but only a "ws:" URL.
            '''
            with replace_loop(Mock()) as loop:
                loop.run_until_complete = Mock(return_value=(Mock(), Mock()))
                runner = ApplicationRunner('ws://127.0.0.1:8080/wss', 'realm',
                                           ssl=True)
                error = (r'^ssl argument value passed to ApplicationRunner '
                         r'conflicts with the "ws:" prefix of the url '
                         r'argument\. Did you mean to use "wss:"\?$')
                self._assertRaisesRegex(Exception, error, runner.run, '_unused_')

        def test_conflict_SSLContext_with_ws_url(self):
            '''
            ApplicationRunner must raise an exception if given an ssl value that is
            an instance of SSLContext, but only a "ws:" URL.
            '''
            import ssl
            try:
                # Try to create an SSLContext, to be as rigorous as we can be
                # by avoiding making assumptions about the ApplicationRunner
                # implementation. If we happen to be on a Python that has no
                # SSLContext, we pass ssl=True, which will simply cause this
                # test to degenerate to the behavior of
                # test_conflict_SSL_True_with_ws_url (above). In fact, at the
                # moment (2015-05-10), none of this matters because the
                # ApplicationRunner implementation does not check to require
                # that its ssl argument is either a bool or an SSLContext. But
                # that may change, so we should be careful.
                ssl.create_default_context
            except AttributeError:
                context = True
            else:
                context = ssl.create_default_context()

            with replace_loop(Mock()) as loop:
                loop.run_until_complete = Mock(return_value=(Mock(), Mock()))
                runner = ApplicationRunner('ws://127.0.0.1:8080/wss', 'realm',
                                           ssl=context)
                error = (r'^ssl argument value passed to ApplicationRunner '
                         r'conflicts with the "ws:" prefix of the url '
                         r'argument\. Did you mean to use "wss:"\?$')
                self._assertRaisesRegex(Exception, error, runner.run, '_unused_')
