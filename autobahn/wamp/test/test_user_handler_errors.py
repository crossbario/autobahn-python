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

import os

if os.environ.get('USE_TWISTED', False):
    from twisted.trial import unittest
    from twisted.internet import defer
    from twisted.python.failure import Failure
    from autobahn.wamp import message, role
    from autobahn.wamp.exception import ProtocolError
    from autobahn.twisted.wamp import ApplicationSession

    class MockTransport:
        def __init__(self):
            self.messages = []

        def send(self, msg):
            self.messages.append(msg)

        def close(self, *args, **kw):
            pass

    class MockApplicationSession(ApplicationSession):
        '''
        This is used by tests, which typically attach their own handler to
        on*() methods. This just collects any errors from onUserError
        '''

        def __init__(self, *args, **kw):
            ApplicationSession.__init__(self, *args, **kw)
            self.errors = []
            self._realm = u'dummy'
            self._transport = MockTransport()

        def onUserError(self, e, msg):
            self.errors.append((e.value, msg))

    def exception_raiser(exc):
        '''
        Create a method that takes any args and always raises the given
        Exception instance.
        '''
        assert isinstance(exc, Exception), "Must derive from Exception"

        def method(*args, **kw):
            raise exc
        return method

    def async_exception_raiser(exc):
        '''
        Create a method that takes any args, and always returns a Deferred
        that has failed.
        '''
        assert isinstance(exc, Exception), "Must derive from Exception"

        def method(*args, **kw):
            try:
                raise exc
            except:
                return defer.fail(Failure())
        return method

    def create_mock_welcome():
        return message.Welcome(
            1234,
            {
                u'broker': role.RoleBrokerFeatures(),
            },
        )

    class TestSessionCallbacks(unittest.TestCase):
        '''
        These test that callbacks on user-overridden ApplicationSession
        methods that produce errors are handled correctly.

        XXX should do state-diagram documenting where we are when each
        of these cases arises :/
        '''

        # XXX sure would be nice to use py.test @fixture to do the
        # async/sync exception-raising stuff (i.e. make each test run
        # twice)...but that would mean switching all test-running over
        # to py-test

        skip = True

        def test_on_join(self):
            session = MockApplicationSession()
            exception = RuntimeError("blammo")
            session.onJoin = exception_raiser(exception)
            msg = create_mock_welcome()

            # give the sesion a WELCOME, from which it should call onJoin
            session.onMessage(msg)

            # make sure we got the right error out of onUserError
            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_join_deferred(self):
            session = MockApplicationSession()
            exception = RuntimeError("blammo")
            session.onJoin = async_exception_raiser(exception)
            msg = create_mock_welcome()

            # give the sesion a WELCOME, from which it should call onJoin
            session.onMessage(msg)

            # make sure we got the right error out of onUserError
            # import traceback
            # traceback.print_exception(*session.errors[0][:3])
            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_leave(self):
            session = MockApplicationSession()
            exception = RuntimeError("boom")
            session.onLeave = exception_raiser(exception)
            msg = message.Abort(u"testing")

            # we haven't done anything, so this is "abort before we've
            # connected"
            session.onMessage(msg)

            # make sure we got the right error out of onUserError
            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_leave_deferred(self):
            session = MockApplicationSession()
            exception = RuntimeError("boom")
            session.onLeave = async_exception_raiser(exception)
            msg = message.Abort(u"testing")

            # we haven't done anything, so this is "abort before we've
            # connected"
            session.onMessage(msg)

            # make sure we got the right error out of onUserError
            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_leave_valid_session(self):
            '''
            cover when onLeave called after we have a valid session
            '''
            session = MockApplicationSession()
            exception = RuntimeError("such challenge")
            session.onLeave = exception_raiser(exception)
            # we have to get to an established connection first...
            session.onMessage(create_mock_welcome())
            self.assertTrue(session._session_id is not None)

            # okay we have a session ("because ._session_id is not None")
            msg = message.Goodbye()
            session.onMessage(msg)

            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_leave_valid_session_deferred(self):
            '''
            cover when onLeave called after we have a valid session
            '''
            session = MockApplicationSession()
            exception = RuntimeError("such challenge")
            session.onLeave = async_exception_raiser(exception)
            # we have to get to an established connection first...
            session.onMessage(create_mock_welcome())
            self.assertTrue(session._session_id is not None)

            # okay we have a session ("because ._session_id is not None")
            msg = message.Goodbye()
            session.onMessage(msg)

            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_leave_after_bad_challenge(self):
            '''
            onLeave raises error after onChallenge fails
            '''
            session = MockApplicationSession()
            exception = RuntimeError("such challenge")
            session.onLeave = exception_raiser(exception)
            session.onChallenge = exception_raiser(exception)
            # make a challenge (which will fail, and then the
            # subsequent onLeave will also fail)
            msg = message.Challenge(u"foo")
            session.onMessage(msg)

            self.assertEqual(2, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_disconnect_via_close(self):
            session = MockApplicationSession()
            exception = RuntimeError("sideways")
            session.onDisconnect = exception_raiser(exception)
            # we short-cut the whole state-machine traversal here by
            # just calling onClose directly, which would normally be
            # called via a Protocol, e.g.,
            # autobahn.wamp.websocket.WampWebSocketProtocol
            session.onClose(False)

            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_disconnect_via_close_deferred(self):
            session = MockApplicationSession()
            exception = RuntimeError("sideways")
            session.onDisconnect = async_exception_raiser(exception)
            # we short-cut the whole state-machine traversal here by
            # just calling onClose directly, which would normally be
            # called via a Protocol, e.g.,
            # autobahn.wamp.websocket.WampWebSocketProtocol
            session.onClose(False)

            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        # XXX FIXME Probably more ways to call onLeave!

        def test_on_challenge(self):
            session = MockApplicationSession()
            exception = RuntimeError("such challenge")
            session.onChallenge = exception_raiser(exception)
            msg = message.Challenge(u"foo")

            # execute
            session.onMessage(msg)

            # we already handle any onChallenge errors as "abort the
            # connection". So make sure our error showed up in the
            # fake-transport.
            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])
            self.assertEqual(1, len(session._transport.messages))
            reply = session._transport.messages[0]
            self.assertIsInstance(reply, message.Abort)
            self.assertEqual("such challenge", reply.message)

        def test_on_challenge_deferred(self):
            session = MockApplicationSession()
            exception = RuntimeError("such challenge")
            session.onChallenge = async_exception_raiser(exception)
            msg = message.Challenge(u"foo")

            # execute
            session.onMessage(msg)

            # we already handle any onChallenge errors as "abort the
            # connection". So make sure our error showed up in the
            # fake-transport.
            self.assertEqual(1, len(session.errors))
            self.assertEqual(session.errors[0][0], exception)
            self.assertEqual(1, len(session._transport.messages))
            reply = session._transport.messages[0]
            self.assertIsInstance(reply, message.Abort)
            self.assertEqual("such challenge", reply.message)

        def test_no_session(self):
            '''
            test "all other cases" when we don't yet have a session
            established, which should all raise ProtocolErrors and
            *not* go through the onUserError handler. We cheat and
            just test one.
            '''
            session = MockApplicationSession()
            exception = RuntimeError("such challenge")
            session.onConnect = exception_raiser(exception)

            for msg in [message.Goodbye()]:
                self.assertRaises(ProtocolError, session.onMessage, (msg,))
            self.assertEqual(0, len(session.errors))

        def test_on_disconnect(self):
            session = MockApplicationSession()
            exception = RuntimeError("oh sadness")
            session.onDisconnect = exception_raiser(exception)
            # we short-cut the whole state-machine traversal here by
            # just calling onClose directly, which would normally be
            # called via a Protocol, e.g.,
            # autobahn.wamp.websocket.WampWebSocketProtocol
            session.onClose(False)

            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_disconnect_deferred(self):
            session = MockApplicationSession()
            exception = RuntimeError("oh sadness")
            session.onDisconnect = async_exception_raiser(exception)
            # we short-cut the whole state-machine traversal here by
            # just calling onClose directly, which would normally be
            # called via a Protocol, e.g.,
            # autobahn.wamp.websocket.WampWebSocketProtocol
            session.onClose(False)

            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_disconnect_with_session(self):
            session = MockApplicationSession()
            exception = RuntimeError("the pain runs deep")
            session.onDisconnect = exception_raiser(exception)
            # create a valid session
            session.onMessage(create_mock_welcome())

            # we short-cut the whole state-machine traversal here by
            # just calling onClose directly, which would normally be
            # called via a Protocol, e.g.,
            # autobahn.wamp.websocket.WampWebSocketProtocol
            session.onClose(False)

            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_disconnect_with_session_deferred(self):
            session = MockApplicationSession()
            exception = RuntimeError("the pain runs deep")
            session.onDisconnect = async_exception_raiser(exception)
            # create a valid session
            session.onMessage(create_mock_welcome())

            # we short-cut the whole state-machine traversal here by
            # just calling onClose directly, which would normally be
            # called via a Protocol, e.g.,
            # autobahn.wamp.websocket.WampWebSocketProtocol
            session.onClose(False)

            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_connect(self):
            session = MockApplicationSession()
            exception = RuntimeError("the pain runs deep")
            session.onConnect = exception_raiser(exception)
            trans = MockTransport()

            # normally would be called from a Protocol?
            session.onOpen(trans)

            # shouldn't have done the .join()
            self.assertEqual(0, len(trans.messages))
            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        def test_on_connect_deferred(self):
            session = MockApplicationSession()
            exception = RuntimeError("the pain runs deep")
            session.onConnect = async_exception_raiser(exception)
            trans = MockTransport()

            # normally would be called from a Protocol?
            session.onOpen(trans)

            # shouldn't have done the .join()
            self.assertEqual(0, len(trans.messages))
            self.assertEqual(1, len(session.errors))
            self.assertEqual(exception, session.errors[0][0])

        # XXX likely missing other ways to invoke the above. need to
        # cover, for sure:
        #
        # onChallenge
        # onJoin
        # onLeave
        # onDisconnect
        #
        # what about other ISession ones?
        # onConnect
        # onDisconnect

        # NOTE: for Event stuff, that is publish() handlers,
        # test_publish_callback_exception in test_protocol.py already
        # covers exceptions coming from user-code.
