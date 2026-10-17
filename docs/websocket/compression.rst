WebSocket Compression
=====================

Autobahn|Python implements WebSocket per-message compression (`RFC 7692
<https://www.rfc-editor.org/rfc/rfc7692.html>`__) with four compression
extensions. Only ``permessage-deflate`` is standardized; the other three are
Autobahn|Python specific, and both peers must be Autobahn|Python (or another
implementation of the same extension) to use them.

The compression itself is done by a library for each extension, which is
either part of Python or a separate package. This page lists which library,
in which version, each extension uses, on CPython and on PyPy.

Extensions and Libraries
------------------------

.. list-table::
   :header-rows: 1
   :widths: 16 14 30 40

   * - Extension
     - Installed by
     - Python package
     - Compression library used
   * - ``permessage-deflate``
     - always available
     - ``zlib`` (Python standard library)
     - `zlib <https://zlib.net/>`__ - the zlib the Python interpreter was built with
   * - ``permessage-bzip2``
     - always available [1]_
     - ``bz2`` (Python standard library)
     - `bzip2 <https://sourceware.org/bzip2/>`__ (libbz2) - the libbz2 the Python interpreter was built with
   * - ``permessage-brotli``
     - ``compress`` extra
     - CPython: `brotli <https://pypi.org/project/Brotli/>`__ ``>= 1.2.0``
       (C extension, from the `google/brotli <https://github.com/google/brotli>`__
       repository itself)

       PyPy: `brotlicffi <https://pypi.org/project/brotlicffi/>`__ ``>= 1.2.0``
       (CFFI, `python-hyper/brotlicffi <https://github.com/python-hyper/brotlicffi>`__)
     - `google/brotli <https://github.com/google/brotli>`__ (libbrotli), bundled
       in the package: brotli 1.2.0, brotlicffi 1.2.0.0 and brotlicffi 1.2.0.2
       all bundle libbrotli **1.2.0**
   * - ``permessage-snappy``
     - installed separately (``pip install python-snappy``)
     - `python-snappy <https://pypi.org/project/python-snappy/>`__ (tested with
       0.7.3), a pure Python package on top of
       `cramjam <https://github.com/milesgranger/pyrus-cramjam>`__ (Rust, PyO3)
     - The Rust `snap <https://github.com/BurntSushi/rust-snappy>`__ crate, an
       independent implementation of the Snappy format, bundled in cramjam
       (cramjam 2.14.0 bundles snap **1.1.1**). **Not** `google/snappy
       <https://github.com/google/snappy>`__ (libsnappy).

.. [1] Unless the Python interpreter was built without ``bz2``; the extension
   is then not available.

Notes:

* ``brotli`` ``>= 1.2.0`` / ``brotlicffi`` ``>= 1.2.0`` is required: older
  versions lack ``Decompressor.process(output_buffer_limit=...)``, which
  ``permessage-brotli`` needs to bound decompression (see below).
* Before version 0.7, python-snappy was a C extension linking google/snappy
  (libsnappy). Autobahn|Python is tested with python-snappy 0.7.3 only.
* python-snappy declares no minimum version for cramjam.
* On PyPy, cramjam (a PyO3 extension) runs through PyPy's emulation of the
  CPython C API (cpyext), unlike brotlicffi, which uses CFFI.
* python-snappy is not part of the ``compress`` extra; install it yourself
  where you need ``permessage-snappy``.
* zlib and libbz2 come with the Python interpreter, so their version depends
  on how it was built - not on Autobahn|Python. For zlib, check with

  .. code-block:: python

     import zlib
     print(zlib.ZLIB_RUNTIME_VERSION)

  For example, the PyPy 3.11 Linux binaries that ``uv`` installs ship their
  own ``libz.so.1``.

To list the compression extensions available in an environment:

.. code-block:: python

   from autobahn.websocket.compress import PERMESSAGE_COMPRESSION_EXTENSION

   print(sorted(PERMESSAGE_COMPRESSION_EXTENSION))

In a development checkout, ``just check-compressors <venv>`` does the same
and fails unless all four are available; CI runs it on every supported
Python.

Context Takeover
----------------

With context takeover (the default), a compressor keeps its state from one
message to the next, so later messages can refer back to earlier ones.

* ``permessage-deflate`` takes over context as negotiated
  (``client_no_context_takeover`` / ``server_no_context_takeover``).
* ``permessage-snappy`` negotiates the same parameters. The Snappy framing
  format has no back-references across chunks, so context takeover makes no
  difference to the compression ratio.
* ``permessage-bzip2`` and ``permessage-brotli`` never take over context:
  each message is one complete bzip2 or brotli stream. ``permessage-brotli``
  still negotiates the parameters.

Decompression Limits and Invalid Data
-------------------------------------

``maxMessagePayloadSize`` (see :doc:`programming`) bounds the size of a
message *after* decompression. All four extensions decompress incrementally
and stop once the remaining budget of the message is exceeded, rather than
decompressing a whole frame first:

* ``permessage-deflate`` and ``permessage-bzip2`` stop one octet over the
  budget,
* ``permessage-brotli`` stops within one output buffer of the budget,
* ``permessage-snappy`` stops within one Snappy chunk (at most 64 KiB) of
  the budget.

A message over the limit fails the connection with close code 1009 (message
too big).

Data an extension cannot decompress - corrupt, truncated, or not in the
extension's format - raises ``autobahn.exception.PayloadCorruptError`` and
fails the connection with close code 1007 (invalid frame payload data). This
is the same for all four extensions, on both Twisted and asyncio.

Without a limit (``maxMessagePayloadSize = 0``, the default), a small
compressed message can decompress to a very large one. Set a limit when
accepting compressed messages from peers you do not trust.

Example
-------

A complete example is in the repository:
`examples/twisted/websocket/echo_compressed
<https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_compressed>`__.
