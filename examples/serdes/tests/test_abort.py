"""
WAMP ABORT Message SerDes Tests

Tests ABORT message serialization and deserialization:
1. Single-serializer roundtrip correctness

ABORT is sent by a Peer to abort the opening of a WAMP session.

Uses test vectors from: wamp-proto/testsuite/singlemessage/basic/abort.json
"""
import pytest
from autobahn.wamp.message import Abort
from autobahn.wamp.serializer import create_transport_serializer

from .utils import (
    load_test_vector,
    bytes_from_hex,
    matches_any_byte_representation,
)


# =============================================================================
# Test Vector Loading
# =============================================================================

@pytest.fixture(scope="module")
def abort_test_vector():
    """Load ABORT test vector from wamp-proto"""
    return load_test_vector("singlemessage/basic/abort.json")


@pytest.fixture(scope="module")
def abort_samples(abort_test_vector):
    """Extract serialization samples from ABORT test vector"""
    return [s for s in abort_test_vector["samples"] if "serializers" in s]


# =============================================================================
# SerDes Tests
# =============================================================================

def test_abort_deserialize_from_bytes(serializer_id, abort_samples, create_serializer):
    """
    Test ABORT deserialization from canonical bytes.

    For each serializer:
    1. Take canonical bytes from test vector
    2. Deserialize to message object
    3. Validate message attributes
    """
    serializer = create_serializer(serializer_id)

    for sample in abort_samples:
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
                test_bytes = variant["bytes"].encode('utf-8')
            else:
                continue

            # Deserialize
            msg = serializer.unserialize(test_bytes)[0]

            # Basic validations
            assert isinstance(msg, Abort)
            assert msg.reason == sample["expected_attributes"]["reason"]


def test_abort_serialize_to_bytes(serializer_id, abort_samples, create_serializer):
    """
    Test ABORT serialization to bytes.

    For each serializer:
    1. Construct message object from test vector attributes
    2. Serialize to bytes
    3. Verify bytes match one of the valid representations
    """
    serializer = create_serializer(serializer_id)

    for sample in abort_samples:
        # Skip if this serializer is not in the test vector
        if serializer_id not in sample["serializers"]:
            pytest.skip(f"Serializer {serializer_id} not in test vector")

        # Construct message
        attrs = sample["expected_attributes"]
        msg = Abort(reason=attrs["reason"])

        # Serialize
        serialized_bytes, is_binary = serializer.serialize(msg)

        # Verify it matches at least one valid byte representation
        assert matches_any_byte_representation(
            serialized_bytes, sample["serializers"][serializer_id]
        ), f"Serialized bytes don't match any valid representation for {serializer_id}"


def test_abort_roundtrip(serializer_id, abort_samples, create_serializer):
    """
    Test ABORT roundtrip: deserialize → serialize → deserialize.

    Verifies that:
    1. Message can be deserialized from test vector bytes
    2. Re-serialized to bytes
    3. Deserialized again with identical attributes
    """
    serializer = create_serializer(serializer_id)

    for sample in abort_samples:
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
            original_bytes = variant["bytes"].encode('utf-8')
        else:
            continue

        # First deserialization
        msg1 = serializer.unserialize(original_bytes)[0]
        assert isinstance(msg1, Abort)

        # Serialize
        serialized_bytes, is_binary = serializer.serialize(msg1)

        # Second deserialization
        msg2 = serializer.unserialize(serialized_bytes)[0]
        assert isinstance(msg2, Abort)

        # Compare attributes
        assert msg2.reason == msg1.reason
