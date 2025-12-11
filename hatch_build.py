"""
Hatchling custom build hook for CFFI extension modules.

This builds the NVX (Native Vector Extensions) for WebSocket frame masking
and UTF-8 validation using CFFI.

Also captures the git version of deps/flatbuffers submodule at build time.

See: https://hatch.pypa.io/latest/plugins/build-hook/custom/
"""

import os
import subprocess
import sys
import sysconfig
import importlib.util
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CFfiBuildHook(BuildHookInterface):
    """Build hook for compiling CFFI extension modules."""

    PLUGIN_NAME = "cffi"

    def initialize(self, version, build_data):
        """
        Called before each build.

        For wheel builds, compile the CFFI modules.
        For sdist builds, just ensure source files are included.
        """
        # Always capture flatbuffers git version (for both wheel and sdist)
        self._update_flatbuffers_git_version()

        if self.target_name != "wheel":
            # Only compile for wheel builds, sdist just includes source
            return

        # Check if NVX build is disabled
        if os.environ.get("AUTOBAHN_USE_NVX", "1") in ("0", "false"):
            print("AUTOBAHN_USE_NVX is disabled, skipping CFFI build")
            return

        # Build CFFI modules
        built_extensions = self._build_cffi_modules(build_data)

        # If we built extensions, mark this as a platform-specific wheel
        if built_extensions:
            # Setting infer_tag tells hatchling to use platform-specific wheel tag
            build_data["infer_tag"] = True
            # Mark as having binary extensions
            build_data["pure_python"] = False

    def _get_ext_suffix(self):
        """Get the extension suffix for the current Python interpreter.

        E.g., '.cpython-311-x86_64-linux-gnu.so' or '.pypy311-pp73-x86_64-linux-gnu.so'
        """
        return sysconfig.get_config_var("EXT_SUFFIX") or ".so"

    def _build_cffi_modules(self, build_data):
        """Compile the CFFI extension modules using direct file execution.

        Returns True if any extensions were successfully built.
        """
        src_path = Path(self.root) / "src"
        nvx_dir = src_path / "autobahn" / "nvx"
        built_any = False

        # Get the extension suffix for current Python to filter artifacts
        ext_suffix = self._get_ext_suffix()
        print(f"Building for Python with extension suffix: {ext_suffix}")

        # CFFI module files to build
        cffi_modules = [
            ("_utf8validator.py", "ffi"),
            ("_xormasker.py", "ffi"),
        ]

        for module_file, ffi_name in cffi_modules:
            module_path = nvx_dir / module_file
            print(f"Building CFFI module: {module_path}")

            try:
                # Load the module directly from file (like CFFI's setuptools integration)
                # This avoids triggering package-level imports
                spec = importlib.util.spec_from_file_location(
                    f"_cffi_build_{module_file}",
                    module_path
                )
                module = importlib.util.module_from_spec(spec)

                # We need to set up sys.path so the module can find _compile_args.py
                old_path = sys.path.copy()
                sys.path.insert(0, str(nvx_dir))
                sys.path.insert(0, str(src_path))

                try:
                    spec.loader.exec_module(module)
                    ffi = getattr(module, ffi_name)

                    # Compile the CFFI module
                    # The compiled .so/.pyd goes to the current directory by default
                    # We want it in the nvx_dir
                    old_cwd = os.getcwd()
                    os.chdir(nvx_dir)
                    try:
                        ffi.compile(verbose=True)
                    finally:
                        os.chdir(old_cwd)

                finally:
                    sys.path = old_path

                # Find the compiled artifact matching CURRENT Python and add to build_data
                # Only include .so files that match the current interpreter's extension suffix
                #
                # IMPORTANT: The .so files must be placed at the WHEEL ROOT (not in autobahn/nvx/)
                # because CFFI creates top-level modules (e.g., "_nvx_utf8validator")
                # and the Python code does `import _nvx_utf8validator` (top-level import).
                for artifact in nvx_dir.glob("_nvx_*" + ext_suffix):
                    src_file = str(artifact)
                    # Place at wheel root for top-level import
                    dest_path = artifact.name
                    build_data["force_include"][src_file] = dest_path
                    print(f"  -> Added artifact: {artifact.name} -> {dest_path} (wheel root)")
                    built_any = True

            except Exception as e:
                print(f"Warning: Could not build {module_file}: {e}")
                import traceback
                traceback.print_exc()

        return built_any

    def _update_flatbuffers_git_version(self):
        """
        Capture the git describe version of deps/flatbuffers submodule.

        This writes the version to flatbuffers/_git_version.py and patches
        __init__.py with the version() function so that
        autobahn.flatbuffers.version() returns the exact git version at runtime.
        """
        print("=" * 70)
        print("Capturing FlatBuffers git version from deps/flatbuffers")
        print("=" * 70)

        flatbuffers_dir = Path(self.root) / "deps" / "flatbuffers"
        flatbuffers_dst = Path(self.root) / "src" / "autobahn" / "flatbuffers"
        git_version_file = flatbuffers_dst / "_git_version.py"
        init_file = flatbuffers_dst / "__init__.py"

        # Check if flatbuffers directory exists (vendored)
        if not flatbuffers_dst.exists():
            print("  -> src/autobahn/flatbuffers not found, skipping")
            print("  -> Run 'just vendor-flatbuffers' first")
            return

        # Default version if git is not available or submodule not initialized
        git_version = "unknown"

        if flatbuffers_dir.exists() and (flatbuffers_dir / ".git").exists():
            try:
                result = subprocess.run(
                    ["git", "describe", "--tags", "--always"],
                    cwd=flatbuffers_dir,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    git_version = result.stdout.strip()
                    print(f"  -> Git version: {git_version}")
                else:
                    print(f"  -> git describe failed: {result.stderr}")
            except FileNotFoundError:
                print("  -> git command not found, using existing version")
                return
            except subprocess.TimeoutExpired:
                print("  -> git describe timed out, using existing version")
                return
            except Exception as e:
                print(f"  -> Error getting git version: {e}")
                return
        else:
            print("  -> deps/flatbuffers not found or not a git repo")
            if git_version_file.exists():
                print(f"  -> Using existing version in {git_version_file.name}")
            return

        # Write the _git_version.py file
        git_version_content = '''\
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

__git_version__ = "{version}"
'''.format(version=git_version)

        git_version_file.write_text(git_version_content)
        print(f"  -> Updated {git_version_file.name}")

        # Check if __init__.py already has version() function
        init_content = init_file.read_text()
        if "def version()" not in init_content:
            # Patch __init__.py to add version() function
            version_func = '''
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

    pattern = r"^v(\\d+)\\.(\\d+)\\.(\\d+)(?:-(\\d+))?(?:-g([0-9a-f]+))?$"

    match = re.match(pattern, __git_version__)

    if match:
        major, minor, patch, commits, commit_hash = match.groups()
        commits_int = int(commits) if commits else None
        return (int(major), int(minor), int(patch), commits_int, commit_hash)

    # Fallback if regex fails entirely
    return (0, 0, 0, None, None)
'''
            init_file.write_text(init_content + version_func)
            print(f"  -> Patched {init_file.name} with version() function")
        else:
            print(f"  -> {init_file.name} already has version() function")
