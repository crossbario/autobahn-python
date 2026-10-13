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

# Importing autobahn for WebSocket only - without WAMP, with either Twisted or
# asyncio - must not load the vendored FlatBuffers runtime, nor numpy, which that
# runtime imports at module level whenever numpy is installed. See issue #1983.
#
# Each import runs in a fresh interpreter, since Twisted and asyncio bindings
# cannot share one process. The child sees a fake "numpy" package first on its
# path, so the tests do not depend on whether numpy is installed: the vendored
# runtime finds numpy via importlib.machinery.PathFinder, which finds the fake.

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

WEBSOCKET_ONLY_IMPORTS = [
    "autobahn",
    "autobahn.twisted.websocket",
    "autobahn.asyncio.websocket",
]

# imported by autobahn/flatbuffers/__init__.py only when the runtime really loads
FLATBUFFERS_RUNTIME_MODULE = "autobahn.flatbuffers.builder"

FAKE_NUMPY_OK = "__version__ = '0.0.0'\n"
FAKE_NUMPY_BROKEN = "raise ImportError('simulating a broken numpy install')\n"


def _run_child(code: str, fake_numpy: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, "numpy"))
        with open(os.path.join(tmpdir, "numpy", "__init__.py"), "w") as f:
            f.write(fake_numpy)
        # the child selects its txaio backend itself, as for a user who sets
        # neither USE_TWISTED nor USE_ASYNCIO
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("USE_TWISTED", "USE_ASYNCIO")
        }
        env["PYTHONPATH"] = os.pathsep.join(
            [tmpdir] + [p for p in [os.environ.get("PYTHONPATH")] if p]
        )
        return subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, env=env
        )


def _loaded_after_import(modname: str, fake_numpy: str) -> dict:
    code = (
        "import json, sys\n"
        f"import {modname}\n"
        "print(json.dumps({'numpy': 'numpy' in sys.modules,"
        f" 'flatbuffers': {FLATBUFFERS_RUNTIME_MODULE!r} in sys.modules}}))\n"
    )
    result = _run_child(code, fake_numpy)
    if result.returncode != 0:
        raise AssertionError(f"import {modname} failed:\n{result.stderr}")
    return json.loads(result.stdout.strip().splitlines()[-1])


class TestWebSocketOnlyImports(unittest.TestCase):
    def test_no_flatbuffers_no_numpy(self):
        for modname in WEBSOCKET_ONLY_IMPORTS:
            with self.subTest(modname=modname):
                loaded = _loaded_after_import(modname, FAKE_NUMPY_OK)
                self.assertFalse(
                    loaded["flatbuffers"],
                    f"import {modname} loads the FlatBuffers runtime",
                )
                self.assertFalse(loaded["numpy"], f"import {modname} loads numpy")

    def test_broken_numpy_does_not_break_import(self):
        for modname in WEBSOCKET_ONLY_IMPORTS:
            with self.subTest(modname=modname):
                loaded = _loaded_after_import(modname, FAKE_NUMPY_BROKEN)
                self.assertFalse(loaded["numpy"])


class TestFlatBuffersStillAvailable(unittest.TestCase):
    def test_flatbuffers_serializer_roundtrip(self):
        # after a WebSocket-only import, FlatBuffers still works when used
        code = (
            "import sys, txaio\n"
            "import autobahn.asyncio.websocket\n"
            "from autobahn import flatbuffers\n"
            "from autobahn.wamp.message import Event\n"
            "from autobahn.wamp.serializer import FlatBuffersSerializer\n"
            "assert isinstance(flatbuffers.Builder(0), flatbuffers.Builder)\n"
            "s = FlatBuffersSerializer()\n"
            "data, _ = s.serialize(Event(1, 2, args=[1, 'a'], kwargs={'x': 3}))\n"
            "msg = s.unserialize(data)[0]\n"
            "assert (msg.subscription, msg.publication, msg.args, msg.kwargs) == (1, 2, [1, 'a'], {'x': 3}), msg\n"
            f"assert {FLATBUFFERS_RUNTIME_MODULE!r} in sys.modules\n"
        )
        result = _run_child(code, FAKE_NUMPY_OK)
        self.assertEqual(result.returncode, 0, result.stderr)
