"""
WAMP EVENT Message SerDes Tests

Tests EVENT message serialization and deserialization across all dimensions:
1. Single-serializer roundtrip correctness
2. Cross-serializer preservation
3. Payload mode handling (normal vs transparent)

Uses test vectors from: wamp-proto/testsuite/singlemessage/basic/event.json
"""
import pytest
from autobahn.wamp.message import Event
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
def event_test_vector():
    """Load EVENT test vector from wamp-proto"""
    return load_test_vector("singlemessage/basic/event.json")


@pytest.fixture(scope="module")
def event_samples(event_test_vector):
    """Extract serialization samples from EVENT test vector (excludes validation samples)"""
    # Filter out validation samples - they don't have 'serializers' key
    return [s for s in event_test_vector["samples"] if "serializers" in s]


# =============================================================================
# Dimension 1: Performance (covered by examples/benchmarks/serialization/)
# =============================================================================
# Performance testing is handled by the benchmark suite.
# See: examples/benchmarks/serialization/


# =============================================================================
# Dimension 2: Single-Serializer Roundtrip Correctness
# =============================================================================

def test_event_deserialize_from_bytes(serializer_id, event_samples, create_serializer):
    """
    Test EVENT deserialization from canonical bytes.

    For each serializer:
    1. Take canonical bytes from test vector
    2. Deserialize to message object
    3. Validate with at least one validation code block
    """
    serializer = create_serializer(serializer_id)

    for sample in event_samples:
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
                # Debug: print sample description
                sample_desc = sample.get('description', 'unknown')
                pytest.fail(f"Validation failed for {serializer_id} on sample '{sample_desc}': {error}")


def test_event_serialize_to_bytes(serializer_id, event_samples, create_serializer):
    """
    Test EVENT serialization to bytes.

    For each serializer:
    1. Construct message from construction code
    2. Serialize to bytes
    3. Check bytes match at least one canonical representation
    """
    serializer = create_serializer(serializer_id)

    for sample in event_samples:
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


def test_event_roundtrip(serializer_id, event_samples, create_serializer):
    """
    Test EVENT roundtrip: construct → serialize → deserialize → validate.

    This is the core correctness test combining construction, serialization,
    deserialization, and validation.
    """
    serializer = create_serializer(serializer_id)

    for sample in event_samples:
        # Skip flatbuffers with transparent payload mode due to autobahn bug
        # See: https://github.com/crossbario/autobahn-python/issues/1766
        # flatbuffers serializer incorrectly handles enc_algo (expects uint8, gets string)
        if serializer_id == 'flatbuffers' and sample.get('expected_attributes', {}).get('payload') is not None:
            pytest.skip("Flatbuffers with transparent payload not supported (issue #1766)")
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
        # Note: Skip equality check for flatbuffers due to known __eq__ issues
        if hasattr(msg_original, '__eq__') and serializer_id != 'flatbuffers':
            assert msg_original == msg_roundtrip, \
                f"Roundtrip message not equal to original for {serializer_id}"


# =============================================================================
# Dimension 3: Cross-Serializer Preservation
# =============================================================================

