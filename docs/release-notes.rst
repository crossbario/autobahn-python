:tocdepth: 1

.. _release-notes:

Release Notes
=============

This page provides a high-level overview of important changes in each release.
For detailed technical changes, see the :ref:`changelog <changelog>`.

26.10.2
-------

**Release Type:** Stable release (bug fix)

Highlights
^^^^^^^^^^

* **WAMP over TLS**: the TLS peer certificate (``TransportDetails.peer_cert``) is
  read again with pyOpenSSL 26.2.0 and later, and on Twisted WebSocket and
  RawSocket connections it is read after the TLS handshake (it was always
  ``None``), so TLS client certificate authentication works again. On asyncio,
  ``peer_cert`` is filled, and a TLS server connection without a client
  certificate is secure and has a channel ID. The certificate is read with
  ``cryptography``, in the new ``autobahn.util.peer_certificate_details()``.

* **⚠ TLS channel binding**: ``tls-unique`` on Twisted now follows RFC 5929, as
  Python's ``ssl`` module does, so WAMP-cryptosign with channel binding works
  between Twisted and asyncio peers. Twisted peers on 26.10.1 or older and on
  26.10.2 no longer agree on the channel ID over WebSocket: upgrade both sides of
  connections that use channel binding. On PyPy, autobahn works around a PyPy
  ``ssl`` bug (`pypy/pypy#5676 <https://github.com/pypy/pypy/issues/5676>`__).

* **⚠ peer_cert format**: ``extensions[].value`` is OpenSSL's text only for
  subject and issuer alternative names, other extensions are given as
  ``cryptography`` prints them; ``signature_algorithm`` is ``ed25519`` instead of
  ``ED25519`` for Ed25519 certificates.

Release Links
^^^^^^^^^^^^^

* `PyPI Package <https://pypi.org/project/autobahn/26.10.2/>`__

**Detailed Changes:** See :ref:`changelog` (26.10.2 section)

26.10.1
-------

**Release Type:** Stable release

Highlights
^^^^^^^^^^

* **WebSocket compression**: all four per-message compression extensions
  (``permessage-deflate``, ``-bzip2``, ``-brotli``, ``-snappy``) enforce the
  ``maxMessagePayloadSize`` decompression budget the same way, and invalid
  compressed data fails the connection with close code 1007
  (``PayloadCorruptError``). ``permessage-brotli`` no longer fails on the second
  message of a connection. New floors: ``brotli>=1.2.0`` / ``brotlicffi>=1.2.0``.
  New page: :doc:`/websocket/compression`.

* **Memory footprint**: importing autobahn no longer loads the FlatBuffers runtime
  or numpy; it is loaded when a FlatBuffers message is first used. Every import
  needs about 13-17 MB less on CPython and 18-24 MB less on PyPy. New page:
  :ref:`memory-footprint`.

* **CPython 3.14 / asyncio**: ``run()``, ``ApplicationRunner.run()``,
  ``Component.start()`` and the asyncio WebSocket factories work when started from
  synchronous code (no implicit event loop on 3.14).

* **Windows ARM64**: native ``win_arm64`` wheels for CPython 3.11-3.14 (thanks
  @ndabas). ARM64 Linux wheels are now built natively instead of under QEMU.

* **Dependencies**: ``cbor2`` split by runtime (CPython ``>=6.1.0``, PyPy
  ``==5.9.0``), ``cryptography>=50``, ``zope.interface>=6.2``.

Release Links
^^^^^^^^^^^^^

* `PyPI Package <https://pypi.org/project/autobahn/26.10.1/>`__

**Detailed Changes:** See :ref:`changelog` (26.10.1 section)

26.7.1 (2026-07-15)
-------------------

**Release Type:** Stable release (security)

Highlights
^^^^^^^^^^

* **Security**: WebSocket ``maxMessagePayloadSize`` is enforced against the
  uncompressed message size when per-message compression is negotiated, not against
  the compressed frame length (security advisory GHSA-hxp9-w8x3-p566). Decompression
  is bounded for every compression extension, and the asyncio RawSocket receive
  limit is configurable, at parity with Twisted.

