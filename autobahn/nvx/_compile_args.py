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
Centralized compiler flag selection for NVX (Native Vector Extensions) builds.

This module determines appropriate architecture-specific optimization flags
for building native C extensions using CFFI. It balances portability and
performance based on the build context.

Strategy
--------

For **WHEEL BUILDS** (distribution via PyPI):
    Use safe, portable baseline architectures to ensure wheels work on a wide
    range of CPUs without causing SIGILL (Illegal Instruction) crashes.

For **SOURCE BUILDS** (local installation):
    Use -march=native to generate optimal code for the specific CPU where
    the build is happening, maximizing performance.

Architecture Baselines
----------------------

x86-64 (portable baseline):
    -march=x86-64-v2 (microarchitecture level 2, 2009+)
    Includes: SSE4.2, POPCNT, SSSE3, SSE4.1
    Compatible with: Intel Nehalem+, AMD Bulldozer+ (2009+)
    Coverage: ~99% of x86-64 CPUs from 2010 onwards

ARM64 (portable baseline):
    -march=armv8-a (baseline ARMv8-A architecture)
    Compatible with: Raspberry Pi 4/5, AWS Graviton, Apple M1/M2, etc.
    Coverage: All 64-bit ARM CPUs

Environment Variables
---------------------

AUTOBAHN_ARCH_TARGET : str, optional
    User/distro override for architecture target:
    - "native" : Force -march=native (maximum performance, may break portability)
    - "safe"   : Force portable baseline (ensures compatibility)
    - Not set  : Auto-detect based on build context (recommended)

AUTOBAHN_WHEEL_BUILD : str, optional
    Explicit marker for wheel builds ("true" or "1")
    When set, forces portable baseline regardless of auto-detection

CI : str, optional
    Standard CI environment variable. When "true" or "1", assumes wheel build.

CIBUILDWHEEL : str, optional
    Set by cibuildwheel. Indicates wheel build for distribution.

AUDITWHEEL_PLAT : str, optional
    Set by auditwheel/manylinux builds. Indicates wheel build.

Examples
--------

**GitHub Actions building wheels:**
    >>> # Automatically detects CI=true, uses -march=x86-64-v2
    >>> get_compile_args()
    ['-std=c99', '-Wall', '-Wno-strict-prototypes', '-O3', '-march=x86-64-v2']

**User installing from source:**
    >>> # Detects local build, uses -march=native
    >>> get_compile_args()
    ['-std=c99', '-Wall', '-Wno-strict-prototypes', '-O3', '-march=native']

**Gentoo building package:**
    >>> # Gentoo wants -march=native for optimized binaries
    >>> import os
    >>> os.environ['AUTOBAHN_ARCH_TARGET'] = 'native'
    >>> get_compile_args()
    ['-std=c99', '-Wall', '-Wno-strict-prototypes', '-O3', '-march=native']

**Debian building package:**
    >>> # Debian wants portable binaries for all users
    >>> import os
    >>> os.environ['AUTOBAHN_ARCH_TARGET'] = 'safe'
    >>> get_compile_args()
    ['-std=c99', '-Wall', '-Wno-strict-prototypes', '-O3', '-march=x86-64-v2']

Notes
-----

This module is used by all NVX components:
- autobahn.nvx._xormasker (WebSocket frame XOR masking)
- autobahn.nvx._utf8validator (WebSocket UTF-8 validation)

Related Issues
--------------
- #1717: SIGILL crashes from -march=native in distributed wheels

