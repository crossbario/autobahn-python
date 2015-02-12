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

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from mock import patch


class FakeReactor:
    '''
    This just fakes out enough reactor methods so .run() can work.
    '''
    stop_called = False

    def __init__(self, to_raise):
        self.stop_called = False
        self.to_raise = to_raise

    def run(self, *args, **kw):
        raise self.to_raise

    def stop(self):
        self.stop_called = True

    def connectTCP(self, *args, **kw):
        raise RuntimeError("ConnectTCP shouldn't get called")


class TestWampTwistedRunner(unittest.TestCase):

    def test_connect_error(self):
        '''
        Ensure the runner doesn't swallow errors and that it exits the
        reactor properly if there is one.
        '''
        try:
            from autobahn.twisted.wamp import ApplicationRunner
            from twisted.internet.error import ConnectionRefusedError
            # the 'reactor' member doesn't exist until we import it
            from twisted.internet import reactor  # noqa: F401
        except ImportError:
            raise unittest.SkipTest('No twisted')

        runner = ApplicationRunner('ws://localhost:1', 'realm')
        exception = ConnectionRefusedError("It's a trap!")

        with patch('twisted.internet.reactor', FakeReactor(exception)) as mockreactor:
            self.assertRaises(
                ConnectionRefusedError,
                # pass a no-op session-creation method
                runner.run, lambda _: None, start_reactor=True
            )
            self.assertTrue(mockreactor.stop_called)

if __name__ == '__main__':
    unittest.main()
