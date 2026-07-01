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

    def test_version_falls_back_to_dunder_version_on_bare_hash(self):
        "version() falls back to __version__ when __git_version__ is a non-matching bare hash"
        # On built wheels / shallow clones `git describe --tags --always` yields a bare
        # commit hash that does NOT match the vX.Y.Z pattern; version() must fall back to
        # the reliable static __version__, NOT return (0, 0, 0, None, None).
        orig = flatbuffers.__git_version__
        try:
            flatbuffers.__git_version__ = "19b2300f"
            v = flatbuffers.version()
            self.assertNotEqual(v, (0, 0, 0, None, None))
            expected = tuple(int(x) for x in flatbuffers.__version__.split(".")[:3])
            self.assertEqual(v, (*expected, None, None))
        finally:
            flatbuffers.__git_version__ = orig

    def test_version_falls_back_to_dunder_version_on_unknown(self):
        "version() falls back to __version__ when __git_version__ is 'unknown'"
        orig = flatbuffers.__git_version__
        try:
            flatbuffers.__git_version__ = "unknown"  # hatch_build default on describe failure
            expected = tuple(int(x) for x in flatbuffers.__version__.split(".")[:3])
            self.assertEqual(flatbuffers.version(), (*expected, None, None))
        finally:
            flatbuffers.__git_version__ = orig

    def test_version_preserves_git_describe_detail(self):
        "version() still returns rich git-describe detail when __git_version__ matches"
        orig = flatbuffers.__git_version__
        try:
            flatbuffers.__git_version__ = "v25.9.23-71-g19b2300f"
            self.assertEqual(flatbuffers.version(), (25, 9, 23, 71, "19b2300f"))
        finally:
            flatbuffers.__git_version__ = orig

    @unittest.skipUnless(HAS_ZLMDB, "zlmdb not installed")
    def test_zlmdb_flatbuffers_in_sync(self):
        "autobahn and zlmdb vendor the same FlatBuffers version (data-in-transit vs data-at-rest)"
        version = autobahn.check_zlmdb_flatbuffers_version_in_sync()
        self.assertEqual(version, flatbuffers.__version__)
        import zlmdb.flatbuffers

        self.assertEqual(version, zlmdb.flatbuffers.__version__)

    @unittest.skipUnless(HAS_ZLMDB, "zlmdb not installed")
    def test_zlmdb_flatbuffers_mismatch_raises(self):
        "check_zlmdb_flatbuffers_version_in_sync() raises when the two vendored __version__ differ"
        # guard against regressions to comparing version() (which is (0,0,0,...) on
        # built wheels and would never detect a mismatch): force the two vendored
        # __version__ strings apart and assert the check actually raises.
        orig = flatbuffers.__version__
        try:
            flatbuffers.__version__ = orig + "-mismatch"
            with self.assertRaises(RuntimeError):
                autobahn.check_zlmdb_flatbuffers_version_in_sync()
        finally:
            flatbuffers.__version__ = orig
