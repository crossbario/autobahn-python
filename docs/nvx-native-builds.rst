.. _nvx-native-builds:

NVX, CPU ISA Levels, and Native/Cross Builds
=============================================

This page is the single reference for |ab|'s native-code story: **NVX**, |ab|'s
own small SIMD accelerator; the CPU instruction-set-architecture (ISA) floors its
binary wheels are built to; what a native (host-targeted) or cross-compiled build
does differently; and how to check, after the fact, what a wheel or a CPU actually
supports. It consolidates and cross-links material that was previously scattered
across :doc:`wheels-inventory`, :doc:`environments/conda`, :doc:`release-notes`,
:doc:`changelog` and the ``autobahn.nvx._compile_args`` module docstring (also
published via the generated API reference (``sphinx-autoapi``), despite its
leading underscore).

.. note::

   Every claim on this page was checked against the |ab| source in this
   repository, or measured on a real build performed while writing this page
   (an x86-64 KVM guest, CPython 3.14.7, GCC). Where something could not be
   measured on this machine - an aarch64 target, a true cross-build, a CPU below
   the published floor, or another host entirely - that is said explicitly, and
   the claim is attributed to its source instead of presented as measured.

Two-layer model
----------------

|ab|'s WebSocket hot paths - UTF-8 validation of text frames and XOR masking of
frame payloads - have two implementations:

* A **pure-Python implementation**, always present, with no ISA floor and no
  compiler involved. It runs on any CPU, any architecture, CPython and PyPy
  alike. This is what makes the claim "autobahn always runs" true: there is no
  configuration in which |ab| fails to import or fails to process WebSocket
  traffic for lack of native code.
* **NVX** (Native Vector Extensions), an optional CFFI-compiled C accelerator
  for the same two operations (``autobahn.nvx._utf8validator`` and
  ``autobahn.nvx._xormasker``), built against a fixed, documented ISA floor (see
  below). NVX does not change behaviour, only speed.

Both configurations - with and without NVX - are tested for WebSocket protocol
conformance using `Autobahn|Testsuite
<https://github.com/crossbario/autobahn-testsuite>`_, and both pass every test
case in strict mode. See the "Configuration: with-nvx" and "Configuration:
without-nvx" conformance tables in :doc:`release-notes` (25.12.1's 246/246
client and server results on CPython and PyPy, Twisted and asyncio) - the same
two configurations this page describes.

ISA floors of the published native wheels
-------------------------------------------

NVX is built with a fixed, no-runtime-dispatch ``-march`` floor per target
architecture - not with runtime CPUID feature detection. This is implemented in
``autobahn/nvx/_compile_args.py`` (``get_compile_args()``), which is the single
authoritative source for the floors below:

.. list-table::
   :header-rows: 1

   * - Target
     - ``-march`` floor
     - Meaning
   * - x86-64 (wheels, source default)
     - ``x86-64-v2``
     - SSSE3, SSE4.1, SSE4.2, POPCNT, CMPXCHG16B (~2009+ CPUs: Intel Nehalem+,
       AMD Bulldozer+)
   * - aarch64 (wheels, source default)
     - ``armv8-a``
     - The 64-bit ARM baseline. Every 64-bit ARM CPU qualifies - there is no
       aarch64 sub-floor case.
   * - Either, with ``AUTOBAHN_ARCH_TARGET=native``
     - ``-march=native``
     - Host-CPU-locked, maximum performance. Opt-in only; see below.

Verified on this machine (x86-64, NVX built from source, no override):

.. code-block:: console

   $ python -c "from autobahn.nvx._compile_args import get_compile_args; print(get_compile_args())"
   ['-std=c99', '-Wall', '-Wno-strict-prototypes', '-O3', '-march=x86-64-v2']

This matches the module's own documented example exactly. The aarch64 floor
(``-march=armv8-a``) is read from the same function and could not be built or
measured on this x86-64 machine; it is taken from the source as authoritative.

Native and cross builds
------------------------

