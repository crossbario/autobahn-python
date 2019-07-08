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

from __future__ import absolute_import

from autobahn.wamp import role
from autobahn.wamp import message
from autobahn.wamp.exception import ProtocolError, InvalidUriError

import unittest


class Foo(object):
    pass


class TestIds(unittest.TestCase):

    def test_valid_ids(self):
        for val in [0, 1, 23, 100000, 9007199254740992]:
            self.assertEqual(val, message.check_or_raise_id(val))

    def test_invalid_ids(self):
        for val in [-1, -9007199254740992, None, b"", b"abc", u"", u"abc", 0.9, Foo(), False, True, [], {}]:
            self.assertRaises(ProtocolError, message.check_or_raise_id, val)


class TestUris(unittest.TestCase):

    def test_valid_uris_loose_nonempty(self):
        for u in [u"com.myapp.topic1",
                  u"com.myapp.product.123",
                  u"com.myapp.product.1.delete",
                  u"Com-star.MyApp.**+$for",
                  u"\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5",
                  u"hello\x24world",
                  u"hello\xC2\xA2world",
                  u"hello\xE2\x82\xACworld",
                  u"hello\xF0\xA4\xAD\xA2world",
                  ]:
            self.assertEqual(u, message.check_or_raise_uri(u))

    def test_invalid_uris_loose_nonempty(self):
        for u in [0,
                  None,
                  True,
                  False,
                  0.8,
                  b"abc",
                  Foo(),
                  u"",
                  u".",
                  u"com.",
                  u"com..product",
                  u"com.my app.product",
                  u"com.my\tapp.product",
                  u"com.my\napp.product",
                  u"com.myapp.product#",
                  u"com.#.product",
                  ]:
            self.assertRaises(InvalidUriError, message.check_or_raise_uri, u)

    def test_valid_uris_loose_empty(self):
        for u in [u"com.myapp.topic1",
                  u"com.myapp..123",
                  u"com.myapp.product.1.",
                  u"com.",
                  u".",
                  u"",
                  u"Com-star.MyApp.**+$for..foo",
                  u"\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5..foo",
                  u"hello\x24world..foo",
                  u"hello\xC2\xA2world..foo",
                  u"hello\xE2\x82\xACworld..foo",
                  u"hello\xF0\xA4\xAD\xA2world..foo",
                  ]:
            self.assertEqual(u, message.check_or_raise_uri(u, allow_empty_components=True))

    def test_invalid_uris_loose_empty(self):
        for u in [0,
                  None,
                  True,
                  False,
                  0.8,
                  b"abc",
                  Foo(),
                  u"com.my app.product",
                  u"com.my\tapp.product",
                  u"com.my\napp.product",
                  u"com.myapp.product#",
                  u"com.#.product",
                  ]:
            self.assertRaises(InvalidUriError, message.check_or_raise_uri, u, allow_empty_components=True)

    def test_valid_uris_strict_nonempty(self):
        for u in [u"com.myapp.topic1",
                  u"com.myapp.product.123",
                  u"com.myapp.product.1.delete",
                  ]:
            self.assertEqual(u, message.check_or_raise_uri(u, strict=True))

    def test_invalid_uris_strict_nonempty(self):
        for u in [0,
                  None,
                  True,
                  False,
                  0.8,
                  b"abc",
                  Foo(),
                  u"",
                  u".",
                  u"com.",
                  u"com..product",
                  u"com.my app.product",
                  u"com.my\tapp.product",
                  u"com.my\napp.product",
                  u"com.myapp.product#",
                  u"com.#.product",
                  u"Com-star.MyApp.**+$for",
                  u"\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5",
                  u"hello\x24world",
                  u"hello\xC2\xA2world",
                  u"hello\xE2\x82\xACworld",
                  u"hello\xF0\xA4\xAD\xA2world",
                  ]:
            self.assertRaises(InvalidUriError, message.check_or_raise_uri, u, strict=True)

    def test_valid_uris_strict_empty(self):
        for u in [u"com.myapp.topic1",
                  u"com.myapp..123",
                  u"com.myapp.product.1.",
                  u"com.",
                  u".",
                  u"",
                  ]:
            self.assertEqual(u, message.check_or_raise_uri(u, strict=True, allow_empty_components=True))

    def test_invalid_uris_strict_empty(self):
        for u in [0,
                  None,
                  True,
                  False,
                  0.8,
                  b"abc",
                  Foo(),
                  u"com.my app.product",
                  u"com.my\tapp.product",
                  u"com.my\napp.product",
                  u"com.myapp.product#",
                  u"com.#.product",
                  u"Com-star.MyApp.**+$for..foo",
                  u"\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5..foo",
                  u"hello\x24world..foo",
                  u"hello\xC2\xA2world..foo",
                  u"hello\xE2\x82\xACworld..foo",
                  u"hello\xF0\xA4\xAD\xA2world..foo",
                  ]:
            self.assertRaises(InvalidUriError, message.check_or_raise_uri, u, strict=True, allow_empty_components=True)


class TestErrorMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Error(message.Call.MESSAGE_TYPE, 123456, u'com.myapp.error1')
        msg = e.marshal()
        self.assertEqual(len(msg), 5)
        self.assertEqual(msg[0], message.Error.MESSAGE_TYPE)
        self.assertEqual(msg[1], message.Call.MESSAGE_TYPE)
        self.assertEqual(msg[2], 123456)
        self.assertEqual(msg[3], {})
        self.assertEqual(msg[4], u'com.myapp.error1')

        e = message.Error(message.Call.MESSAGE_TYPE, 123456, u'com.myapp.error1', args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'})
        msg = e.marshal()
        self.assertEqual(len(msg), 7)
        self.assertEqual(msg[0], message.Error.MESSAGE_TYPE)
        self.assertEqual(msg[1], message.Call.MESSAGE_TYPE)
        self.assertEqual(msg[2], 123456)
        self.assertEqual(msg[3], {})
        self.assertEqual(msg[4], u'com.myapp.error1')
        self.assertEqual(msg[5], [1, 2, 3])
        self.assertEqual(msg[6], {u'foo': 23, u'bar': u'hello'})

    def test_parse_and_marshal(self):
        wmsg = [message.Error.MESSAGE_TYPE, message.Call.MESSAGE_TYPE, 123456, {}, u'com.myapp.error1']
        msg = message.Error.parse(wmsg)
        self.assertIsInstance(msg, message.Error)
        self.assertEqual(msg.request_type, message.Call.MESSAGE_TYPE)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.error, u'com.myapp.error1')
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Error.MESSAGE_TYPE, message.Call.MESSAGE_TYPE, 123456, {}, u'com.myapp.error1', [1, 2, 3], {u'foo': 23, u'bar': u'hello'}]
        msg = message.Error.parse(wmsg)
        self.assertIsInstance(msg, message.Error)
        self.assertEqual(msg.request_type, message.Call.MESSAGE_TYPE)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.error, u'com.myapp.error1')
        self.assertEqual(msg.args, [1, 2, 3])
        self.assertEqual(msg.kwargs, {u'foo': 23, u'bar': u'hello'})
        self.assertEqual(msg.marshal(), wmsg)


class TestSubscribeMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Subscribe(123456, u'com.myapp.topic1')
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Subscribe.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})
        self.assertEqual(msg[3], u'com.myapp.topic1')

        e = message.Subscribe(123456, u'com.myapp.topic1', match=message.Subscribe.MATCH_PREFIX)
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Subscribe.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {u'match': u'prefix'})
        self.assertEqual(msg[3], u'com.myapp.topic1')

    def test_parse_and_marshal(self):
        wmsg = [message.Subscribe.MESSAGE_TYPE, 123456, {}, u'com.myapp.topic1']
        msg = message.Subscribe.parse(wmsg)
        self.assertIsInstance(msg, message.Subscribe)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.topic, u'com.myapp.topic1')
        self.assertEqual(msg.match, message.Subscribe.MATCH_EXACT)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Subscribe.MESSAGE_TYPE, 123456, {u'match': u'prefix'}, u'com.myapp.topic1']
        msg = message.Subscribe.parse(wmsg)
        self.assertIsInstance(msg, message.Subscribe)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.topic, u'com.myapp.topic1')
        self.assertEqual(msg.match, message.Subscribe.MATCH_PREFIX)
        self.assertEqual(msg.marshal(), wmsg)

    def test_get_retained_default_false(self):
        wmsg = [message.Subscribe.MESSAGE_TYPE, 123456, {u'match': u'prefix'}, u'com.myapp.topic1']
        msg = message.Subscribe.parse(wmsg)
        self.assertIsInstance(msg, message.Subscribe)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.topic, u'com.myapp.topic1')
        self.assertEqual(msg.get_retained, None)
        self.assertNotEqual(msg.get_retained, True)
        self.assertEqual(msg.match, message.Subscribe.MATCH_PREFIX)
        self.assertEqual(msg.marshal(), wmsg)

    def test_get_retained_explicit_false(self):
        wmsg = [message.Subscribe.MESSAGE_TYPE, 123456, {u'match': u'prefix', u'get_retained': False}, u'com.myapp.topic1']
        msg = message.Subscribe.parse(wmsg)
        self.assertIsInstance(msg, message.Subscribe)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.topic, u'com.myapp.topic1')
        self.assertEqual(msg.get_retained, False)
        self.assertNotEqual(msg.get_retained, True)
        self.assertEqual(msg.match, message.Subscribe.MATCH_PREFIX)
        self.assertEqual(msg.marshal(), wmsg)

    def test_get_retained_explicit_true(self):
        wmsg = [message.Subscribe.MESSAGE_TYPE, 123456, {u'match': u'prefix', u'get_retained': True}, u'com.myapp.topic1']
        msg = message.Subscribe.parse(wmsg)
        self.assertIsInstance(msg, message.Subscribe)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.topic, u'com.myapp.topic1')
        self.assertEqual(msg.get_retained, True)
        self.assertEqual(msg.match, message.Subscribe.MATCH_PREFIX)
        self.assertEqual(msg.marshal(), wmsg)


class TestSubscribedMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Subscribed(123456, 789123)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Subscribed.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)

    def test_parse_and_marshal(self):
        wmsg = [message.Subscribed.MESSAGE_TYPE, 123456, 789123]
        msg = message.Subscribed.parse(wmsg)
        self.assertIsInstance(msg, message.Subscribed)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.subscription, 789123)
        self.assertEqual(msg.marshal(), wmsg)


class TestUnsubscribeMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Unsubscribe(123456, 789123)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Unsubscribe.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)

    def test_parse_and_marshal(self):
        wmsg = [message.Unsubscribe.MESSAGE_TYPE, 123456, 789123]
        msg = message.Unsubscribe.parse(wmsg)
        self.assertIsInstance(msg, message.Unsubscribe)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.subscription, 789123)
        self.assertEqual(msg.marshal(), wmsg)


class TestUnsubscribedMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Unsubscribed(123456)
        msg = e.marshal()
        self.assertEqual(len(msg), 2)
        self.assertEqual(msg[0], message.Unsubscribed.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)

        e = message.Unsubscribed(0, subscription=123456)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Unsubscribed.MESSAGE_TYPE)
        self.assertEqual(msg[1], 0)
        self.assertEqual(msg[2], {u'subscription': 123456})

        e = message.Unsubscribed(0, subscription=123456, reason=u"wamp.subscription.revoked")
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Unsubscribed.MESSAGE_TYPE)
        self.assertEqual(msg[1], 0)
        self.assertEqual(msg[2], {u'subscription': 123456, u'reason': u"wamp.subscription.revoked"})

    def test_parse_and_marshal(self):
        wmsg = [message.Unsubscribed.MESSAGE_TYPE, 123456]
        msg = message.Unsubscribed.parse(wmsg)
        self.assertIsInstance(msg, message.Unsubscribed)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.subscription, None)
        self.assertEqual(msg.reason, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Unsubscribed.MESSAGE_TYPE, 0, {u'subscription': 123456}]
        msg = message.Unsubscribed.parse(wmsg)
        self.assertIsInstance(msg, message.Unsubscribed)
        self.assertEqual(msg.request, 0)
        self.assertEqual(msg.subscription, 123456)
        self.assertEqual(msg.reason, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Unsubscribed.MESSAGE_TYPE, 0, {u'subscription': 123456, u'reason': u"wamp.subscription.revoked"}]
        msg = message.Unsubscribed.parse(wmsg)
        self.assertIsInstance(msg, message.Unsubscribed)
        self.assertEqual(msg.request, 0)
        self.assertEqual(msg.subscription, 123456)
        self.assertEqual(msg.reason, u"wamp.subscription.revoked")
        self.assertEqual(msg.marshal(), wmsg)


class TestPublishMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Publish(123456, u'com.myapp.topic1')
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Publish.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})
        self.assertEqual(msg[3], u'com.myapp.topic1')

        e = message.Publish(123456, u'com.myapp.topic1', args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'})
        msg = e.marshal()
        self.assertEqual(len(msg), 6)
        self.assertEqual(msg[0], message.Publish.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})
        self.assertEqual(msg[3], u'com.myapp.topic1')
        self.assertEqual(msg[4], [1, 2, 3])
        self.assertEqual(msg[5], {u'foo': 23, u'bar': u'hello'})

        e = message.Publish(123456, u'com.myapp.topic1', exclude_me=False, exclude=[300], eligible=[100, 200, 300])
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Publish.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {u'exclude_me': False, u'exclude': [300], u'eligible': [100, 200, 300]})
        self.assertEqual(msg[3], u'com.myapp.topic1')

    def test_parse_and_marshal(self):
        wmsg = [message.Publish.MESSAGE_TYPE, 123456, {}, u'com.myapp.topic1']
        msg = message.Publish.parse(wmsg)
        self.assertIsInstance(msg, message.Publish)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.topic, u'com.myapp.topic1')
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.exclude_me, None)
        self.assertEqual(msg.exclude, None)
        self.assertEqual(msg.eligible, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Publish.MESSAGE_TYPE, 123456, {}, u'com.myapp.topic1', [1, 2, 3], {u'foo': 23, u'bar': u'hello'}]
        msg = message.Publish.parse(wmsg)
        self.assertIsInstance(msg, message.Publish)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.topic, u'com.myapp.topic1')
        self.assertEqual(msg.args, [1, 2, 3])
        self.assertEqual(msg.kwargs, {u'foo': 23, u'bar': u'hello'})
        self.assertEqual(msg.exclude_me, None)
        self.assertEqual(msg.exclude, None)
        self.assertEqual(msg.eligible, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Publish.MESSAGE_TYPE, 123456, {u'exclude_me': False, u'exclude': [300], u'eligible': [100, 200, 300]}, u'com.myapp.topic1']
        msg = message.Publish.parse(wmsg)
        self.assertIsInstance(msg, message.Publish)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.topic, u'com.myapp.topic1')
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.exclude_me, False)
        self.assertEqual(msg.exclude, [300])
        self.assertEqual(msg.eligible, [100, 200, 300])
        self.assertEqual(msg.marshal(), wmsg)

    def test_retain_default_false(self):
        """
        Retain, when not specified, is False-y by default.
        """
        wmsg = [message.Publish.MESSAGE_TYPE, 123456, {u'exclude_me': False, u'exclude': [300], u'eligible': [100, 200, 300]}, u'com.myapp.topic1']
        msg = message.Publish.parse(wmsg)
        self.assertIsInstance(msg, message.Publish)
        self.assertEqual(msg.retain, None)
        self.assertIsNot(msg.retain, True)
        self.assertEqual(msg.marshal(), wmsg)

    def test_retain_explicit_false(self):
        """
        Retain, when specified as False, shows up in the message.
        """
        wmsg = [message.Publish.MESSAGE_TYPE, 123456, {u'exclude_me': False, u'retain': False, u'exclude': [300], u'eligible': [100, 200, 300]}, u'com.myapp.topic1']
        msg = message.Publish.parse(wmsg)
        self.assertIsInstance(msg, message.Publish)
        self.assertEqual(msg.retain, False)
        self.assertIsNot(msg.retain, True)
        self.assertEqual(msg.marshal(), wmsg)

    def test_retain_explicit_true(self):
        """
        Retain, when specified as True, shows up in the message.
        """
        wmsg = [message.Publish.MESSAGE_TYPE, 123456, {u'exclude_me': False, u'retain': True, u'exclude': [300], u'eligible': [100, 200, 300]}, u'com.myapp.topic1']
        msg = message.Publish.parse(wmsg)
        self.assertIsInstance(msg, message.Publish)
        self.assertEqual(msg.retain, True)
        self.assertIs(msg.retain, True)
        self.assertEqual(msg.marshal(), wmsg)


class TestPublishedMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Published(123456, 789123)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Published.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)

    def test_parse_and_marshal(self):
        wmsg = [message.Published.MESSAGE_TYPE, 123456, 789123]
        msg = message.Published.parse(wmsg)
        self.assertIsInstance(msg, message.Published)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.publication, 789123)
        self.assertEqual(msg.marshal(), wmsg)


class TestEventMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Event(123456, 789123)
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Event.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)
        self.assertEqual(msg[3], {})

        e = message.Event(123456, 789123, args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'})
        msg = e.marshal()
        self.assertEqual(len(msg), 6)
        self.assertEqual(msg[0], message.Event.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)
        self.assertEqual(msg[3], {})
        self.assertEqual(msg[4], [1, 2, 3])
        self.assertEqual(msg[5], {u'foo': 23, u'bar': u'hello'})

        e = message.Event(123456, 789123, publisher=300)
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Event.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)
        self.assertEqual(msg[3], {u'publisher': 300})

    def test_parse_and_marshal(self):
        wmsg = [message.Event.MESSAGE_TYPE, 123456, 789123, {}]
        msg = message.Event.parse(wmsg)
        self.assertIsInstance(msg, message.Event)
        self.assertEqual(msg.subscription, 123456)
        self.assertEqual(msg.publication, 789123)
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.publisher, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Event.MESSAGE_TYPE, 123456, 789123, {}, [1, 2, 3], {u'foo': 23, u'bar': u'hello'}]
        msg = message.Event.parse(wmsg)
        self.assertIsInstance(msg, message.Event)
        self.assertEqual(msg.subscription, 123456)
        self.assertEqual(msg.publication, 789123)
        self.assertEqual(msg.args, [1, 2, 3])
        self.assertEqual(msg.kwargs, {u'foo': 23, u'bar': u'hello'})
        self.assertEqual(msg.publisher, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Event.MESSAGE_TYPE, 123456, 789123, {u'publisher': 300}]
        msg = message.Event.parse(wmsg)
        self.assertIsInstance(msg, message.Event)
        self.assertEqual(msg.subscription, 123456)
        self.assertEqual(msg.publication, 789123)
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.publisher, 300)
        self.assertEqual(msg.marshal(), wmsg)

    def test_retained_default_false(self):
        wmsg = [message.Event.MESSAGE_TYPE, 123456, 789123, {}]
        msg = message.Event.parse(wmsg)
        self.assertIsInstance(msg, message.Event)
        self.assertEqual(msg.retained, None)
        self.assertNotEqual(msg.retained, True)
        self.assertEqual(msg.marshal(), wmsg)

    def test_retained_explicit_false(self):
        wmsg = [message.Event.MESSAGE_TYPE, 123456, 789123, {u'retained': False}]
        msg = message.Event.parse(wmsg)
        self.assertIsInstance(msg, message.Event)
        self.assertEqual(msg.retained, False)
        self.assertNotEqual(msg.retained, True)
        self.assertEqual(msg.marshal(), wmsg)

    def test_retained_explicit_true(self):
        wmsg = [message.Event.MESSAGE_TYPE, 123456, 789123, {u'retained': True}]
        msg = message.Event.parse(wmsg)
        self.assertIsInstance(msg, message.Event)
        self.assertEqual(msg.retained, True)
        self.assertEqual(msg.marshal(), wmsg)


class TestRegisterMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Register(123456, u'com.myapp.procedure1')
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Register.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})
        self.assertEqual(msg[3], u'com.myapp.procedure1')

        e = message.Register(123456, u'com.myapp.procedure1', match=u'wildcard')
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Register.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {u'match': u'wildcard'})
        self.assertEqual(msg[3], u'com.myapp.procedure1')

    def test_ctor_reregister(self):
        e = message.Register(123456, u'com.myapp.procedure1', force_reregister=True)
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Register.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {u'force_reregister': True})
        self.assertEqual(msg[3], u'com.myapp.procedure1')

        e2 = message.Register.parse(msg)
        str(e2)

    def test_parse_reregister_illegal_force(self):
        msg = [
            message.Register.MESSAGE_TYPE,
            123456,
            {u'force_reregister': 'truthy'},
            u'com.myapp.procedure1',
        ]

        with self.assertRaises(ProtocolError) as ctx:
            message.Register.parse(msg)
        self.assertIn("invalid type", str(ctx.exception))

    def test_parse_and_marshal(self):
        wmsg = [message.Register.MESSAGE_TYPE, 123456, {}, u'com.myapp.procedure1']
        msg = message.Register.parse(wmsg)
        self.assertIsInstance(msg, message.Register)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.procedure, u'com.myapp.procedure1')
        self.assertEqual(msg.match, u'exact')
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Register.MESSAGE_TYPE, 123456, {u'match': u'wildcard'}, u'com.myapp.procedure1']
        msg = message.Register.parse(wmsg)
        self.assertIsInstance(msg, message.Register)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.procedure, u'com.myapp.procedure1')
        self.assertEqual(msg.match, u'wildcard')
        self.assertEqual(msg.marshal(), wmsg)


class TestRegisteredMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Registered(123456, 789123)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Registered.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)

    def test_parse_and_marshal(self):
        wmsg = [message.Registered.MESSAGE_TYPE, 123456, 789123]
        msg = message.Registered.parse(wmsg)
        self.assertIsInstance(msg, message.Registered)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.registration, 789123)
        self.assertEqual(msg.marshal(), wmsg)


class TestUnregisterMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Unregister(123456, 789123)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Unregister.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)

    def test_parse_and_marshal(self):
        wmsg = [message.Unregister.MESSAGE_TYPE, 123456, 789123]
        msg = message.Unregister.parse(wmsg)
        self.assertIsInstance(msg, message.Unregister)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.registration, 789123)
        self.assertEqual(msg.marshal(), wmsg)


class TestUnregisteredMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Unregistered(123456)
        msg = e.marshal()
        self.assertEqual(len(msg), 2)
        self.assertEqual(msg[0], message.Unregistered.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)

        e = message.Unregistered(0, registration=123456)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Unregistered.MESSAGE_TYPE)
        self.assertEqual(msg[1], 0)
        self.assertEqual(msg[2], {u'registration': 123456})

        e = message.Unregistered(0, registration=123456, reason=u"wamp.registration.revoked")
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Unregistered.MESSAGE_TYPE)
        self.assertEqual(msg[1], 0)
        self.assertEqual(msg[2], {u'registration': 123456, u'reason': u"wamp.registration.revoked"})

    def test_parse_and_marshal(self):
        wmsg = [message.Unregistered.MESSAGE_TYPE, 123456]
        msg = message.Unregistered.parse(wmsg)
        self.assertIsInstance(msg, message.Unregistered)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.registration, None)
        self.assertEqual(msg.reason, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Unregistered.MESSAGE_TYPE, 0, {u'registration': 123456}]
        msg = message.Unregistered.parse(wmsg)
        self.assertIsInstance(msg, message.Unregistered)
        self.assertEqual(msg.request, 0)
        self.assertEqual(msg.registration, 123456)
        self.assertEqual(msg.reason, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Unregistered.MESSAGE_TYPE, 0, {u'registration': 123456, u'reason': u"wamp.registration.revoked"}]
        msg = message.Unregistered.parse(wmsg)
        self.assertIsInstance(msg, message.Unregistered)
        self.assertEqual(msg.request, 0)
        self.assertEqual(msg.registration, 123456)
        self.assertEqual(msg.reason, u"wamp.registration.revoked")
        self.assertEqual(msg.marshal(), wmsg)


class TestCallMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Call(123456, u'com.myapp.procedure1')
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Call.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})
        self.assertEqual(msg[3], u'com.myapp.procedure1')

        e = message.Call(123456, u'com.myapp.procedure1', args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'})
        msg = e.marshal()
        self.assertEqual(len(msg), 6)
        self.assertEqual(msg[0], message.Call.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})
        self.assertEqual(msg[3], u'com.myapp.procedure1')
        self.assertEqual(msg[4], [1, 2, 3])
        self.assertEqual(msg[5], {u'foo': 23, u'bar': u'hello'})

        e = message.Call(123456, u'com.myapp.procedure1', timeout=10000)
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Call.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {u'timeout': 10000})
        self.assertEqual(msg[3], u'com.myapp.procedure1')

    def test_parse_and_marshal(self):
        wmsg = [message.Call.MESSAGE_TYPE, 123456, {}, u'com.myapp.procedure1']
        msg = message.Call.parse(wmsg)
        self.assertIsInstance(msg, message.Call)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.procedure, u'com.myapp.procedure1')
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.timeout, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Call.MESSAGE_TYPE, 123456, {}, u'com.myapp.procedure1', [1, 2, 3], {u'foo': 23, u'bar': u'hello'}]
        msg = message.Call.parse(wmsg)
        self.assertIsInstance(msg, message.Call)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.procedure, u'com.myapp.procedure1')
        self.assertEqual(msg.args, [1, 2, 3])
        self.assertEqual(msg.kwargs, {u'foo': 23, u'bar': u'hello'})
        self.assertEqual(msg.timeout, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Call.MESSAGE_TYPE, 123456, {u'timeout': 10000}, u'com.myapp.procedure1']
        msg = message.Call.parse(wmsg)
        self.assertIsInstance(msg, message.Call)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.procedure, u'com.myapp.procedure1')
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.timeout, 10000)
        self.assertEqual(msg.marshal(), wmsg)


class TestCancelMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Cancel(123456)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Cancel.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})

        e = message.Cancel(123456, mode=message.Cancel.KILL)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Cancel.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {u'mode': message.Cancel.KILL})

    def test_parse_and_marshal(self):
        wmsg = [message.Cancel.MESSAGE_TYPE, 123456, {}]
        msg = message.Cancel.parse(wmsg)
        self.assertIsInstance(msg, message.Cancel)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.mode, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Cancel.MESSAGE_TYPE, 123456, {u'mode': message.Cancel.KILL}]
        msg = message.Cancel.parse(wmsg)
        self.assertIsInstance(msg, message.Cancel)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.mode, message.Cancel.KILL)
        self.assertEqual(msg.marshal(), wmsg)


class TestResultMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Result(123456)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Result.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})

        e = message.Result(123456, args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'})
        msg = e.marshal()
        self.assertEqual(len(msg), 5)
        self.assertEqual(msg[0], message.Result.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})
        self.assertEqual(msg[3], [1, 2, 3])
        self.assertEqual(msg[4], {u'foo': 23, u'bar': u'hello'})

        e = message.Result(123456, progress=True)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Result.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {u'progress': True})

    def test_parse_and_marshal(self):
        wmsg = [message.Result.MESSAGE_TYPE, 123456, {}]
        msg = message.Result.parse(wmsg)
        self.assertIsInstance(msg, message.Result)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.progress, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Result.MESSAGE_TYPE, 123456, {}, [1, 2, 3], {u'foo': 23, u'bar': u'hello'}]
        msg = message.Result.parse(wmsg)
        self.assertIsInstance(msg, message.Result)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.args, [1, 2, 3])
        self.assertEqual(msg.kwargs, {u'foo': 23, u'bar': u'hello'})
        self.assertEqual(msg.progress, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Result.MESSAGE_TYPE, 123456, {u'progress': True}]
        msg = message.Result.parse(wmsg)
        self.assertIsInstance(msg, message.Result)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.progress, True)
        self.assertEqual(msg.marshal(), wmsg)


class TestInvocationMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Invocation(123456, 789123)
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Invocation.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)
        self.assertEqual(msg[3], {})

        e = message.Invocation(123456, 789123, args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'})
        msg = e.marshal()
        self.assertEqual(len(msg), 6)
        self.assertEqual(msg[0], message.Invocation.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)
        self.assertEqual(msg[3], {})
        self.assertEqual(msg[4], [1, 2, 3])
        self.assertEqual(msg[5], {u'foo': 23, u'bar': u'hello'})

        e = message.Invocation(123456, 789123, timeout=10000)
        msg = e.marshal()
        self.assertEqual(len(msg), 4)
        self.assertEqual(msg[0], message.Invocation.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], 789123)
        self.assertEqual(msg[3], {u'timeout': 10000})

    def test_parse_and_marshal(self):
        wmsg = [message.Invocation.MESSAGE_TYPE, 123456, 789123, {}]
        msg = message.Invocation.parse(wmsg)
        self.assertIsInstance(msg, message.Invocation)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.registration, 789123)
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.timeout, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Invocation.MESSAGE_TYPE, 123456, 789123, {}, [1, 2, 3], {u'foo': 23, u'bar': u'hello'}]
        msg = message.Invocation.parse(wmsg)
        self.assertIsInstance(msg, message.Invocation)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.registration, 789123)
        self.assertEqual(msg.args, [1, 2, 3])
        self.assertEqual(msg.kwargs, {u'foo': 23, u'bar': u'hello'})
        self.assertEqual(msg.timeout, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Invocation.MESSAGE_TYPE, 123456, 789123, {u'timeout': 10000}]
        msg = message.Invocation.parse(wmsg)
        self.assertIsInstance(msg, message.Invocation)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.registration, 789123)
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.timeout, 10000)
        self.assertEqual(msg.marshal(), wmsg)


class TestInterruptMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Interrupt(123456)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Interrupt.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})

        e = message.Interrupt(123456, mode=message.Interrupt.KILL)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Interrupt.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {u'mode': message.Interrupt.KILL})

    def test_parse_and_marshal(self):
        wmsg = [message.Interrupt.MESSAGE_TYPE, 123456, {}]
        msg = message.Interrupt.parse(wmsg)
        self.assertIsInstance(msg, message.Interrupt)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.mode, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Interrupt.MESSAGE_TYPE, 123456, {u'mode': message.Interrupt.KILL}]
        msg = message.Interrupt.parse(wmsg)
        self.assertIsInstance(msg, message.Interrupt)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.mode, message.Interrupt.KILL)
        self.assertEqual(msg.marshal(), wmsg)


class TestYieldMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Yield(123456)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Yield.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})

        e = message.Yield(123456, args=[1, 2, 3], kwargs={u'foo': 23, u'bar': u'hello'})
        msg = e.marshal()
        self.assertEqual(len(msg), 5)
        self.assertEqual(msg[0], message.Yield.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {})
        self.assertEqual(msg[3], [1, 2, 3])
        self.assertEqual(msg[4], {u'foo': 23, u'bar': u'hello'})

        e = message.Yield(123456, progress=True)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Yield.MESSAGE_TYPE)
        self.assertEqual(msg[1], 123456)
        self.assertEqual(msg[2], {u'progress': True})

    def test_parse_and_marshal(self):
        wmsg = [message.Yield.MESSAGE_TYPE, 123456, {}]
        msg = message.Yield.parse(wmsg)
        self.assertIsInstance(msg, message.Yield)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.progress, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Yield.MESSAGE_TYPE, 123456, {}, [1, 2, 3], {u'foo': 23, u'bar': u'hello'}]
        msg = message.Yield.parse(wmsg)
        self.assertIsInstance(msg, message.Yield)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.args, [1, 2, 3])
        self.assertEqual(msg.kwargs, {u'foo': 23, u'bar': u'hello'})
        self.assertEqual(msg.progress, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Yield.MESSAGE_TYPE, 123456, {u'progress': True}]
        msg = message.Yield.parse(wmsg)
        self.assertIsInstance(msg, message.Yield)
        self.assertEqual(msg.request, 123456)
        self.assertEqual(msg.args, None)
        self.assertEqual(msg.kwargs, None)
        self.assertEqual(msg.progress, True)
        self.assertEqual(msg.marshal(), wmsg)


class TestHelloMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Hello(u"realm1", {u'publisher': role.RolePublisherFeatures()})
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Hello.MESSAGE_TYPE)
        self.assertEqual(msg[1], u"realm1")
        self.assertEqual(msg[2], {u'roles': {u'publisher': {}}})

        e = message.Hello(u"realm1", {u'publisher': role.RolePublisherFeatures(subscriber_blackwhite_listing=True)})
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Hello.MESSAGE_TYPE)
        self.assertEqual(msg[1], u"realm1")
        self.assertEqual(msg[2], {u'roles': {u'publisher': {u'features': {u'subscriber_blackwhite_listing': True}}}})

        e = message.Hello(u"realm1", {u'publisher': role.RolePublisherFeatures(subscriber_blackwhite_listing=True)}, resumable=True)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Hello.MESSAGE_TYPE)
        self.assertEqual(msg[1], u"realm1")
        self.assertEqual(msg[2], {u'roles': {u'publisher': {u'features': {u'subscriber_blackwhite_listing': True}}}, u'resumable': True})

    def test_parse_and_marshal(self):
        wmsg = [message.Hello.MESSAGE_TYPE, u"realm1", {u'roles': {u'publisher': {}}}]
        msg = message.Hello.parse(wmsg)
        self.assertIsInstance(msg, message.Hello)
        self.assertEqual(msg.realm, u"realm1")
        self.assertEqual(msg.roles, {u'publisher': role.RolePublisherFeatures()})
        self.assertEqual(msg.resumable, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Hello.MESSAGE_TYPE, u"realm1", {u'roles': {u'publisher': {u'features': {u'subscriber_blackwhite_listing': True}}}}]
        msg = message.Hello.parse(wmsg)
        self.assertIsInstance(msg, message.Hello)
        self.assertEqual(msg.realm, u"realm1")
        self.assertEqual(msg.roles, {u'publisher': role.RolePublisherFeatures(subscriber_blackwhite_listing=True)})
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Hello.MESSAGE_TYPE, u"realm1", {u'roles': {u'publisher': {}}, u'resumable': False}]
        msg = message.Hello.parse(wmsg)
        self.assertIsInstance(msg, message.Hello)
        self.assertEqual(msg.realm, u"realm1")
        self.assertEqual(msg.roles, {u'publisher': role.RolePublisherFeatures()})
        self.assertEqual(msg.resumable, False)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Hello.MESSAGE_TYPE, u"realm1", {u'roles': {u'publisher': {}}, u'resumable': True, u'resume-session': 1234, u'resume-token': u"dsjgsg"}]
        msg = message.Hello.parse(wmsg)
        self.assertIsInstance(msg, message.Hello)
        self.assertEqual(msg.realm, u"realm1")
        self.assertEqual(msg.roles, {u'publisher': role.RolePublisherFeatures()})
        self.assertEqual(msg.resumable, True)
        self.assertEqual(msg.resume_session, 1234)
        self.assertEqual(msg.resume_token, u"dsjgsg")
        self.assertEqual(msg.marshal(), wmsg)

    def test_str(self):
        e = message.Hello(u"realm1", {u'publisher': role.RolePublisherFeatures()})
        self.assertIsInstance(str(e), str)


class TestGoodbyeMessage(unittest.TestCase):

    def test_ctor(self):
        reason = u'wamp.error.system_shutdown'
        reason_msg = u'The host is shutting down now.'

        e = message.Goodbye()
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Goodbye.MESSAGE_TYPE)
        self.assertEqual(msg[1], {})
        self.assertEqual(msg[2], message.Goodbye.DEFAULT_REASON)

        e = message.Goodbye(reason=reason)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Goodbye.MESSAGE_TYPE)
        self.assertEqual(msg[1], {})
        self.assertEqual(msg[2], reason)

        e = message.Goodbye(reason=reason, message=reason_msg)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
        self.assertEqual(msg[0], message.Goodbye.MESSAGE_TYPE)
        self.assertEqual(msg[1], {u'message': reason_msg})
        self.assertEqual(msg[2], reason)

    def test_parse_and_marshal(self):
        reason = u'wamp.error.system_shutdown'
        reason_msg = u'The host is shutting down now.'

        wmsg = [message.Goodbye.MESSAGE_TYPE]
        self.assertRaises(ProtocolError, message.Goodbye.parse, wmsg)

        wmsg = [message.Goodbye.MESSAGE_TYPE, reason]
        self.assertRaises(ProtocolError, message.Goodbye.parse, wmsg)

        wmsg = [message.Goodbye.MESSAGE_TYPE, {u'message': 100}, reason]
        self.assertRaises(ProtocolError, message.Goodbye.parse, wmsg)

        wmsg = [message.Goodbye.MESSAGE_TYPE, {}, reason]
        msg = message.Goodbye.parse(wmsg)
        self.assertIsInstance(msg, message.Goodbye)
        self.assertEqual(msg.reason, reason)
        self.assertEqual(msg.message, None)
        self.assertEqual(msg.marshal(), wmsg)

        wmsg = [message.Goodbye.MESSAGE_TYPE, {u'message': reason_msg}, reason]
        msg = message.Goodbye.parse(wmsg)
        self.assertIsInstance(msg, message.Goodbye)
        self.assertEqual(msg.reason, reason)
        self.assertEqual(msg.message, reason_msg)
        self.assertEqual(msg.marshal(), wmsg)

    def test_str(self):
        e = message.Goodbye(reason=u'wamp.error.system_shutdown', message=u'The host is shutting down now.')
        self.assertIsInstance(str(e), str)
