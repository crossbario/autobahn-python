"""
WAMP CALL Message SerDes Tests

Tests CALL message serialization and deserialization:
1. Single-serializer roundtrip correctness

CALL initiates a remote procedure call with optional args/kwargs.

Uses test vectors from: wamp-proto/testsuite/singlemessage/basic/call.json
"""
import pytest
from autobahn.wamp.message import Call
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
def call_test_vector():
    """Load CALL test vector from wamp-proto"""
    return load_test_vector("singlemessage/basic/call.json")


@pytest.fixture(scope="module")
def call_samples(call_test_vector):
    """Extract serialization samples from CALL test vector"""
    return [s for s in call_test_vector["samples"] if "serializers" in s]


# =============================================================================
# SerDes Tests
# =============================================================================

def test_call_deserialize_from_bytes(serializer_id, call_samples, create_serializer):
    """
    Test CALL deserialization from canonical bytes.

    For each serializer:
    1. Take canonical bytes from test vector
    2. Deserialize to message object
    3. Validate message attributes
    """
    serializer = create_serializer(serializer_id)

    for sample in call_samples:
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
            assert isinstance(msg, Call)
            assert msg.request == sample["expected_attributes"]["request_id"]
            assert msg.procedure == sample["expected_attributes"]["procedure"]

            # Validate args
            expected_args = sample["expected_attributes"].get("args")
            if expected_args is not None:
                assert msg.args == expected_args
            else:
                assert msg.args is None

            # Validate kwargs
            expected_kwargs = sample["expected_attributes"].get("kwargs")
            if expected_kwargs is not None:
                assert msg.kwargs == expected_kwargs
            else:
                assert msg.kwargs is None or msg.kwargs == {}


def test_call_serialize_to_bytes(serializer_id, call_samples, create_serializer):
    """
    Test CALL serialization to bytes.

    For each serializer:
    1. Construct message object from test vector attributes
    2. Serialize to bytes
    3. Verify bytes match one of the valid representations
    """
    serializer = create_serializer(serializer_id)

    for sample in call_samples:
        # Skip if this serializer is not in the test vector
        if serializer_id not in sample["serializers"]:
            pytest.skip(f"Serializer {serializer_id} not in test vector")

        # Construct message
        attrs = sample["expected_attributes"]
        msg = Call(
            request=attrs["request_id"],
            procedure=attrs["procedure"],
            args=attrs.get("args"),
            kwargs=attrs.get("kwargs")
        )

        # Serialize
        serialized_bytes, is_binary = serializer.serialize(msg)

        # Verify it matches at least one valid byte representation
        assert matches_any_byte_representation(
            serialized_bytes, sample["serializers"][serializer_id]
        ), f"Serialized bytes don't match any valid representation for {serializer_id}"


def test_call_roundtrip(serializer_id, call_samples, create_serializer):
    """
    Test CALL roundtrip: deserialize → serialize → deserialize.

    Verifies that:
    1. Message can be deserialized from test vector bytes
    2. Re-serialized to bytes
    3. Deserialized again with identical attributes
    """
    serializer = create_serializer(serializer_id)

    for sample in call_samples:
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
        assert isinstance(msg1, Call)

        # Serialize
        serialized_bytes, is_binary = serializer.serialize(msg1)

        # Second deserialization
        msg2 = serializer.unserialize(serialized_bytes)[0]
        assert isinstance(msg2, Call)

        # Compare attributes
        assert msg2.request == msg1.request
        assert msg2.procedure == msg1.procedure
        assert msg2.args == msg1.args

        # kwargs can be None or empty dict
        if msg1.kwargs is None or msg1.kwargs == {}:
            assert msg2.kwargs is None or msg2.kwargs == {}
        else:
            assert msg2.kwargs == msg1.kwargs
