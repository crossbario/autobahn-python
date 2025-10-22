.. _conda:

============================
Autobahn on Conda
============================

.. contents::
   :local:
   :depth: 2

Overview
========

`Conda <https://docs.conda.io/>`_ is a popular cross-platform package manager
and environment manager widely used in scientific computing, data science, and
machine learning workflows. While Autobahn|Python is available on the
`conda-forge <https://conda-forge.org/>`_ channel, the conda-forge version may
lag behind the latest releases on `PyPI <https://pypi.org/project/autobahn/>`_.

**TL;DR:** Use ``pip install autobahn`` within your Conda environment to get
the latest version with native wheels from PyPI.

Why Conda-Forge Lags Behind PyPI
=================================

Conda packages require additional steps beyond publishing to PyPI:

1. A maintainer must update the `autobahn-feedstock <https://github.com/conda-forge/autobahn-feedstock>`_
   repository with the new version
2. The conda-forge CI/CD pipeline builds packages for all platforms
3. Review and merge process adds additional time
4. Build times can vary depending on conda-forge infrastructure load

As a result, the conda-forge version may be **weeks or months** behind PyPI.

Current Version Status
======================

You can check the current versions at:

* **PyPI (latest):** https://pypi.org/project/autobahn/#history
* **conda-forge:** https://anaconda.org/conda-forge/autobahn

As of this writing:

* PyPI has v25.10.1 (October 2025)
* conda-forge has v24.4.2 (March 2024)

Recommended Installation Method
================================

The **officially supported** approach is to use ``pip`` within a Conda environment:

.. code-block:: bash

    # Create a new Conda environment
    conda create -n myproject python=3.11

    # Activate the environment
    conda activate myproject

    # Install Autobahn from PyPI using pip
    pip install autobahn

    # Or specify an exact version
    pip install autobahn==25.10.1

Why This Works Well
-------------------

1. **Official Support**

   Conda explicitly supports and recommends using ``pip`` within Conda
   environments. See the `Conda documentation on pip
   <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#using-pip-in-an-environment>`_.

2. **Native Wheels**

   pip will automatically download and install the correct platform-specific
   wheel from PyPI, including:

   * **macOS** (ARM64 Apple Silicon)
   * **Windows** (x86_64)
   * **Linux** (x86_64, with/without NVX acceleration)
   * **manylinux wheels** for broad Linux compatibility

3. **Latest Versions**

   PyPI receives new releases immediately, often within minutes of tagging.

4. **Environment Isolation**

   pip installs packages into the Conda environment's ``site-packages``,
   maintaining complete isolation from other environments and the system
   Python.

5. **Dependency Resolution**

   pip correctly resolves dependencies (``cryptography``, ``twisted``,
   ``txaio``, etc.) and installs compatible versions.

Understanding Native Wheels vs Source Distribution
===================================================

When you install with pip, you may get one of two formats:

Native Wheel (Recommended)
--------------------------

* **File extension:** ``.whl``
* **Contains:** Pre-compiled binary code (if applicable) + Python code
* **Installation:** Fast (no compilation required)
* **NVX Acceleration:** Automatically included in "with-nvx" wheels

PyPI provides wheels for:

.. code-block:: text

    autobahn-25.10.1-cp311-cp311-macosx_11_0_arm64.whl       # macOS ARM64
    autobahn-25.10.1-cp311-cp311-win_amd64.whl               # Windows x64
    autobahn-25.10.1-cp311-cp311-manylinux_2_17_x86_64.whl   # Linux x64
    autobahn-25.10.1-py3-none-any.whl                        # Pure Python (no NVX)

Source Distribution (Fallback)
------------------------------

* **File extension:** ``.tar.gz``
* **Contains:** Source code only
* **Installation:** May require compilation (slower)
* **Use case:** Platforms without pre-built wheels

To verify which format was installed:

.. code-block:: bash

    pip list --format=freeze | grep autobahn

Native Acceleration (NVX)
=========================

Autobahn includes optional native acceleration called **NVX** (Native eXtensions)
for improved WebSocket and WAMP performance on CPython and PyPy. See
:doc:`../wheels-inventory` for details.

When installing from PyPI wheels:

* **"with-nvx" wheels:** Include compiled NVX extensions (automatic)
* **"without-nvx" wheels:** Pure Python fallback (automatic on incompatible systems)

NVX Status in Conda
-------------------

If you see errors like:

.. code-block:: text

    ModuleNotFoundError: No module named '_nvx_utf8validator'

This means Autobahn is trying to use NVX but the extension is missing. This
can happen if:

1. You installed from conda-forge (which may not include NVX)
2. The wheel didn't match your platform
3. Your system doesn't support NVX (very old CPU)

**Solution:** Disable NVX with an environment variable:

.. code-block:: bash

    export AUTOBAHN_USE_NVX=0
    # Or on Windows:
    set AUTOBAHN_USE_NVX=0

Alternatively, reinstall from PyPI to get the correct wheel:

