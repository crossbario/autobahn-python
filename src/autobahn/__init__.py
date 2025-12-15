###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from autobahn._version import __version__

version = __version__

import os

import txaio

from autobahn import flatbuffers


def check_zlmdb_flatbuffers_version_in_sync() -> tuple[int, int, int, int | None, str | None]:
    """
    Check that autobahn and zlmdb have the same vendored flatbuffers version.

    This is important for applications like Crossbar.io that use both autobahn
    (for data-in-transit) and zlmdb (for data-at-rest) with FlatBuffers
    serialization. When sending a FlatBuffers database record as a WAMP
    application payload, both libraries must use compatible FlatBuffers
    runtimes to avoid subtle serialization issues.

    :returns: The flatbuffers version tuple (e.g. (25, 9, 23, 2, "95053e6a"))
              if both are in sync.
    :raises RuntimeError: If the versions differ.
    :raises ImportError: If zlmdb is not installed.

    Example::

        import autobahn
        version = autobahn.check_zlmdb_flatbuffers_version_in_sync()
        print(f"FlatBuffers version: {version}")
    """
    import zlmdb.flatbuffers

    autobahn_version = flatbuffers.version()
    zlmdb_version = zlmdb.flatbuffers.version()

    if autobahn_version != zlmdb_version:
        raise RuntimeError(
            f"FlatBuffers version mismatch: autobahn has {autobahn_version!r}, "
            f"zlmdb has {zlmdb_version!r}. Both should be the same for "
            f"reliable data-in-transit/data-at-rest interoperability."
        )

    return autobahn_version

# this is used in the unit tests (trial/pytest), and when already done here, there
# is no risk and headaches with finding out if/where an import implies a framework
if os.environ.get("USE_TWISTED", False) and os.environ.get("USE_ASYNCIO", False):
    raise RuntimeError("fatal: _both_ USE_TWISTED and USE_ASYNCIO are set!")

if os.environ.get("USE_TWISTED", False):
    txaio.use_twisted()
elif os.environ.get("USE_ASYNCIO", False):
    txaio.use_asyncio()
else:
    # neither USE_TWISTED nor USE_ASYNCIO selected from env var
    pass