**Native distro builds (Gentoo, Arch, single-machine deployments):** set
``AUTOBAHN_ARCH_TARGET=native`` to get ``-march=native`` - host-CPU-optimized,
host-locked code. This is correct only when the build host is also the run
host. It is opt-in; it is never the default, for any build context (wheels,
local source installs, or cross-compilation) - this was fixed for #1717 and
#1834 (SIGILL crashes from an over-optimized distributed wheel, and a
cross-compiler rejecting ``-march=native`` outright).

**Cross-compilation (Yocto, Buildroot, OpenWrt - e.g. building aarch64 wheels on
an x86-64 host):** two rules, both read directly from
``autobahn/nvx/_compile_args.py``:

* ``-march=native`` is **host-only** and would be **wrong** under
  cross-compilation: it would encode the *build* host's ISA into a binary meant
  for a different *target* host. NVX therefore never defaults to it.
* The target architecture is read with ``sysconfig.get_platform()``, not
  ``platform.machine()``: during a cross-build, ``platform.machine()`` reports
  the *build* host's ``uname`` architecture, while ``sysconfig`` reflects the
  interpreter's configured *target* platform. Confirmed by reading
  ``_get_target_machine()``:

  .. code-block:: python

     def _get_target_machine():
         plat = sysconfig.get_platform().lower()
         ...

  For an architecture the module does not recognise, ``get_compile_args()``
  emits **no** ``-march`` flag at all, and the toolchain's own flags (e.g. a
  Buildroot/Yocto-supplied ``CFLAGS``/``-march``) govern code generation
  instead.

Net effect: a Buildroot/Yocto cross-build gets the cross toolchain's own
baseline, not ``x86-64-v2`` and not ``-march=native``. An integrator who needs a
different baseline sets it via their toolchain's own flags, or via
``AUTOBAHN_ARCH_TARGET``.

.. note::

   This machine cannot perform or measure an actual cross-build (there is no
   second target toolchain here, and the published aarch64 wheels are built
   natively, under QEMU system emulation, which never exercises the cross-build
   code path). The cross-build *behaviour* above is read directly from
   ``_compile_args.py``, which is the same source the project's own
   cross-compilation promise (`#1935
   <https://github.com/crossbario/autobahn-python/issues/1935>`_) is tracked
   against; that issue notes there is, as of this writing, no CI job that
   actually cross-compiles anything, so "works out of the box" for a given
   cross toolchain is a claim backed by this source reading, not by a
   cross-build test.

Runtime selection and fallback
--------------------------------

Whether a given process actually uses NVX is governed by two independent
flags, both exported from ``autobahn.websocket``:

* ``HAS_NVX`` - a **build-time availability** check: were the compiled CFFI
  modules (``_nvx_utf8validator``, ``_nvx_xormasker``) importable at process
  start? This is a plain ``try: import ... except ImportError`` probe.
* ``USES_NVX`` - whether NVX is actually used, after also considering the
  ``AUTOBAHN_USE_NVX`` environment variable: unset or ``1`` uses NVX if
  available (``USES_NVX = HAS_NVX``); ``0`` forces the pure-Python path even
  when NVX is available; requesting ``1`` when NVX was **not** built raises a
  loud ``RuntimeError`` rather than silently falling back.

Verified on this machine, built with NVX:

.. code-block:: console

   $ python -c "from autobahn.websocket import HAS_NVX, USES_NVX; print(HAS_NVX, USES_NVX)"
   True True
   $ AUTOBAHN_USE_NVX=0 python -c "from autobahn.websocket import HAS_NVX, USES_NVX; print(HAS_NVX, USES_NVX)"
   True False

And with the compiled NVX modules removed (simulating a pure-Python install):

.. code-block:: console

   $ python -c "from autobahn.websocket import HAS_NVX, USES_NVX; print(HAS_NVX, USES_NVX)"
   False False
   $ AUTOBAHN_USE_NVX=1 python -c "from autobahn.websocket import HAS_NVX, USES_NVX; print(HAS_NVX, USES_NVX)"
   Traceback (most recent call last):
     ...
   RuntimeError: NVX native acceleration explicitly requested via AUTOBAHN_USE_NVX=1, ...

