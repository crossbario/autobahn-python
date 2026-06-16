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

import os
import sys
import unittest
from unittest import mock

from autobahn.nvx import _compile_args
from autobahn.nvx._compile_args import (
    get_compile_args,
    _get_safe_march_flag,
    _get_target_machine,
)


class TestSafeMarchFlag(unittest.TestCase):
    """Architecture -> safe -march flag mapping (#1834, #1717)."""

    def test_x86_64_variants(self):
        for machine in ("x86_64", "amd64", "x64"):
            self.assertEqual(_get_safe_march_flag(machine), "-march=x86-64-v2")

    def test_arm64_variants(self):
        for machine in ("aarch64", "arm64"):
            self.assertEqual(_get_safe_march_flag(machine), "-march=armv8-a")

    def test_unknown_arch_returns_none(self):
        # Unknown architectures must not get a -march flag (let the toolchain
        # defaults / CFLAGS decide), so cross-compilation is never broken.
        self.assertIsNone(_get_safe_march_flag("riscv64"))


class TestTargetMachine(unittest.TestCase):
    def test_returns_nonempty_lowercase(self):
        machine = _get_target_machine()
        self.assertIsInstance(machine, str)
        self.assertTrue(machine)
        self.assertEqual(machine, machine.lower())

    def test_uses_sysconfig_target_arch(self):
        # When cross-compiling, sysconfig.get_platform() reflects the *target*
        # (e.g. aarch64) even on an x86-64 build host - this is the whole point
        # of preferring it over platform.machine() (#1834 / PR #1835).
        with mock.patch(
            "autobahn.nvx._compile_args.sysconfig.get_platform",
            return_value="linux-aarch64",
        ):
            self.assertEqual(_get_target_machine(), "aarch64")


class TestGetCompileArgs(unittest.TestCase):
    """Default-safe / opt-in-native behaviour (#1834)."""

    def test_default_is_never_native(self):
        # The core #1834 guard: with no override, -march=native must NEVER be
        # emitted (it breaks cross-compilation and can SIGILL distributed wheels).
        with mock.patch.dict("os.environ", {}, clear=False):
            os.environ.pop("AUTOBAHN_ARCH_TARGET", None)
            self.assertNotIn("-march=native", get_compile_args())

    def test_safe_matches_default(self):
        with mock.patch.dict("os.environ", {}, clear=False):
            os.environ.pop("AUTOBAHN_ARCH_TARGET", None)
            default_args = get_compile_args()
        with mock.patch.dict("os.environ", {"AUTOBAHN_ARCH_TARGET": "safe"}):
            self.assertEqual(get_compile_args(), default_args)

    @unittest.skipIf(sys.platform == "win32", "MSVC path uses /arch, not -march")
    def test_native_is_opt_in(self):
        with mock.patch.dict("os.environ", {"AUTOBAHN_ARCH_TARGET": "native"}):
            self.assertIn("-march=native", get_compile_args())

    @unittest.skipIf(sys.platform == "win32", "MSVC path uses /arch, not -march")
    def test_unknown_target_emits_no_march(self):
        # An unrecognized cross-compile target must yield no -march flag at all.
        with mock.patch.dict("os.environ", {}, clear=False):
            os.environ.pop("AUTOBAHN_ARCH_TARGET", None)
            with mock.patch.object(
                _compile_args, "_get_target_machine", return_value="riscv64"
            ):
                args = get_compile_args()
        self.assertFalse(any(a.startswith("-march") for a in args))

    @unittest.skipIf(sys.platform != "win32", "MSVC-specific flags")
    def test_windows_uses_msvc_flags(self):
        self.assertEqual(get_compile_args(), ["/O2", "/W3"])


if __name__ == "__main__":
    unittest.main()
