#!/usr/bin/env bash
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
#
# Measure the import memory footprint of autobahn for one Python environment, for
# each autobahn variant, in fresh throwaway venvs, and write the results as JSON to
# scripts/memory-footprint/results/<env>-<variant>.json (see docs/memory-footprint.rst).
#
# usage: scripts/memory-footprint/run.sh <env> [<local-label>]
#
#   env          cpy314 | pypy311 (same interpreters as the justfile)
#   local-label  column label for this working tree (default: the current git branch)
#
# Variants measured:
#   25.10.2      last release with FlatBuffers as an optional extra (from PyPI)
#   26.7.1       latest release, with the vendored FlatBuffers runtime (from PyPI)
#   <local>      this working tree
#
# Every venv gets numpy installed (on PyPy numpy<2.5: 2.5 ships no PyPy wheels), so
# the tables show whether autobahn loads it. crossbar is measured in a separate venv
# (crossbar 26.7.1 from PyPI), and not for 25.10.2, which no crossbar release supports.

set -euo pipefail

ENV_NAME="${1:?usage: run.sh <cpy314|pypy311> [<local-label>]}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${HERE}/../.." && pwd)"
LOCAL_LABEL="${2:-$(git -C "${REPO}" rev-parse --abbrev-ref HEAD)}"
RUNS="${MEMORY_FOOTPRINT_RUNS:-5}"
CROSSBAR_VERSION="26.7.1"

case "${ENV_NAME}" in
    cpy314)  PYTHON_SPEC="cpython-3.14"; NUMPY="numpy" ;;
    pypy311) PYTHON_SPEC="pypy-3.11.15"; NUMPY="numpy<2.5" ;;
    *)       echo "unknown env: ${ENV_NAME}" >&2; exit 1 ;;
esac

WORKDIR="$(mktemp -d -t autobahn-memory-footprint-XXXXXX)"
trap 'rm -rf "${WORKDIR}"' EXIT
mkdir -p "${HERE}/results"

measure() {
    # measure <venv> <variant> <output> [measure.py options...]
    local venv="$1" variant="$2" output="$3"
    shift 3
    "${venv}/bin/python" "${HERE}/measure.py" --variant "${variant}" --runs "${RUNS}" \
        "$@" --output "${output}"
}

for variant in 25.10.2 26.7.1 "${LOCAL_LABEL}"; do
    # requirement for autobahn, with the extras crossbar uses: autobahn_req <extras>
    if [ "${variant}" = "${LOCAL_LABEL}" ]; then
        autobahn_req() { echo "${REPO}${1:+[$1]}"; }
    else
        autobahn_req() { echo "autobahn${1:+[$1]}==${variant}"; }
    fi

    echo "==> ${ENV_NAME} / autobahn ${variant}"
    venv="${WORKDIR}/${variant}"
    uv venv -q -p "${PYTHON_SPEC}" "${venv}"
    uv pip install -q -p "${venv}/bin/python" "$(autobahn_req)" "twisted[tls]" cryptography "${NUMPY}" daphne
    measure "${venv}" "${variant}" "${HERE}/results/${ENV_NAME}-${variant}.json" --skip-group crossbar

    if [ "${variant}" != "25.10.2" ]; then
        echo "==> ${ENV_NAME} / autobahn ${variant} / crossbar ${CROSSBAR_VERSION}"
        venv="${WORKDIR}/${variant}-crossbar"
        uv venv -q -p "${PYTHON_SPEC}" "${venv}"
        uv pip install -q -p "${venv}/bin/python" \
            "crossbar==${CROSSBAR_VERSION}" \
            "$(autobahn_req compress,encryption,scram,serialization,twisted)" "${NUMPY}"
        measure "${venv}" "${variant}" "${HERE}/results/${ENV_NAME}-${variant}-crossbar.json" --only-group crossbar
    fi
done

echo "==> results written to ${HERE}/results/${ENV_NAME}-*.json"
