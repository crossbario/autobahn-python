"""
WAMP SUBSCRIBE Message SerDes Tests

Tests SUBSCRIBE message serialization and deserialization:
1. Single-serializer roundtrip correctness
2. Cross-serializer preservation
3. Options validation

Uses test vectors from: wamp-proto/testsuite/singlemessage/basic/subscribe.json
"""

import pytest
from autobahn.wamp.message import Subscribe
from autobahn.wamp.serializer import create_transport_serializer

from .utils import (
    load_test_vector,
    bytes_from_hex,
    validate_message_with_code,
    construct_message_with_code,
    matches_any_byte_representation,
    validates_with_any_code,
)


# =============================================================================
# Test Vector Loading
# =============================================================================


@pytest.fixture(scope="module")
def subscribe_test_vector():
    """Load SUBSCRIBE test vector from wamp-proto"""
    return load_test_vector("singlemessage/basic/subscribe.json")


@pytest.fixture(scope="module")
def subscribe_samples(subscribe_test_vector):
    """Extract serialization samples from SUBSCRIBE test vector (excludes validation samples)"""
    # Filter out validation samples - they don't have 'serializers' key
    return [s for s in subscribe_test_vector["samples"] if "serializers" in s]


@pytest.fixture(scope="module")
def subscribe_validation_samples(subscribe_test_vector):
    """Extract Options validation samples from SUBSCRIBE test vector"""
    return [s for s in subscribe_test_vector["samples"] if "test_category" in s]


# =============================================================================
# Dimension 1: Single-Serializer Roundtrip Correctness
# =============================================================================


def test_subscribe_deserialize_from_bytes(
    serializer_id, subscribe_samples, create_serializer
):
    """
    Test SUBSCRIBE deserialization from canonical bytes.

    For each serializer:
    1. Take canonical bytes from test vector
    2. Deserialize to message object
    3. Validate message attributes
    """
    serializer = create_serializer(serializer_id)

    for sample in subscribe_samples:
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
            assert isinstance(msg, Subscribe)
            assert msg.request == sample["expected_attributes"]["request_id"]
            assert msg.topic == sample["expected_attributes"]["topic"]

            # Validate Options
            expected_options = sample["expected_attributes"].get("options", {})
            if "match" in expected_options:
                assert msg.match == expected_options["match"]
            if "get_retained" in expected_options:
                assert msg.get_retained == expected_options["get_retained"]
            if "forward_for" in expected_options:
                assert msg.forward_for == expected_options["forward_for"]


def test_subscribe_serialize_to_bytes(
    serializer_id, subscribe_samples, create_serializer
):
    """
    Test SUBSCRIBE serialization to bytes.

    For each serializer:
    1. Construct message object from test vector attributes
    2. Serialize to bytes
    3. Verify bytes match one of the valid representations
    """
    serializer = create_serializer(serializer_id)

    for sample in subscribe_samples:
        # Skip if this serializer is not in the test vector
        if serializer_id not in sample["serializers"]:
            pytest.skip(f"Serializer {serializer_id} not in test vector")

        # Construct message
        attrs = sample["expected_attributes"]
        options = attrs.get("options", {})

        msg = Subscribe(
            request=attrs["request_id"],
            topic=attrs["topic"],
            match=options.get("match"),
            get_retained=options.get("get_retained"),
            forward_for=options.get("forward_for"),
        )

        # Serialize
        serialized_bytes, is_binary = serializer.serialize(msg)

        # Verify it matches at least one valid byte representation
        assert matches_any_byte_representation(
            serialized_bytes, sample["serializers"][serializer_id]
        ), f"Serialized bytes don't match any valid representation for {serializer_id}"


def test_subscribe_roundtrip(serializer_id, subscribe_samples, create_serializer):
    """
    Test SUBSCRIBE roundtrip: deserialize → serialize → deserialize.

    Verifies that:
    1. Message can be deserialized from test vector bytes
    2. Re-serialized to bytes
    3. Deserialized again with identical attributes
    """
    serializer = create_serializer(serializer_id)

    for sample in subscribe_samples:
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
        assert isinstance(msg1, Subscribe)

        # Serialize
        serialized_bytes, is_binary = serializer.serialize(msg1)

        # Second deserialization
        msg2 = serializer.unserialize(serialized_bytes)[0]
        assert isinstance(msg2, Subscribe)

        # Compare attributes
        assert msg2.request == msg1.request
        assert msg2.topic == msg1.topic
        assert msg2.match == msg1.match
        assert msg2.get_retained == msg1.get_retained
        assert msg2.forward_for == msg1.forward_for


# =============================================================================
# Dimension 2: Options Validation
# =============================================================================


def test_subscribe_options_validation_sample_count(subscribe_validation_samples):
    """Verify we have the expected number of validation samples"""
    assert len(subscribe_validation_samples) > 0, "No validation samples found"
    print(
        f"\nLoaded {len(subscribe_validation_samples)} SUBSCRIBE.Options validation samples from JSON"
    )


@pytest.mark.parametrize("sample_index", range(11))  # We have 11 validation samples
def test_subscribe_options_validation_from_json(
    subscribe_validation_samples, sample_index
):
    """Test SUBSCRIBE.Options validation using language-agnostic JSON test vectors

    This test loads validation samples from wamp-proto/testsuite/singlemessage/basic/subscribe.json
    Each sample specifies a wmsg (deserialized message) and optionally an expected_error.

    This approach makes the test vectors reusable across all WAMP implementations:
    - AutobahnPython (this test)
    - AutobahnJS
    - AutobahnJava
    - AutobahnC++
    """
    from autobahn.wamp.exception import ProtocolError

    # Skip if sample_index is beyond available samples
    if sample_index >= len(subscribe_validation_samples):
        pytest.skip(f"Sample index {sample_index} beyond available samples")

    sample = subscribe_validation_samples[sample_index]
    wmsg = sample["wmsg"][:]  # Make a copy to avoid modifying the original
    expected_error = sample.get("expected_error")
    description = sample.get("description", f"Sample {sample_index}")

    if expected_error:
        # This sample should trigger a ProtocolError
        with pytest.raises(ProtocolError) as exc_info:
            Subscribe.parse(wmsg)

        # Verify the error message contains the expected attribute name
        error_msg = str(exc_info.value).lower()
        expected_contains = expected_error["contains"].lower()
        assert expected_contains in error_msg, (
            f"Expected ProtocolError containing '{expected_contains}', but got: {error_msg}\n"
            f"Test: {description}"
        )
    else:
        # This sample should parse successfully
        try:
            msg = Subscribe.parse(wmsg)
            assert isinstance(msg, Subscribe), (
                f"parse() should return Subscribe instance for: {description}"
            )
            assert msg.request == wmsg[1], f"request mismatch for: {description}"
            assert msg.topic == wmsg[3], f"topic mismatch for: {description}"
        except Exception as e:
            pytest.fail(
                f"Expected successful parse, but got {type(e).__name__}: {e}\nTest: {description}"
            )
