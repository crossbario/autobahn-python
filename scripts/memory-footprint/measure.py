#!/usr/bin/env python
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
"""
Measure the memory footprint (peak RSS, ``VmHWM`` from ``/proc/self/status``, Linux)
of importing autobahn and related packages, each in a fresh interpreter.

Run this with the Python of the venv to measure (it uses ``sys.executable`` for the
child processes) - see ``run.sh``, which creates the venvs. The result is written as
JSON to stdout, or to the file given with ``--output``.

Each scenario runs ``--runs`` times in a fresh process (``python -I``, without
``USE_TWISTED`` / ``USE_ASYNCIO`` in the environment), after one discarded warm-up
run (which may compile ``.pyc`` files). The median is reported, in KiB. A scenario whose imports are not installed in the venv
is reported as unavailable.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
from importlib import metadata

# (group, label, code) - the order here is the order of the rows in the docs tables
SCENARIOS = [
    ("interpreter", "bare interpreter", "pass"),
    ("cryptography", "import cryptography", "import cryptography"),
    (
        "cryptography",
        "from cryptography.hazmat.primitives import hashes",
        "from cryptography.hazmat.primitives import hashes",
    ),
    ("numpy", "import numpy", "import numpy"),
    ("asyncio", "import asyncio", "import asyncio"),
    (
        "twisted",
        "from twisted.internet import reactor",
        "from twisted.internet import reactor",
    ),
    ("txaio", "import txaio", "import txaio"),
    ("txaio", "import txaio; txaio.use_asyncio()", "import txaio; txaio.use_asyncio()"),
    ("txaio", "import txaio; txaio.use_twisted()", "import txaio; txaio.use_twisted()"),
    ("autobahn", "import autobahn", "import autobahn"),
    (
        "autobahn",
        "txaio.use_asyncio(); import autobahn.wamp",
        "import txaio; txaio.use_asyncio(); import autobahn.wamp",
    ),
    (
        "autobahn",
        "txaio.use_twisted(); import autobahn.wamp",
        "import txaio; txaio.use_twisted(); import autobahn.wamp",
    ),
    (
        "autobahn",
        "import autobahn.asyncio.websocket",
        "import autobahn.asyncio.websocket",
    ),
    (
        "autobahn",
        "import autobahn.twisted.websocket",
        "import autobahn.twisted.websocket",
    ),
    ("daphne", "from daphne.server import Server", "from daphne.server import Server"),
    (
        "crossbar",
        "from crossbar.edge.worker.router import ExtRouterController",
        "from crossbar.edge.worker.router import ExtRouterController",
    ),
]

# the packages whose versions are recorded with the results
PACKAGES = [
    "autobahn",
    "txaio",
    "twisted",
    "cryptography",
    "numpy",
    "cbor2",
    "daphne",
    "crossbar",
    "zlmdb",
]

# runs in the child: execute the scenario, then report peak RSS and whether numpy
# got loaded; an import error of the scenario itself means "not installed here".
#
# Peak RSS is read as VmHWM from /proc/self/status: the high-water mark of this
# process's own address space, which starts fresh at exec(). getrusage()'s ru_maxrss
# is not usable here: on Linux it carries over the peak of the address space replaced
# by exec(), i.e. of the measuring parent process (this script).
CHILD = """
import json, sys
try:
    exec(sys.argv[1])
except ImportError as e:
    print(json.dumps({"error": f"{type(e).__name__}: {e}"}))
else:
    with open("/proc/self/status") as f:
        hwm = next(int(line.split()[1]) for line in f if line.startswith("VmHWM:"))
    print(json.dumps({"maxrss_kib": hwm, "numpy": "numpy" in sys.modules}))
"""


def run_once(code: str) -> dict:
    env = {
        k: v for k, v in os.environ.items() if k not in ("USE_TWISTED", "USE_ASYNCIO")
    }
    result = subprocess.run(
        [sys.executable, "-I", "-c", CHILD, code],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        return {
            "error": result.stderr.strip().splitlines()[-1]
            if result.stderr
            else "failed"
        }
    return json.loads(result.stdout.strip().splitlines()[-1])


def measure(code: str, runs: int) -> dict:
    first = run_once(code)
    if "error" in first:
        return {"available": False, "error": first["error"]}
    samples = [run_once(code) for _ in range(runs)]
    errors = [s["error"] for s in samples if "error" in s]
    if errors:
        return {"available": False, "error": errors[0]}
    return {
        "available": True,
        "maxrss_kib": int(statistics.median(s["maxrss_kib"] for s in samples)),
        "samples_kib": [s["maxrss_kib"] for s in samples],
        "numpy": any(s["numpy"] for s in samples),
    }


def installed_versions() -> dict:
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            pass
    return versions


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--variant", required=True, help="label of the autobahn variant, e.g. 26.7.1"
    )
    parser.add_argument(
        "--runs", type=int, default=5, help="measured runs per scenario (default: 5)"
    )
    parser.add_argument(
        "--only-group", action="append", help="measure only these groups (repeatable)"
    )
    parser.add_argument(
        "--skip-group", action="append", help="do not measure these groups (repeatable)"
    )
    parser.add_argument("--output", help="write JSON here instead of stdout")
    args = parser.parse_args()

    results = []
    for group, label, code in SCENARIOS:
        if args.only_group and group not in args.only_group:
            continue
        if args.skip_group and group in args.skip_group:
            continue
        result = measure(code, args.runs)
        results.append({"group": group, "label": label, "code": code, **result})
        print(
            f"  {label:60s} {result.get('maxrss_kib', '-')!s:>8} KiB", file=sys.stderr
        )

    report = {
        "variant": args.variant,
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "build": " ".join(sys.version.split()),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "runs": args.runs,
        "packages": installed_versions(),
        "results": results,
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
