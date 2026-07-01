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

from . import util
from ._version import __version__
from .builder import Builder
from .compat import range_func as compat_range
from .table import Table

# --- Autobahn additions for bundled flatc support ---
import re
from ._git_version import __git_version__


def version() -> tuple[int, int, int, int | None, str | None]:
    """
    Return the version of the vendored FlatBuffers runtime as a 5-tuple
    ``(major, minor, patch, commits, commit_hash)``.

    The primary source is ``__git_version__`` (``git describe`` output), which on a
    genuine dev/git build carries rich detail:

    1. "v25.9.23"              -> (25, 9, 23, None, None)       # Release (Named Tag, CalVer Year.Month.Day)
    2. "v25.9.23-71"           -> (25, 9, 23, 71, None)         # 71 commits ahead of the Release v25.9.23
    3. "v25.9.23-71-g19b2300f" -> (25, 9, 23, 71, "19b2300f")   # dito, with Git commit hash

    On installed wheels / shallow clones ``__git_version__`` may be a bare commit hash
    or "unknown" (``git describe`` found no tags); in that case fall back to the always
    reliable static ``__version__`` and return ``(major, minor, patch, None, None)``.
    """
    pattern = r"^v(\d+)\.(\d+)\.(\d+)(?:-(\d+))?(?:-g([0-9a-f]+))?$"
    match = re.match(pattern, __git_version__)
    if match:
        major, minor, patch, commits, commit_hash = match.groups()
        commits_int = int(commits) if commits else None
        return (int(major), int(minor), int(patch), commits_int, commit_hash)
    # Fallback: static vendored __version__ ("YY.MM.DD", no 'v' prefix) is reliable on
    # wheels where __git_version__ may be a bare hash / "unknown". No end-anchor so a
    # trailing dev suffix is tolerated.
    fallback = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", __version__)
    if fallback:
        major, minor, patch = fallback.groups()
        return (int(major), int(minor), int(patch), None, None)
    return (0, 0, 0, None, None)
