"""
WAMP PUBLISH Message SerDes Tests

Tests PUBLISH message serialization and deserialization across all dimensions:
1. Single-serializer roundtrip correctness
2. Cross-serializer preservation
3. Payload mode handling (normal vs transparent)

Uses test vectors from: wamp-proto/testsuite/singlemessage/basic/publish.json
"""
import pytest
from autobahn.wamp.message import Publish
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
def publish_test_vector():
    """Load PUBLISH test vector from wamp-proto"""
    return load_test_vector("singlemessage/basic/publish.json")


@pytest.fixture(scope="module")
def publish_samples(publish_test_vector):
    """Extract samples from PUBLISH test vector"""
    return publish_test_vector["samples"]


# =============================================================================
# Dimension 1: Performance (covered by examples/benchmarks/serialization/)
# =============================================================================
# Performance testing is handled by the benchmark suite.
# See: examples/benchmarks/serialization/


# =============================================================================
# Dimension 2: Single-Serializer Roundtrip Correctness
# =============================================================================

def test_publish_deserialize_from_bytes(serializer_id, publish_samples, create_serializer):
    """
    Test PUBLISH deserialization from canonical bytes.

    For each serializer:
    1. Take canonical bytes from test vector
    2. Deserialize to message object
    3. Validate with at least one validation code block
    """
    serializer = create_serializer(serializer_id)

    for sample in publish_samples:
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
            msgs = serializer.unserialize(test_bytes)
            assert len(msgs) == 1, "Expected exactly one message"
            msg = msgs[0]

            # Validate with at least one validation code block
            validation_codes = sample["validation"].get("autobahn-python", [])
            if not validation_codes:
                pytest.skip("No validation code for autobahn-python")

            error = validates_with_any_code(msg, validation_codes)
            if error:
                pytest.fail(f"Validation failed for {serializer_id}: {error}")


def test_publish_serialize_to_bytes(serializer_id, publish_samples, create_serializer):
    """
    Test PUBLISH serialization to bytes.

    For each serializer:
    1. Construct message from construction code
    2. Serialize to bytes
    3. Check bytes match at least one canonical representation
    """
    serializer = create_serializer(serializer_id)

    for sample in publish_samples:
        # Skip if this serializer is not in the test vector
        if serializer_id not in sample["serializers"]:
            pytest.skip(f"Serializer {serializer_id} not in test vector")

        # Skip if no construction code for autobahn-python
        construction_code = sample["construction"].get("autobahn-python")
        if not construction_code:
            pytest.skip("No construction code for autobahn-python")

        # Construct message
        msg = construct_message_with_code(construction_code)

        # Serialize
        serialized, is_binary = serializer.serialize(msg)

        # Check if it matches at least one canonical byte representation
        expected_variants = sample["serializers"][serializer_id]
        matches = matches_any_byte_representation(serialized, expected_variants)

        if not matches:
            pytest.fail(
                f"Serialized bytes don't match any canonical representation for {serializer_id}. "
                f"Got: {serialized.hex()}"
            )


def test_publish_roundtrip(serializer_id, publish_samples, create_serializer):
    """
    Test PUBLISH roundtrip: construct → serialize → deserialize → validate.

    This is the core correctness test combining construction, serialization,
    deserialization, and validation.
    """
    serializer = create_serializer(serializer_id)

    for sample in publish_samples:
        # Skip if no construction code
        construction_code = sample["construction"].get("autobahn-python")
        if not construction_code:
            pytest.skip("No construction code for autobahn-python")

        # Skip if no validation code
        validation_codes = sample["validation"].get("autobahn-python", [])
        if not validation_codes:
            pytest.skip("No validation code for autobahn-python")

        # 1. Construct message
        msg_original = construct_message_with_code(construction_code)

        # 2. Serialize
        serialized, is_binary = serializer.serialize(msg_original)

        # 3. Deserialize
        msgs = serializer.unserialize(serialized)
        assert len(msgs) == 1, "Expected exactly one message"
        msg_roundtrip = msgs[0]

        # 4. Validate
        error = validates_with_any_code(msg_roundtrip, validation_codes)
        if error:
            pytest.fail(f"Roundtrip validation failed for {serializer_id}: {error}")

        # 5. Check equality (if message class implements __eq__)
        if hasattr(msg_original, '__eq__'):
            assert msg_original == msg_roundtrip, \
                f"Roundtrip message not equal to original for {serializer_id}"


# =============================================================================
# Dimension 3: Cross-Serializer Preservation
# =============================================================================

