#!/usr/bin/env python3
"""
IMPORTANT: Why does this file still exist?

This setup.py is ONLY needed for CFFI extension module building (NVX).
All other package configuration is in pyproject.toml.

The cffi_modules parameter cannot be specified in pyproject.toml - there is
no standard PEP-defined way to declare CFFI build hooks. The CFFI library
requires this setup.py hook to:

1. Read the FFI definitions from _utf8validator.py and _xormasker.py
2. Compile the C code into platform-specific .so/.pyd shared libraries
3. Package the compiled extensions into the wheel

Without this file, the NVX (Native Vector Extensions) for WebSocket
frame masking and UTF-8 validation would not be built.

If CFFI ever gets pyproject.toml support, this file can be removed.
See: https://cffi.readthedocs.io/en/latest/cdef.html#ffi-set-source-preparing-out-of-line-modules
"""

import os
from setuptools import setup

# cffi based extension modules to build, currently only NVX
cffi_modules = []
if "AUTOBAHN_USE_NVX" not in os.environ or os.environ["AUTOBAHN_USE_NVX"] not in [
    "0",
    "false",
]:
    cffi_modules.append("src/autobahn/nvx/_utf8validator.py:ffi")
    cffi_modules.append("src/autobahn/nvx/_xormasker.py:ffi")

# Include package data from MANIFEST.in
include_package_data = True

# Use setuptools with pyproject.toml for most configuration
setup(
    cffi_modules=cffi_modules,
    include_package_data=include_package_data,
)
