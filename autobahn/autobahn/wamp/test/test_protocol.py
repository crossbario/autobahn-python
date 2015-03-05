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

    from six import StringIO
    from mock import Mock, patch
    from twisted.trial import unittest
    # import unittest

    from twisted.internet.defer import inlineCallbacks, Deferred

    from autobahn.wamp import message
    from autobahn.wamp import serializer
    from autobahn.wamp import role
    from autobahn import util
    from autobahn.wamp.exception import ApplicationError, NotAuthorized, InvalidUri
    from autobahn.wamp import types

    from autobahn.twisted.wamp import ApplicationSession

    class MockTransport:

        def __init__(self, handler):
            self._log = False
            self._handler = handler
            self._serializer = serializer.JsonSerializer()
            self._registrations = {}
            self._invocations = {}
            self._topic_subscriptions = {}

            self._handler.onOpen(self)

            self._my_session_id = util.id()

            roles = [
                role.RoleBrokerFeatures(),
                role.RoleDealerFeatures()
            ]

            msg = message.Welcome(self._my_session_id, roles)
            self._handler.onMessage(msg)

        def send(self, msg):
            if self._log:
                payload, isbinary = self._serializer.serialize(msg)
                print("Send: {0}".format(payload))

            reply = None

            if isinstance(msg, message.Publish):
                if msg.topic.startswith(u'com.myapp'):
                    if msg.acknowledge:
                        reply = message.Published(msg.request, util.id())
                elif len(msg.topic) == 0:
                    reply = message.Error(message.Publish.MESSAGE_TYPE, msg.request, u'wamp.error.invalid_uri')
                else:
                    reply = message.Error(message.Publish.MESSAGE_TYPE, msg.request, u'wamp.error.not_authorized')

            elif isinstance(msg, message.Call):
                if msg.procedure == u'com.myapp.procedure1':
                    reply = message.Result(msg.request, args=[100])
                elif msg.procedure == u'com.myapp.procedure2':
                    reply = message.Result(msg.request, args=[1, 2, 3])
                elif msg.procedure == u'com.myapp.procedure3':
                    reply = message.Result(msg.request, args=[1, 2, 3], kwargs={u'foo': u'bar', u'baz': 23})

                elif msg.procedure.startswith(u'com.myapp.myproc'):
                    registration = self._registrations[msg.procedure]
                    request = util.id()
                    self._invocations[request] = msg.request
                    reply = message.Invocation(request, registration, args=msg.args, kwargs=msg.kwargs)
                else:
                    reply = message.Error(message.Call.MESSAGE_TYPE, msg.request, u'wamp.error.no_such_procedure')

            elif isinstance(msg, message.Yield):
                if msg.request in self._invocations:
                    request = self._invocations[msg.request]
                    reply = message.Result(request, args=msg.args, kwargs=msg.kwargs)

            elif isinstance(msg, message.Subscribe):
                # fake out that we can do duplicate subscriptions to
                # the same topic
                if msg.topic in self._topic_subscriptions:
                    reply_id = self._topic_subscriptions[msg.topic]
                else:
                    reply_id = util.id()
                    self._topic_subscriptions[msg.topic] = reply_id
                reply = message.Subscribed(msg.request, reply_id)

            elif isinstance(msg, message.Unsubscribe):
                reply = message.Unsubscribed(msg.request)

            elif isinstance(msg, message.Register):
                registration = util.id()
                self._registrations[msg.procedure] = registration
                reply = message.Registered(msg.request, registration)

            elif isinstance(msg, message.Unregister):
                reply = message.Unregistered(msg.request)

            if reply:
                if self._log:
                    payload, isbinary = self._serializer.serialize(reply)
                    print("Receive: {0}".format(payload))
                self._handler.onMessage(reply)

        def isOpen(self):
            return True

        def close(self):
            pass

        def abort(self):
            pass

    class TestPublisher(unittest.TestCase):

        @inlineCallbacks
        def test_publish(self):
            handler = ApplicationSession()
            MockTransport(handler)

            publication = yield handler.publish(u'com.myapp.topic1')
            self.assertEqual(publication, None)

            publication = yield handler.publish(u'com.myapp.topic1', 1, 2, 3)
            self.assertEqual(publication, None)

            publication = yield handler.publish(u'com.myapp.topic1', 1, 2, 3, foo=23, bar='hello')
            self.assertEqual(publication, None)

            publication = yield handler.publish(u'com.myapp.topic1', options=types.PublishOptions(exclude_me=False))
            self.assertEqual(publication, None)

            publication = yield handler.publish(u'com.myapp.topic1', 1, 2, 3, foo=23, bar='hello', options=types.PublishOptions(exclude_me=False, exclude=[100, 200, 300]))
            self.assertEqual(publication, None)

        @inlineCallbacks
        def test_publish_acknowledged(self):
            handler = ApplicationSession()
            MockTransport(handler)

            publication = yield handler.publish(u'com.myapp.topic1', options=types.PublishOptions(acknowledge=True))
            self.assertTrue(type(publication.id) in (int, long))

            publication = yield handler.publish(u'com.myapp.topic1', 1, 2, 3, options=types.PublishOptions(acknowledge=True))
            self.assertTrue(type(publication.id) in (int, long))

            publication = yield handler.publish(u'com.myapp.topic1', 1, 2, 3, foo=23, bar='hello', options=types.PublishOptions(acknowledge=True))
            self.assertTrue(type(publication.id) in (int, long))

            publication = yield handler.publish(u'com.myapp.topic1', options=types.PublishOptions(exclude_me=False, acknowledge=True))
            self.assertTrue(type(publication.id) in (int, long))

            publication = yield handler.publish(u'com.myapp.topic1', 1, 2, 3, foo=23, bar='hello', options=types.PublishOptions(exclude_me=False, exclude=[100, 200, 300], acknowledge=True))
            self.assertTrue(type(publication.id) in (int, long))

        @inlineCallbacks
        def test_publish_undefined_exception(self):
            handler = ApplicationSession()
            MockTransport(handler)

            options = types.PublishOptions(acknowledge=True)

            yield self.assertFailure(handler.publish(u'de.myapp.topic1', options=options), ApplicationError)
            yield self.assertFailure(handler.publish(u'', options=options), ApplicationError)

        @inlineCallbacks
        def test_publish_defined_exception(self):
            handler = ApplicationSession()
            MockTransport(handler)

            options = types.PublishOptions(acknowledge=True)

            handler.define(NotAuthorized)
            yield self.assertFailure(handler.publish(u'de.myapp.topic1', options=options), NotAuthorized)

            handler.define(InvalidUri)
            yield self.assertFailure(handler.publish(u'', options=options), InvalidUri)

        @inlineCallbacks
        def test_call(self):
            handler = ApplicationSession()
            MockTransport(handler)

            res = yield handler.call(u'com.myapp.procedure1')
            self.assertEqual(res, 100)

            res = yield handler.call(u'com.myapp.procedure1', 1, 2, 3)
            self.assertEqual(res, 100)

            res = yield handler.call(u'com.myapp.procedure1', 1, 2, 3, foo=23, bar='hello')
            self.assertEqual(res, 100)

            res = yield handler.call(u'com.myapp.procedure1', options=types.CallOptions(timeout=10000))
            self.assertEqual(res, 100)

            res = yield handler.call(u'com.myapp.procedure1', 1, 2, 3, foo=23, bar='hello', options=types.CallOptions(timeout=10000))
            self.assertEqual(res, 100)

        @inlineCallbacks
        def test_call_with_complex_result(self):
            handler = ApplicationSession()
            MockTransport(handler)

            res = yield handler.call(u'com.myapp.procedure2')
            self.assertIsInstance(res, types.CallResult)
            self.assertEqual(res.results, (1, 2, 3))
            self.assertEqual(res.kwresults, {})

            res = yield handler.call(u'com.myapp.procedure3')
            self.assertIsInstance(res, types.CallResult)
            self.assertEqual(res.results, (1, 2, 3))
            self.assertEqual(res.kwresults, {'foo': 'bar', 'baz': 23})

        @inlineCallbacks
        def test_subscribe(self):
            handler = ApplicationSession()
            MockTransport(handler)

            def on_event(*args, **kwargs):
                print("got event", args, kwargs)

            subscription = yield handler.subscribe(on_event, u'com.myapp.topic1')
            self.assertTrue(type(subscription.id) in (int, long))

            subscription = yield handler.subscribe(on_event, u'com.myapp.topic1', options=types.SubscribeOptions(match=u'wildcard'))
            self.assertTrue(type(subscription.id) in (int, long))

        @inlineCallbacks
        def test_double_subscribe(self):
            handler = ApplicationSession()
            MockTransport(handler)

            event0 = Deferred()
            event1 = Deferred()

            subscription0 = yield handler.subscribe(lambda: event0.callback(42), u'com.myapp.topic1')
            subscription1 = yield handler.subscribe(lambda: event1.callback('foo'), u'com.myapp.topic1')
            # same topic, *HAS* to be the same ID for protocol to
            # work, because "EVENT, SUBSCRIBED.Subscription|id" is the
            # only way to send one.
            self.assertTrue(subscription0.id == subscription1.id)

            # do a publish, and then fake the acknowledgement message
            publish = yield handler.publish(
                u'com.myapp.topic1',
                options=types.PublishOptions(acknowledge=True, exclude_me=False),
            )
            msg = message.Event(subscription0.id, publish.id)
            handler.onMessage(msg)

            # ensure that the publish "did the right thing" and called
            # both callbacks
            self.assertTrue(event0.called, "Didn't get first subscribe's callback")
            self.assertTrue(event1.called, "Didn't get second subscribe's callback")



        @inlineCallbacks
        def test_publish_callback_exception(self):
            """
            Ensure we handle an exception from the user code.
            """
            handler = ApplicationSession()
            handler.debug_app = True  # to check we print the traceback
            MockTransport(handler)

            # monkey-patch a couple APIs that the debug-version should
            # be calling (FIXME: use mock better? tried it but ...)

            import traceback
            import sys
            orig_tb = traceback.print_exc
            orig_stdout = sys.stdout
            traceback.print_exc = Mock()
            sys.stdout = StringIO()
            try:
                error_instance = RuntimeError("we have a problem")
                def boom():
                    raise error_instance

                sub = yield handler.subscribe(boom, u'com.myapp.topic1')
                # we want to confirm we get an error, so we monkey-patch
                # the onUserError callback to ensure we see the error
                handler.onUserError = Mock(return_value=None)

                # MockTransport gives us the ack reply and then we do our
                # own event message
                publish = yield handler.publish(
                    u'com.myapp.topic1',
                    options=types.PublishOptions(acknowledge=True, exclude_me=False),
                )
                msg = message.Event(sub.id, publish.id)
                handler.onMessage(msg)

                # the onUserError method should have been called, with our
                # exception as the only argument
                self.assertTrue(handler.onUserError.called)
                self.assertEqual(1, handler.onUserError.call_count)
                args, kwargs = handler.onUserError.call_args_list[0]
                self.assertEqual(1, len(args))
                self.assertEqual(error_instance, args[0])
                # since we set debug_app, we should also have called traceback.print_exc
                self.assertTrue(traceback.print_exc.called)
                self.assertTrue('function boom at' in sys.stdout.getvalue())

            finally:
                traceback.print_exc = orig_tb
                sys.stdout = orig_stdout

        @inlineCallbacks
        def test_unsubscribe(self):
            handler = ApplicationSession()
            MockTransport(handler)

            def on_event(*args, **kwargs):
                print("got event", args, kwargs)

            subscription = yield handler.subscribe(on_event, u'com.myapp.topic1')
            yield subscription.unsubscribe()

        @inlineCallbacks
        def test_register(self):
            handler = ApplicationSession()
            MockTransport(handler)

            def on_call(*args, **kwargs):
                print("got call", args, kwargs)

            registration = yield handler.register(on_call, u'com.myapp.procedure1')
            self.assertTrue(type(registration.id) in (int, long))

            registration = yield handler.register(on_call, u'com.myapp.procedure1', options=types.RegisterOptions(match=u'prefix'))
            self.assertTrue(type(registration.id) in (int, long))

        @inlineCallbacks
        def test_unregister(self):
            handler = ApplicationSession()
            MockTransport(handler)

            def on_call(*args, **kwargs):
                print("got call", args, kwargs)

            registration = yield handler.register(on_call, u'com.myapp.procedure1')
            yield registration.unregister()

        @inlineCallbacks
        def test_invoke(self):
            handler = ApplicationSession()
            MockTransport(handler)

            def myproc1():
                return 23

            yield handler.register(myproc1, u'com.myapp.myproc1')

            res = yield handler.call(u'com.myapp.myproc1')
            self.assertEqual(res, 23)

        # ## variant 1: works
        # def test_publish1(self):
        #    d = self.handler.publish(u'de.myapp.topic1')
        #    self.assertFailure(d, ApplicationError)

        # ## variant 2: works
        # @inlineCallbacks
        # def test_publish2(self):
        #    yield self.assertFailure(self.handler.publish(u'de.myapp.topic1'), ApplicationError)

        # ## variant 3: does NOT work
        # @inlineCallbacks
        # def test_publish3(self):
        #    with self.assertRaises(ApplicationError):
        #       yield self.handler.publish(u'de.myapp.topic1')


if __name__ == '__main__':
    unittest.main()
