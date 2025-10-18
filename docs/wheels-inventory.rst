.. _wheels-inventory:

Wheels Inventory
================

Autobahn|Python provides pre-built binary wheels for multiple Python implementations, versions, and platforms. This page documents all available wheel variants and their characteristics.

Overview
--------

Wheels are built automatically for every release via GitHub Actions and published to:

* **PyPI** - https://pypi.org/project/autobahn/
* **GitHub Releases** - https://github.com/crossbario/autobahn-python/releases

All wheels include full WebSocket and WAMP functionality. Platform-specific builds may include NVX (Native Vector Extensions) for accelerated WebSocket frame masking/unmasking.

What's Next / Future Directions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Python packaging ecosystem is evolving rapidly, and we're committed to staying at the forefront of these developments:

* **Wheel Variants** - We're following the development of `WheelNext <https://wheelnext.dev/>`_ and the transition from platform tags to build variants as described in `Python Wheels: From Tags to Variants <https://labs.quansight.org/blog/python-wheels-from-tags-to-variants>`_. This will enable more flexible wheel distribution strategies, particularly for optional binary optimizations like NVX.

* **PyX Packaging** - We plan to fully support `PyX <https://astral.sh/pyx>`_ (Astral's next-generation Python package format) once it becomes available. PyX promises to address many current limitations in Python packaging, including better handling of optional native extensions and build variants.

* **Expanded Platform Coverage** - As GitHub Actions and QEMU support improve, we aim to expand our wheel coverage to additional platforms and architectures where there's user demand.

These initiatives will allow us to provide even better wheel distribution strategies, particularly for use cases like NVX acceleration where users should have the choice between pure Python (maximum compatibility) and optimized binary wheels (maximum performance).

Supported Platforms
-------------------

x86_64 (AMD64) Platforms
~~~~~~~~~~~~~~~~~~~~~~~~

Linux x86_64
^^^^^^^^^^^^

**Pure Python wheels** (without NVX acceleration):

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Python Version
     - Wheel Tag Pattern
     - NVX Acceleration
   * - CPython 3.11
     - ``autobahn-{version}-cp311-cp311-linux_x86_64.whl``
     - ❌ No (pure Python)
   * - CPython 3.12
     - ``autobahn-{version}-cp312-cp312-linux_x86_64.whl``
     - ❌ No (pure Python)
   * - CPython 3.13
     - ``autobahn-{version}-cp313-cp313-linux_x86_64.whl``
     - ❌ No (pure Python)
   * - CPython 3.14
     - ``autobahn-{version}-cp314-cp314-linux_x86_64.whl``
     - ❌ No (pure Python)
   * - PyPy 3.11
     - ``autobahn-{version}-pp311-pypy311_pp73-linux_x86_64.whl``
     - ❌ No (pure Python)

**Note:** Linux x86_64 wheels are built WITHOUT NVX to ensure maximum compatibility across different Linux distributions. Users on modern x86_64 systems can still benefit from NVX by installing from source or using platform-specific builds.

macOS ARM64 (Apple Silicon)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Binary wheels with NVX acceleration**:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Python Version
     - Wheel Tag Pattern
     - NVX Acceleration
   * - CPython 3.11
     - ``autobahn-{version}-cp311-cp311-macosx_15_0_arm64.whl``
     - ✅ Yes (binary)
   * - CPython 3.12
     - ``autobahn-{version}-cp312-cp312-macosx_15_0_arm64.whl``
     - ✅ Yes (binary)
   * - CPython 3.13
     - ``autobahn-{version}-cp313-cp313-macosx_15_0_arm64.whl``
     - ✅ Yes (binary)
   * - CPython 3.14
     - ``autobahn-{version}-cp314-cp314-macosx_15_0_arm64.whl``
     - ✅ Yes (binary)
   * - PyPy 3.11
     - ``autobahn-{version}-pp311-pypy311_pp73-macosx_15_0_arm64.whl``
     - ✅ Yes (binary)

Windows x86_64
^^^^^^^^^^^^^^

**Binary wheels with NVX acceleration**:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Python Version
     - Wheel Tag Pattern
     - NVX Acceleration
   * - CPython 3.11
     - ``autobahn-{version}-cp311-cp311-win_amd64.whl``
     - ✅ Yes (binary)
   * - CPython 3.12
     - ``autobahn-{version}-cp312-cp312-win_amd64.whl``
     - ✅ Yes (binary)
   * - CPython 3.13
     - ``autobahn-{version}-cp313-cp313-win_amd64.whl``
     - ✅ Yes (binary)
   * - CPython 3.14
     - ``autobahn-{version}-cp314-cp314-win_amd64.whl``
     - ✅ Yes (binary)
   * - PyPy 3.11
     - ``autobahn-{version}-pp311-pypy311_pp73-win_amd64.whl``
     - ✅ Yes (binary)

ARM64 (aarch64) Platforms
~~~~~~~~~~~~~~~~~~~~~~~~~

Linux ARM64 (CPython)
^^^^^^^^^^^^^^^^^^^^^

**Binary wheels with NVX acceleration** (manylinux_2_28):

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Python Version
     - Wheel Tag Pattern
     - NVX Acceleration
   * - CPython 3.11
     - ``autobahn-{version}-cp311-cp311-manylinux_2_28_aarch64.whl``
     - ✅ Yes (binary)
   * - CPython 3.13
     - ``autobahn-{version}-cp313-cp313-manylinux_2_28_aarch64.whl``
     - ✅ Yes (binary)

**Compatibility:** Requires glibc 2.28 or later (Debian 10+, Ubuntu 18.04+, RHEL 8+)

Linux ARM64 (PyPy) - Debian 12
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Binary wheels with NVX acceleration** (manylinux_2_36):

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Python Version
     - Wheel Tag Pattern
     - NVX Acceleration
   * - PyPy 3.11
     - ``autobahn-{version}-pp311-pypy311_pp73-manylinux_2_36_aarch64.whl``
     - ✅ Yes (binary)

**Compatibility:** Requires glibc 2.36 or later (Debian 12+, Ubuntu 22.04+)

Linux ARM64 (PyPy) - Debian 13
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Binary wheels with NVX acceleration** (manylinux_2_38):

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Python Version
     - Wheel Tag Pattern
     - NVX Acceleration
   * - PyPy 3.11
     - ``autobahn-{version}-pp311-pypy311_pp73-manylinux_2_38_aarch64.whl``
     - ✅ Yes (binary)

**Compatibility:** Requires glibc 2.38 or later (Debian 13+, Ubuntu 24.04+)

**Note:** ARM64 wheels are built via QEMU emulation on x86_64 runners. They are fully functional native ARM64 binaries.

Source Distribution
-------------------

In addition to binary wheels, a source distribution is provided for all platforms:

.. code-block:: text

   autobahn-{version}.tar.gz

The source distribution includes:

* All Python source code
* FlatBuffers schema files (.fbs and .bfbs)
* Generated Python wrapper classes
* Build configuration (pyproject.toml)
* Documentation sources

NVX Acceleration
----------------

NVX (Native Vector Extensions) provides hardware-accelerated XOR operations for WebSocket frame masking/unmasking, offering up to 100x performance improvement on supported CPUs.

**NVX is automatically enabled** in binary wheels on:

* ✅ macOS ARM64 (all wheels)
* ✅ Windows x86_64 (all wheels)
* ✅ Linux ARM64 (all wheels)
* ❌ Linux x86_64 (pure Python for compatibility)

**Runtime Control:**

NVX can be disabled at runtime via environment variable:

.. code-block:: bash

   # Disable NVX acceleration
   export AUTOBAHN_USE_NVX=0
   python your_app.py

   # Enable NVX acceleration (default for binary wheels)
   export AUTOBAHN_USE_NVX=1
   python your_app.py

CPU Requirements
~~~~~~~~~~~~~~~~

NVX acceleration requires:

* **x86_64**: AVX2-capable CPU (Intel Haswell/2013+ or AMD Excavator/2015+)
* **ARM64**: NEON-capable CPU (all modern ARM64 CPUs)

If the CPU doesn't support the required instruction set, Autobahn falls back to pure Python implementation automatically.

Installation
------------

Installing from PyPI
~~~~~~~~~~~~~~~~~~~~

Standard installation (uses pre-built wheels when available):

.. code-block:: bash

   pip install autobahn

With optional dependencies:

.. code-block:: bash

   # Full installation with all serializers and crypto
   pip install autobahn[all]

   # Specific feature sets
   pip install autobahn[serialization]  # CBOR, MessagePack, FlatBuffers
   pip install autobahn[encryption]     # TLS, WAMP-cryptosign, WAMP-cryptobox
   pip install autobahn[compress]       # WebSocket compression

Installing from GitHub Releases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download specific wheels from GitHub Releases:

.. code-block:: bash

   # Example: Download and install Linux ARM64 wheel
   wget https://github.com/crossbario/autobahn-python/releases/download/v25.10.1/autobahn-25.10.1-cp311-cp311-manylinux_2_28_aarch64.whl
   pip install autobahn-25.10.1-cp311-cp311-manylinux_2_28_aarch64.whl

Building from Source
~~~~~~~~~~~~~~~~~~~~

To build with NVX acceleration from source:

.. code-block:: bash

   # Clone repository
   git clone https://github.com/crossbario/autobahn-python.git
   cd autobahn-python

   # Install build tools
   pip install uv
   curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s

   # Build with NVX
   export AUTOBAHN_USE_NVX=1
   just build-all

   # Wheels will be in dist/
   ls -la dist/

Wheel Naming Convention
------------------------

Wheel filenames follow the `PEP 427 <https://peps.python.org/pep-0427/>`_ naming convention:

.. code-block:: text

   {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl

Example breakdown:

.. code-block:: text

   autobahn-25.10.1-cp313-cp313-manylinux_2_28_aarch64.whl
   ^^^^^^^^ ^^^^^^^ ^^^^^ ^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^
   │        │       │     │     └─ Platform: manylinux 2.28 on ARM64
   │        │       │     └─────── ABI: CPython 3.13 stable ABI
   │        │       └───────────── Python: CPython 3.13
   │        └───────────────────── Version: 25.10.1
   └────────────────────────────── Package: autobahn

Common Tags
~~~~~~~~~~~

**Python tags:**

* ``cp311``, ``cp312``, ``cp313``, ``cp314`` - CPython 3.11, 3.12, 3.13, 3.14
* ``pp311`` - PyPy 3.11

**Platform tags:**

* ``linux_x86_64`` - Linux on x86_64 (AMD64)
* ``manylinux_2_28_aarch64`` - Linux on ARM64 with glibc 2.28+
* ``manylinux_2_36_aarch64`` - Linux on ARM64 with glibc 2.36+
* ``manylinux_2_38_aarch64`` - Linux on ARM64 with glibc 2.38+
* ``macosx_15_0_arm64`` - macOS 15+ on Apple Silicon
* ``win_amd64`` - Windows on x86_64

Verifying Wheels
----------------

All wheels are cryptographically signed and can be verified:

.. code-block:: bash

   # Verify wheel integrity
   pip install autobahn --no-deps --dry-run

   # Check wheel metadata
   unzip -l autobahn-25.10.1-cp313-cp313-linux_x86_64.whl | grep -E "\.dist-info"

Source distribution integrity verification reports are included in GitHub Releases.

Build Infrastructure
--------------------

x86_64 Wheels
~~~~~~~~~~~~~

Built on **GitHub-hosted runners** using native compilation:

* **Linux x86_64**: ubuntu-24.04 runners
* **macOS ARM64**: macos-15 runners (Apple Silicon)
* **Windows x86_64**: windows-2022 runners

ARM64 Wheels
~~~~~~~~~~~~

Built via **QEMU emulation** on ubuntu-latest runners using Docker containers:

* **CPython wheels**: Official PyPA manylinux images (quay.io/pypa/manylinux_2_28_aarch64)
* **PyPy wheels**: Custom Debian-based manylinux images with PyPy pre-installed

The ARM64 build process:

1. Set up QEMU user-mode emulation for ARM64
2. Build wheels inside ARM64 Docker containers
3. Repair wheels with auditwheel for manylinux compatibility
4. Upload to PyPI and GitHub Releases

Related Documentation
---------------------

* `PyPI Package <https://pypi.org/project/autobahn/>`_
* `GitHub Releases <https://github.com/crossbario/autobahn-python/releases>`_
* `PEP 427 - The Wheel Binary Package Format <https://peps.python.org/pep-0427/>`_
* `PEP 600 - Future manylinux Platform Tags <https://peps.python.org/pep-0600/>`_
