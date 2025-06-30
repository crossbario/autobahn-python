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

import unittest

# from .test_wamp_transport_details import TRANSPORT_DETAILS_1
from autobahn.wamp.test.test_wamp_transport_details import TRANSPORT_DETAILS_1
from autobahn.wamp.types import SessionDetails, TransportDetails


class TestSessionDetails(unittest.TestCase):
    def test_empty(self):
        sd1 = SessionDetails()
        data = sd1.marshal()
        self.assertEqual(
            data,
            {
                "realm": None,
                "session": None,
                "authid": None,
                "authrole": None,
                "authmethod": None,
                "authprovider": None,
                "authextra": None,
                "serializer": None,
                "transport": None,
                "resumed": None,
                "resumable": None,
                "resume_token": None,
            },
        )
        sd2 = SessionDetails.parse(data)
        self.assertEqual(sd2, sd1)

    def test_attributes(self):
        sd1 = SessionDetails()
        td1 = TransportDetails.parse(TRANSPORT_DETAILS_1)
        sd1.realm = "realm1"
        sd1.session = 666
        sd1.authid = "homer"
        sd1.authrole = "user"
        sd1.authmethod = "wampcra"
        sd1.authprovider = "static"
        sd1.authextra = {"foo": "bar", "baz": [1, 2, 3]}
        sd1.serializer = "json"
        sd1.transport = td1
        sd1.resumed = False
        sd1.resumable = True
        sd1.resume_token = "8713e25a-d4f5-48b7-9d6d-eda66603a1ab"
        data = sd1.marshal()
        self.assertEqual(
            data,
            {
                "realm": sd1.realm,
                "session": sd1.session,
                "authid": sd1.authid,
                "authrole": sd1.authrole,
                "authmethod": sd1.authmethod,
                "authprovider": sd1.authprovider,
                "authextra": sd1.authextra,
                "serializer": sd1.serializer,
                "transport": sd1.transport.marshal(),
                "resumed": sd1.resumed,
                "resumable": sd1.resumable,
                "resume_token": sd1.resume_token,
            },
        )
        sd2 = SessionDetails.parse(data)
        self.assertEqual(sd2, sd1)
