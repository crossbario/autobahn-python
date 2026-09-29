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

# Import smoke test for the framework-agnostic core modules.
#
# This guards against import-time regressions that only surface on some Python
# versions - in particular eager evaluation of annotations on CPython < 3.14
# (PEP 649 defers it on 3.14): a string forward-reference combined with
# ``| None`` (e.g. ``"ISecurityModule" | None``) raises ``TypeError`` at
# class-definition time. See issue #1878.
#
# We import an explicit, curated set rather than walking every submodule: a full
# single-process walk is unreliable for autobahn because (a) Twisted and asyncio
# bindings are mutually exclusive in one process (txaio backend selection) and
# (b) several modules require optional extras (snappy, flatbuffers runtime).
# These core modules are framework-agnostic and must always import with the
# crypto extras installed.
#
# IMPORTANT: run with crypto extras (``autobahn[all]`` / ``[encryption]`` ->
# PyNaCl) so the ``autobahn.wamp.cryptosign`` ``HAS_CRYPTOSIGN`` code paths
# (where #1878 lived) are actually exercised - see ``test_crypto_extras_present``.

from __future__ import annotations

import importlib
import os
import subprocess
import sys

import pytest

CORE_MODULES = [
    "autobahn",
    "autobahn.util",
    "autobahn.wamp",
    "autobahn.wamp.cryptosign",  # regressed in 26.6.1 -> see #1878
    "autobahn.wamp.auth",
    "autobahn.wamp.interfaces",
    "autobahn.wamp.types",
    "autobahn.wamp.message",
    "autobahn.wamp.role",
    "autobahn.wamp.serializer",
    "autobahn.wamp.component",
    "autobahn.websocket.protocol",
    "autobahn.websocket.types",
    "autobahn.websocket.compress",
]


@pytest.mark.parametrize("modname", CORE_MODULES)
def test_import(modname):
    """
    Importing each core autobahn module must not raise.
    """
    importlib.import_module(modname)


# Framework bindings. Each module is imported in a fresh interpreter, since
# Twisted and asyncio bindings cannot share one process: txaio's use_twisted()
# and use_asyncio() are mutually exclusive per interpreter. The Twisted modules
# annotate with zope.interface ``InterfaceClass`` unions, which only support
# ``|`` from zope.interface 6.2 on - see issue #1955.
TWISTED_MODULES = [
    "autobahn.twisted",
    "autobahn.twisted.util",  # regressed with zope.interface < 6.2 -> see #1955
    "autobahn.twisted.wamp",  # regressed with zope.interface < 6.2 -> see #1955
    "autobahn.twisted.websocket",
    "autobahn.twisted.rawsocket",
    "autobahn.twisted.component",
    "autobahn.twisted.cryptosign",
    "autobahn.twisted.resource",
    "autobahn.twisted.forwarder",
    "autobahn.twisted.choosereactor",
    "autobahn.twisted.testing",
]

ASYNCIO_MODULES = [
    "autobahn.asyncio",
    "autobahn.asyncio.util",
    "autobahn.asyncio.wamp",
    "autobahn.asyncio.websocket",
    "autobahn.asyncio.rawsocket",
    "autobahn.asyncio.component",
]


@pytest.mark.parametrize(
    "modname,framework",
    [(m, "twisted") for m in TWISTED_MODULES]
    + [(m, "asyncio") for m in ASYNCIO_MODULES],
)
def test_import_framework(modname, framework):
    """
    Each binding module imports in a fresh interpreter and selects its txaio backend.
    """
    # autobahn/__init__.py selects the txaio backend from USE_TWISTED / USE_ASYNCIO
    # at import, and the test runs set one of them (the asyncio run sets
    # USE_ASYNCIO=1), which a child process would inherit. The child gets neither:
    # the module must select its backend itself, as it does for a user who sets no
    # such variable.
    env = {
        k: v for k, v in os.environ.items() if k not in ("USE_TWISTED", "USE_ASYNCIO")
    }
    code = (
        f"import txaio, {modname}; "
        f"assert txaio.using_{framework}, 'txaio backend is not {framework}'"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env
    )
    assert result.returncode == 0, result.stderr


def test_crypto_extras_present():
    """
    The cryptosign import guard is only meaningful when PyNaCl is installed,
    since the ``autobahn.wamp.cryptosign`` class bodies (and thus the #1878
    regression) are gated behind ``HAS_CRYPTOSIGN``.
    """
    import autobahn.wamp.cryptosign as cryptosign

    assert (
        cryptosign.HAS_CRYPTOSIGN
    ), "install crypto extras (autobahn[all] / [encryption]) so this import guard is exercised"
