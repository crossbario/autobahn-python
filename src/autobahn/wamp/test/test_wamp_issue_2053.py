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

"""
Regression tests for autobahn-python#2053 (framework neutral).
"""

import os

if os.environ.get("USE_TWISTED", False) or os.environ.get("USE_ASYNCIO", False):
    import unittest
    from unittest.mock import Mock

    from autobahn.wamp import message
    from autobahn.wamp.exception import TransportLost
    from autobahn.wamp.message import _lazy_import
    from autobahn.wamp.protocol import ApplicationSession, _SessionShim
    from autobahn.wamp.types import ComponentConfig
    from autobahn.websocket.compress import (
        PERMESSAGE_COMPRESSION_EXTENSION,
        PerMessageCompress,
        PerMessageCompressOffer,
        PerMessageCompressResponse,
    )

    class TestRequireTransport(unittest.TestCase):
        def test_no_transport(self):
            session = ApplicationSession(ComponentConfig("realm1"))
            with self.assertRaises(TransportLost):
                session._require_transport()

        def test_transport(self):
            session = ApplicationSession(ComponentConfig("realm1"))
            transport = Mock()
            session._transport = transport
            self.assertIs(session._require_transport(), transport)

        def test_leave_without_transport(self):
            # a joined session whose transport is gone: TransportLost, not
            # AttributeError on None
            session = ApplicationSession(ComponentConfig("realm1"))
            session._session_id = 1
            with self.assertRaises(TransportLost):
                session.leave()

    class TestShimChallengeWithoutAuthenticators(unittest.TestCase):
        def test_challenge_without_authenticators(self):
            # Used to raise TypeError ('NoneType' object is not subscriptable),
            # not the RuntimeError naming the unknown authmethod.
            shim = _SessionShim(ComponentConfig("realm1"))
            self.assertIsNone(shim._authenticators)
            with self.assertRaises(RuntimeError) as ctx:
                shim.onChallenge(message.Challenge("ticket"))
            self.assertIn("unknown authmethod 'ticket'", str(ctx.exception))
            self.assertIn("authenticators=[]", str(ctx.exception))

        def test_merged_authextra_without_authenticators(self):
            shim = _SessionShim(ComponentConfig("realm1"))
            self.assertEqual(shim._merged_authextra(), {})

    class TestLazyImport(unittest.TestCase):
        def test_missing_module(self):
            # what a plain import raises, so callers' except ImportError works
            # (used to be AttributeError on None)
            with self.assertRaises(ModuleNotFoundError):
                _lazy_import("autobahn.no_such_module_2053")

    class TestPerMessageCompressContract(unittest.TestCase):
        def test_base_classes_declare_contract(self):
            with self.assertRaises(NotImplementedError):
                PerMessageCompressOffer.parse([])
            with self.assertRaises(NotImplementedError):
                PerMessageCompressResponse.parse([])
            with self.assertRaises(NotImplementedError):
                PerMessageCompress.create_from_offer_accept(True, None)
            with self.assertRaises(NotImplementedError):
                PerMessageCompress.create_from_response_accept(False, None)

        def test_registered_extensions_implement_contract(self):
            for name, classes in PERMESSAGE_COMPRESSION_EXTENSION.items():
                with self.subTest(extension=name):
                    for kind in ("Offer", "Response"):
                        self.assertIsNot(
                            classes[kind].__dict__.get("parse"), None, kind
                        )
                    pmce = classes["PMCE"].__dict__
                    self.assertIn("create_from_offer_accept", pmce)
                    self.assertIn("create_from_response_accept", pmce)