* **Alpine Linux**: ``musllinux_1_2`` wheels with NVX for CPython 3.11-3.14 on
  x86_64 and aarch64.

* **Wheels**: the aarch64 CPython 3.14 wheel no longer ships the free-threaded ABI
  in the ``cp314`` slot; build and release gates reject a wrong-ABI wheel.

Release Links
^^^^^^^^^^^^^

* `GitHub Release <https://github.com/crossbario/autobahn-python/releases/tag/v26_7_1>`__
* `PyPI Package <https://pypi.org/project/autobahn/26.7.1/>`__

**Detailed Changes:** See :ref:`changelog` (26.7.1 section)

26.6.2 (2026-06-19)
-------------------

**Release Type:** Stable release (bug fix)

Highlights
^^^^^^^^^^

* **WAMP Cryptosign**: fix ``import autobahn.wamp.cryptosign`` raising ``TypeError``
  on CPython 3.11-3.13 when ``nacl`` is installed (a regression in 26.6.1). An import
  smoke test now covers every public submodule on all supported Pythons.

Release Links
^^^^^^^^^^^^^

* `GitHub Release <https://github.com/crossbario/autobahn-python/releases/tag/v26_6_2>`__
* `PyPI Package <https://pypi.org/project/autobahn/26.6.2/>`__

**Detailed Changes:** See :ref:`changelog` (26.6.2 section)

26.6.1 (2026-06-18)
-------------------

**Release Type:** Stable release

Highlights
^^^^^^^^^^

* **WAMP serialization**: ``py-ubjson`` is no longer a dependency; the ``ubjson``
  serializer is backed by ``bjdata`` in the optional ``serialization`` extra
  (CPython only). Note: bjdata's encoding is not byte-identical to py-ubjson's.

* **FlatBuffers**: vendored FlatBuffers v25.12.19, in sync with zlmdb 26.6.1; the
  binary schemas are committed, so building from the sdist no longer runs ``flatc``
  (cross-compilation from the sdist works).

* **RawSocket**: a failed opening handshake on Twisted (e.g. from a port scanner)
  closes the connection cleanly instead of raising ``TransportLost``.

* **Wheels**: the release fileset is symmetric across macOS arm64, Linux x86_64,
  Linux aarch64 and Windows x86_64 for CPython 3.11-3.14 and PyPy 3.11 (the
  aarch64 CPython 3.12 and 3.14 wheels were missing before).

Release Links
^^^^^^^^^^^^^

* `GitHub Release <https://github.com/crossbario/autobahn-python/releases/tag/v26_6_1>`__
* `PyPI Package <https://pypi.org/project/autobahn/26.6.1/>`__

**Detailed Changes:** See :ref:`changelog` (26.6.1 section)

25.12.2 (2025-12-15)
--------------------

**Release Type:** Stable release

**Source Build:** `master-202512150317 <https://github.com/crossbario/autobahn-python/releases/tag/master-202512150317>`__

Highlights
^^^^^^^^^^

This release synchronizes the CI/CD infrastructure and FlatBuffers vendoring
between autobahn-python and zlmdb, ensuring consistent behavior for applications
using both libraries (like Crossbar.io).

Key changes:

* **manylinux compatibility fix**: Switched from manylinux_2_34 to manylinux_2_28
  containers to avoid x86_64_v2 ISA requirements that caused auditwheel failures
  when bundling the flatc compiler.

* **FlatBuffers version sync**: Added ``check_zlmdb_flatbuffers_version_in_sync()``
  function to verify autobahn and zlmdb use compatible FlatBuffers runtimes.

* **Improved release workflow**: Consolidated artifact download recipes with
  checksum verification for supply chain security.

Artifact Verification
^^^^^^^^^^^^^^^^^^^^^

All release artifacts include SHA256 checksums for integrity verification.

* `wheels-CHECKSUMS.sha256 <https://github.com/crossbario/autobahn-python/releases/download/master-202512150317/wheels-CHECKSUMS.sha256>`__
* `docker-CHECKSUMS.sha256 <https://github.com/crossbario/autobahn-python/releases/download/master-202512150317/docker-CHECKSUMS.sha256>`__
* `arm64-CHECKSUMS.sha256 <https://github.com/crossbario/autobahn-python/releases/download/master-202512150317/arm64-CHECKSUMS.sha256>`__

