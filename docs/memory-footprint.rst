.. _memory-footprint:

Memory Footprint
================

This page shows how much memory a Python process uses after importing autobahn,
compared with the frameworks and libraries it builds on, for CPython and PyPy. It
helps to see what a given use of autobahn costs, and it documents how that cost
changed across releases.

Background
----------

Since 25.12.1, autobahn includes its own copy of the
`FlatBuffers <https://flatbuffers.dev/>`_ runtime, which it needs for WAMP
FlatBuffers serialization (before that, ``flatbuffers`` was an optional dependency,
the ``serialization`` extra). That runtime imports **numpy** at module level whenever
numpy is installed. Up to 26.7.1, autobahn imported the runtime eagerly, so every
process that imported autobahn also loaded numpy - including processes that use
only WebSocket, not WAMP, such as Django Channels applications served by
`Daphne`_ [#fn-daphne]_. See `issue #1983 <https://github.com/crossbario/autobahn-python/issues/1983>`_.

Since then, the goals are:

1. The autobahn package, and the wheels we build, include the vendored FlatBuffers
   runtime, including reflection.
2. For an application that depends on both autobahn and zlmdb, both of which vendor
   FlatBuffers, such as Crossbar.io, the two vendored versions are exactly the same:
   :func:`autobahn.check_zlmdb_flatbuffers_version_in_sync` checks that.
3. A user of autobahn who uses **WebSocket only, not WAMP**, with either Twisted or
   asyncio, loads no FlatBuffers code and no numpy.

autobahn now loads the FlatBuffers runtime only when a FlatBuffers message is first
built or parsed.

What is measured
----------------

Each row is one import, run in a fresh interpreter. The value is the peak resident
set size of that process right after the import, in MB (MiB): ``VmHWM`` from
``/proc/self/status`` on Linux. It is the memory the import costs at least, not the
memory a running application uses under load.

(``ru_maxrss`` from :func:`resource.getrusage` would be the obvious choice, but on
Linux it carries over the peak memory of the process that started the measured one,
so for a child of a Python process it never drops below that parent's size.)

* Every venv has numpy installed, so the tables show whether an import loads it.
  A value marked **†** means numpy was loaded by that import.
* Each import runs once as a warm-up (which may compile ``.pyc`` files) and is then
  measured 5 times; the table shows the median.
* Each autobahn version is measured in its own fresh venv, together with Twisted,
  cryptography, numpy and Daphne. The rows that do not involve autobahn are measured
  in every venv, so their spread across the columns shows the measurement noise.
* Crossbar.io [#fn-crossbar]_ is measured in a separate venv per autobahn version, with
  crossbar |crossbar_version| from PyPI. No crossbar release supports autobahn 25.10.2,
  hence "n/a".
* Columns: **25.10.2** is the last release with FlatBuffers as an optional
  dependency, measured *without* that extra (as Daphne installs it). **26.7.1** is the
  last release that loaded the FlatBuffers runtime on import. **26.10.1** loads it on
  first use (#1983).

.. |crossbar_version| replace:: 26.7.1

CPython 3.14
------------

.. include:: memory-footprint/cpy314.inc

.. include:: memory-footprint/cpy314-versions.inc

PyPy 3.11
---------

PyPy is a different runtime (a tracing JIT compiler with its own garbage collector),
so compare these values with each other, not with the CPython table. On PyPy, the
venvs use numpy 2.4.x, the last numpy release with PyPy wheels.

.. include:: memory-footprint/pypy311.inc

.. include:: memory-footprint/pypy311-versions.inc

Findings
--------

* **26.10.1:** every row that imports autobahn drops by about 13-17 MB on
  CPython, and by about 18-24 MB on PyPy, and none of them loads numpy any more. For
  example, ``from daphne.server import Server`` drops from 64.8 MB to 51.8 MB on CPython
  3.14, and ``import autobahn`` alone is back to the size of the bare interpreter.
* **Compared with 25.10.2:** the WebSocket and WAMP rows remain about 1.2-1.6 MB above
  25.10.2 on CPython (about 0.5-0.6 MB on PyPy). In 25.10.2 without the ``serialization``
  extra, cbor2 was not installed and the WAMP message module skipped that import. Since
  26.x, cbor2 is a regular dependency.
* **WebSocket only:** with Twisted, most of what remains is Twisted itself; with
  asyncio, the asyncio standard library.
* **Twisted and cryptography:** ``import autobahn.twisted.websocket`` still loads the
  native ``cryptography`` bindings (about 8 MB on CPython), because
  ``autobahn/twisted/__init__.py`` imports ``autobahn.twisted.wamp``, which imports
  ``autobahn.wamp.auth``. A pure WebSocket user does not need them. ``import cryptography``
  alone costs next to nothing; the cost comes with the native bindings
  (``from cryptography.hazmat.primitives import hashes``).
* **WAMP:** WAMP users still load the FlatBuffers runtime (and numpy, if installed)
  as soon as they import ``autobahn.wamp.serializer``, also when they use another
  serializer.
* **Crossbar.io** loads numpy itself, so its router worker loads it regardless of
  this change; on CPython, its footprint is unchanged. On PyPy, the crossbar row comes
  out about 16 MB lower with this change, in repeated measurements, but we have not
  analysed why. Two things to keep in mind: on PyPy, the samples of a single import
  can spread by about 10 MB from run to run (garbage collection and JIT timing), and
  the two crossbar venvs differ in more than autobahn: on PyPy, autobahn 26.7.1 installs
  cbor2 6.x, while the development version installs cbor2 5.9.0 (see the versions
  below the PyPy table).

Reproducing
-----------

The scripts are in `scripts/memory-footprint/
<https://github.com/crossbario/autobahn-python/tree/master/scripts/memory-footprint>`_.
They create throwaway venvs with `uv <https://docs.astral.sh/uv/>`_, measure, and
regenerate the tables on this page:

.. code-block:: console

    just memory-footprint cpy314
    just memory-footprint pypy311

``measure.py`` alone measures the venv it runs in, e.g. for your own environment:

.. code-block:: console

    python scripts/memory-footprint/measure.py --variant mine

.. rubric:: Footnotes

.. [#fn-daphne] `Daphne <https://pypi.org/project/daphne/>`_
   (`repository <https://github.com/django/daphne>`_), the ASGI server of Django
   Channels. Its `server <https://github.com/django/daphne/blob/main/daphne/server.py>`_
   and `WebSocket protocol <https://github.com/django/daphne/blob/main/daphne/ws_protocol.py>`_
   use ``autobahn.twisted.websocket``. Row: ``from daphne.server import Server``.

.. [#fn-crossbar] `Crossbar.io <https://github.com/crossbario/crossbar>`_, the WAMP
   router. Row: ``from crossbar.edge.worker.router import ExtRouterController``, the
   `router worker <https://github.com/crossbario/crossbar/blob/master/src/crossbar/edge/worker/router.py>`_.

.. _Daphne: https://github.com/django/daphne