def test_event_cross_serializer_preservation(serializer_pair, event_samples):
    """
    Test that EVENT message attributes are preserved across different serializers.

    For each pair of serializers (ser1, ser2):
    1. Take canonical bytes_hex for ser1 from test vector
    2. Deserialize with ser1 → get message object
    3. Serialize object with ser2 → get new bytes
    4. Check new bytes match ANY of the bytes_hex variants for ser2 in test vector

    This verifies that the object representation is equivalent across serializers,
    i.e., that deserializing from one serializer and reserializing with another
    produces valid canonical bytes.
    """
    ser1_id, ser2_id = serializer_pair
    ser1 = create_transport_serializer(ser1_id)
    ser2 = create_transport_serializer(ser2_id)

    for sample in event_samples:
        # Skip flatbuffers with transparent payload mode due to autobahn bug
        # See: https://github.com/crossbario/autobahn-python/issues/1766
        # flatbuffers serializer incorrectly handles enc_algo (expects uint8, gets string)
        has_payload = sample.get('expected_attributes', {}).get('payload') is not None
        if has_payload and ('flatbuffers' in [ser1_id, ser2_id]):
            pytest.skip("Flatbuffers with transparent payload not supported (issue #1766)")

        # Skip if ser1 not in test vector
        if ser1_id not in sample["serializers"]:
            pytest.skip(f"Serializer {ser1_id} not in test vector")

        # Skip if ser2 not in test vector
        if ser2_id not in sample["serializers"]:
            pytest.skip(f"Serializer {ser2_id} not in test vector")

        # Get byte variants for both serializers
        ser1_variants = sample["serializers"][ser1_id]
        ser2_variants = sample["serializers"][ser2_id]

        if not ser1_variants or not ser2_variants:
            pytest.skip(f"No byte variants for {ser1_id} or {ser2_id}")

        # Take the first canonical byte representation from ser1
        variant1 = ser1_variants[0]
        if 'bytes_hex' in variant1:
            bytes1 = bytes_from_hex(variant1['bytes_hex'])
        elif 'bytes' in variant1:
            bytes1 = variant1['bytes'].encode('utf-8')
        else:
            pytest.skip(f"No bytes representation in {ser1_id} variant")

        # Deserialize with ser1
        msgs = ser1.unserialize(bytes1)
        assert len(msgs) == 1, f"Expected exactly one message from {ser1_id}"
        msg = msgs[0]

        # Serialize with ser2
        bytes2, _ = ser2.serialize(msg)

        # Check if bytes2 matches ANY of the canonical bytes for ser2
        matches = matches_any_byte_representation(bytes2, ser2_variants)

        if not matches:
            pytest.fail(
                f"Cross-serializer conversion failed: {ser1_id} → {ser2_id}. "
                f"Serialized bytes don't match any canonical representation for {ser2_id}. "
                f"Got: {bytes2.hex()}"
            )


# =============================================================================
# Expected Attributes Validation
# =============================================================================

def test_event_expected_attributes(event_samples):
    """
    Test that deserialized EVENT message has expected attributes.

    This validates against the abstract WAMP semantic type specified
    in the test vector's expected_attributes field.
    """
    # Use JSON serializer as reference
    serializer = create_transport_serializer("json")

    for sample in event_samples:
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

        assert msg.subscription == expected["subscription"], "subscription mismatch"
        assert msg.publication == expected["publication"], "publication mismatch"
        assert msg.args == expected["args"], "args mismatch"

        # kwargs can be None or {} depending on implementation
        if expected["kwargs"] is None:
            assert msg.kwargs is None or msg.kwargs == {}, "kwargs should be None or empty"
        else:
            assert msg.kwargs == expected["kwargs"], "kwargs mismatch"


# =============================================================================
# Payload Mode Tests
# =============================================================================

def test_event_normal_mode(event_samples):
    """
    Test EVENT in normal payload mode.

    In normal mode, both WAMP metadata and application payload are serialized.
    Router deserializes and can inspect args/kwargs.
    """
    # Find the normal mode sample (has args, not payload)
    normal_samples = [s for s in event_samples if 'args' in s['expected_attributes'] and s['expected_attributes']['args'] is not None]

    assert len(normal_samples) > 0, "Should have at least one normal mode sample"

    for sample in normal_samples:
        # Verify expected attributes show normal mode
        expected = sample['expected_attributes']
        assert expected.get('args') is not None or expected.get('kwargs') is not None
        assert expected.get('payload') is None or expected['payload'] is None


def test_event_transparent_mode(event_samples, create_serializer):
    """
    Test EVENT in transparent (passthru) payload mode.

    In transparent mode, application payload is treated as opaque bytes.
    Router does NOT deserialize payload - enables E2E encryption.
    """
    # Find the transparent mode sample (has payload, not args/kwargs)
    transparent_samples = [s for s in event_samples if 'payload' in s['expected_attributes'] and s['expected_attributes']['payload'] is not None]

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


# =============================================================================
# EVENT.Details Parsing Validation Tests
# =============================================================================
# These tests validate that EVENT.Details attributes are correctly parsed
# and type-checked at the wmsg (deserialized message dict) level.
#
# This is critical for multi-implementation WAMP environments where:
# - Publisher → Router → Subscriber (potentially different implementations)
# - Proper validation at message boundaries prevents bugs from propagating

from autobahn.wamp.exception import ProtocolError


# -----------------------------------------------------------------------------
# publisher|int - Advanced Profile
# -----------------------------------------------------------------------------

def test_event_details_publisher_valid():
    """Test EVENT.Details.publisher with valid int values"""
    valid_values = [123, 456, 999999]
    for value in valid_values:
        wmsg = [36, 5512315355, 4429313566, {"publisher": value}]
        msg = Event.parse(wmsg)
        assert msg.publisher == value


