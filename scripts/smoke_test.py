#!/usr/bin/env python3
# Copyright (c) typedef int GmbH, Germany, 2025. All rights reserved.
#
# Smoke tests for autobahn package verification.
# Used by CI to verify wheels and sdists actually work after building.

"""
Smoke tests for autobahn package.

This script verifies that an autobahn installation is functional by testing:
1. Import autobahn and check version
2. Import autobahn.websocket (WebSocket protocol)
3. Import autobahn.wamp (WAMP protocol)
4. Import autobahn.flatbuffers and check version (shared test)
5. Verify flatc binary is available and executable (shared test)
6. Verify reflection files are present (shared test)

ALL TESTS ARE REQUIRED. Both wheel installs and sdist installs MUST
provide identical functionality including the flatc binary and
reflection.bfbs file.

Note: FlatBuffers/flatc tests use shared functions from smoke_test_flatc.py
      (source: wamp-cicd/scripts/flatc/smoke_test_flatc.py)
"""

import sys

# Import shared FlatBuffers test functions
from smoke_test_flatc import (
    test_import_flatbuffers,
    test_flatc_binary,
    test_reflection_files,
)

# Package name for shared tests
PACKAGE_NAME = "autobahn"


def test_import_autobahn():
    """Test 1: Import autobahn and check version."""
    print("Test 1: Importing autobahn and checking version...")
    try:
        import autobahn
        print(f"  autobahn version: {autobahn.__version__}")
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import autobahn: {e}")
        return False


def test_import_websocket():
    """Test 2: Import autobahn.websocket (WebSocket protocol)."""
    print("Test 2: Importing autobahn.websocket...")
    try:
        from autobahn.websocket import protocol
        print("  WebSocket protocol module loaded")
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import autobahn.websocket: {e}")
        return False


def test_import_wamp():
    """Test 3: Import autobahn.wamp (WAMP protocol)."""
    print("Test 3: Importing autobahn.wamp...")
    try:
        from autobahn.wamp import types
        print("  WAMP types module loaded")
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import autobahn.wamp: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("=" * 72)
    print("  SMOKE TESTS - Verifying autobahn installation")
    print("=" * 72)
    print()
    print(f"Python: {sys.version}")
    print()

    # All tests are REQUIRED - sdist MUST provide same functionality as wheels
    # Tests 4-6 use shared functions from smoke_test_flatc.py
    tests = [
        ("Test 1", test_import_autobahn),
        ("Test 2", test_import_websocket),
        ("Test 3", test_import_wamp),
        ("Test 4", lambda: test_import_flatbuffers(PACKAGE_NAME)),
        ("Test 5", lambda: test_flatc_binary(PACKAGE_NAME)),
        ("Test 6", lambda: test_reflection_files(PACKAGE_NAME)),
    ]

    failures = 0
    passed = 0

    for name, test in tests:
        result = test()
        if result is True:
            passed += 1
        else:
            failures += 1
        print()

    total = len(tests)
    print("=" * 72)
    if failures == 0:
        print(f"ALL SMOKE TESTS PASSED ({passed}/{total})")
        print("=" * 72)
        return 0
    else:
        print(f"SMOKE TESTS FAILED ({passed} passed, {failures} failed)")
        print("=" * 72)
        return 1


if __name__ == "__main__":
    sys.exit(main())
