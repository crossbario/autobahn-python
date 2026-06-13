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

import autobahn
from autobahn import flatbuffers

# zlmdb is not a hard dependency of autobahn; the cross-project version-sync
# check (and its test) only run when zlmdb is also installed.
try:
    import zlmdb.flatbuffers  # noqa: F401

    HAS_ZLMDB = True
except ImportError:
    HAS_ZLMDB = False


class TestFlatBuffersVersion(unittest.TestCase):
    def test_version_tuple(self):
        "autobahn.flatbuffers.version() returns a parsed 5-tuple"
        v = flatbuffers.version()
        self.assertIsInstance(v, tuple)
        self.assertEqual(len(v), 5)
        major, minor, patch, commits, commit_hash = v
        self.assertIsInstance(major, int)
        self.assertIsInstance(minor, int)
        self.assertIsInstance(patch, int)
        # a released, tagged runtime has no extra commits/hash
        self.assertTrue(commits is None or isinstance(commits, int))
        self.assertTrue(commit_hash is None or isinstance(commit_hash, str))

    @unittest.skipUnless(HAS_ZLMDB, "zlmdb not installed")
    def test_zlmdb_flatbuffers_in_sync(self):
        "autobahn and zlmdb vendor the same FlatBuffers version (data-in-transit vs data-at-rest)"
        version = autobahn.check_zlmdb_flatbuffers_version_in_sync()
        self.assertEqual(version, flatbuffers.version())
        import zlmdb.flatbuffers

        self.assertEqual(version, zlmdb.flatbuffers.version())
