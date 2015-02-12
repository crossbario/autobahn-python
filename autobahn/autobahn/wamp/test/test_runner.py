###############################################################################
##
# Copyright (C) 2014 Tavendo GmbH
##
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
##
# http://www.apache.org/licenses/LICENSE-2.0
##
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##
###############################################################################

from __future__ import absolute_import

# from twisted.trial import unittest
import unittest
import platform

from twisted.internet.error import DNSLookupError
from twisted.internet.error import ConnectionRefusedError

from autobahn.twisted.wamp import ApplicationRunner

class TestWampTwistedRunner(unittest.TestCase):

    def test_connect_error(self):
        '''
        Ensure the runner doesn't swallow errors, and exit the reactor
        properly if there is one.
        '''
        runner = ApplicationRunner('ws://localhost:1', 'realm')

        # FIXME: we're really running the reactor here; that's not so awesome...
        # could we pass a reactor to the runner somehow?
        self.assertRaises(
            ConnectionRefusedError,
            # pass a no-op session-creation method
            runner.run, lambda _: None
        )

if __name__ == '__main__':
    unittest.main()
