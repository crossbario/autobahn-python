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
Render the results of ``run.sh`` (``results/<env>-*.json``) as reStructuredText
fragments, included by ``docs/memory-footprint.rst``:

- ``docs/memory-footprint/<env>.inc``: the table, one column per autobahn variant
- ``docs/memory-footprint/<env>-versions.inc``: interpreter, platform and package versions

usage: render.py <env> [<env> ...]
"""

from __future__ import annotations

import json
import pathlib
import sys

from measure import PACKAGES, SCENARIOS

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"
DOCS = HERE.parent.parent / "docs" / "memory-footprint"

# released variants first, in this order; any other (local) variant after them
RELEASES = ["25.10.2", "26.7.1"]


def load(env: str) -> tuple[list[str], dict, dict]:
    """
    Returns the variants (column order), the results by (variant, label), and the
    reports (without results) by variant, for the main and the crossbar venv.
    """
    values, reports = {}, {}
    for path in sorted(RESULTS.glob(f"{env}-*.json")):
        report = json.loads(path.read_text())
        variant = report["variant"]
        kind = "crossbar" if path.stem.endswith("-crossbar") else "main"
        reports[(variant, kind)] = report
        for result in report["results"]:
            # never let "not installed in this venv" replace a measured value
            if result.get("available") or (variant, result["label"]) not in values:
                values[(variant, result["label"])] = result
    found = {variant for variant, _ in reports}
    variants = [v for v in RELEASES if v in found] + sorted(found - set(RELEASES))
    return variants, values, reports


def cell(result: dict | None) -> str:
    if not result or not result.get("available"):
        return "n/a"
    text = f"{result['maxrss_kib'] / 1024:.1f} MB"
    return f"{text} †" if result["numpy"] else text


def render_table(env: str, variants: list[str], values: dict) -> str:
    lines = [
        ".. list-table::",
        "   :header-rows: 1",
        "   :widths: 12 46" + " 14" * len(variants),
        "",
        "   * - group",
        "     - import",
    ]
    lines += [f"     - {v}" for v in variants]
    previous_group = None
    for group, label, _ in SCENARIOS:
        if not any((v, label) in values for v in variants):
            continue
        lines.append(f"   * - {group if group != previous_group else ''}".rstrip())
        lines.append(f"     - ``{label}``")
        lines += [f"     - {cell(values.get((v, label)))}" for v in variants]
        previous_group = group
    return "\n".join(lines) + "\n"


def render_versions(variants: list[str], reports: dict) -> str:
    lines = []
    for variant in variants:
        for kind in ("main", "crossbar"):
            report = reports.get((variant, kind))
            if not report:
                continue
            python, plat = report["python"], report["platform"]
            packages = ", ".join(
                f"{name} {report['packages'][name]}"
                for name in PACKAGES
                if name in report["packages"]
            )
            venv = "crossbar venv" if kind == "crossbar" else "venv"
            lines.append(f"* **{variant}** ({venv}): {packages}")
            build = f"{python['implementation']} {python['version']}"
            context = f"{plat['system']} {plat['release']} {plat['machine']}, median of {report['runs']} runs"
    lines += ["", f"Interpreter: ``{build}`` ({python['build']}); {context}."]
    return "\n".join(lines) + "\n"


def main() -> None:
    envs = sys.argv[1:]
    if not envs:
        sys.exit(__doc__)
    DOCS.mkdir(parents=True, exist_ok=True)
    for env in envs:
        variants, values, reports = load(env)
        if not variants:
            sys.exit(f"no results for {env} in {RESULTS}")
        (DOCS / f"{env}.inc").write_text(render_table(env, variants, values))
        (DOCS / f"{env}-versions.inc").write_text(render_versions(variants, reports))
        print(f"wrote {DOCS / f'{env}.inc'} and {DOCS / f'{env}-versions.inc'}")


if __name__ == "__main__":
    main()
