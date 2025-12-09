:tocdepth: 1

.. _release-notes:

Release Notes
=============

This page provides a high-level overview of important changes in each release.
For detailed technical changes, see the :ref:`changelog <changelog>`.

25.12.1 (2025-12-09)
--------------------

**Release Type:** Maintenance release

**Important Changes**

This release focuses on supply chain security improvements for the CI/CD pipeline.

* **Verified Artifact Actions:** Migrated all GitHub Actions workflows to use cryptographically verified artifact upload/download actions from wamp-proto/wamp-cicd. Every artifact now includes SHA256 checksums and meta-checksums embedded in artifact names for chain-of-custody verification.

* **Self-Verification:** The download action now verifies that the artifact name's embedded checksum matches the actual content checksum. This detected and helped diagnose a GitHub infrastructure issue where the wrong artifact was being served.

* **Isolation Improvements:** Download retries now use staging directories to prevent cleanup from destroying files from other successful downloads when multiple artifacts share a destination directory.

**CI/CD Fixes**

* Fixed container job path handling to use relative paths (avoids host/container path conflicts)
* Fixed hidden file inclusion in artifact uploads (actions/upload-artifact@v4.4+ compatibility)
* Added artifact prefix matching for downloads when names include meta-checksum suffix
* Fixed recursive copy for artifacts containing directory structures

**Upgrade Notes**

No breaking changes. This is a drop-in replacement for 25.10.1.

**Release Artifacts**

* `GitHub Release <https://github.com/crossbario/autobahn-python/releases/tag/v25.12.1>`__
* `PyPI Package <https://pypi.org/project/autobahn/25.12.1/>`__
* `Documentation <https://autobahn.readthedocs.io/en/v25.12.1/>`__

**Links**

* Detailed changes: :ref:`changelog <changelog>` (25.12.1 section)


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

Overview
^^^^^^^^

The release workflow is designed to be **automated where possible** while maintaining
**human oversight** for security-critical steps (commits, tags, publishing).

**Key principles:**

* **Automated content generation**: Release notes and changelogs are generated from
  CI artifacts and git history, ensuring accuracy and consistency
* **Human review gate**: All generated content is reviewed before committing
* **Cryptographic verification**: Artifacts include SHA256 checksums and chain-of-custody
  verification files
* **Self-contained documentation**: Release notes include conformance results, artifact
  inventory, and verification info - users don't need to hunt through GitHub

**Information flow:**

.. code-block:: text

   GitHub Actions (CI)
       ↓ builds wheels, runs tests, generates metadata
   GitHub Release (nightly/stable)
       ↓ stores artifacts with checksums
   just download-release-artifacts <release>
       ↓ downloads to local /tmp/release-artifacts/
   just prepare-release <version>
       ↓ reads metadata, generates docs/release-notes.rst entry
   just prepare-changelog <version>
       ↓ reads git log + audit files, generates docs/changelog.rst entry
   Human review + commit + tag
       ↓ pushes to GitHub
   GitHub Actions (release workflow)
       ↓ publishes to PyPI, triggers RTD

Prerequisites
^^^^^^^^^^^^^

Before releasing, ensure you have:

* Push access to the repository (with tag permissions)
* GitHub CLI (``gh``) authenticated for artifact downloads
* ``just`` and ``uv`` installed
* Access to a recent nightly release to base the stable release on

Step 1: Download Release Artifacts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, identify the nightly release to promote to stable. Check recent releases at
https://github.com/crossbario/autobahn-python/releases

.. code-block:: bash

   # Download all artifacts from a nightly release
   just download-release-artifacts master-202512092131

This downloads to ``/tmp/release-artifacts/<release-name>/`` and includes:

* **Wheels**: Platform-specific binary distributions
* **Source distribution**: ``autobahn-<version>.tar.gz``
* **Conformance reports**: WebSocket test results (``*-wstest-summary.md``)
* **Checksums**: ``CHECKSUMS.sha256`` files for each build job
* **Audit files**: ``oberstet_*.md`` linking PRs to issues
* **Verification files**: Chain-of-custody metadata

Step 2: Generate Release Notes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generate the release notes entry from downloaded artifacts:

.. code-block:: bash

   just prepare-release 25.12.1

This reads from the downloaded artifacts and generates:

* **Conformance matrix**: Client/server test results (with-nvx/without-nvx)
* **Artifact inventory**: Wheels with platforms, Python versions, checksums
* **Chain of custody**: Verification file references
* **Links**: GitHub Release, PyPI, RTD documentation

The generated entry is inserted into ``docs/release-notes.rst``.

Step 3: Generate Changelog
^^^^^^^^^^^^^^^^^^^^^^^^^^

Generate the changelog entry from git history and audit files:

.. code-block:: bash

   just prepare-changelog 25.12.1

This:

1. Finds the previous version in ``docs/changelog.rst``
2. Gets commits since then: ``git log <prev-tag>..HEAD``
3. For each PR commit, finds the matching audit file in ``.audit/``
4. Extracts ``Related issue(s):`` from audit files
5. Fetches issue titles via GitHub API
6. Categorizes changes (new/fix/other) and generates RST

The generated entry is inserted into ``docs/changelog.rst``.

Step 4: Review and Edit
^^^^^^^^^^^^^^^^^^^^^^^

**Important**: Review the generated content before committing!

* Check that conformance results are 100% pass
* Verify artifact inventory matches expectations
* Edit changelog entries for clarity if needed
* Add any manual notes not captured by automation

Step 5: Validate the Release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run validation to ensure everything is in place:

.. code-block:: bash

   just prepare-release 25.12.1

This validates:

* Version in ``pyproject.toml`` matches
* Changelog entry exists for this version
* Release notes entry exists for this version
* Tests pass
* Documentation builds successfully

Step 6: Commit and Push
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git add docs/changelog.rst docs/release-notes.rst
   git commit -m "Release 25.12.1"
   git push upstream master

Step 7: Create and Push Tag
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Note**: Tags should only be created on your dev PC (not on AI-assisted workstations)
per the security architecture.

.. code-block:: bash

   # Disable git hooks if needed (AI hooks may block tagging)
   git config core.hooksPath /dev/null

   # Create annotated tag
   git tag -a v25.12.1 -m "Release 25.12.1"

   # Push tag to trigger release workflow
   git push upstream v25.12.1

   # Re-enable git hooks
   git config core.hooksPath .ai/.githooks

Step 8: Automated Publishing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After pushing the tag, GitHub Actions automatically:

1. Builds and tests the tagged version
2. Creates a GitHub Release with all artifacts
3. Publishes to PyPI via trusted publishing (OIDC)
4. Triggers Read the Docs to build versioned documentation

Monitor the workflow at: https://github.com/crossbario/autobahn-python/actions

Manual PyPI Upload (if needed)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If automated publishing fails:

.. code-block:: bash

   just download-github-release v25.12.1
   just publish-pypi "" v25.12.1

Artifact Verification
^^^^^^^^^^^^^^^^^^^^^

Users can verify downloaded artifacts using the checksums in each release:

.. code-block:: bash

   # Download checksums
   curl -LO https://github.com/crossbario/autobahn-python/releases/download/v25.12.1/CHECKSUMS.sha256

   # Verify a wheel
   openssl sha256 autobahn-25.12.1-cp311-cp311-manylinux_2_28_x86_64.whl
   grep autobahn-25.12.1-cp311-cp311-manylinux_2_28_x86_64.whl CHECKSUMS.sha256

The release notes include checksums for all artifacts, providing an additional
verification path independent of GitHub.
