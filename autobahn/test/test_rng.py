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
import sys
import unittest

import uuid
import random
from nacl import utils, public

from autobahn import util


@unittest.skipIf(not ('AUTOBAHN_CI_ENABLE_RNG_DEPLETION_TESTS' in os.environ and os.environ['AUTOBAHN_CI_ENABLE_RNG_DEPLETION_TESTS']), 'entropy depletion tests not enabled (env var AUTOBAHN_CI_ENABLE_RNG_DEPLETION_TESTS not set)')
@unittest.skipIf(not sys.platform.startswith('linux'), 'entropy depletion tests only available on Linux')
class TestEntropy(unittest.TestCase):

    def test_non_depleting(self):
        res = {}

        with open('/dev/urandom', 'rb') as rng:
            for i in range(1000):
                for j in range(100):

                    # "reseed" (seems pointless, but ..)
                    random.seed()

                    # random UUIDs
                    v1 = uuid.uuid4()  # noqa

                    # stdlib random
                    v2 = random.random()  # noqa
                    v3 = random.getrandbits(32)  # noqa
                    v4 = random.randint(0, 9007199254740992)  # noqa
                    v5 = random.normalvariate(10, 100)  # noqa
                    v6 = random.choice(range(100))  # noqa

                    # PyNaCl
                    v7 = utils.random(public.Box.NONCE_SIZE)  # noqa

                    # Autobahn utils
                    v8 = util.generate_token(4, 4)  # noqa
                    v9 = util.id()  # noqa
                    v10 = util.rid()  # noqa
                    v11 = util.newid()  # noqa

                # direct procfs access to PRNG
                d = rng.read(1000)  # noqa

                # check available entropy
                with open('/proc/sys/kernel/random/entropy_avail', 'r') as ent:
                    ea = int(ent.read()) // 100
                    if ea not in res:
                        res[ea] = 0
                    res[ea] += 1

        skeys = sorted(res.keys())

        print('\nsystem entropy depletion stats:')
        for k in skeys:
            print('{}: {}'.format(k, res[k]))

        self.assertTrue(skeys[0] > 0)

    def test_depleting(self):
        res = {}

        with open('/dev/random', 'rb') as rng:
            for i in range(10000):

                # direct procfs access to "real" RNG
                d = rng.read(1000)  # noqa

                # check available entropy
                with open('/proc/sys/kernel/random/entropy_avail', 'r') as ent:
                    ea = int(ent.read()) // 100
                    if ea not in res:
                        res[ea] = 0
                    res[ea] += 1

        skeys = sorted(res.keys())

        print('\nsystem entropy depletion stats:')
        for k in skeys:
            print('{}: {}'.format(k, res[k]))

        self.assertTrue(skeys[0] == 0)
