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

# Issues #1952 / #1965: starting a component or an ApplicationRunner from plain synchronous
# code, with no event loop created beforehand. Python 3.12 / 3.13 deprecate the implicit loop
# creation of asyncio.get_event_loop() (DeprecationWarning), and Python 3.14 removes it
# (RuntimeError: There is no current event loop).
#
# Each case runs in a FRESH interpreter: inside the test process an earlier test may have
# left an event loop set for the main thread, which hides exactly this bug (it did - the
# full suite passed on CPython 3.14 while the bug was there). DeprecationWarning is turned
# into an error, so 3.12 / 3.13 cover the same code path 3.14 breaks on.
#
# No router is needed: the transport points at a closed port, so the connection fails
# at once, and run() / ApplicationRunner.run() must return normally afterwards.

from __future__ import annotations

import os
import subprocess
import sys

import pytest

COMPONENT_RUN = """
from autobahn.asyncio.component import Component, run

component = Component(
    transports=[{"type": "websocket", "url": "ws://127.0.0.1:9/ws", "max_retries": 0}],
    realm="realm1",
)
run([component], log_level="critical")
print("RUN RETURNED")
"""

APPLICATION_RUNNER = """
from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession

try:
    ApplicationRunner("ws://127.0.0.1:9/ws", "realm1").run(ApplicationSession)
except OSError:
    pass  # connection refused: expected, there is no router
print("RUN RETURNED")
"""

PRESET_LOOP = """
import asyncio
from autobahn.asyncio.component import Component, run

mine = asyncio.new_event_loop()
asyncio.set_event_loop(mine)
used = []
component = Component(
    transports=[{"type": "websocket", "url": "ws://127.0.0.1:9/ws", "max_retries": 0}],
    realm="realm1",
)

@component.on_connectfailure
def _(comp, err):
    used.append(asyncio.get_running_loop())

run([component], log_level="critical")
assert used and used[0] is mine, "run() did not use the loop set beforehand"
print("RUN RETURNED")
"""


@pytest.mark.parametrize(
    "code",
    [COMPONENT_RUN, APPLICATION_RUNNER, PRESET_LOOP],
    ids=["component-run", "application-runner", "preset-loop"],
)
def test_run_from_sync_code(code):
    # the child selects its txaio backend itself (autobahn.asyncio does); an inherited
    # USE_TWISTED / USE_ASYNCIO from the test run must not decide it
    env = {
        k: v for k, v in os.environ.items() if k not in ("USE_TWISTED", "USE_ASYNCIO")
    }
    result = subprocess.run(
        [sys.executable, "-W", "error::DeprecationWarning", "-c", code],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "RUN RETURNED" in result.stdout, result.stdout + result.stderr
