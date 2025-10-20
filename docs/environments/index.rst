.. _environments-index:

=======================================
Runtime Environment Notes
=======================================

.. contents::
   :local:
   :depth: 1

Overview
========

Autobahn|Python is designed to run across a wide range of Python environments,
operating systems, and deployment scenarios. This section provides guidance
for running Autobahn in specific environments that may have unique
characteristics, limitations, or best practices.

Topics Covered
==============

.. toctree::
   :maxdepth: 2

   conda
   free-threaded-python

General Compatibility
=====================

Autobahn|Python supports:

* **Python Runtimes:** CPython and PyPy
* **Event Loops:** asyncio (standard library) and Twisted
* **Operating Systems:** Linux, macOS, BSD, Windows
* **Python Versions:** 3.9+ (CPython), PyPy 7.3+

For standard installations on these platforms, see the main
:doc:`../installation` guide.

When to Consult This Section
=============================

Refer to the environment-specific pages in this section if you are:

* Installing Autobahn in a **Conda environment** and need native wheels
* Running on **free-threaded Python** (PEP 703) with GIL disabled
* Using specialized deployment scenarios (Docker, embedded systems, etc.)
* Encountering platform-specific issues

Getting Help
============

If you encounter issues not covered in these guides:

1. Check the `GitHub Issues <https://github.com/crossbario/autobahn-python/issues>`_
2. Review the :doc:`../changelog` for known issues
3. Join the discussion on the `Crossbar.io mailing list
   <https://groups.google.com/forum/#!forum/crossbario>`_
