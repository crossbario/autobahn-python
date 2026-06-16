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

**By default** - for *every* build context (PyPI wheels, local source installs,
and cross-compilation) - a safe, portable baseline architecture is used. This
keeps the resulting binaries runnable on a wide range of CPUs without SIGILL
(Illegal Instruction) crashes, and never hands a cross-compilation toolchain the
host-only ``-march=native`` flag (which it rejects).

Maximum-performance ``-march=native`` code generation is **opt-in** via
``AUTOBAHN_ARCH_TARGET=native``; use it only when the build host is also the run
host (e.g. Gentoo/Arch packages, dedicated single-machine deployments).

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
    - "native" : Force -march=native (maximum performance, build host only;
                 unsafe for distributed wheels and cross-compilation)
    - "safe"   : Force portable baseline (explicit; same as the default)
    - Not set  : Portable baseline (the safe default; works for cross-compilation)

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

**GitHub Actions building wheels (default):**
    >>> # Default is the portable baseline
    >>> get_compile_args()
    ['-std=c99', '-Wall', '-Wno-strict-prototypes', '-O3', '-march=x86-64-v2']

**User installing from source (default):**
    >>> # Default is the portable baseline (safe for cross-compilation too)
    >>> get_compile_args()
    ['-std=c99', '-Wall', '-Wno-strict-prototypes', '-O3', '-march=x86-64-v2']

**Opting in to -march=native (build host == run host):**
    >>> import os
    >>> os.environ['AUTOBAHN_ARCH_TARGET'] = 'native'
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
- #1834: -march=native breaks cross-compilation; the default is now the portable
  baseline for all build contexts, with -march=native available opt-in.

See Also
--------
- https://en.wikipedia.org/wiki/X86-64#Microarchitecture_levels
- https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html
"""

import os
import sys
import sysconfig
import platform


def is_building_wheel():
    """
    Detect if we're building a wheel for distribution vs. a local source install.

    .. note::

        As of #1834 the default architecture target is the portable baseline for
        *every* build context (wheels, local source installs, cross-compilation),
        so this helper no longer influences :func:`get_compile_args`. It is
        retained for backward compatibility and for external callers/tooling.

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
    machine = _get_target_machine()

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
        # Explicit opt-in only: -march=native generates code for the exact CPU of
        # the *build* host (maximum performance). Use this when the build host is
        # also the run host (e.g. Gentoo, Arch Linux, performance-critical
        # deployments). It is NOT safe for distributed wheels or cross-compilation.
        return base_args + ["-march=native"]

    # Default for everyone (AUTOBAHN_ARCH_TARGET unset or "safe"): a portable
    # baseline architecture. Defaulting to "safe" rather than -march=native is
    # what makes cross-compilation work out of the box - a cross toolchain
    # rejects -march=native ("unknown value 'native' for '-march'", #1834) - and
    # also prevents SIGILL crashes from over-optimized distributed wheels (#1717).
    arch_flag = _get_safe_march_flag(machine)
    if arch_flag:
        return base_args + [arch_flag]

    # Unknown / cross target architecture: emit no -march flag and let the
    # toolchain defaults (or distro-supplied CFLAGS, e.g. Buildroot/Yocto)
    # govern code generation.
    return base_args


def _get_target_machine():
    """
    Return the *target* machine architecture for the build.

    Uses ``sysconfig.get_platform()`` rather than ``platform.machine()`` so that
    the correct architecture is detected when cross-compiling (e.g.
    Buildroot/Yocto building aarch64 on an x86-64 host): ``platform.machine()``
    reports the build host (``uname``), whereas ``sysconfig`` reflects the
    interpreter's configured target platform. Falls back to
    ``platform.machine()`` when no architecture token can be derived.

    (Target-detection approach contributed in PR #1835 by @jameshilliard.)

    Returns
    -------
    str
        Lower-cased target architecture token, e.g. "x86_64", "aarch64",
        "arm64".
    """
    plat = sysconfig.get_platform().lower()
    # Examples: 'linux-x86_64', 'linux-aarch64', 'macosx-11.0-arm64',
    #           'win-amd64', 'win32'.
    if plat == "win32":
        return "x86"
    machine = plat.rsplit("-", 1)[-1]
    return machine or platform.machine().lower()


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