Both "not built" and "explicitly disabled" fall back to the pure-Python
implementation, which stays fully functional and conformance-tested; a
pure-Python ``Utf8Validator().validate(...)`` call still works correctly on
this machine with both NVX ``.so`` files removed.

.. warning::

   **The one gap worth stating prominently: a v2 wheel on a sub-v2 CPU.**
   ``import _nvx_utf8validator`` *succeeds* purely because the dynamic linker
   can load the object - the SSE4.x code paths inside it only execute once
   ``validate()``/``process()`` is actually called. So on a CPU below the
   ``x86-64-v2`` floor, ``HAS_NVX`` comes back ``True``, ``USES_NVX`` defaults
   to ``True``, and the **first** real NVX call executes an instruction the CPU
   does not have: ``SIGILL``, not a Python exception. The build-availability
   probe is not a CPU-capability probe. The escape hatch is
   ``AUTOBAHN_USE_NVX=0``, which forces the pure-Python path regardless of what
   was built.

   This machine's CPU is above the ``x86-64-v2`` floor (see `Determining a
   machine's capability`_ below), so the ``SIGILL`` itself could not be
   reproduced here - no sub-floor CPU and no CPU-restricted emulator (e.g.
   ``qemu-x86_64 -cpu ...``) was available on this host. The mechanism above is
   read from the source (``HAS_NVX`` is an import-success probe, the compiled
   code's floor is ``x86-64-v2``, below-floor instructions are architecturally
   guaranteed to trap), not executed end-to-end. A proposed runtime ISA-floor
   guard - checking the CPU against the floor before enabling NVX, closing this
   gap - is tracked as a follow-up, not yet implemented; see the FAQ_ below.

Build-side hardening
-----------------------

Since #1856, requesting NVX explicitly during a wheel build
(``AUTOBAHN_USE_NVX=1``) while the CFFI extension **fails to compile** now
aborts the build with a non-zero exit, instead of silently falling back to a
pure-Python (``py3-none-any``) wheel. This means a transient native-compile
failure (the changelog's example: a ``gcc`` SIGSEGV under QEMU ARM64
emulation) fails the CI job, so it can be retried, rather than quietly
uploading a structurally valid but unintended artifact. Building with
``AUTOBAHN_USE_NVX=0`` is unaffected and still produces a pure-Python wheel, by
request rather than by accident. (Source: :doc:`changelog`, 26.11.x entry for
#1856; not independently re-exercised on this machine, which does not run the
release wheel-build workflow.)

Determining a wheel's ISA
----------------------------

``file`` and ``ldd`` cannot tell you a binary's micro-architecture level - they
report the base architecture (e.g. "x86-64") and its dynamic library
dependencies, nothing about which instruction extensions were actually
compiled in.

* The **contract** is ``get_compile_args()`` - the ``-march`` value is the
  *minimum promised* ISA for that build. For the default build on this
  machine, that contract is ``x86-64-v2``.
* ``readelf -n <module>.so`` may show a GNU ISA property note, but often does
  not for a plain ``-march=x86-64-v2`` build without ``-fcf-protection``.
  Verified on this machine: the NVX ``.so`` files built here carry only a
  ``NT_GNU_BUILD_ID`` note, no ISA property note.
* ``objdump -d <module>.so`` lets you check what was actually emitted: grep for
  ``%ymm``/``%zmm`` registers (AVX/AVX-512 presence) and for v2/SSE4.2-era
  mnemonics (``pcmpistri``, ``popcnt``, ``crc32``, ``ptest``, ``pblendvb``,
  ``roundps``/``roundpd``, ``pextrb``/``pinsrb``).
