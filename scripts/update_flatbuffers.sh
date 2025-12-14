#!/usr/bin/env bash
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
#
# Update vendored flatbuffers Python runtime from deps/flatbuffers submodule.
#
# This script:
# 1. Copies the Python runtime from the submodule
# 2. Adds _git_version.py for version tracking
# 3. Copies reflection.fbs for runtime schema access
# 4. Patches __init__.py with version() function
# 5. Captures the git version from submodule
#
# Usage: ./scripts/update_flatbuffers.sh
#
###############################################################################

set -e

echo "==> Updating vendored flatbuffers from submodule..."

# 1. Remove old vendored flatbuffers
rm -rf ./src/autobahn/flatbuffers

# 2. Copy the Python runtime from submodule
cp -R deps/flatbuffers/python/flatbuffers ./src/autobahn/flatbuffers

# 3. Add _git_version.py template (will be updated during build)
cat > ./src/autobahn/flatbuffers/_git_version.py << 'EOF'
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
# This file is regenerated at build time by hatch_build.py.
# The version is captured via `git describe --tags` in the submodule.
#
# Format: "v25.9.23" (tagged release) or "v25.9.23-2-g95053e6a" (post-tag)
#
# If building from sdist without git, this will retain the version
# from when the sdist was created.

__git_version__ = "unknown"
EOF

# 4. Copy reflection.fbs for runtime schema access
cp deps/flatbuffers/reflection/reflection.fbs ./src/autobahn/flatbuffers/

# 5. Patch __init__.py to add version() function and _git_version import
cat >> ./src/autobahn/flatbuffers/__init__.py << 'EOF'

# --- Autobahn additions for bundled flatc support ---
import re
from ._git_version import __git_version__


def version() -> tuple[int, int, int, int | None, str | None]:
    """
    Return the exact git version of the vendored FlatBuffers runtime.

    Handles:

    1. "v25.9.23"              -> (25, 9, 23, None, None)       # Release (Named Tag, CalVer Year.Month.Day)
    2. "v25.9.23-71"           -> (25, 9, 23, 71, None)         # 71 commits ahead of the Release v25.9.23
    3. "v25.9.23-71-g19b2300f" -> (25, 9, 23, 71, "19b2300f")   # dito, with Git commit hash
    """
    pattern = r"^v(\d+)\.(\d+)\.(\d+)(?:-(\d+))?(?:-g([0-9a-f]+))?$"
    match = re.match(pattern, __git_version__)
    if match:
        major, minor, patch, commits, commit_hash = match.groups()
        commits_int = int(commits) if commits else None
        return (int(major), int(minor), int(patch), commits_int, commit_hash)
    return (0, 0, 0, None, None)
EOF

# 6. Capture current git version from submodule
if [ -d deps/flatbuffers/.git ]; then
    GIT_VERSION=$(cd deps/flatbuffers && git describe --tags --always 2>/dev/null || echo "unknown")
    sed -i "s/__git_version__ = \"unknown\"/__git_version__ = \"${GIT_VERSION}\"/" ./src/autobahn/flatbuffers/_git_version.py
    echo "  Git version captured: ${GIT_VERSION}"
fi

echo "Flatbuffers vendor updated in src/autobahn/flatbuffers"
echo ""
echo "Files added/updated:"
echo "  - _git_version.py (git version tracking)"
echo "  - reflection.fbs (schema for reflection)"
echo "  - __init__.py (patched with version() function)"
