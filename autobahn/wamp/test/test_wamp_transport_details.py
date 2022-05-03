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

TRANSPORT_DETAILS_1 = {
    # TransportDetails.CHANNEL_TYPE_TO_STR[TransportDetails.CHANNEL_TYPE_TCP]
    'channel_type': 'tcp',

    # TransportDetails.CHANNEL_FRAMING_TO_STR[TransportDetails.CHANNEL_FRAMING_WEBSOCKET]
    'channel_framing': 'websocket',

    # TransportDetails.CHANNEL_SERIALIZER_TO_STR[TransportDetails.CHANNEL_SERIALIZER_CBOR]
    'channel_serializer': 'cbor',

    # This end of the connection
    'own': 'ws://localhost:8080/ws',
    'own_pid': 9182731,
    'own_tid': 7563483,
    'own_fd': 20914571,

    # Peer of the connection
    'peer': 'tcp4:127.0.0.1:48576',
    'is_server': True,

    # TLS
    'is_secure': False,
    'channel_id': None,
    'peer_cert': None,

    # only filled when using WebSocket
    'websocket_protocol': 'wamp.2.cbor.batched',
    'websocket_extensions_in_use': None,

    # only filled when using HTTP (including regular WebSocket)
    'http_headers_received': {'cache-control': 'no-cache',
                              'connection': 'Upgrade',
                              'host': 'localhost:8080',
                              'pragma': 'no-cache',
                              'sec-websocket-extensions': 'permessage-deflate; '
                                                          'client_no_context_takeover; '
                                                          'client_max_window_bits',
                              'sec-websocket-key': 'Q+t++aGQJPaFLzDW7LktEQ==',
                              'sec-websocket-protocol': 'wamp.2.cbor.batched,wamp.2.cbor,wamp.2.msgpack.batched,wamp.2.msgpack,wamp.2.ubjson.batched,wamp.2.ubjson,wamp.2.json.batched,wamp.2.json',
                              'sec-websocket-version': '13',
                              'upgrade': 'WebSocket',
                              'user-agent': 'AutobahnPython/22.4.1.dev5'},
    'http_headers_sent': {'Set-Cookie': 'cbtid=JD27oZC18xS+O4VE9+x5iyKR;max-age=604800'},
    'http_cbtid': 'JD27oZC18xS+O4VE9+x5iyKR',
}


class TestTransportDetails(unittest.TestCase):

    def test_ctor_empty(self):
        td = TransportDetails()
        data = td.marshal()
        self.assertEqual(data, {
            'channel_type': None,
            'channel_framing': None,
            'channel_serializer': None,
            'own': None,
            'peer': None,
            'is_server': None,
            'own_pid': None,
            'own_tid': None,
            'own_fd': None,
            'is_secure': None,
            'channel_id': None,
            'peer_cert': None,
            'websocket_protocol': None,
            'websocket_extensions_in_use': None,
            'http_headers_received': None,
            'http_headers_sent': None,
            'http_cbtid': None,
        })
        td2 = TransportDetails.parse(td.marshal())
        self.assertEqual(td2, td)

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

    def test_parse(self):
        td = TransportDetails.parse(TRANSPORT_DETAILS_1)
        data2 = td.marshal()
        self.maxDiff = None
        self.assertEqual(data2, TRANSPORT_DETAILS_1)

    def test_channel_typeid(self):
        # test empty
        td = TransportDetails()
        self.assertEqual(td.channel_typeid, 'null-null-null')

        # test all combinations
        for channel_type in TransportDetails.CHANNEL_TYPE_TO_STR:
            for channel_framing in TransportDetails.CHANNEL_FRAMING_TO_STR:
                for channel_serializer in TransportDetails.CHANNEL_SERIALIZER_TO_STR:
                    td = TransportDetails(channel_type=channel_type, channel_framing=channel_framing, channel_serializer=channel_serializer)
                    channel_typeid = '{}-{}-{}'.format(TransportDetails.CHANNEL_TYPE_TO_STR[channel_type],
                                                       TransportDetails.CHANNEL_FRAMING_TO_STR[channel_framing],
                                                       TransportDetails.CHANNEL_SERIALIZER_TO_STR[channel_serializer])
                    self.assertEqual(td.channel_typeid, channel_typeid)