To verify a downloaded artifact:

.. code-block:: bash

   # Download checksum file
   curl -LO https://github.com/crossbario/autobahn-python/releases/download/master-202512150317/wheels-CHECKSUMS.sha256

   # Verify a wheel (example)
   openssl sha256 autobahn-25.12.2-cp311-cp311-manylinux_2_28_x86_64.whl
   # Compare output with corresponding line in CHECKSUMS file

Release Links
^^^^^^^^^^^^^

* `GitHub Release <https://github.com/crossbario/autobahn-python/releases/tag/v25.12.2>`__
* `PyPI Package <https://pypi.org/project/autobahn/25.12.2/>`__
* `Documentation <https://autobahn.readthedocs.io/en/v25.12.2/>`__

**Detailed Changes:** See :ref:`changelog` (25.12.2 section)

25.12.1 (2025-12-10)
--------------------

**Release Type:** Stable release

**Source Build:** `master-202512092131 <https://github.com/crossbario/autobahn-python/releases/tag/master-202512092131>`__

WebSocket Conformance
^^^^^^^^^^^^^^^^^^^^^

Autobahn|Python passes 100% of the WebSocket conformance tests from the
`Autobahn|Testsuite <https://github.com/crossbario/autobahn-testsuite>`_.

Configuration: with-nvx (NVX acceleration)
""""""""""""""""""""""""""""""""""""""""""

**Client Conformance**

.. list-table::
   :header-rows: 1
   :widths: 60 20 10

   * - Testee
     - Cases
     - Status
   * - ``Autobahn/25.12.1-NVXCFFI/1.18.0.dev0-Twisted/25.5.0-PyPy/3.11.13``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-NVXCFFI/1.18.0.dev0-asyncio-PyPy/3.11.13``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-NVXCFFI/2.0.0-Twisted/25.5.0-CPython/3.11.14``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-NVXCFFI/2.0.0-Twisted/25.5.0-CPython/3.14.2``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-NVXCFFI/2.0.0-asyncio-CPython/3.11.14``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-NVXCFFI/2.0.0-asyncio-CPython/3.14.2``
     - 246 / 246
     - ✅

**Server Conformance**

.. list-table::
   :header-rows: 1
   :widths: 60 20 10

   * - Testee
     - Cases
     - Status
   * - ``Autobahn/25.12.1-NVXCFFI/1.18.0.dev0-Twisted/25.5.0-PyPy/3.11.13``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-NVXCFFI/1.18.0.dev0-asyncio-PyPy/3.11.13``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-NVXCFFI/2.0.0-Twisted/25.5.0-CPython/3.11.14``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-NVXCFFI/2.0.0-Twisted/25.5.0-CPython/3.14.2``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-NVXCFFI/2.0.0-asyncio-CPython/3.11.14``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-NVXCFFI/2.0.0-asyncio-CPython/3.14.2``
     - 246 / 246
     - ✅

Configuration: without-nvx (pure Python)
""""""""""""""""""""""""""""""""""""""""""

**Client Conformance**

.. list-table::
   :header-rows: 1
   :widths: 60 20 10

   * - Testee
     - Cases
     - Status
   * - ``Autobahn/25.12.1-Twisted/25.5.0-CPython/3.11.14``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-Twisted/25.5.0-CPython/3.14.2``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-Twisted/25.5.0-PyPy/3.11.13``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-asyncio-CPython/3.11.14``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-asyncio-CPython/3.14.2``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-asyncio-PyPy/3.11.13``
     - 246 / 246
     - ✅

**Server Conformance**

.. list-table::
   :header-rows: 1
   :widths: 60 20 10

   * - Testee
     - Cases
     - Status
   * - ``Autobahn/25.12.1-Twisted/25.5.0-CPython/3.11.14``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-Twisted/25.5.0-CPython/3.14.2``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-Twisted/25.5.0-PyPy/3.11.13``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-asyncio-CPython/3.11.14``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-asyncio-CPython/3.14.2``
     - 246 / 246
     - ✅
   * - ``Autobahn/25.12.1-asyncio-PyPy/3.11.13``
     - 246 / 246
     - ✅