* The issue that prompted this page recommends **elfx86exts** - a small,
  purpose-built, pinned, prebuilt tool (install via ``apt``, not ``cargo``: a
  reproducible ISA gate wants a toolchain-free binary, not a floating Rust
  build) - for exactly this. **This machine has no route to the Debian package
  archive** (only this project's own repository and GitHub are reachable from
  here; general outbound internet, including ``deb.debian.org``, is not), so
  ``elfx86exts`` itself could not be installed or run here. The equivalent
  check was done directly with ``objdump``/``readelf`` instead, on the NVX
  modules built on this machine:

  .. code-block:: console

     $ objdump -d _nvx_utf8validator.cpython-314-x86_64-linux-gnu.so \
         | grep -cE '%ymm|%zmm'
     0
     $ objdump -d _nvx_utf8validator.cpython-314-x86_64-linux-gnu.so \
         | grep -c 'pextrb'
     142
     $ readelf -n _nvx_utf8validator.cpython-314-x86_64-linux-gnu.so
     Displaying notes found in: .note.gnu.build-id
       ...NT_GNU_BUILD_ID...

  Zero ``%ymm``/``%zmm`` references confirms no AVX/AVX-512 code was emitted
  (consistent with the ``x86-64-v2`` contract, which predates AVX). 142
  occurrences of ``pextrb`` (an SSE4.1 instruction, used by the
  ``_nvx_utf8vld_validate_sse4`` code path in ``_utf8validator.c``) confirm the
  highest instruction set actually used is SSE4.1 - comfortably *inside* the
  declared ``x86-64-v2`` (SSE4.2) contract. This is the same distinction the
  issue draws using ``elfx86exts``: the **contract** (what you may rely on,
  here ``x86-64-v2``) is not the same thing as the **emitted floor** (what is
  actually in this particular binary, here SSE4.1) - a binary built to a
  contract is free to use less than the contract allows, never more.

elfx86exts limits
~~~~~~~~~~~~~~~~~~~

An "actual highest instruction found" tool like ``elfx86exts`` (or the
``objdump`` substitute above) reports the **union of instructions present** in
a binary - a static property. For NVX, that union *is* the requirement,
because NVX is built with a **fixed ``-march``, with no runtime CPUID
dispatch**: reading ``_utf8validator.c`` and ``_xormasker.c`` shows the
available implementation (``impl``) is chosen once, from compile-time
``#ifdef __SSE2__`` / ``#ifdef __SSE4_1__`` macros, never at runtime by probing
the CPU. For a **runtime-dispatching** binary - one that bundles several code
paths (say, SSE2 through AVX-512) and picks one per-call based on a CPUID
check - the union of instructions present is *not* the requirement: such a
binary can run correctly on a CPU that only satisfies its lowest bundled path.
Do not apply "highest instruction found = required ISA" to a dispatching
third-party binary; it only holds for a non-dispatching build like NVX's.

Determining a machine's capability
-------------------------------------

* ``grep -m1 '^flags' /proc/cpuinfo`` lists the CPU's supported extensions by
  name. Flag-name mapping for the instructions named above: SSE4.1 →
  ``sse4_1``, SSE4.2 → ``sse4_2``, AVX2 → ``avx2``, AVX-512 (foundation) →
  ``avx512f``, AES-NI → ``aes``, carry-less multiply → ``pclmulqdq``, BMI2 →
  ``bmi2``, ADX → ``adx``.
* ``/lib64/ld-linux-x86-64.so.2 --help`` reports which x86-64 micro-architecture
  levels (v2/v3/v4) the dynamic linker considers this CPU to support.
* **Ground truth:** run a real workload. A CPU missing a required instruction
  faults immediately, with ``SIGILL``, the first time that instruction
  executes - there is no soft failure mode.

Measured on this machine (one x86-64 KVM guest):

.. code-block:: console

   $ grep -m1 '^flags' /proc/cpuinfo | tr ' ' '\n' | grep -E '^(ssse3|sse4_1|sse4_2|popcnt|avx2|aes|pclmulqdq|bmi2|adx)$'
   pclmulqdq
   ssse3
   sse4_1
   sse4_2
   popcnt
   aes
   avx2
   bmi2
   adx
   $ /lib64/ld-linux-x86-64.so.2 --help | grep -i 'x86-64-v'
     x86-64-v4
     x86-64-v3 (supported, searched)
     x86-64-v2 (supported, searched)