def test_publish_cross_serializer_preservation(serializer_pair, publish_samples):
    """
    Test that PUBLISH message attributes are preserved across different serializers.

    For each pair of serializers (ser1, ser2):
    1. Construct message
    2. Roundtrip through ser1: construct → serialize(ser1) → deserialize(ser1)
    3. Roundtrip through ser2: construct → serialize(ser2) → deserialize(ser2)
    4. Validate that both resulting messages are equivalent
    """
    ser1_id, ser2_id = serializer_pair
    ser1 = create_transport_serializer(ser1_id)
    ser2 = create_transport_serializer(ser2_id)

    for sample in publish_samples:
        # Skip if no construction code
        construction_code = sample["construction"].get("autobahn-python")
        if not construction_code:
            pytest.skip("No construction code for autobahn-python")

        # Skip if no validation code
        validation_codes = sample["validation"].get("autobahn-python", [])
        if not validation_codes:
            pytest.skip("No validation code for autobahn-python")

        # Construct original message
        msg_original = construct_message_with_code(construction_code)

        # Roundtrip through ser1
        bytes1, _ = ser1.serialize(msg_original)
        msgs1 = ser1.unserialize(bytes1)
        assert len(msgs1) == 1, "Expected exactly one message from ser1"
        msg_from_ser1 = msgs1[0]

        # Roundtrip through ser2
        bytes2, _ = ser2.serialize(msg_original)
        msgs2 = ser2.unserialize(bytes2)
        assert len(msgs2) == 1, "Expected exactly one message from ser2"
        msg_from_ser2 = msgs2[0]

        # Both should validate
        error1 = validates_with_any_code(msg_from_ser1, validation_codes)
        error2 = validates_with_any_code(msg_from_ser2, validation_codes)

        if error1:
            pytest.fail(f"Validation failed for {ser1_id}: {error1}")
        if error2:
            pytest.fail(f"Validation failed for {ser2_id}: {error2}")

        # Both should be equal (if __eq__ is implemented)
        if hasattr(msg_from_ser1, '__eq__'):
            assert msg_from_ser1 == msg_from_ser2, \
                f"Messages not equal across {ser1_id} and {ser2_id}"


# =============================================================================
# Expected Attributes Validation
# =============================================================================

def test_publish_expected_attributes(publish_samples):
    """
    Test that deserialized PUBLISH message has expected attributes.

    This validates against the abstract WAMP semantic type specified
    in the test vector's expected_attributes field.
    """
    # Use JSON serializer as reference
    serializer = create_transport_serializer("json")

    for sample in publish_samples:
        # Get JSON bytes
        if "json" not in sample["serializers"]:
            pytest.skip("No JSON serializer in test vector")

        json_variants = sample["serializers"]["json"]
        if not json_variants:
            pytest.skip("No JSON byte variants")

        # Deserialize from first JSON variant
        variant = json_variants[0]
        if "bytes" in variant:
            test_bytes = variant["bytes"].encode('utf-8')
        elif "bytes_hex" in variant:
            test_bytes = bytes_from_hex(variant["bytes_hex"])
        else:
            pytest.skip("No bytes in JSON variant")

        msgs = serializer.unserialize(test_bytes)
        assert len(msgs) == 1, "Expected exactly one message"
        msg = msgs[0]

        # Check expected attributes
        expected = sample["expected_attributes"]

        assert msg.request == expected["request_id"], "request_id mismatch"
        assert msg.topic == expected["topic"], "topic mismatch"
        assert msg.args == expected["args"], "args mismatch"

        # kwargs can be None or {} depending on implementation
        if expected["kwargs"] is None:
            assert msg.kwargs is None or msg.kwargs == {}, "kwargs should be None or empty"
        else:
            assert msg.kwargs == expected["kwargs"], "kwargs mismatch"


# =============================================================================
# Payload Mode Tests
# =============================================================================

def test_publish_normal_mode(publish_samples):
    """
    Test PUBLISH in normal payload mode.

    In normal mode, both WAMP metadata and application payload are serialized.
    Router deserializes and can inspect args/kwargs.
    """
    # Find the normal mode sample (has args, not payload)
    normal_samples = [s for s in publish_samples if 'args' in s['expected_attributes'] and s['expected_attributes']['args'] is not None]

    assert len(normal_samples) > 0, "Should have at least one normal mode sample"

    for sample in normal_samples:
        # Verify expected attributes show normal mode
        expected = sample['expected_attributes']
        assert expected.get('args') is not None or expected.get('kwargs') is not None
        assert expected.get('payload') is None or expected['payload'] is None


def test_publish_transparent_mode(publish_samples, create_serializer):
    """
    Test PUBLISH in transparent (passthru) payload mode.

    In transparent mode, application payload is treated as opaque bytes.
    Router does NOT deserialize payload - enables E2E encryption.
    """
    # Find the transparent mode sample (has payload, not args/kwargs)
    transparent_samples = [s for s in publish_samples if 'payload' in s['expected_attributes'] and s['expected_attributes']['payload'] is not None]

    if not transparent_samples:
        pytest.skip("No transparent payload mode samples in test vector")

    for sample in transparent_samples:
        # Verify expected attributes show transparent mode
        expected = sample['expected_attributes']
        assert expected.get('payload') is not None
        assert expected.get('args') is None
        assert expected.get('kwargs') is None

        # Test roundtrip for each serializer
        construction_code = sample['construction'].get('autobahn-python')
        if not construction_code:
            continue

        validation_codes = sample['validation'].get('autobahn-python', [])
        if not validation_codes:
            continue

        # Construct message with transparent payload
        msg_original = construct_message_with_code(construction_code)

        # Verify it's in transparent mode
        assert msg_original.payload is not None
        assert isinstance(msg_original.payload, bytes)
        assert msg_original.args is None
        assert msg_original.kwargs is None

        # Test with JSON serializer (most common)
        serializer = create_serializer('json')
        serialized, is_binary = serializer.serialize(msg_original)
        msgs = serializer.unserialize(serialized)
        assert len(msgs) == 1
        msg_roundtrip = msgs[0]

        # Validate roundtrip preserved transparent payload
        error = validates_with_any_code(msg_roundtrip, validation_codes)
        if error:
            pytest.fail(f"Transparent mode validation failed: {error}")

        # Critical: payload bytes must be preserved exactly (byte-for-byte)
        assert msg_roundtrip.payload == msg_original.payload, \
            "Transparent payload must be preserved byte-for-byte through serialization"