Release Artifacts
^^^^^^^^^^^^^^^^^

Binary wheels are available for the following platforms:

.. list-table:: Platform Support Matrix
   :header-rows: 1
   :widths: 20 15 15 50

   * - Platform
     - Python
     - Arch
     - Wheel
   * - Linux
     - CPython 3.11
     - x86_64
     - ``autobahn-25.12.1-cp311-cp311-manylinux1_x86_64.manylinux_2_34_x86_64.manylinux_2_5_x86_64.whl``
   * - Linux
     - CPython 3.11
     - ARM64
     - ``autobahn-25.12.1-cp311-cp311-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl``
   * - Linux
     - CPython 3.12
     - x86_64
     - ``autobahn-25.12.1-cp312-cp312-manylinux1_x86_64.manylinux_2_34_x86_64.manylinux_2_5_x86_64.whl``
   * - Linux
     - CPython 3.13
     - x86_64
     - ``autobahn-25.12.1-cp313-cp313-manylinux1_x86_64.manylinux_2_34_x86_64.manylinux_2_5_x86_64.whl``
   * - Linux
     - CPython 3.13
     - ARM64
     - ``autobahn-25.12.1-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl``
   * - Linux
     - CPython 3.14
     - x86_64
     - ``autobahn-25.12.1-cp314-cp314-manylinux1_x86_64.manylinux_2_34_x86_64.manylinux_2_5_x86_64.whl``
   * - Linux
     - PyPy 3.11
     - x86_64
     - ``autobahn-25.12.1-pp311-pypy311_pp73-manylinux1_x86_64.manylinux_2_34_x86_64.manylinux_2_5_x86_64.whl``
   * - Linux
     - PyPy 3.11
     - ARM64
     - ``autobahn-25.12.1-pp311-pypy311_pp73-manylinux2014_aarch64.manylinux_2_17_aarch64.whl``
   * - macOS
     - CPython 3.13
     - ARM64
     - ``autobahn-25.12.1-cp313-cp313-macosx_15_0_arm64.whl``
   * - macOS
     - CPython 3.14
     - ARM64
     - ``autobahn-25.12.1-cp314-cp314-macosx_15_0_arm64.whl``
   * - macOS
     - PyPy 3.11
     - ARM64
     - ``autobahn-25.12.1-pp311-pypy311_pp73-macosx_15_0_arm64.whl``
   * - Windows
     - CPython 3.11
     - x86_64
     - ``autobahn-25.12.1-cp311-cp311-win_amd64.whl``
   * - Windows
     - CPython 3.12
     - x86_64
     - ``autobahn-25.12.1-cp312-cp312-win_amd64.whl``
   * - Windows
     - CPython 3.13
     - x86_64
     - ``autobahn-25.12.1-cp313-cp313-win_amd64.whl``
   * - Windows
     - CPython 3.14
     - x86_64
     - ``autobahn-25.12.1-cp314-cp314-win_amd64.whl``
   * - Windows
     - PyPy 3.11
     - x86_64
     - ``autobahn-25.12.1-pp311-pypy311_pp73-win_amd64.whl``

Source distribution: ``autobahn-25.12.1.tar.gz``

Artifact Verification
^^^^^^^^^^^^^^^^^^^^^

All release artifacts include SHA256 checksums for integrity verification.

* `CHECKSUMS.sha256 <https://github.com/crossbario/autobahn-python/releases/download/master-202512092131/CHECKSUMS.sha256>`__

To verify a downloaded artifact:

.. code-block:: bash

   # Download checksum file
   curl -LO https://github.com/crossbario/autobahn-python/releases/download/master-202512092131/CHECKSUMS.sha256

   # Verify a wheel (example)
   openssl sha256 autobahn-25.12.1-cp311-cp311-manylinux_2_28_x86_64.whl
   # Compare output with corresponding line in CHECKSUMS.sha256

Release Links
^^^^^^^^^^^^^