This CPU supports **x86-64-v3** (it has AVX2, BMI2, and the rest of the v3
set), comfortably above the published ``x86-64-v2`` wheel floor - which is why
the gap described under `Runtime selection and fallback`_ could not be
reproduced here: there is no way, on this specific machine, to observe the
sub-v2 ``SIGILL`` case first-hand.

Vendored FlatBuffers
------------------------

|ab| also vendors `FlatBuffers <https://flatbuffers.dev/>`_ (schema + ``flatc``
codegen) and exposes it from Python, independently of NVX - this is autobahn's
*other* native/vendoring dimension, with no ISA floor of its own (pure,
portable generated code).

Verified on this machine:

.. code-block:: console

   $ python -c "from autobahn import flatbuffers; print(flatbuffers.__version__)"
   25.12.19

**zlmdb also vendors FlatBuffers**, and the two vendored copies must stay
version-synced: ``autobahn.check_zlmdb_flatbuffers_version_in_sync()`` (see the generated API
reference, and :ref:`memory-footprint`, which uses the same function) compares ``autobahn.flatbuffers.__version__`` against
``zlmdb.flatbuffers.__version__`` and raises if they differ. This matters
because **Crossbar.io depends on both autobahn and zlmdb**; see `Stack
context`_ below. The ``just check-flatbuffers-sync`` recipe runs this check;
on this machine, with zlmdb not installed, it reports:

.. code-block:: console

   $ just check-flatbuffers-sync cpy314
   autobahn FlatBuffers version: (25, 12, 19, None, None)
   zlmdb not installed -> skipping cross-project sync check

zlmdb is a separate repository and was not available to install here, so the
actual cross-project version match could not be checked on this machine; the
check function's behaviour (skip cleanly when zlmdb is absent, raise on a
genuine mismatch when present) is read from ``autobahn/__init__.py``.

Consolidated and corrected
------------------------------