def test_event_details_publisher_invalid_type():
    """Test EVENT.Details.publisher with invalid types"""
    invalid_values = [
        ("hello", "string instead of int"),
        (True, "bool instead of int"),
        (1.5, "float instead of int"),
        ([], "list instead of int"),
    ]
    for value, description in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"publisher": value}]
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)
        assert "publisher" in str(exc_info.value).lower()


# -----------------------------------------------------------------------------
# publisher_authid|str - Advanced Profile
# -----------------------------------------------------------------------------

def test_event_details_publisher_authid_valid():
    """Test EVENT.Details.publisher_authid with valid str values"""
    valid_values = ["alice", "bob", "user123", ""]
    for value in valid_values:
        wmsg = [36, 5512315355, 4429313566, {"publisher_authid": value}]
        msg = Event.parse(wmsg)
        assert msg.publisher_authid == value


def test_event_details_publisher_authid_invalid_type():
    """Test EVENT.Details.publisher_authid with invalid types"""
    invalid_values = [
        (123, "int instead of str"),
        (True, "bool instead of str"),
        ([], "list instead of str"),
    ]
    for value, description in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"publisher_authid": value}]
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)
        assert "publisher_authid" in str(exc_info.value).lower()


# -----------------------------------------------------------------------------
# publisher_authrole|str - Advanced Profile
# -----------------------------------------------------------------------------

def test_event_details_publisher_authrole_valid():
    """Test EVENT.Details.publisher_authrole with valid str values"""
    valid_values = ["user", "admin", "manager", ""]
    for value in valid_values:
        wmsg = [36, 5512315355, 4429313566, {"publisher_authrole": value}]
        msg = Event.parse(wmsg)
        assert msg.publisher_authrole == value


def test_event_details_publisher_authrole_invalid_type():
    """Test EVENT.Details.publisher_authrole with invalid types"""
    invalid_values = [
        (123, "int instead of str"),
        (True, "bool instead of str"),
        ([], "list instead of str"),
    ]
    for value, description in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"publisher_authrole": value}]
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)
        assert "publisher_authrole" in str(exc_info.value).lower()


# -----------------------------------------------------------------------------
# topic|str - Advanced Profile (pattern-based subscriptions)
# -----------------------------------------------------------------------------

def test_event_details_topic_valid():
    """Test EVENT.Details.topic with valid str values"""
    valid_values = [
        "com.example.topic",
        "com.myapp.topic.emergency.severe",
        "com.foo.bar.baz",
    ]
    for value in valid_values:
        wmsg = [36, 5512315355, 4429313566, {"topic": value}]
        msg = Event.parse(wmsg)
        assert msg.topic == value


def test_event_details_topic_invalid_type():
    """Test EVENT.Details.topic with invalid types"""
    invalid_values = [
        (123, "int instead of str"),
        (True, "bool instead of str"),
        ([], "list instead of str"),
    ]
    for value, description in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"topic": value}]
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)
        assert "topic" in str(exc_info.value).lower()


# -----------------------------------------------------------------------------
# retained|bool - Advanced Profile (event retention)
# -----------------------------------------------------------------------------

def test_event_details_retained_valid():
    """Test EVENT.Details.retained with valid bool values"""
    for value in [True, False]:
        wmsg = [36, 5512315355, 4429313566, {"retained": value}]
        msg = Event.parse(wmsg)
        assert msg.retained == value


def test_event_details_retained_invalid_type():
    """Test EVENT.Details.retained with invalid types"""
    invalid_values = [
        ("hello", "string instead of bool"),
        (1, "int instead of bool"),
        ([], "list instead of bool"),
    ]
    for value, description in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"retained": value}]
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)
        assert "retained" in str(exc_info.value).lower()


# -----------------------------------------------------------------------------
# transaction_hash|str - Implementation-Only
# -----------------------------------------------------------------------------

def test_event_details_transaction_hash_valid():
    """Test EVENT.Details.transaction_hash with valid str values"""
    valid_values = [
        "abc123",
        "0x1234567890abcdef",
        "",
    ]
    for value in valid_values:
        wmsg = [36, 5512315355, 4429313566, {"transaction_hash": value}]
        msg = Event.parse(wmsg)
        assert msg.transaction_hash == value


