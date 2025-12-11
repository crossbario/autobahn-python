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

import re

from . import util
from ._git_version import __git_version__
from ._version import __version__
from .builder import Builder
from .compat import range_func as compat_range
from .table import Table


def version() -> tuple[int, int, int, int | None, str | None]:
    """
    Return the exact git version of the vendored FlatBuffers runtime.

    Handles:

    1. "v25.9.23"              -> (25, 9, 23, None, None)       # Release (Named Tag, CalVer Year.Month.Day)
    2. "v25.9.23-71"           -> (25, 9, 23, 71, None)         # 71 commits ahead of the Release v25.9.23
    3. "v25.9.23-71-g19b2300f" -> (25, 9, 23, 71, "19b2300f")   # dito, with Git commit hash
    """

    # Pattern explanation:
    # ^v                : Start of string, literal 'v'
    # (\d+)\.(\d+)\.(\d+) : Groups 1,2,3 - Major.Minor.Patch (Required)
    #
    # (?: ... )?        : Non-capturing group (grouping only, not saved), optional '?'
    # -(\d+)            : Literal hyphen, Group 4 (Commits)
    #
    # (?: ... )?        : Non-capturing group, optional '?'
    # -g                : Literal hyphen and 'g' (separator)
    # ([0-9a-f]+)       : Group 5 (Hash)

    pattern = r"^v(\d+)\.(\d+)\.(\d+)(?:-(\d+))?(?:-g([0-9a-f]+))?$"

    match = re.match(pattern, __git_version__)

    if match:
        major, minor, patch, commits, commit_hash = match.groups()

        # Convert commits to int if present, else None
        commits_int = int(commits) if commits else None

        return (int(major), int(minor), int(patch), commits_int, commit_hash)

    # Fallback if regex fails entirely (returns 0.0.0 to satisfy type hint)
    return (0, 0, 0, None, None)
