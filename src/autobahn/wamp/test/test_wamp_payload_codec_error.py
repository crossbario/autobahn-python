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

# Issue #1988: ApplicationSession.call() with a payload codec whose encode()
# raises must re-raise the codec's exception, on Twisted AND asyncio.
# Backend-neutral: runs under trial (USE_TWISTED) and pytest (USE_ASYNCIO).
# session.log is deliberately NOT mocked: a Mock has every method, so it
# would hide a logger method that one backend lacks.

import os
import unittest

from autobahn.wamp.types import TransportDetails

USE_TWISTED = bool(os.environ.get("USE_TWISTED", False))

if USE_TWISTED:
    from autobahn.twisted.wamp import ApplicationSession
else:
    from autobahn.asyncio.wamp import ApplicationSession


class CodecError(Exception):
    pass


class FailingPayloadCodec:
    def encode(self, is_originating, uri, args=None, kwargs=None):
        raise CodecError("encode failed")

    def decode(self, is_originating, uri, encoded_payload):
        raise NotImplementedError()


class MockTransport:
    def __init__(self):
        self.messages = []
        self._transport_details = TransportDetails()

    def transport_details(self):
        return self._transport_details

    def send(self, msg):
        self.messages.append(msg)

    def close(self, *args, **kw):
        pass


def check_call_reraises_payload_codec_error(test: unittest.TestCase) -> None:
    session = ApplicationSession()
    session._transport = MockTransport()
    session._payload_codec = FailingPayloadCodec()

    with test.assertRaises(CodecError):
        session.call("com.example.procedure", 1, 2)

    # nothing went out on the wire
    test.assertEqual(session._transport.messages, [])


# One class per backend (a base class chosen at import time is a union type,
# which the type checker cannot use as a base).
if USE_TWISTED:
    from twisted.trial import unittest as trial_unittest

    class TestPayloadCodecError(trial_unittest.TestCase):
        def test_call_reraises_payload_codec_error(self):
            check_call_reraises_payload_codec_error(self)
            # trial fails a test that logged a Failure; the error is logged
            # on purpose (if it is logged as a Failure at all), so accept it
            self.flushLoggedErrors(CodecError)

else:

    class TestPayloadCodecError(unittest.TestCase):
        def test_call_reraises_payload_codec_error(self):
            check_call_reraises_payload_codec_error(self)
