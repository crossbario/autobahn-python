"""
WAMP WELCOME Message SerDes Tests

Tests WELCOME message serialization and deserialization:
1. Single-serializer roundtrip correctness

WELCOME is sent by a Router to accept a Client. The WAMP session is now open.

Uses test vectors from: wamp-proto/testsuite/singlemessage/basic/welcome.json
"""

import pytest
from autobahn.wamp.message import Welcome
from autobahn.wamp.serializer import create_transport_serializer
from autobahn.wamp.role import RoleBrokerFeatures, RoleDealerFeatures

from .utils import (
    load_test_vector,
    bytes_from_hex,
    matches_any_byte_representation,
)


# =============================================================================
# Test Vector Loading
# =============================================================================


@pytest.fixture(scope="module")
def welcome_test_vector():
    """Load WELCOME test vector from wamp-proto"""
    return load_test_vector("singlemessage/basic/welcome.json")


@pytest.fixture(scope="module")
def welcome_samples(welcome_test_vector):
    """Extract serialization samples from WELCOME test vector"""
    return [s for s in welcome_test_vector["samples"] if "serializers" in s]


# =============================================================================
# Helper Functions
# =============================================================================


def _convert_roles_dict_to_objects(roles_dict):
    """
    Convert a plain dict of roles to Role objects.

    The test vectors use plain dicts like {"broker": {}, "dealer": {}}
    but the Welcome message constructor requires Role objects.
    """
    role_map = {
        "broker": RoleBrokerFeatures,
        "dealer": RoleDealerFeatures,
    }

    roles = {}
    for role_name, role_features in roles_dict.items():
        if role_name in role_map:
            roles[role_name] = role_map[role_name]()

    return roles


# =============================================================================
# SerDes Tests
# =============================================================================


def test_welcome_deserialize_from_bytes(
    serializer_id, welcome_samples, create_serializer
):
    """
    Test WELCOME deserialization from canonical bytes.

    For each serializer:
    1. Take canonical bytes from test vector
    2. Deserialize to message object
    3. Validate message attributes
    """
    serializer = create_serializer(serializer_id)

    for sample in welcome_samples:
        # Skip if this serializer is not in the test vector
        if serializer_id not in sample["serializers"]:
            pytest.skip(f"Serializer {serializer_id} not in test vector")

        # Get byte representations for this serializer
        byte_variants = sample["serializers"][serializer_id]

        # Try deserializing each byte variant
        for variant in byte_variants:
            # Get bytes
            if "bytes_hex" in variant:
                test_bytes = bytes_from_hex(variant["bytes_hex"])
            elif "bytes" in variant:
                test_bytes = variant["bytes"].encode("utf-8")
            else:
                continue

            # Deserialize
            msg = serializer.unserialize(test_bytes)[0]

            # Basic validations
            assert isinstance(msg, Welcome)
            assert msg.session == sample["expected_attributes"]["session_id"]
            assert msg.roles is not None


def test_welcome_serialize_to_bytes(serializer_id, welcome_samples, create_serializer):
    """
    Test WELCOME serialization to bytes.

    For each serializer:
    1. Construct message object from test vector attributes
    2. Serialize to bytes
    3. Verify bytes match one of the valid representations
    """
    serializer = create_serializer(serializer_id)

    for sample in welcome_samples:
        # Skip if this serializer is not in the test vector
        if serializer_id not in sample["serializers"]:
            pytest.skip(f"Serializer {serializer_id} not in test vector")

        # Construct message
        attrs = sample["expected_attributes"]
        msg = Welcome(
            session=attrs["session_id"],
            roles=_convert_roles_dict_to_objects(attrs["roles"]),
        )

        # Serialize
        serialized_bytes, is_binary = serializer.serialize(msg)

        # Verify it matches at least one valid byte representation
        assert matches_any_byte_representation(
            serialized_bytes, sample["serializers"][serializer_id]
        ), f"Serialized bytes don't match any valid representation for {serializer_id}"


def test_welcome_roundtrip(serializer_id, welcome_samples, create_serializer):
    """
    Test WELCOME roundtrip: deserialize → serialize → deserialize.

    Verifies that:
    1. Message can be deserialized from test vector bytes
    2. Re-serialized to bytes
    3. Deserialized again with identical attributes
    """
    serializer = create_serializer(serializer_id)

    for sample in welcome_samples:
        # Skip if this serializer is not in the test vector
        if serializer_id not in sample["serializers"]:
            pytest.skip(f"Serializer {serializer_id} not in test vector")

        # Get first byte representation
        byte_variants = sample["serializers"][serializer_id]
        if not byte_variants:
            continue

        variant = byte_variants[0]
        if "bytes_hex" in variant:
            original_bytes = bytes_from_hex(variant["bytes_hex"])
        elif "bytes" in variant:
            original_bytes = variant["bytes"].encode("utf-8")
        else:
            continue

        # First deserialization
        msg1 = serializer.unserialize(original_bytes)[0]
        assert isinstance(msg1, Welcome)

        # Serialize
        serialized_bytes, is_binary = serializer.serialize(msg1)

        # Second deserialization
        msg2 = serializer.unserialize(serialized_bytes)[0]
        assert isinstance(msg2, Welcome)

        # Compare attributes
        assert msg2.session == msg1.session
        assert msg2.roles is not None
