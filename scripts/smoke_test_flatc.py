#!/usr/bin/env python3
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
"""
Shared smoke tests for FlatBuffers and flatc bundling verification.

This module provides reusable test functions for verifying that FlatBuffers
runtime and flatc compiler are correctly bundled in a package.

Note: This file is shared across WAMP ecosystem projects via wamp-cicd.
      Source: wamp-cicd/scripts/flatc/smoke_test_flatc.py
      Projects copy this file to: scripts/smoke_test_flatc.py
      Then import and call from their main smoke_test.py

Usage in project's smoke_test.py::

    from smoke_test_flatc import (
        test_import_flatbuffers,
        test_flatc_binary,
        test_reflection_files,
    )

    # In main test list:
    tests = [
        ...,
        lambda: test_import_flatbuffers("zlmdb"),
        lambda: test_flatc_binary("zlmdb"),
        lambda: test_reflection_files("zlmdb"),
    ]
"""

import os
import subprocess
from pathlib import Path


def test_import_flatbuffers(package_name: str) -> bool:
    """
    Test importing the vendored flatbuffers module and check version.

    :param package_name: Name of the package (e.g., "zlmdb", "autobahn")
    :returns: True if test passed, False otherwise
    """
    print(f"Test: Importing {package_name}.flatbuffers...")
    try:
        import importlib
        flatbuffers = importlib.import_module(f"{package_name}.flatbuffers")
        print(f"  FlatBuffers version: {flatbuffers.__version__}")
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import {package_name}.flatbuffers: {e}")
        return False


def test_flatc_binary(package_name: str) -> bool:
    """
    Test that flatc binary is available and works.

    This is a REQUIRED test - both wheel and sdist installs MUST include flatc.

    :param package_name: Name of the package (e.g., "zlmdb", "autobahn")
    :returns: True if test passed, False otherwise
    """
    print("Test: Checking flatc binary...")
    try:
        import importlib
        _flatc = importlib.import_module(f"{package_name}._flatc")
        get_flatc_path = _flatc.get_flatc_path

        flatc_path = get_flatc_path()
        print(f"  flatc path: {flatc_path}")

        if not os.path.isfile(flatc_path):
            print("  FAIL: flatc binary not found")
            print("        This is a packaging bug - flatc MUST be included")
            return False

        if not os.access(flatc_path, os.X_OK):
            print("  FAIL: flatc exists but not executable")
            return False

        # Try running flatc --version
        result = subprocess.run(
            [str(flatc_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        version_output = result.stdout.strip() or result.stderr.strip()
        print(f"  flatc version: {version_output}")

        if "flatc" in version_output.lower():
            print("  PASS")
            return True
        else:
            print("  FAIL: flatc --version returned unexpected output")
            return False
    except ImportError as e:
        print(f"  FAIL: {package_name}._flatc module not available: {e}")
        return False
    except Exception as e:
        print(f"  FAIL: Unexpected error: {e}")
        return False


def test_reflection_files(package_name: str) -> bool:
    """
    Test that FlatBuffers reflection files are present.

    This is a REQUIRED test - both wheel and sdist installs MUST include reflection files.

    :param package_name: Name of the package (e.g., "zlmdb", "autobahn")
    :returns: True if test passed, False otherwise
    """
    print("Test: Checking FlatBuffers reflection files...")
    try:
        import importlib
        flatbuffers = importlib.import_module(f"{package_name}.flatbuffers")

        fbs_dir = Path(flatbuffers.__file__).parent
        fbs_file = fbs_dir / "reflection.fbs"
        bfbs_file = fbs_dir / "reflection.bfbs"

        # reflection.fbs MUST be present
        if not fbs_file.exists():
            print(f"  FAIL: reflection.fbs not found at {fbs_file}")
            return False
        print(f"  reflection.fbs: {fbs_file.stat().st_size} bytes")

        # reflection.bfbs MUST be present (generated by flatc during build)
        if not bfbs_file.exists():
            print(f"  FAIL: reflection.bfbs not found at {bfbs_file}")
            print("        This is a packaging bug - reflection.bfbs MUST be included")
            return False

        print(f"  reflection.bfbs: {bfbs_file.stat().st_size} bytes")
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Reflection files check failed: {e}")
        return False
