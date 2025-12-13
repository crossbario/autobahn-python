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
FlatBuffers compiler (flatc) bundled with the package.

This module provides access to the flatc binary that is bundled with the package,
ensuring version compatibility with the vendored FlatBuffers runtime.

Usage from command line::

    flatc --version
    flatc --python -o output/ schema.fbs

Usage from Python::

    from <package>._flatc import get_flatc_path, run_flatc

    # Get path to flatc binary
    flatc_path = get_flatc_path()

    # Run flatc with arguments
    returncode = run_flatc(["--version"])

Note: This file is shared across WAMP ecosystem projects via wamp-cicd.
      Source: wamp-cicd/scripts/flatc/_flatc.py
      Projects copy this file to: src/<package>/_flatc/__init__.py
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def get_flatc_path() -> Path:
    """
    Get the path to the bundled flatc executable.

    :returns: Path to the flatc binary
    :raises FileNotFoundError: If flatc binary is not found
    """
    exe_name = "flatc.exe" if os.name == "nt" else "flatc"
    flatc_path = Path(__file__).parent / "bin" / exe_name

    if not flatc_path.exists():
        # Determine package name from module path for helpful error message
        module_parts = __name__.split(".")
        pkg_name = module_parts[0] if module_parts else "package"
        raise FileNotFoundError(
            f"flatc binary not found at {flatc_path}. "
            f"This may indicate a corrupted installation. "
            f"Try reinstalling: pip install --force-reinstall {pkg_name}"
        )

    return flatc_path


def run_flatc(args: List[str], cwd: Optional[str] = None) -> int:
    """
    Run the bundled flatc with the given arguments.

    :param args: Command line arguments to pass to flatc
    :param cwd: Working directory for flatc execution
    :returns: Return code from flatc
    """
    flatc_path = get_flatc_path()
    return subprocess.call([str(flatc_path)] + args, cwd=cwd)


def main() -> None:
    """
    Entry point for the flatc console script.

    Forwards all CLI arguments to the bundled flatc binary.
    """
    try:
        flatc_path = get_flatc_path()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(1)

    # Forward all CLI arguments to flatc
    ret = subprocess.call([str(flatc_path)] + sys.argv[1:])
    raise SystemExit(ret)


if __name__ == "__main__":
    main()