* `GitHub Release <https://github.com/crossbario/autobahn-python/releases/tag/v25.12.1>`__
* `PyPI Package <https://pypi.org/project/autobahn/25.12.1/>`__
* `Documentation <https://autobahn.readthedocs.io/en/v25.12.1/>`__

**Detailed Changes:** See :ref:`changelog` (25.12.1 section)

25.10.1 (2025-10-18)
--------------------

**Release Type:** Stable release

**Important Fixes**

This maintenance release focuses on supply chain security, testing infrastructure improvements, and documentation enhancements.

* **Server Conformance Testing:** Fixed critical bug where both with-nvx and without-nvx server conformance tests were testing against the same server configuration. Servers now properly restart between NVX configuration changes, ensuring accurate test results.

* **Supply Chain Security (Issue #1716):** Added comprehensive source distribution integrity verification with cryptographic fingerprints and chain of custody verification throughout the release workflow.

* **Documentation Integration:** WebSocket conformance reports and FlatBuffers schemas are now properly integrated into Read the Docs builds via GitHub Release artifacts.

**Documentation Improvements**

* New justfile recipes for streamlined release artifact management
* Improved pre-release checklist with artifact integration workflow
* Enhanced WebSocket conformance documentation structure

**Wheel Building**

* Fixed ARM64 wheel builds to eliminate duplicate wheels
* Improved PyPI publishing to filter out non-package files

**Upgrade Notes**

No breaking changes. This is a drop-in replacement for 25.9.1.

**Release Artifacts**

* `GitHub Release <https://github.com/crossbario/autobahn-python/releases/tag/v25.10.1>`__
* `PyPI Package <https://pypi.org/project/autobahn/25.10.1/>`__
* `Documentation <https://autobahn.readthedocs.io/en/v25.10.1/>`__

**Links**

* Detailed changes: :ref:`changelog <changelog>` (25.10.1 section)


25.9.1 (2025-09-15)
-------------------

**Release Type:** Feature release

**Major New Features**

* **NVX Native XOR Masking Acceleration (#1697):** Up to 100x faster WebSocket frame masking/unmasking on supported CPUs through hardware-accelerated XOR operations. Automatically enabled on x86_64 CPUs with AVX2 support. Control via ``AUTOBAHN_USE_NVX`` environment variable.

* **ARM64 Wheel Building:** Full ARM64 support via QEMU emulation for CPython 3.11, 3.13 and PyPy 3.11. Docker-based multi-arch wheel building system supporting both manylinux_2_17 and manylinux_2_28.

* **Modern Python Toolchain:** Complete migration to modern build tools:

  - ``just`` for task automation (replacing Make)
  - ``uv`` for fast Python package management
  - ``ruff`` for fast linting and formatting
  - Removed setuptools dependency - now using pure pyproject.toml-based builds

**Deprecation Removals**

* Removed ``twisted.internet.defer.returnValue`` usage throughout codebase (#1667, #1651)
* Replaced with native Python ``return`` statements (Python 3.3+ syntax)
* Various deprecation warnings in tests cleaned up (#1647)

**CI/CD Improvements**

* Symmetric release structure across all 3 release types (stable, nightly, development)
* Early Exit Pattern prevents unnecessary workflow runs
* FlatBuffers schema packaged as tarball in GitHub releases
* GitHub Discussions support for automated release announcements

**Platform Support**

* Full PyPy ARM64 support with proper PATH configuration
* Platform-specific wheel building (manylinux_2_17 for older systems, manylinux_2_28 for newer)
* Windows builds use MSVC attributes
* Fixed auditwheel handling under QEMU emulation

**Refactoring**

* LMDB & XBR code refactored and broken out to separate packages (#1664)
* Removed unnecessary dependencies - plain Twisted utilities are sufficient (#1661)
* Improved code organization and maintainability

**AI Policy Announcement**

* New AI policy for AI-assisted contributions (#1663)

**Upgrade Notes**

* **Breaking Change:** Minimum Twisted version may have changed - check your dependencies
* **Performance:** NVX acceleration is automatically enabled on supported CPUs. Set ``AUTOBAHN_USE_NVX=0`` to disable if needed
* **Build System:** If you build from source, note the migration to modern tooling (just, uv, pyproject.toml)

**Release Artifacts**

* `GitHub Release <https://github.com/crossbario/autobahn-python/releases/tag/v25.9.1>`__
* `PyPI Package <https://pypi.org/project/autobahn/25.9.1/>`__
* `Documentation <https://autobahn.readthedocs.io/en/v25.9.1/>`__

**Links**

* Detailed changes: :ref:`changelog <changelog>` (25.9.1 section)


24.4.2 (2024-04-15)
-------------------

**Release Type:** Bug fix release

**Fixes**

* Ensure ID generator stays in range [1, 2^53] (#1637)

**Release Artifacts**

* `GitHub Release <https://github.com/crossbario/autobahn-python/releases/tag/v24.4.2>`__
* `PyPI Package <https://pypi.org/project/autobahn/24.4.2/>`__
* `Documentation <https://autobahn.readthedocs.io/en/v24.4.2/>`__

**Links**

* Detailed changes: :ref:`changelog <changelog>` (24.4.2 section)


Where to Get Help
-----------------

If you encounter issues upgrading or have questions:

* `GitHub Issues <https://github.com/crossbario/autobahn-python/issues>`_ - Bug reports and feature requests
* `GitHub Discussions <https://github.com/crossbario/autobahn-python/discussions>`_ - Community Q&A
* `Stack Overflow <https://stackoverflow.com/questions/tagged/autobahn>`_ - Tag questions with ``autobahn``
* `Documentation <https://autobahnpython.readthedocs.io/>`_ - Full documentation on Read the Docs

See Also
--------

* :ref:`changelog <changelog>` - Detailed technical changelog
* Installation instructions - see README.md
* `GitHub Releases <https://github.com/crossbario/autobahn-python/releases>`_ - Release artifacts and announcements

--------------

.. _release-workflow:

Release Workflow (for Maintainers)
----------------------------------

This section documents the release process for maintainers.

Prerequisites
^^^^^^^^^^^^^

Before releasing, ensure you have:

* Push access to the repository
* PyPI credentials configured (or trusted publishing via GitHub Actions)
* ``just`` and ``uv`` installed

Step 1: Draft the Release
^^^^^^^^^^^^^^^^^^^^^^^^^

Generate changelog and release note templates:

.. code-block:: bash

   # Generate changelog entry from git history (for catching up)
   just prepare-changelog <version>

   # Generate release draft with templates for both files
   just draft-release <version>

This will:

* Add a changelog entry template to ``docs/changelog.rst``
* Add a release entry template to ``docs/release-notes.rst``
* Update the version in ``pyproject.toml``

Step 2: Edit Changelog
^^^^^^^^^^^^^^^^^^^^^^

Edit ``docs/changelog.rst`` and fill in the changelog details:

* **New**: New features and capabilities
* **Fix**: Bug fixes
* **Other**: Breaking changes, deprecations, other notes

Step 3: Validate the Release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ensure everything is in place:

.. code-block:: bash

   just prepare-release <version>

This validates:

* Changelog entry exists for this version
* Release entry exists for this version
* Version in ``pyproject.toml`` matches
* All tests pass
* Documentation builds successfully

Step 4: Disable Git Hooks (if needed)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git config core.hooksPath /dev/null
   git config core.hooksPath

Step 5: Commit and Tag
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git add docs/changelog.rst docs/release-notes.rst pyproject.toml
   git commit -m "Release <version>"
   git tag v<version>
   git push && git push --tags

Step 6: Enable Git Hooks (if previously disabled)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git config core.hooksPath .ai/.githooks
   git config core.hooksPath

Step 7: Automated Release
^^^^^^^^^^^^^^^^^^^^^^^^^

After pushing the tag:

1. GitHub Actions builds and tests the release
2. Wheels and source distributions are uploaded to GitHub Releases
3. PyPI publishing is triggered via trusted publishing (OIDC)
4. Read the Docs builds documentation for the tagged version

Manual PyPI Upload (if needed)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If automated publishing fails:

.. code-block:: bash

   just download-github-release v<version>
   just publish-pypi "" v<version>
