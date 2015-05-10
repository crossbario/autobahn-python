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

import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest

if os.environ.get('USE_TWISTED', False):
    from mock import patch
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
        def test_connect_error(self):
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
    # Asyncio tests.
    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed to asyncio
        # noinspection PyUnresolvedReferences
        import trollius as asyncio
    from unittest.mock import patch, Mock
    from autobahn.asyncio.wamp import ApplicationRunner


    class TestApplicationRunner(unittest.TestCase):
        '''
        Test the autobahn.asyncio.wamp.ApplicationRunner class.
        '''
        def test_explicit_SSLContext(self):
            '''
            Ensure that loop.create_connection is called with the exact SSL
            context object that is passed (as ssl) to the __init__ method of
            ApplicationRunner.
            '''
            loop = Mock()
            loop.create_connection = Mock()
            with patch.object(asyncio, 'get_event_loop', return_value=loop):
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
            loop = Mock()
            loop.create_connection = Mock()
            with patch.object(asyncio, 'get_event_loop', return_value=loop):
                runner = ApplicationRunner('ws://127.0.0.1:8080/ws', 'realm')
                runner.run('_unused_')
                self.assertIs(False, loop.create_connection.call_args[1]['ssl'])

        def test_omitted_SSLContext_secure(self):
            '''
            Ensure that loop.create_connection is called with ssl=True
            if no ssl argument is passed to the __init__ method of
            ApplicationRunner and the websocket URL starts with "wss:".
            '''
            loop = Mock()
            loop.create_connection = Mock()
            with patch.object(asyncio, 'get_event_loop', return_value=loop):
                runner = ApplicationRunner('wss://127.0.0.1:8080/wss', 'realm')
                runner.run('_unused_')
                self.assertIs(True, loop.create_connection.call_args[1]['ssl'])

        def test_conflict_SSL_True_with_ws_url(self):
            '''
            ApplicationRunner must raise an exception if given an ssl value of True
            but only a "ws:" URL.
            '''
            loop = Mock()
            loop.create_connection = Mock()
            with patch.object(asyncio, 'get_event_loop', return_value=loop):
                runner = ApplicationRunner('ws://127.0.0.1:8080/wss', 'realm',
                                           ssl=True)
                error = ('^ssl argument value passed to ApplicationRunner '
                         'conflicts with the "ws:" prefix of the url '
                         'argument\. Did you mean to use "wss:"\?$')
                self.assertRaisesRegex(Exception, error, runner.run, '_unused_')

        def test_conflict_SSLContext_with_ws_url(self):
            '''
            ApplicationRunner must raise an exception if given an ssl value that is
            an instance of SSLContext, but only a "ws:" URL.
            '''
            import ssl
            loop = Mock()
            loop.create_connection = Mock()
            with patch.object(asyncio, 'get_event_loop', return_value=loop):
                runner = ApplicationRunner('ws://127.0.0.1:8080/wss', 'realm',
                                           ssl=ssl.create_default_context())
                error = ('^ssl argument value passed to ApplicationRunner '
                         'conflicts with the "ws:" prefix of the url '
                         'argument\. Did you mean to use "wss:"\?$')
                self.assertRaisesRegex(Exception, error, runner.run, '_unused_')
