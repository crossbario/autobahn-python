:tocdepth: 1

.. _release-notes:

Release Notes
=============

This page provides a high-level overview of important changes in each release.
For detailed technical changes, see the :ref:`changelog <changelog>`.

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

Step 4: Commit and Tag
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git add docs/changelog.rst docs/release-notes.rst pyproject.toml
   git commit -m "Release <version>"
   git tag v<version>
   git push && git push --tags

Step 5: Automated Release
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
