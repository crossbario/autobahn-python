#!/usr/bin/env python3
"""
Modern setup.py that works with pyproject.toml for CFFI module building.
This handles the conditional CFFI module compilation based on environment variables.
"""

import os
from setuptools import setup

# cffi based extension modules to build, currently only NVX
cffi_modules = []
if "AUTOBAHN_USE_NVX" not in os.environ or os.environ["AUTOBAHN_USE_NVX"] not in [
    "0",
    "false",
]:
    cffi_modules.append("autobahn/nvx/_utf8validator.py:ffi")

# Include package data from MANIFEST.in
include_package_data = True

# Use setuptools with pyproject.toml for most configuration
setup(
    cffi_modules=cffi_modules,
    include_package_data=include_package_data,
)