"""
Cross-version CBOR equivalence & provenance guard.

autobahn-python deliberately runs two different cbor2 implementations depending
on the Python runtime (see the cbor2 dependency markers in ``pyproject.toml``):

- **CPython** uses the current cbor2 6.x line (Rust/pyo3).
- **PyPy** is pinned to cbor2 ``5.9.0`` -- the final *pure-Python* release -- and
  is deliberately kept out of the native-extension matrix.

For the WAMP wire protocol this is only safe if both implementations encode and
decode CBOR *byte-for-byte identically*. These tests turn that requirement into
an assertion that runs on BOTH runtimes in CI (the ``test-serdes`` matrix covers
``cpy311``/``cpy315`` and ``pypy311``):

1. ``test_cbor2_version_matches_runtime`` -- a provenance guard: fail loudly if the
   installed cbor2 is not the version the dependency markers intend for this
   runtime. This makes a resolver regression (e.g. PyPy silently getting 6.x, or
   CPython dropping to 5.x) a hard error rather than a silent behaviour change.
2. ``test_all_basic_vectors_have_cbor`` -- ensure every canonical WAMP message
   vector carries a ``cbor`` encoding, so the equivalence check below can never be
   silently skipped for a message type.
3. ``test_cbor_canonical_bytes_roundtrip`` -- for every canonical CBOR vector in the
   wamp-proto testsuite, assert ``cbor2.dumps(cbor2.loads(golden)) == golden``. On
   CPython this proves 6.x is byte-faithful to the canonical bytes; on PyPy it
   proves 5.9.0 is. Green on both legs ==> the two versions are wire-equivalent.
"""

import glob
import os
import sys
import importlib.metadata as importlib_metadata

import pytest

import cbor2

from .utils import get_wamp_proto_path, bytes_from_hex

IS_PYPY = hasattr(sys, "pypy_version_info")

# The exact cbor2 version pinned for PyPy (the final pure-Python release). Keep
# this in lock-step with the ``cbor2==...`` PyPy marker in pyproject.toml.
PYPY_CBOR2_VERSION = "5.9.0"


def _installed_cbor2_version() -> str:
    return importlib_metadata.version("cbor2")


def _all_cbor_vectors():
    """Yield (label, golden_bytes) for every canonical CBOR vector in the testsuite."""
    testsuite = get_wamp_proto_path() / "testsuite" / "singlemessage"
    for path in sorted(glob.glob(str(testsuite / "*" / "*.json"))):
        import json

        with open(path) as f:
            doc = json.load(f)
        name = os.path.basename(path)
        for si, sample in enumerate(doc.get("samples", [])):
            for vi, variant in enumerate(sample.get("serializers", {}).get("cbor", [])):
                if "bytes_hex" in variant:
                    yield (
                        f"{name}[sample={si},variant={vi}]",
                        bytes_from_hex(variant["bytes_hex"]),
                    )


_CBOR_VECTORS = list(_all_cbor_vectors())


def test_cbor2_version_matches_runtime():
    """Provenance guard: the installed cbor2 must match what the markers intend."""
    version = _installed_cbor2_version()
    major = int(version.split(".")[0])

    if IS_PYPY:
        assert version == PYPY_CBOR2_VERSION, (
            f"On PyPy, cbor2 must be exactly {PYPY_CBOR2_VERSION} (the final pure-Python "
            f"release, deliberately kept out of the native-extension matrix), but "
            f"{version} is installed. If the pin in pyproject.toml changed, update "
            f"PYPY_CBOR2_VERSION here to match."
        )
    else:
        assert major >= 6, (
            f"On CPython, cbor2 must be >=6.1.0 (the current line with binary wheels), "
            f"but {version} is installed."
        )


def test_all_basic_vectors_have_cbor():
    """Every canonical WAMP message vector must carry a `cbor` encoding.

    This guarantees the byte-fidelity check below is never silently skipped for a
    message type (a serializer absent from a vector is otherwise pytest.skip'd).
    """
    import json

    basic = get_wamp_proto_path() / "testsuite" / "singlemessage" / "basic"
    missing = []
    for path in sorted(glob.glob(str(basic / "*.json"))):
        with open(path) as f:
            doc = json.load(f)
        for sample in doc.get("samples", []):
            serializers = sample.get("serializers")
            if serializers is not None and "cbor" not in serializers:
                missing.append(os.path.basename(path))
                break
    assert not missing, f"basic vectors missing a `cbor` encoding: {missing}"


@pytest.mark.parametrize(
    "golden", [v[1] for v in _CBOR_VECTORS], ids=[v[0] for v in _CBOR_VECTORS]
)
def test_cbor_canonical_bytes_roundtrip(golden):
    """The installed cbor2 must reproduce the canonical CBOR bytes exactly.

    Run on both CPython (6.x) and PyPy (5.9.0) in CI, this proves the two cbor2
    versions are wire-equivalent against the shared wamp-proto canonical vectors.
    """
    obj = cbor2.loads(golden)
    reencoded = cbor2.dumps(obj)
    assert reencoded == golden, (
        f"cbor2 {_installed_cbor2_version()} did not reproduce the canonical CBOR bytes:\n"
        f"  golden = {golden.hex()}\n"
        f"  got    = {reencoded.hex()}"
    )