This page folds in and supersedes, for NVX/ISA/native-build purposes, the
relevant sections of ``README.md`` (the "Native vector extensions (NVX)"
section), :doc:`wheels-inventory` (the "NVX Acceleration" and "CPU
Requirements" sections), :doc:`environments/conda` (the "Native Acceleration
(NVX)" section), and the #1856 entry in :doc:`changelog`. Those pages keep
their existing per-topic framing (installation steps, the wheel matrix, Conda
specifics) and now also point here for the ISA-floor and cross-build detail;
this page is the one place that detail is maintained going forward.

One correction was needed in :doc:`release-notes`: the 25.9.1 entry for NVX
(#1697) said NVX is *"Automatically enabled on x86_64 CPUs with AVX2
support."* This is inaccurate on both counts checked above: the actual floor
is ``x86-64-v2`` (SSE4.2-era, well below AVX2/``x86-64-v3``), and enablement is
**import-based** (``HAS_NVX``, a build-availability check), not gated on any
CPU feature at all. That entry has been corrected to describe the floor and
the ``HAS_NVX``/``USES_NVX`` fallback semantics documented on this page.

.. note::

   Two further inconsistencies were found while checking this page's sources
   against existing documentation, and are **not** changed by this page (the
   task this page was written for scopes only the AVX2 correction above) - a
   human should decide whether and how to update them:

   1. :doc:`wheels-inventory`'s "CPU Requirements" section currently states
      "NVX has no special CPU requirement: the C extension is always built,
      and it selects an implementation at run time", and describes the SIMD
      paths as "x86-only (SSE2 and SSE4.1)", compiled in only when the
      toolchain *advertises* ``__SSE2__``/``__SSE4_1__``. That describes a
      toolchain-default (no explicit ``-march``) build. It does not match the
      default build on this machine, and in this repository's
      ``_compile_args.py``: a fixed ``-march=x86-64-v2`` floor, which
      *guarantees* ``__SSE2__`` and ``__SSE4_1__`` are defined, and which is
      the actual carrier of the sub-v2-CPU gap described above. The two
      descriptions are not contradictory in outcome on a v2-or-above CPU, but
      "no special CPU requirement" undersells the floor this page documents.
   2. The same section's enablement list ("NVX is automatically enabled" on
      macOS ARM64 / Windows x86_64 / Windows ARM64 / Linux ARM64, pure Python
      on Linux x86_64) does not mention the ``musllinux`` x86_64 wheels, which
      the wheel-matrix table earlier on the very same page lists as shipping
      *with* NVX.

Compatibility: the ``asgard`` fleet
---------------------------------------

The issue this page is based on describes a worked compatibility example
across a fleet of hosts named ``asgard1`` through ``asgard4``:

.. list-table::
   :header-rows: 1

   * - Node
     - CPU
     - ISA level
     - Pure Python
     - Published NVX wheel
   * - asgard1
     - Xeon D-1587 (Broadwell)
     - x86-64-v3 (AVX2)
     - works
     - accelerated
   * - asgard4
     - Celeron J3455 (Goldmont)
     - x86-64-v2 (SSE4.2, no AVX)
     - works
     - accelerated (floor exactly met)
   * - asgard2 / asgard3
     - Atom D525 (Pineview)
     - below x86-64-v2 (no SSE4.x)
     - works
     - **SIGILL on first NVX call** - set ``AUTOBAHN_USE_NVX=0``

**This machine is not any of the ``asgard`` hosts, and they are not reachable
from here.** This table is reproduced as claimed in the originating issue, not
independently measured; it is consistent with, and a concrete instance of, the
ISA-floor and fallback mechanics verified above on this machine's own CPU and
NVX build.

The punchline it illustrates holds regardless: |ab| has no hard ISA cliff - a
working pure-Python path always exists - unlike a closed native binary
shipped with no fallback. The one sharp edge is the sub-v2-wheel gap described
under `Runtime selection and fallback`_.

Stack context
-----------------

**Crossbar.io depends on both autobahn and zlmdb.** The native/vendoring/cross-
compile story spans all three projects:

* autobahn vendors FlatBuffers and NVX (its own SIMD C, with ``-march``
  floors, as described on this page);
* zlmdb vendors a patched LMDB and FlatBuffers (portable C, with no ISA
  floor);
* Crossbar.io consumes both, and is exposed to the union of both projects'
  native/vendoring behaviour.

The FlatBuffers copies in autobahn and zlmdb must stay version-synced (see
`Vendored FlatBuffers`_ above). **None of zlmdb, crossbar, or the asgard hosts
are installed or reachable from this machine**, so this section is reported as
the issue and the ``autobahn.check_zlmdb_flatbuffers_version_in_sync()``
docstring state it, not independently measured end-to-end here.

.. _FAQ:

FAQ
------

**I'm getting a crash (SIGILL) on an old CPU.**
   Set ``AUTOBAHN_USE_NVX=0`` (or install a build without NVX). See `Runtime
   selection and fallback`_ above for why this happens and what a future
   runtime ISA-floor guard would change.

**Does NVX work on PyPy?**
   Yes. NVX is a CFFI extension, and CFFI's ABI/API modes both work on CPython
   and PyPy; see the published PyPy wheels in :doc:`wheels-inventory`. The
   pure-Python fallback paths also benefit from PyPy's JIT.

See also
-----------

* :doc:`wheels-inventory` - the full wheel matrix, including which platforms
  ship NVX.
* :doc:`environments/conda` - NVX-specific guidance for Conda environments.
* :doc:`release-notes` - the corrected 25.9.1 entry, and the with/without-NVX
  WebSocket conformance results.
* :doc:`changelog` - the detailed #1717 / #1834 / #1835 / #1856 entries this
  page draws on.
* `Issue #1946 <https://github.com/crossbario/autobahn-python/issues/1946>`_ -
  the issue this page was written for.
* `Issue #1935 <https://github.com/crossbario/autobahn-python/issues/1935>`_ -
  the companion issue tracking the cross-compilation *promise* (support-status
  tiers, CI coverage) that this page's "Native and cross builds" section
  reads today's code against.