.. code-block:: bash

    pip uninstall autobahn
    pip install autobahn

Verifying Your Installation
============================

After installation, verify everything works:

.. code-block:: bash

    python -c "import autobahn; print(autobahn.__version__)"

Expected output:

.. code-block:: text

    25.10.1

Check if NVX is enabled:

.. code-block:: python

    import autobahn
    print(autobahn.nvx.HAS_NVX)  # True if NVX is available

Test a simple WebSocket echo server:

.. code-block:: python

    from autobahn.asyncio.websocket import WebSocketServerProtocol, \
        WebSocketServerFactory
    import asyncio

    class EchoServerProtocol(WebSocketServerProtocol):
        def onMessage(self, payload, isBinary):
            self.sendMessage(payload, isBinary)

    factory = WebSocketServerFactory("ws://127.0.0.1:9000")
    factory.protocol = EchoServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '127.0.0.1', 9000)
    server = loop.run_until_complete(coro)

    try:
        print("Server running on ws://127.0.0.1:9000")
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()

Using conda-forge (Not Recommended)
====================================

If you must use conda-forge instead of PyPI:

.. code-block:: bash

    conda install -c conda-forge autobahn

**Drawbacks:**

* Older version (likely months behind PyPI)
* May not include NVX acceleration
* Slower release cycle
* Limited platform-specific builds

To update the conda-forge package yourself, see the `autobahn-feedstock
contributing guide
<https://github.com/conda-forge/autobahn-feedstock#updating-autobahn-feedstock>`_.

Managing Dependencies
=====================

Autobahn has several dependencies that may also be installed via pip or conda:

Core Dependencies
-----------------

* **txaio:** Abstraction layer for asyncio/Twisted compatibility
* **cryptography:** TLS/SSL support, WAMP-cryptosign authentication
* **hyperlink:** URL parsing and manipulation

Optional Dependencies
---------------------

* **twisted:** Required for Twisted-based applications
* **msgpack:** MessagePack serialization (WAMP)
* **cbor2:** CBOR serialization (WAMP)
* **flatbuffers:** FlatBuffers serialization (WAMP)
* **ujson:** Fast JSON serialization (optional)
* **pyqrcode:** QR code generation (WAMP-cryptosign)

Install optional features:

.. code-block:: bash

    # All optional dependencies
    pip install autobahn[all]

    # Specific feature sets
    pip install autobahn[twisted]          # Twisted support
    pip install autobahn[asyncio]          # asyncio support (minimal)
    pip install autobahn[serialization]    # All serializers
    pip install autobahn[encryption]       # Crypto/TLS support
    pip install autobahn[compress]         # WebSocket compression

Troubleshooting
===============

Issue: "No module named 'autobahn'"
------------------------------------

**Cause:** Autobahn is not installed, or the wrong Python interpreter is active.

**Solution:**

.. code-block:: bash

    # Verify you're in the correct Conda environment
    conda activate myproject

    # Verify the Python interpreter
    which python

    # Reinstall
    pip install autobahn

Issue: "Import Error: cannot import name X"
--------------------------------------------

**Cause:** Version mismatch between Autobahn and dependencies.

**Solution:**

.. code-block:: bash

    # Update all dependencies
    pip install --upgrade autobahn txaio cryptography

Issue: Old version from conda-forge
------------------------------------

**Cause:** conda-forge package is outdated.

**Solution:**

.. code-block:: bash

    # Uninstall conda version
    conda remove autobahn

    # Install latest from PyPI
    pip install autobahn

Compatibility Matrix
====================

Autobahn works with:

* **Python:** 3.9, 3.10, 3.11, 3.12, 3.13, PyPy 7.3+
* **Operating Systems:** Linux, macOS, Windows, BSD
* **Event Loops:** asyncio (stdlib), Twisted
* **Package Managers:** pip, conda, poetry, pipenv

For the full list of tested platforms and wheels, see :doc:`../wheels-inventory`.

Getting Help
============

If you encounter issues with Conda installations:

1. Check `GitHub Issues <https://github.com/crossbario/autobahn-python/issues>`_
2. Review the :doc:`../installation` guide
3. Ask on `Stack Overflow <https://stackoverflow.com/questions/tagged/autobahn>`_
   with the ``autobahn`` tag
4. Join the `Crossbar.io mailing list
   <https://groups.google.com/forum/#!forum/crossbario>`_

References
==========

* `Conda User Guide <https://docs.conda.io/projects/conda/en/latest/user-guide/>`_
* `Using pip in a conda environment
  <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#using-pip-in-an-environment>`_
* `conda-forge autobahn package <https://anaconda.org/conda-forge/autobahn>`_
* `autobahn-feedstock repository
  <https://github.com/conda-forge/autobahn-feedstock>`_
* `Autobahn PyPI page <https://pypi.org/project/autobahn/>`_

----

.. note::

   **Best Practice:** Always use ``pip install autobahn`` within Conda
   environments to get the latest version with native wheels from PyPI.
   This ensures maximum compatibility and performance.
