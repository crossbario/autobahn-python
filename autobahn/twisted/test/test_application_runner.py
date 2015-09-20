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

# t.i.reactor doesn't exist until we've imported it once, but we
# need it to exist so we can @patch it out in the tests ...
from twisted.internet import reactor  # noqa
from twisted.internet.defer import inlineCallbacks, succeed, maybeDeferred
from twisted.internet.error import ConnectionRefusedError
from twisted.internet.interfaces import IReactorTime, IReactorCore
from twisted.trial import unittest
from zope.interface import implementer

from mock import Mock

from autobahn.twisted.wamp import ApplicationRunner
from autobahn.wamp.runner import Connection
from autobahn.wamp.exception import TransportLost
from autobahn.wamp.interfaces import ISession
from autobahn.wamp.protocol import _ListenerCollection

import txaio


class FakeSession(object):
    def __init__(self, config):
        self.config = config
        self.on = _ListenerCollection(['join', 'leave', 'ready', 'connect', 'disconnect'])

    def onOpen(self, *args, **kw):
        print('onOpen', args, kw)

    def leave(self, *args, **kw):
        return txaio.create_future_success(None)


@implementer(IReactorTime, IReactorCore)
class FakeReactor(object):
    '''
    This just fakes out enough reactor methods so .run() can work.
    '''
    stop_called = False
    running = True

    def __init__(self, to_raise):
        self.stop_called = False
        self.to_raise = to_raise
        self.delayed = []
        self.when_running = []

    def run(self, *args, **kw):
        if self.to_raise:
            for d in self.when_running:
                txaio.reject(d, self.to_raise)

    def stop(self):
        self.stop_called = True

    def callLater(self, delay, func, *args, **kwargs):
        self.delayed.append((delay, func, args, kwargs))

    def connectTCP(self, *args, **kw):
        pass

    def callWhenRunning(self, method, *args, **kw):
        d = maybeDeferred(method, *args, **kw)
        self.when_running.append(d)


ISession.register(FakeSession)


class TestWampTwistedRunner(unittest.TestCase):
    def test_connect_error(self, *args):
        '''
        Ensure the runner doesn't swallow errors and that it exits the
        reactor properly if there is one.
        '''
        exception = ConnectionRefusedError("It's a trap!")
        mockreactor = FakeReactor(exception)
        runner = ApplicationRunner(u'ws://localhost:1', u'realm', loop=mockreactor)

        self.assertRaises(
            ConnectionRefusedError,
            runner.run, FakeSession,
            start_reactor=True,
        )
        self.assertTrue(mockreactor.stop_called)


def raise_error(*args, **kw):
    raise RuntimeError("we always fail")


class TestApplicationRunner(unittest.TestCase):
    def test_runner_default(self):
        fakereactor = FakeReactor(None)
        fakereactor.run = Mock()
        fakereactor.stop = Mock()
        fakereactor.connectTCP = Mock(side_effect=raise_error)
        runner = ApplicationRunner(u'ws://fake:1234/ws', u'dummy realm', loop=fakereactor)

        # we should get "our" RuntimeError when we call run
        self.assertRaises(RuntimeError, runner.run, raise_error)

        # making test general; if we got a "run()" we should also
        # get a "stop()"
        self.assertEqual(
            fakereactor.run.call_count,
            fakereactor.stop.call_count
        )

    @inlineCallbacks
    def test_runner_no_run(self):
        fakereactor = FakeReactor(None)
        fakereactor.run = Mock()
        fakereactor.stop = Mock()
        fakereactor.connectTCP = Mock(side_effect=raise_error)
        runner = ApplicationRunner(u'ws://fake:1234/ws', u'dummy realm', loop=fakereactor)

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

    def test_runner_no_run_happypath(self):
        fakereactor = FakeReactor(None)
        proto = Mock()
        fakereactor.run = Mock()
        fakereactor.stop = Mock()
        fakereactor.connectTCP = Mock(return_value=succeed(proto))
        runner = ApplicationRunner(u'ws://fake:1234/ws', u'dummy realm', loop=fakereactor)

        d = runner.run(Mock(), start_reactor=False)

        # shouldn't have actually connected to anything
        # successfully
        self.assertFalse(d.called)

        # neither reactor.run() NOR reactor.stop() should have been called
        # (just connectTCP() will have been called)
        self.assertEqual(fakereactor.run.call_count, 0)
        self.assertEqual(fakereactor.stop.call_count, 0)


