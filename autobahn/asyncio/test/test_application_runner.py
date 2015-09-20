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

import unittest2 as unittest

import txaio

from autobahn.wamp.runner import Connection
from autobahn.wamp.protocol import _ListenerCollection
from autobahn.wamp.interfaces import ISession

from autobahn.asyncio.wamp import ApplicationRunner

# Asyncio tests.
try:
    import asyncio
    from unittest.mock import Mock
    from asyncio.test_utils import run_once
except ImportError:
    # Trollius >= 0.3 was renamed to asyncio
    # noinspection PyUnresolvedReferences
    import trollius as asyncio
    from mock import Mock

    def run_once(loop):
        """
        copy-pasta from modern asyncio
        """
        loop.stop()
        loop.run_forever()
        asyncio.gather(*asyncio.Task.all_tasks())


class FakeSession(object):
    def __init__(self, config):
        self.config = config
        self.on = _ListenerCollection(['join', 'leave', 'ready', 'connect', 'disconnect'])

    def onOpen(self, *args, **kw):
        print('onOpen', args, kw)

    def leave(self, *args, **kw):
        return txaio.create_future_success(None)


ISession.register(FakeSession)


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

    def setUp(self):
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
            self.ssl_context = ssl.create_default_context()
        except AttributeError:
            self.ssl_context = True

    def test_explicit_SSLContext(self):
        '''
        Ensure that loop.create_connection is called with the exact SSL
        context object that is passed (as ssl) to the __init__ method of
        ApplicationRunner.
        '''
        loop = Mock()
        loop.run_until_complete = Mock(return_value=(Mock(), Mock()))
        transports = [
            {
                "type": "websocket",
                "url": u"wss://localhost:8080/ws",
                "endpoint": {
                    "type": "tcp",
                    "host": "127.0.0.1",
                    "port": 8080,
                    "tls": self.ssl_context,
                },
            },
        ]
        runner = ApplicationRunner(transports, u'realm', loop=loop,)
        runner.run(FakeSession)  # returns future

        self.assertIs(loop.create_connection.call_args[1]['ssl'], self.ssl_context)

    def test_omitted_SSLContext_insecure(self):
        '''
        Ensure that loop.create_connection is called with ssl=False
        if no ssl argument is passed to the __init__ method of
        ApplicationRunner and the websocket URL starts with "ws:".
        '''
        loop = Mock()
        loop.create_connection = Mock(return_value=txaio.create_future(result=(Mock(), Mock())))
        transports = [{
            "type": "websocket",
            "url": u'ws://127.0.0.1:8080/ws',
            "endpoint": {"type": "tcp", "host": '127.0.0.1', "port": 8080}
        }]
        connection = Connection(transports, session_factory=FakeSession, loop=loop)
        connection.open()  # returns future

        # annoying, but you have to "do a trip" through the
        # event-loop to get callbacks called on Futures...
        run_once(asyncio.get_event_loop())

        self.assertTrue(not loop.create_connection.call_args[1]['ssl'])

    def test_omitted_SSLContext_secure(self):
        '''
        Ensure that loop.create_connection is called with ssl=True
        if no ssl argument is passed to the __init__ method of
        ApplicationRunner and the websocket URL starts with "wss:".
        '''
        loop = Mock()
        loop.create_connection = Mock(return_value=txaio.create_future(result=(Mock(), Mock())))
        transports = [{
            "type": "websocket",
            "url": u'wss://127.0.0.1:8080/ws',
            "endpoint": {"type": "tcp", "host": '127.0.0.1', "port": 8080}
        }]
        connection = Connection(transports, session_factory=FakeSession, loop=loop)
        connection.open()

        self.assertTrue(loop.create_connection.call_args[1]['ssl'])
        asyncio.get_event_loop().stop()

    def test_conflict_SSL_True_with_ws_url(self):
        '''
        ApplicationRunner must raise an exception if given an ssl value of True
        but only a "ws:" URL.
        '''
        loop = Mock()
        loop.create_connection = Mock(return_value=txaio.create_future(result=(Mock(), Mock())))
        transports = [{
            "type": "websocket",
            "url": u'ws://127.0.0.1:8080/ws',
            "endpoint": {"type": "tcp", "host": '127.0.0.1', "port": 8080, "tls": True}
        }]
        connection = Connection(transports, session_factory=FakeSession, loop=loop)

        # should get an error when we try to open a "tls=True" connection with a "ws://" URL
        self.assertRaises(RuntimeError, connection.open)

    def test_conflict_SSLContext_with_ws_url(self):
        '''
        ApplicationRunner must raise an exception if given an ssl value that is
        an instance of SSLContext, but only a "ws:" URL.
        '''
        loop = Mock()
        loop.run_until_complete = Mock(return_value=(Mock(), Mock()))
        transports = [
            {
                "type": "websocket",
                "url": u"ws://localhost:8080/ws",
                "endpoint": {
                    "type": "tcp",
                    "host": "127.0.0.1",
                    "port": 8080,
                    "tls": self.ssl_context,
                },
            },
        ]

        # validates all transports when we set up the Runner
        self.assertRaises(RuntimeError, ApplicationRunner, transports, u'realm1', loop=loop)
