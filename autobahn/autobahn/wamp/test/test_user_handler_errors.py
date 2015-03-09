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
    # import unittest

    from twisted.internet.defer import inlineCallbacks, Deferred
    from twisted.python import log

    from autobahn.wamp import message
    from autobahn.wamp import serializer
    from autobahn.wamp import role
    from autobahn import util
    from autobahn.wamp.exception import ApplicationError, NotAuthorized, InvalidUri, ProtocolError
    from autobahn.wamp import types

    from autobahn.twisted.wamp import ApplicationSession


    class MockApplicationSession(ApplicationSession):
        '''
        This is used by tests, which typically attach their own handler to
        on*() methods. This just collects any errors from onUserError
        '''

        def __init__(self, *args, **kw):
            ApplicationSession.__init__(self, *args, **kw)
            self.errors = []

        def onUserError(self, e, msg):
            self.errors.append((e, msg))


    def exception_raiser(exc):
        '''
        Create a method that takes any args and always raises the given
        Exception instance.
        '''
        assert isinstance(exc, Exception), "Must derive from Exception"
        def method(*args, **kw):
            raise exc
        return method


    class TestSessionCallbacks(unittest.TestCase):
        '''
        These test that callbacks on user-overridden ApplicationSession
        methods that produce errors are handled correctly.

        XXX should do state-diagram documenting where we are when each
        of these cases arises :/
        '''

        def test_on_join(self):
            session = MockApplicationSession()
            exception = RuntimeError("blammo")
            session.onJoin = exception_raiser(exception)
            msg = message.Welcome(1234, [])

            # give the sesion a WELCOME, from which it should call onJoin
            session.onMessage(msg)

            # make sure we got the right error out of onUserError
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


if __name__ == '__main__':
    unittest.main()