class TestConnection(unittest.TestCase):
    """
    Connection is generic between asyncio and Twisted, however writing
    tests that work on both is "hard" due to differences in how
    faking out the event-loop works (and, e.g., the fact that
    asyncio needs you to "iterate" the event-loop some arbitrary
    number of times to get Future callbacks to "go").

    So, tests in this test-case should be "generic" in the sense
    of using txaio but can (and do) depend on Twisted reactor
    details to fake things out.
    """
    def setUp(self):
        self.config = dict()  # "should" be a ComponentConfig
        self.loop = FakeReactor(None)
        txaio.config.loop = self.loop
        self.session = FakeSession(self.config)
        # one generic transport for all tests
        self.transports = [{
            "type": "websocket",
            "url": u"ws://localhost:9876/ws",
            "endpoint": {
                "type": "tcp",
                "host": "127.0.0.1",
                "port": 9876,
            }
        }]

        def create_session(config):
            self.config = config
            self.session = FakeSession(config)
            return self.session
        self.connection = Connection(transports=self.transports, session_factory=create_session, loop=self.loop)

    def test_failed_open(self):
        """If the connect fails, the future/deferred from .open() should fail"""
        d = self.connection.open()
        error = Exception("fake error")

        # pretend the connect call failed.
        txaio.reject(self.connection._connecting, error)

        # depending on Twisted impl. details here (i.e. won't work for Future)
        self.assertTrue(d.called)
        self.assertEqual(d.result.value, error)
        # we wanted this error, so ignore it
        txaio.add_callbacks(d, None, lambda _: None)

    def _fail(self, failure):
        failure.printTraceback()
        assert False, "Got errback"

    def test_double_open(self):
        """a second open() before connection is an error"""
        d0 = self.connection.open()
        d0.addErrback(self._fail)
        d1 = self.connection.open()  # should fail; see below

        self.assertFalse(d0.called)
        self.assertTrue(d1.called)

        def check(fail):
            self.assertIsInstance(fail.value, RuntimeError)
        txaio.add_callbacks(d1, None, check)

    def test_successful_open_and_disconnect(self):
        """future/deferred from .open() should callback after disconnect"""
        d = self.connection.open()

        # pretend the connect was successful
        txaio.resolve(self.connection._connecting, None)
        # ...and that we got the on_disconnect event
        self.connection._on_disconnect(self.session, 'closed')

        self.assertTrue(d.called)

    def test_successful_open_and_failed_transport(self):
        """If on_disconnect isn't clean, .open deferred/future should error"""
        d = self.connection.open()

        # pretend the connect was successful
        txaio.resolve(self.connection._connecting, None)
        # ...and that we got the on_disconnect event
        self.connection._on_disconnect(self.session, 'lost')

        self.assertTrue(d.called)
        # ignore this error; we expected it
        txaio.add_callbacks(d, None, lambda _: None)
        return d

    def test_close(self):
        """call session.leave when we have sesion"""
        d0 = self.connection.open()
        d0.addErrback(self._fail)
        # pretend the connect was successful
        txaio.resolve(self.connection._connecting, None)

        # FakeSession.leave() will get called, and return an
        # already-successful Deferred with "None"
        d1 = self.connection.close()
        d1.addErrback(self._fail)

        self.assertTrue(d1.called)

    def test_close_no_session(self):
        """If no session, transport should get closed"""
        d0 = self.connection.open()
        d0.addErrback(self._fail)
        proto = Mock()
        # pretend the connect was successful
        txaio.resolve(self.connection._connecting, proto)
        # fake out that we have no session any longer
        self.connection.session = None

        # FakeSession.leave() will get called, and return an
        # already-successful Deferred with "None"
        self.connection.close()

        self.assertEqual(len(proto.mock_calls), 1)
        self.assertEqual(proto.mock_calls[0][0], 'close')

    def test_close_no_transport(self):
        """TransportLost exception is handled"""
        d0 = self.connection.open()
        d0.addErrback(self._fail)
        proto = Mock()

        def raise_lost():
            raise TransportLost
        proto.close = Mock(side_effect=raise_lost)
        # pretend the connect was successful
        txaio.resolve(self.connection._connecting, proto)
        # fake out that we have no session any longer
        self.connection.session = None

        # FakeSession.leave() will get called, and return an
        # already-successful Deferred with "None"
        d1 = self.connection.close()

        self.assertTrue(d1.called)