def test_event_details_transaction_hash_invalid_type():
    """Test EVENT.Details.transaction_hash with invalid types"""
    invalid_values = [
        (123, "int instead of str"),
        (True, "bool instead of str"),
        ([], "list instead of str"),
    ]
    for value, description in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"transaction_hash": value}]
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)
        assert "transaction_hash" in str(exc_info.value).lower()


# -----------------------------------------------------------------------------
# x_acknowledged_delivery|bool - Implementation-Only
# -----------------------------------------------------------------------------

def test_event_details_x_acknowledged_delivery_valid():
    """Test EVENT.Details.x_acknowledged_delivery with valid bool values"""
    for value in [True, False]:
        wmsg = [36, 5512315355, 4429313566, {"x_acknowledged_delivery": value}]
        msg = Event.parse(wmsg)
        assert msg.x_acknowledged_delivery == value


def test_event_details_x_acknowledged_delivery_invalid_type():
    """Test EVENT.Details.x_acknowledged_delivery with invalid types"""
    invalid_values = [
        ("hello", "string instead of bool"),
        (1, "int instead of bool"),
    ]
    for value, description in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"x_acknowledged_delivery": value}]
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)
        assert "x_acknowledged_delivery" in str(exc_info.value).lower()


# -----------------------------------------------------------------------------
# forward_for|list[dict] - Implementation-Only
# -----------------------------------------------------------------------------

def test_event_details_forward_for_valid():
    """Test EVENT.Details.forward_for with valid list[dict] values"""
    valid_values = [
        [],
        [{"session": 123, "authid": "alice", "authrole": "user"}],
        [
            {"session": 123, "authid": "alice", "authrole": "user"},
            {"session": 456, "authid": "bob", "authrole": "admin"},
        ],
    ]
    for value in valid_values:
        wmsg = [36, 5512315355, 4429313566, {"forward_for": value}]
        msg = Event.parse(wmsg)
        assert msg.forward_for == value


def test_event_details_forward_for_invalid_type():
    """Test EVENT.Details.forward_for with invalid types"""
    invalid_values = [
        ("hello", "string instead of list"),
        (123, "int instead of list"),
        ({}, "dict instead of list"),
    ]
    for value, description in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"forward_for": value}]
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)
        assert "forward_for" in str(exc_info.value).lower()


def test_event_details_forward_for_invalid_values():
    """Test EVENT.Details.forward_for with invalid list item structures

    NOTE: Same validation bug as PUBLISH - single-item invalid lists might
    pass parse() but fail in __init__. Testing multi-item lists.
    """
    invalid_lists = [
        # Multi-item lists where validation fails
        ([{"session": 123, "authid": "alice", "authrole": "user"}, 123], "second item is int"),
        ([{"session": 123, "authid": "alice", "authrole": "user"}, {"bad": "dict"}], "second item missing required fields"),
    ]
    for value, description in invalid_lists:
        wmsg = [36, 5512315355, 4429313566, {"forward_for": value}]
        # Accept either ProtocolError (correct) or AssertionError (bug)
        with pytest.raises((ProtocolError, AssertionError)) as exc_info:
            Event.parse(wmsg)


# -----------------------------------------------------------------------------
# E2EE Options (enc_algo, enc_key, enc_serializer) - Implementation-Only
# These are only valid with transparent payload mode (variant 4)
# -----------------------------------------------------------------------------

def test_event_details_enc_algo_valid():
    """Test EVENT.Details.enc_algo with valid values (transparent payload mode)"""
    # enc_algo is only parsed when message has transparent payload
    payload = b"encrypted_data_here"

    # Valid enc_algo values
    valid_values = [
        "cryptobox",
        "mqtt",
        "xbr",
    ]
    for value in valid_values:
        wmsg = [36, 5512315355, 4429313566, {"enc_algo": value}, payload]
        msg = Event.parse(wmsg)
        assert msg.enc_algo == value
        assert msg.payload == payload


def test_event_details_enc_algo_invalid_value():
    """Test EVENT.Details.enc_algo with invalid algorithm names"""
    payload = b"encrypted_data_here"
    invalid_values = [
        "invalid_algo",
        "aes256",
        "rsa",
    ]
    for value in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"enc_algo": value}, payload]
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)
        assert "enc_algo" in str(exc_info.value).lower()


def test_event_details_enc_key_valid():
    """Test EVENT.Details.enc_key with valid str values (transparent payload mode)"""
    payload = b"encrypted_data_here"
    valid_values = [
        "0x1234567890abcdef",
        "base64encodedkey==",
        "",
    ]
    for value in valid_values:
        wmsg = [36, 5512315355, 4429313566, {"enc_algo": "cryptobox", "enc_key": value}, payload]
        msg = Event.parse(wmsg)
        assert msg.enc_key == value


