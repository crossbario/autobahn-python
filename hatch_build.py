"""
Hatchling custom build hook for CFFI extension modules.

This builds the NVX (Native Vector Extensions) for WebSocket frame masking
and UTF-8 validation using CFFI.

See: https://hatch.pypa.io/latest/plugins/build-hook/custom/
"""

import os
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
                for artifact in nvx_dir.glob("_nvx_*" + ext_suffix):
                    src_file = str(artifact)
                    dest_path = f"autobahn/nvx/{artifact.name}"
                    build_data["force_include"][src_file] = dest_path
                    print(f"  -> Added artifact: {artifact.name} -> {dest_path}")
                    built_any = True

                # Handle Windows .pyd files
                if ext_suffix.endswith(".pyd"):
                    for artifact in nvx_dir.glob("_nvx_*" + ext_suffix):
                        src_file = str(artifact)
                        dest_path = f"autobahn/nvx/{artifact.name}"
                        build_data["force_include"][src_file] = dest_path
                        print(f"  -> Added artifact: {artifact.name} -> {dest_path}")
                        built_any = True

            except Exception as e:
                print(f"Warning: Could not build {module_file}: {e}")
                import traceback
                traceback.print_exc()

        return built_any
