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

import platform
import re
import unittest
from importlib.metadata import PackageNotFoundError, requires, version

# CVE-2026-111497 (out-of-bounds write in the brotli decoder) is fixed in brotli 1.2.1
# and brotlicffi 1.2.1.0, which bundles brotli 1.2.1. See #2024.
FIXED = {"brotli": (1, 2, 1), "brotlicffi": (1, 2, 1, 0)}

# the package permessage-brotli uses on this Python implementation
if platform.python_implementation() == "CPython":
    BACKEND = "brotli"
else:
    BACKEND = "brotlicffi"


def _vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v))


class TestBrotliFloor(unittest.TestCase):
    def test_declared_floor(self):
        "autobahn's extras require a brotli / brotlicffi with the CVE-2026-111497 fix"
        floors = {}
        for req in requires("autobahn") or []:
            m = re.match(r"(brotli|brotlicffi)\s*>=\s*([0-9.]+)", req)
            if m:
                floors.setdefault(m.group(1), []).append(_vtuple(m.group(2)))
        self.assertEqual(sorted(floors), ["brotli", "brotlicffi"], floors)
        for name, found in floors.items():
            for floor in found:
                self.assertGreaterEqual(floor, FIXED[name], name)

    def test_installed_version(self):
        "an installed brotli / brotlicffi has the CVE-2026-111497 fix"
        try:
            installed = version(BACKEND)
        except PackageNotFoundError:
            raise unittest.SkipTest(f"{BACKEND} is not installed")
        self.assertGreaterEqual(_vtuple(installed), FIXED[BACKEND], installed)