See Also
--------
- https://en.wikipedia.org/wiki/X86-64#Microarchitecture_levels
- https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html
"""

import os
import sys
import platform


def is_building_wheel():
    """
    Detect if we're building a wheel for distribution vs. a local source install.

    Returns
    -------
    bool
        True if building a wheel (need portability), False if building locally.

    Notes
    -----
    Detection heuristics:
    1. CI environment variables (CI, CIBUILDWHEEL)
    2. manylinux/auditwheel markers (AUDITWHEEL_PLAT)
    3. Explicit marker (AUTOBAHN_WHEEL_BUILD)
    4. Default: False (assume local source build)
    """
    # CI environments (building wheels for distribution)
    if os.environ.get("CI") in ("true", "1"):
        return True

    # cibuildwheel
    if os.environ.get("CIBUILDWHEEL"):
        return True

    # manylinux/auditwheel builds
    if os.environ.get("AUDITWHEEL_PLAT"):
        return True

    # Explicit marker from our workflows
    if os.environ.get("AUTOBAHN_WHEEL_BUILD") in ("true", "1"):
        return True

    # Default: assume local source build
    return False


def get_compile_args():
    """
    Returns appropriate compiler arguments for building NVX native extensions.

    This function determines the optimal compiler flags based on:
    - Target platform (Windows, Linux, macOS, etc.)
    - Target architecture (x86-64, ARM64, etc.)
    - Build context (wheel distribution vs. local source install)
    - User/distro overrides via environment variables

    Returns
    -------
    list of str
        Compiler arguments suitable for current build context.
        For MSVC: ['/O2', '/W3']
        For GCC/Clang: ['-std=c99', '-Wall', '-O3', '-march=...']

    Examples
    --------
    >>> args = get_compile_args()
    >>> # Use with CFFI:
    >>> ffi.set_source("_nvx_module", c_source, extra_compile_args=args)
    """
    if sys.platform == "win32":
        # MSVC on Windows
        # Note: MSVC doesn't support -march, uses /arch instead
        # But default codegen is already optimized for current arch
        return ["/O2", "/W3"]

    # GCC/Clang on POSIX (Linux, macOS, *BSD)
    machine = platform.machine().lower()

    # Base flags for all POSIX platforms
    base_args = [
        "-std=c99",
        "-Wall",
        "-Wno-strict-prototypes",
        "-O3",
    ]

    # User can explicitly override architecture target
    arch_override = os.environ.get("AUTOBAHN_ARCH_TARGET", "").lower()

    if arch_override == "native":
        # User explicitly wants -march=native (maximum performance)
        # Use case: Gentoo, Arch Linux, performance-critical deployments
        return base_args + ["-march=native"]

    elif arch_override == "safe":
        # User explicitly wants portable baseline
        # Use case: Debian, Ubuntu, RHEL package builds
        arch_flag = _get_safe_march_flag(machine)
        if arch_flag:
            return base_args + [arch_flag]
        else:
            # Unknown arch: use compiler defaults
            return base_args

    elif is_building_wheel():
        # Building wheel for distribution: use portable baseline
        # These wheels may run on CPUs different from build machine
        arch_flag = _get_safe_march_flag(machine)
        if arch_flag:
            return base_args + [arch_flag]
        else:
            # Unknown arch: use compiler defaults
            return base_args

    else:
        # Building from source locally: use -march=native for maximum performance
        # Build machine = runtime machine, so native optimizations are safe and optimal
        return base_args + ["-march=native"]


def _get_safe_march_flag(machine):
    """
    Returns safe -march flag for portable binaries on the given machine architecture.

    Parameters
    ----------
    machine : str
        Machine architecture from platform.machine().lower()

    Returns
    -------
    str or None
        Safe -march flag for the architecture, or None for unknown architectures.
    """
    if machine in ("x86_64", "amd64", "x64"):
        # x86-64: Use microarchitecture level 2 (2009+ CPUs)
        # Includes: SSE4.2, POPCNT, SSSE3, SSE4.1
        # Compatible with: Intel Nehalem+, AMD Bulldozer+
        return "-march=x86-64-v2"

    elif machine in ("aarch64", "arm64"):
        # ARM64: Use ARMv8-A baseline (all 64-bit ARM)
        # Compatible with: Raspberry Pi 4/5, AWS Graviton, Apple Silicon
        return "-march=armv8-a"

    else:
        # Unknown architecture: let compiler use safe defaults
        # (no -march flag = generic code for the architecture)
        return None
