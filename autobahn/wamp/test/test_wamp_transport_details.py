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

from autobahn.wamp.types import TransportDetails

import unittest


class TestTransportDetails(unittest.TestCase):

    def test_ctor_empty(self):
        td = TransportDetails()
        data = td.marshal()
        self.assertEqual(data, {
            'channel_type': None,
            'channel_framing': None,
            'channel_serializer': None,
            'peer': None,
            'is_server': None,
            'is_secure': None,
            'channel_id': None,
            'peer_cert': None,
            'websocket_protocol': None,
            'websocket_extensions_in_use': None,
            'http_headers_received': None,
            'http_headers_sent': None,
            'http_cbtid': None,
        })

    def test_attributes(self):
        td = TransportDetails()
        for channel_type in TransportDetails.CHANNEL_TYPE_TO_STR:
            td.channel_type = channel_type
            self.assertEqual(td.channel_type, channel_type)

        for channel_framing in TransportDetails.CHANNEL_FRAMING_TO_STR:
            td.channel_framing = channel_framing
            self.assertEqual(td.channel_framing, channel_framing)

        for channel_serializer in TransportDetails.CHANNEL_SERIALIZER_TO_STR:
            td.channel_serializer = channel_serializer
            self.assertEqual(td.channel_serializer, channel_serializer)
