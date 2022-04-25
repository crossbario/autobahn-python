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

import os
import unittest

from autobahn.xbr import HAS_XBR

if HAS_XBR:
    from autobahn.xbr import Profile, UserConfig

    class TestXbrUserConfig(unittest.TestCase):

        DOTDIR = '~/.xbrnetwork'
        PROFILE_NAME = 'default'
        NETWORK_URL = 'wss://planet.xbr.network/ws'
        NETWORK_REALM = 'xbrnetwork'
        PASSWORD = 'secret123'

        def test_create_empty_config(self):
            c = UserConfig('config.ini')
            self.assertEqual(c.profiles, {})

        def test_create_empty_profile(self):
            p = Profile()
            self.assertTrue(p.path is None)

        def test_load_home(self):
            config_dir = os.path.expanduser(self.DOTDIR)
            if not os.path.isdir(config_dir):
                os.mkdir(config_dir)
            config_path = os.path.join(config_dir, 'config.ini')
            if os.path.exists(config_path):
                c = UserConfig(config_path)
                c.load()
                self.assertIn(self.PROFILE_NAME, c.profiles)

        def test_write_default_config(self):
            config_dir = os.path.expanduser(self.DOTDIR)
            if not os.path.isdir(config_dir):
                os.mkdir(config_dir)
            config_path = os.path.join(config_dir, 'test.ini')

            c = UserConfig(config_path)
            p = Profile()
            c.profiles[self.PROFILE_NAME] = p
            c.save(self.PASSWORD)

            c2 = UserConfig(config_path)

            def get_pw():
                return self.PASSWORD

            c2.load(cb_get_password=get_pw)
            self.assertIn(self.PROFILE_NAME, c2.profiles)
