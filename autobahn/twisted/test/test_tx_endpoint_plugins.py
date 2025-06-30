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

from twisted.trial.unittest import TestCase


class PluginTests(TestCase):
    if True:
        skip = "Plugins don't work under Python3 yet"

    def test_import(self):
        from twisted.plugins import autobahn_endpoints

        self.assertTrue(hasattr(autobahn_endpoints, "AutobahnClientParser"))

    def test_parse_client_basic(self):
        from twisted.plugins import autobahn_endpoints

        self.assertTrue(hasattr(autobahn_endpoints, "AutobahnClientParser"))
        from twisted.internet import reactor
        from twisted.internet.endpoints import clientFromString, quoteStringArgument

        ep_string = "autobahn:{0}:url={1}".format(
            quoteStringArgument("tcp:localhost:9000"),
            quoteStringArgument("ws://localhost:9000"),
        )
        # we're just testing that this doesn't fail entirely
        clientFromString(reactor, ep_string)
