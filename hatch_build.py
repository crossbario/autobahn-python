"""
Hatchling custom build hook for CFFI extension modules and flatc compiler.

This builds:
1. The NVX (Native Vector Extensions) for WebSocket frame masking and UTF-8 validation
2. The FlatBuffers compiler (flatc) from deps/flatbuffers
3. The reflection.bfbs binary schema for runtime introspection

See: https://hatch.pypa.io/latest/plugins/build-hook/custom/
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CFfiBuildHook(BuildHookInterface):
    """Build hook for compiling CFFI extension modules and flatc compiler."""

    PLUGIN_NAME = "cffi"

    def initialize(self, version, build_data):
        """
        Called before each build.

        For wheel builds, compile the CFFI modules and flatc.
        For sdist builds, just ensure source files are included.
        """
        # Always capture flatbuffers git version (for both wheel and sdist)
        self._update_flatbuffers_git_version()

        if self.target_name != "wheel":
            # Only compile for wheel builds, sdist just includes source
            return

        built_nvx = False
        built_flatc = False

        # Check if NVX build is disabled
        if os.environ.get("AUTOBAHN_USE_NVX", "1") not in ("0", "false"):
            # Build CFFI modules (NVX)
            built_nvx = self._build_cffi_modules(build_data)
        else:
            print("AUTOBAHN_USE_NVX is disabled, skipping CFFI build")

        # Build flatc compiler
        built_flatc = self._build_flatc(build_data)

        # Generate reflection.bfbs using the built flatc
        if built_flatc:
            self._generate_reflection_bfbs(build_data)
            # Generate WAMP schema .bfbs files
            self._generate_wamp_bfbs(build_data)

        # If we built any extensions, mark this as a platform-specific wheel
        if built_nvx or built_flatc:
            build_data["infer_tag"] = True
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

    def _build_flatc(self, build_data):
        """Build the FlatBuffers compiler (flatc) from deps/flatbuffers.

        Returns True if flatc was successfully built.
        """
        print("\n" + "=" * 70)
        print("Building FlatBuffers compiler (flatc)")
        print("=" * 70)

        flatbuffers_dir = Path(self.root) / "deps" / "flatbuffers"
        build_dir = flatbuffers_dir / "build"
        flatc_bin_dir = Path(self.root) / "src" / "autobahn" / "_flatc" / "bin"

        # Determine executable name based on platform
        exe_name = "flatc.exe" if os.name == "nt" else "flatc"

        # Check if cmake is available
        cmake_path = shutil.which("cmake")
        if not cmake_path:
            print("WARNING: cmake not found, skipping flatc build")
            print("  -> Install cmake to enable flatc bundling")
            return False

        # Check if flatbuffers source exists
        if not flatbuffers_dir.exists():
            print(f"WARNING: {flatbuffers_dir} not found")
            print("  -> Initialize git submodule: git submodule update --init")
            return False

        # Clean and create build directory (remove any cached cmake config)
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Configure with cmake
        print("  -> Configuring with cmake...")
        cmake_args = [
            cmake_path,
            "..",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DFLATBUFFERS_BUILD_TESTS=OFF",
            "-DFLATBUFFERS_BUILD_FLATLIB=OFF",
            "-DFLATBUFFERS_BUILD_FLATHASH=OFF",
            "-DFLATBUFFERS_BUILD_GRPCTEST=OFF",
            "-DFLATBUFFERS_BUILD_SHAREDLIB=OFF",
        ]

        # ====================================================================
        # Note on manylinux compatibility:
        # ====================================================================
        # For manylinux-compatible Linux wheels, flatc must be built inside
        # official PyPA manylinux containers (e.g., manylinux_2_28_x86_64).
        # These containers have toolchains pre-configured for the correct
        # glibc and ISA requirements. No special compiler flags needed.
        #
        # The wheels-docker.yml and wheels-arm64.yml workflows handle Linux
        # builds using these containers. This hatch_build.py works correctly
        # in those environments without any ISA-specific flags.
        #
        # macOS and Windows builds use native GitHub runners (wheels.yml).
        # ====================================================================

        result = subprocess.run(
            cmake_args,
            cwd=build_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"ERROR: cmake configure failed:\n{result.stderr}")
            return False

        # Step 2: Build flatc
        print("  -> Building flatc...")
        build_args = [
            cmake_path,
            "--build",
            ".",
            "--config",
            "Release",
            "--target",
            "flatc",
        ]

        result = subprocess.run(
            build_args,
            cwd=build_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"ERROR: cmake build failed:\n{result.stderr}")
            return False

        # Step 3: Find and copy the built flatc
        # flatc might be in different locations depending on platform/generator
        possible_locations = [
            build_dir / exe_name,
            build_dir / "Release" / exe_name,  # Windows/MSVC
            build_dir / "Debug" / exe_name,
        ]

        flatc_src = None
        for loc in possible_locations:
            if loc.exists():
                flatc_src = loc
                break

        if not flatc_src:
            print(f"ERROR: Built flatc not found in {build_dir}")
            for loc in possible_locations:
                print(f"  Checked: {loc}")
            return False

        # Copy flatc to package bin directory
        flatc_bin_dir.mkdir(parents=True, exist_ok=True)
        flatc_dest = flatc_bin_dir / exe_name
        shutil.copy2(flatc_src, flatc_dest)

        # Make executable on Unix
        if os.name != "nt":
            flatc_dest.chmod(0o755)

        print(f"  -> Built flatc: {flatc_dest}")

        # Verify ISA level on Linux (check for x86_64_v2 instructions)
        if sys.platform.startswith("linux"):
            print("  -> Verifying ISA level...")
            readelf_result = subprocess.run(
                ["readelf", "-A", str(flatc_dest)],
                capture_output=True,
                text=True,
            )
            if readelf_result.returncode == 0:
                # Look for ISA info in output
                for line in readelf_result.stdout.splitlines():
                    if "ISA" in line or "x86" in line.lower():
                        print(f"     {line.strip()}")
            # Also check file command for architecture info
            file_result = subprocess.run(
                ["file", str(flatc_dest)],
                capture_output=True,
                text=True,
            )
            if file_result.returncode == 0:
                print(f"     {file_result.stdout.strip()}")

        # Add flatc to wheel
        src_file = str(flatc_dest)
        dest_path = f"autobahn/_flatc/bin/{exe_name}"
        build_data["force_include"][src_file] = dest_path
        print(f"  -> Added to wheel: {dest_path}")

        # Store flatc path for later use (reflection.bfbs generation)
        self._flatc_path = flatc_dest
        return True

    def _generate_reflection_bfbs(self, build_data):
        """Generate reflection.bfbs using the built flatc.

        This creates the binary FlatBuffers schema that allows runtime
        schema introspection.
        """
        print("\n" + "=" * 70)
        print("Generating reflection.bfbs")
        print("=" * 70)

        if not hasattr(self, "_flatc_path") or not self._flatc_path.exists():
            print("WARNING: flatc not available, skipping reflection.bfbs generation")
            return False

        flatbuffers_dir = Path(self.root) / "deps" / "flatbuffers"
        reflection_fbs = flatbuffers_dir / "reflection" / "reflection.fbs"
        output_dir = Path(self.root) / "src" / "autobahn" / "flatbuffers"

        if not reflection_fbs.exists():
            print(f"WARNING: {reflection_fbs} not found")
            return False

        # Generate reflection.bfbs
        result = subprocess.run(
            [
                str(self._flatc_path),
                "--binary",
                "--schema",
                "--bfbs-comments",
                "--bfbs-builtins",
                "-o",
                str(output_dir),
                str(reflection_fbs),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"ERROR: flatc failed:\n{result.stderr}")
            return False

        reflection_bfbs = output_dir / "reflection.bfbs"
        if reflection_bfbs.exists():
            print(f"  -> Generated: {reflection_bfbs}")

            # Add to wheel
            src_file = str(reflection_bfbs)
            dest_path = "autobahn/flatbuffers/reflection.bfbs"
            build_data["force_include"][src_file] = dest_path
            print(f"  -> Added to wheel: {dest_path}")
            return True
        else:
            print("WARNING: reflection.bfbs not generated")
            return False

    def _generate_wamp_bfbs(self, build_data):
        """Generate .bfbs files for WAMP FlatBuffers schemas.

        This creates binary FlatBuffers schemas for the WAMP protocol schemas
        located in src/autobahn/wamp/flatbuffers/.
        """
        print("\n" + "=" * 70)
        print("Generating WAMP schema .bfbs files")
        print("=" * 70)

        if not hasattr(self, "_flatc_path") or not self._flatc_path.exists():
            print("WARNING: flatc not available, skipping WAMP .bfbs generation")
            return False

        wamp_fbs_dir = Path(self.root) / "src" / "autobahn" / "wamp" / "flatbuffers"

        if not wamp_fbs_dir.exists():
            print(f"WARNING: {wamp_fbs_dir} not found")
            return False

        # The main schema file that includes all others
        wamp_fbs = wamp_fbs_dir / "wamp.fbs"
        if not wamp_fbs.exists():
            print(f"WARNING: {wamp_fbs} not found")
            return False

        # Generate wamp.bfbs (which includes all dependent schemas)
        result = subprocess.run(
            [
                str(self._flatc_path),
                "--binary",
                "--schema",
                "--bfbs-comments",
                "--bfbs-builtins",
                "-o",
                str(wamp_fbs_dir),
                str(wamp_fbs),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"ERROR: flatc failed:\n{result.stderr}")
            return False

        wamp_bfbs = wamp_fbs_dir / "wamp.bfbs"
        if wamp_bfbs.exists():
            print(f"  -> Generated: {wamp_bfbs}")

            # Add to wheel
            src_file = str(wamp_bfbs)
            dest_path = "autobahn/wamp/flatbuffers/wamp.bfbs"
            build_data["force_include"][src_file] = dest_path
            print(f"  -> Added to wheel: {dest_path}")
            return True
        else:
            print("WARNING: wamp.bfbs not generated")
            return False

    def _update_flatbuffers_git_version(self):
        """
        Capture the git describe version of deps/flatbuffers submodule.

        This writes the version to flatbuffers/_git_version.py so that
        autobahn.flatbuffers.version() returns the exact git version at runtime.
        """
        print("=" * 70)
        print("Capturing FlatBuffers git version from deps/flatbuffers")
        print("=" * 70)

        flatbuffers_dir = Path(self.root) / "deps" / "flatbuffers"
        git_version_file = (
            Path(self.root) / "src" / "autobahn" / "flatbuffers" / "_git_version.py"
        )

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
                # Keep existing version in file if git not available
                return
            except subprocess.TimeoutExpired:
                print("  -> git describe timed out, using existing version")
                return
            except Exception as e:
                print(f"  -> Error getting git version: {e}")
                return
        else:
            print("  -> deps/flatbuffers not found or not a git repo")
            print(f"  -> Using existing version in {git_version_file.name}")
            return

        # Write the version file
        content = """\
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
""".format(version=git_version)

        git_version_file.write_text(content)
        print(f"  -> Updated {git_version_file.name}")
