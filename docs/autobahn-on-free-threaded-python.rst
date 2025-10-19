.. _autobahn-on-free-threaded-python:

==========================================
Autobahn on Free-Threaded Python (PEP 703)
==========================================

.. contents::
   :local:
   :depth: 2

Preface
=======

Running Autobahn on free-threaded Python is a deep rabbit hole, and there is
no single “easy” answer we can give. Autobahn|Python supports a wide range
of combinations:

* **Runtimes:** CPython with CPyExt, and PyPy with cffi
* **Operating systems:** Linux (``epoll``), BSD (``kqueue``), and Windows (IOCP)
* **Event loops:** Python stdlib ``asyncio`` and Twisted reactors

Multiplying these dimensions quickly produces a large compatibility matrix,
and with it many opportunities for subtle issues.

Autobahn|Python itself is mostly pure Python. Optionally, there is a small
amount of native code for acceleration (primarily for CPython):
`autobahn/nvx <https://github.com/crossbario/autobahn-python/tree/master/autobahn/nvx>`_.
This code is written with `CFFI <https://github.com/python-cffi/cffi/>`_, avoids writable global state, and is therefore
considered **low risk** in the context of free-threaded Python.

Most of the potential problems do not originate in Autobahn itself, but in
the layers beneath it (Python runtime, OS event APIs, and event loop
implementations). These only become relevant when a user chooses to run
Autobahn on a free-threaded Python build.

It is also worth stressing that **Crossbar.io does not rely on free-threaded
Python**. Crossbar.io is designed for *process-based* scalability with
efficient IPC, which avoids threading pitfalls while still taking full
advantage of many-core (SMP) systems. We have tested Crossbar.io at scale
on machines with 64+ CPU cores under real-world load, and the process-based
architecture remains robust and performant.

Introduction
============

This page gives an overview of running Autobahn on Python builds where the
Global Interpreter Lock (GIL) is **disabled** (so-called *free-threaded*
builds). This feature originates from :pep:`703` and is available
experimentally in CPython 3.13+.

Autobahn’s networking relies on Python’s runtime, the event loop
(`asyncio` or Twisted), and the host operating system’s networking APIs.
With the GIL disabled, new pitfalls appear because concurrency semantics
change.

Status Summary
==============

* **CPython (default, GIL enabled):** Stable and supported.
* **CPython (``--disable-gil`` / ``-X gil=0``):** Experimental.
  Known thread-safety issues in ``asyncio`` internals
  (see `asyncio issue tracker <https://github.com/python/cpython/issues/116760>`_).
* **PyPy:** Uses cffi rather than the CPython C-API. Pure-Python code (like
  most of Autobahn) runs fine, but C extension dependencies may break.

Operating System Event Backends
===============================

Autobahn is transport-agnostic but uses asyncio or Twisted, which in turn
depend on the OS event notification API:

* **Linux:** ``epoll`` (readiness-based)
* **BSD / macOS:** ``kqueue`` (filter-based)
* **Windows:** IOCP (completion-based), or selector fallbacks

These kernel interfaces are thread-safe. The complexity lies in how Python
libraries wrap them:

* **epoll:** Level- or edge-triggered; widely understood semantics.
* **kqueue:** Requires explicit re-arming; subtle differences vs. epoll.
* **IOCP:** Completion-based (not readiness-based); asyncio provides a
  dedicated *ProactorEventLoop* for this.

Pitfalls in Free-Threaded Mode
==============================

1. **asyncio thread-safety**
   * Not all internal data structures are safe without the GIL.
   * Concurrent socket register/unregister can corrupt internal state.

2. **Twisted reactor thread affinity**
   * Twisted expects all reactor interaction from a single thread.
   * Use ``callFromThread`` / ``callInThread`` when crossing threads.

3. **C extension assumptions**
   * Many extensions assume the GIL exists.
   * Some re-enable a GIL internally, negating free-threading benefits.
   * On PyPy, C extensions must be ported to cffi.

4. **Cross-platform divergence**
   * Different semantics between epoll, kqueue, and IOCP.
   * Test across all intended platforms.

Practical Guidance
==================

* **Start small:** run an Autobahn echo server under ``python -X gil=0``.
* **Stress test:** with many concurrent connections and rapid open/close.
* **Audit dependencies:** especially TLS libraries, HTTP parsers, DB drivers.
* **Stick to documented APIs:** e.g. in Twisted, do not touch reactor
  internals outside its thread.
* **Be prepared to pin versions:** many libraries may only work with the
  traditional GIL until they are ported.

Testing Matrix
==============

Recommended environments to validate:

* **Runtimes:** CPython (GIL on), CPython (GIL off), PyPy
* **OS backends:** Linux (epoll), BSD/macOS (kqueue), Windows (IOCP)
* **Frameworks:** asyncio (default/proactor), Twisted

Future Work
===========

* CPython developers are actively fixing stdlib thread-safety issues.
* Third-party libraries are starting to publish guidance for free-threaded
  support.
* Autobahn will track these developments and update documentation.

References
==========

* :pep:`703` -- Making the Global Interpreter Lock Optional in CPython
* `CPython free-threading howto
  <https://docs.python.org/3/howto/free-threading-python.html>`_
* `asyncio thread-safety issues
  <https://github.com/python/cpython/issues/116760>`_
* `Twisted: Using Threads
  <https://docs.twistedmatrix.com/en/stable/core/howto/threading.html>`_
* `Autobahn issue #1653
  <https://github.com/crossbario/autobahn-python/issues/1653>`_

----

.. note::

   Free-threaded Python builds are **experimental** and not yet recommended
   for production use. Autobahn maintainers are tracking compatibility and
   will update this page as the ecosystem matures.