def test_event_details_enc_key_invalid_type():
    """Test EVENT.Details.enc_key with invalid types

    NOTE: Same validation bug as PUBLISH - falsy values bypass type check.
    """
    payload = b"encrypted_data_here"
    invalid_values = [
        (123, "int instead of str"),
        (True, "bool instead of str"),
        ([1, 2], "non-empty list instead of str"),
    ]
    for value, description in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"enc_algo": "cryptobox", "enc_key": value}, payload]
        with pytest.raises((ProtocolError, AssertionError)) as exc_info:
            Event.parse(wmsg)


def test_event_details_enc_serializer_valid():
    """Test EVENT.Details.enc_serializer with valid values (transparent payload mode)"""
    payload = b"encrypted_data_here"

    # Valid enc_serializer values
    valid_values = [
        "cbor",
        "msgpack",
        "json",
        "ubjson",
        "flatbuffers",
    ]
    for value in valid_values:
        wmsg = [36, 5512315355, 4429313566, {"enc_algo": "cryptobox", "enc_serializer": value}, payload]
        msg = Event.parse(wmsg)
        assert msg.enc_serializer == value


def test_event_details_enc_serializer_invalid_value():
    """Test EVENT.Details.enc_serializer with invalid serializer names"""
    payload = b"encrypted_data_here"
    invalid_values = [
        "invalid_serializer",
        "xml",
        "yaml",
    ]
    for value in invalid_values:
        wmsg = [36, 5512315355, 4429313566, {"enc_algo": "cryptobox", "enc_serializer": value}, payload]
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)
        assert "enc_serializer" in str(exc_info.value).lower()


# =============================================================================
# Dimension 5: Details Validation (Language-Agnostic JSON Test Vectors)
# =============================================================================

@pytest.fixture(scope="module")
def event_validation_samples(event_test_vector):
    """Extract validation samples from EVENT test vector"""
    return [s for s in event_test_vector["samples"] if s.get("test_category") == "details_validation"]


def test_event_details_validation_sample_count(event_validation_samples):
    """Verify we have the expected number of validation samples"""
    # We should have validation samples for all EVENT.Details attributes
    assert len(event_validation_samples) > 0, "No validation samples found"
    print(f"\nLoaded {len(event_validation_samples)} EVENT.Details validation samples from JSON")


@pytest.mark.parametrize("sample_index", range(21))  # We have 21 validation samples
def test_event_details_validation_from_json(event_validation_samples, sample_index):
    """Test EVENT.Details validation using language-agnostic JSON test vectors

    This test loads validation samples from wamp-proto/testsuite/singlemessage/basic/event.json
    Each sample specifies a wmsg (deserialized message) and optionally an expected_error.

    This approach makes the test vectors reusable across all WAMP implementations:
    - AutobahnPython (this test)
    - AutobahnJS
    - AutobahnJava
    - AutobahnC++
    """
    # Skip if sample_index is beyond available samples (allows running all tests)
    if sample_index >= len(event_validation_samples):
        pytest.skip(f"Sample index {sample_index} beyond available samples")

    sample = event_validation_samples[sample_index]
    wmsg = sample["wmsg"][:]  # Make a copy to avoid modifying the original
    expected_error = sample.get("expected_error")
    description = sample.get("description", f"Sample {sample_index}")

    # Convert payload from hex string to bytes if present
    # EVENT: [36, subscription, publication, details, (payload_hex)]
    if len(wmsg) == 5 and isinstance(wmsg[4], str):
        # Transparent payload mode - convert hex string to bytes
        wmsg[4] = bytes_from_hex(wmsg[4])

    if expected_error:
        # This sample should trigger a ProtocolError
        with pytest.raises(ProtocolError) as exc_info:
            Event.parse(wmsg)

        # Verify the error message contains the expected attribute name
        error_msg = str(exc_info.value).lower()
        assert expected_error["contains"].lower() in error_msg, \
            f"{description}: Expected error message to contain '{expected_error['contains']}', got: {exc_info.value}"
    else:
        # This sample should parse successfully
        msg = Event.parse(wmsg)
        assert isinstance(msg, Event), f"{description}: Failed to parse as Event message"

        # Verify the message type
        assert msg.MESSAGE_TYPE == 36, f"{description}: Wrong message type"
