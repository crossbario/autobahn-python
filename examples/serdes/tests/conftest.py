"""
Pytest configuration and fixtures for WAMP serdes tests
"""

import pytest
import txaio

# Initialize txaio framework BEFORE importing autobahn (required for serializers)
txaio.use_asyncio()

from autobahn.wamp.serializer import create_transport_serializer, SERID_TO_OBJSER
from .utils import load_test_vector, get_serializer_ids


# The WAMP "ubjson" serializer is now backed by bjdata (autobahn #1849). Every
# test in this conformance suite is built on the wamp-proto canonical byte vectors
# (serialize-to / deserialize-from / cross-serializer all reference the stored
# ``bytes_hex``). bjdata's octet-level encoding intentionally differs from the
# legacy UBJSON bytes in those vectors, so "ubjson" is excluded from the byte-vector
# conformance suite until the wamp-proto UBJSON vectors are regenerated (a follow-up
# wamp-proto PR after the next autobahn-python release). bjdata round-trip
# correctness is covered by src/autobahn/wamp/test/test_wamp_serializer.py.
_VECTOR_EXCLUDED_SERIALIZERS = ("ubjson",)


def _conformance_serializer_ids():
    return [s for s in get_serializer_ids() if s not in _VECTOR_EXCLUDED_SERIALIZERS]


@pytest.fixture(scope="session")
def wamp_test_vector_publish():
    """Load PUBLISH test vector"""
    return load_test_vector("singlemessage/basic/publish.json")


@pytest.fixture(scope="session")
def wamp_test_vector_event():
    """Load EVENT test vector"""
    return load_test_vector("singlemessage/basic/event.json")


@pytest.fixture(scope="session")
def all_serializer_ids():
    """Get all available WAMP serializer IDs"""
    return get_serializer_ids()


@pytest.fixture
def create_serializer():
    """Factory fixture to create serializers by ID"""

    def _create(serializer_id: str):
        return create_transport_serializer(serializer_id)

    return _create


# Parameterization helpers
def pytest_generate_tests(metafunc):
    """
    Custom test parameterization for serializer tests.

    This generates test parameters for serializer_id based on available serializers.
    """
    if "serializer_id" in metafunc.fixturenames:
        serializer_ids = _conformance_serializer_ids()
        metafunc.parametrize("serializer_id", serializer_ids)

    if "serializer_pair" in metafunc.fixturenames:
        # Generate all unique pairs of serializers for cross-serializer tests
        serializer_ids = _conformance_serializer_ids()
        pairs = []
        for i, ser1 in enumerate(serializer_ids):
            for ser2 in serializer_ids[i + 1 :]:
                pairs.append((ser1, ser2))
        metafunc.parametrize("serializer_pair", pairs)
