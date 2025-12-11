#!/usr/bin/env python3
"""
Vendor flatbuffers Python runtime from git submodule into autobahn namespace.

This script:
1. Copies flatbuffers from deps/flatbuffers/python/flatbuffers to src/autobahn/flatbuffers
2. Captures the git version from the submodule via `git describe --tags --always`
3. Generates _git_version.py with the version string
4. Patches __init__.py with a version() function that parses the git version

This avoids conflicts with the standalone 'flatbuffers' PyPI package.
The vendored copy is gitignored and must be regenerated before build.
"""

import shutil
import subprocess
from pathlib import Path


def main():
    # Get project root (script is in scripts/ directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    src_dir = project_root / "deps" / "flatbuffers" / "python" / "flatbuffers"
    dst_dir = project_root / "src" / "autobahn" / "flatbuffers"

    if not src_dir.exists():
        print(f"ERROR: Flatbuffers submodule not found at {src_dir}")
        print("Run: git submodule update --init --recursive")
        raise SystemExit(1)

    print(f"==> Vendoring flatbuffers from {src_dir} to {dst_dir}...")
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)

    # Capture git version from submodule
    flatbuffers_submodule = project_root / "deps" / "flatbuffers"
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            cwd=flatbuffers_submodule,
            capture_output=True,
            text=True,
            timeout=10,
        )
        git_version = result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        git_version = "unknown"

    print(f"==> FlatBuffers git version: {git_version}")

    # Generate _git_version.py
    git_version_content = f'''\
# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Git version from deps/flatbuffers submodule.
# This file is generated at build time by scripts/vendor_flatbuffers.py
# The version is captured via `git describe --tags` in the submodule.
#
# Format: "v25.9.23" (tagged release) or "v25.9.23-2-g95053e6a" (post-tag)

__git_version__ = "{git_version}"
'''
    (dst_dir / "_git_version.py").write_text(git_version_content)

    # Append version() function to __init__.py
    init_file = dst_dir / "__init__.py"
    init_content = init_file.read_text()

    version_func = '''
import re

from ._git_version import __git_version__


def version() -> tuple[int, int, int, int | None, str | None]:
    """
    Return the exact git version of the vendored FlatBuffers runtime.

    Handles:

    1. "v25.9.23"              -> (25, 9, 23, None, None)       # Release
    2. "v25.9.23-71"           -> (25, 9, 23, 71, None)         # 71 commits ahead
    3. "v25.9.23-71-g19b2300f" -> (25, 9, 23, 71, "19b2300f")   # with hash
    """
    pattern = r"^v(\\d+)\\.(\\d+)\\.(\\d+)(?:-(\\d+))?(?:-g([0-9a-f]+))?$"
    match = re.match(pattern, __git_version__)
    if match:
        major, minor, patch, commits, commit_hash = match.groups()
        commits_int = int(commits) if commits else None
        return (int(major), int(minor), int(patch), commits_int, commit_hash)
    return (0, 0, 0, None, None)
'''
    init_file.write_text(init_content + version_func)

    print("==> Flatbuffers vendored successfully with version() function.")


if __name__ == "__main__":
    main()
