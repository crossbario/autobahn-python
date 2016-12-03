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
import unittest

if os.environ.get('USE_TWISTED', False):
    from autobahn.twisted.component import Component

    class InvalidTransportConfigs(unittest.TestCase):

        def test_invalid_key(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=dict(
                        foo='bar',  # totally invalid key
                    ),
                )
            self.assertIn("'foo' is not", str(ctx.exception))

        def test_invalid_key_transport_list(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=[
                        dict(type='websocket', url='ws://127.0.0.1/ws'),
                        dict(foo='bar'),  # totally invalid key
                    ]
                )
            self.assertIn("'foo' is not a valid configuration item", str(ctx.exception))

        def test_invalid_serializer_key(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=[
                        {
                            "url": "ws://127.0.0.1/ws",
                            "serializer": ["quux"],
                        }
                    ]
                )
            self.assertIn("only for rawsocket", str(ctx.exception))

        def test_invalid_serializer(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=[
                        {
                            "url": "ws://127.0.0.1/ws",
                            "serializers": ["quux"],
                        }
                    ]
                )
            self.assertIn("Invalid serializer", str(ctx.exception))

        def test_invalid_serializer_type_0(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=[
                        {
                            "url": "ws://127.0.0.1/ws",
                            "serializers": [1, 2],
                        }
                    ]
                )
            self.assertIn("must be a list", str(ctx.exception))

        def test_invalid_serializer_type_1(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=[
                        {
                            "url": "ws://127.0.0.1/ws",
                            "serializers": 1,
                        }
                    ]
                )
            self.assertIn("must be a list", str(ctx.exception))

        def test_invalid_type_key(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=[
                        {
                            "type": "bad",
                        }
                    ]
                )
            self.assertIn("Invalid transport type", str(ctx.exception))

        def test_invalid_type(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=[
                        "foo"
                    ]
                )
            self.assertIn("must be a dict", str(ctx.exception))

        def test_no_url(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=[
                        {
                            "type": "websocket",
                        }
                    ]
                )
            self.assertIn("Transport requires 'url'", str(ctx.exception))

        def test_endpoint_bogus_object(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=[
                        {
                            "type": "websocket",
                            "url": "ws://example.com/ws",
                            "endpoint": ("not", "a", "dict"),
                        }
                    ]
                )
            self.assertIn("'endpoint' configuration must be", str(ctx.exception))

        def test_endpoint_valid(self):
            Component(
                main=lambda r, s: None,
                transports=[
                    {
                        "type": "websocket",
                        "url": "ws://example.com/ws",
                        "endpoint": {
                            "type": "tcp",
                            "host": "1.2.3.4",
                            "port": "4321",
                        }
                    }
                ]
            )
