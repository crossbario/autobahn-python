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

# from twisted.trial import unittest
import unittest

from zope.interface import implementer

from autobahn.wamp.interfaces import *
from autobahn.wamp.types import *

from autobahn.wamp.exception import ApplicationError, ProtocolError

from twisted.internet.defer import Deferred, inlineCallbacks


import random


def newid():
    return random.randint(0, 2**53)


@implementer(ISubscriber)
@implementer(IPublisher)
@implementer(ICallee)
@implementer(ICaller)
class MockSession:

    def __init__(self):
        self._subscriptions = {}
        self._registrations = {}

    def subscribe(self, topic, options=None):
        assert(isinstance(topic, str))
        assert(options is None or isinstance(options, SubscribeOptions))
        if topic not in self._subscriptions:
            self._subscriptions[topic] = Subscription(newid(), topic)
        d = Deferred()
        d.callback(self._subscriptions[topic])
        return d

    def unsubscribe(self, subscription):
        assert(isinstance(subscription, Subscription))
        assert(subscription._isActive)
        assert(subscription._topic in self._subscriptions)
        subscription._isActive = False
        del self._subscriptions[subscription._topic]
        d = Deferred()
        d.callback(None)
        return d

    def publish(self, topic, payload=None, options=None):
        assert(isinstance(topic, str))
        assert(options is None or isinstance(options, PublishOptions))

        d = Deferred()
        if topic not in ["com.myapp.mytopic1"]:
            d.errback(ApplicationError(ApplicationError.NOT_AUTHORIZED))
        else:
            id = newid()
            if topic in self._subscriptions:
                event = Event(topic, payload, id)
                self._subscriptions[topic].notify(event)
            d.callback(id)
        return d

    def register(self, procedure, endpoint, options=None):
        assert(isinstance(procedure, str))
        assert(options is None or isinstance(options, RegisterOptions))
        if procedure not in self._registrations:
            self._registrations[procedure] = Registration(newid(), procedure, endpoint)
        d = Deferred()
        d.callback(self._registrations[procedure])
        return d

    def unregister(self, registration):
        assert(isinstance(registration, Registration))
        assert(registration._isActive)
        assert(registration._procedure in self._registrations)
        registration._isActive = False
        del self._registrations[registration._procedure]
        d = Deferred()
        d.callback(None)
        return d

    def call(self, procedure, *args, **kwargs):
        assert(isinstance(procedure, str))
        if 'options' in kwargs:
            options = kwargs['options']
            del kwargs['options']
            assert(isinstance(options, CallOptions))

        d = Deferred()
        if procedure == "com.myapp.echo":
            if len(args) != 1 or len(kwargs) != 0 or not isinstance(args[0], str):
                d.errback(ApplicationError(ApplicationError.INVALID_ARGUMENT, "procedure takes exactly 1 positional argument of type string"))
            else:
                d.callback(args[0])
        elif procedure == "com.myapp.complex":
            d.callback(CallResult(23, 7, foo="bar"))

        elif procedure in self._registrations:
            try:
                res = self._registrations[procedure]._endpoint(*args, **kwargs)
            except TypeError as err:
                d.errback(ApplicationError(ApplicationError.INVALID_ARGUMENT, str(err)))
            else:
                d.callback(res)

        else:
            d.errback(ApplicationError(ApplicationError.NO_SUCH_PROCEDURE, "no procedure with URI {}".format(procedure)))
        return d


@inlineCallbacks
def test_rpc(session):

    def hello(msg):
        return "You said {}. I say hello!".format(msg)

    try:
        reg1 = yield session.register("com.myapp.hello", hello)
        print(reg1)
    except ApplicationError as err:
        print(err)
    else:
        res = yield session.call("com.myapp.hello", "foooo")
        print (res)
        yield session.unregister(reg1)
        res = yield session.call("com.myapp.hello", "baaar")
        print (res)

    try:
        # res = yield session.call("com.myapp.echo", "Hello, world!", 23)
        # res = yield session.call("com.myapp.complex", "Hello, world!", 23)
        res = yield session.call("com.myapp.complex", "Hello, world!", 23, options=CallOptions(timeout=2))
        print(res.results)
        print(res.kwresults)
    except ApplicationError as err:
        print(err)


@inlineCallbacks
def test_pubsub(session):
    try:
        sub1 = yield session.subscribe("com.myapp.mytopic1", SubscribeOptions(match='prefix'))
        print(sub1)
    except ApplicationError as err:
        print(err)
    else:
        def watcher1(event):
            print("watcher1: publication {} on topic {} with payload {}".format(event.publication, event.topic, event.payload))

        def watcher2(event):
            print("watcher1: publication {} on topic {} with payload {}".format(event.publication, event.topic, event.payload))

        sub1.watch(watcher1)
        sub1.watch(watcher2)

        session.publish("com.myapp.mytopic1", "Hello, world!")

        sub1.unwatch(watcher1)

        publicationId = yield session.publish("com.myapp.mytopic1", "Hello, world!")
        print(publicationId)

        session.publish("com.myapp.mytopic2", "Hello, world!")


class Publisher(unittest.TestCase):

    def setUp(self):
        self.session = MockSession()

    def tearDown(self):
        pass

    @inlineCallbacks
    def test_register(self):

        def hello(msg):
            return "You said {}. I say hello!".format(msg)

        try:
            yield self.session.register("com.myapp.hello", hello)
        except ApplicationError as err:
            print(err)


if __name__ == '__main__':
    unittest.main()
