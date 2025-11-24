#!/usr/bin/env python3
"""
Generate FlatBuffers test vectors for WAMP messages.

This script:
1. Loads test vector JSON files from wamp-proto/testsuite
2. For each sample, creates a WAMP message object
3. Serializes it to FlatBuffers
4. Adds the bytes_hex to the test vector
5. Saves the updated JSON back to wamp-proto

Usage:
    python gen_flatbuffers_testvectors.py

Requirements:
    - autobahn-python with FlatBuffers support installed
    - wamp-proto repo in sibling directory: ../../../wamp-proto
"""

import json
import sys
from binascii import hexlify
from pathlib import Path

# Add autobahn to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Initialize txaio before importing autobahn modules
import txaio

txaio.use_asyncio()

from autobahn.wamp import message as wamp_messages
from autobahn.wamp.gen.wamp.proto.PPTScheme import PPTScheme
from autobahn.wamp.gen.wamp.proto.PPTSerializer import PPTSerializer
from autobahn.wamp.serializer import FlatBuffersSerializer

# Enum mappings for E2EE payloads (renamed from Payload -> PPTScheme)
PAYLOAD_ALGO_MAP = {
    "none": PPTScheme.NONE,
    "cryptobox": PPTScheme.CRYPTOBOX,
    "mqtt": PPTScheme.MQTT,
    "xbr": PPTScheme.XBR,
    "opaque": PPTScheme.OPAQUE,
}

# Enum mappings for serializers (renamed from Serializer -> PPTSerializer)
SERIALIZER_MAP = {
    "transport": PPTSerializer.TRANSPORT,
    "json": PPTSerializer.JSON,
    "msgpack": PPTSerializer.MSGPACK,
    "cbor": PPTSerializer.CBOR,
    "ubjson": PPTSerializer.UBJSON,
    "opaque": PPTSerializer.OPAQUE,
    "flatbuffers": PPTSerializer.FLATBUFFERS,
    "flexbuffers": PPTSerializer.FLEXBUFFERS,
}


# Message type mapping
MESSAGE_TYPE_MAP = {
    "HELLO": (wamp_messages.Hello, 1),
    "WELCOME": (wamp_messages.Welcome, 2),
    "ABORT": (wamp_messages.Abort, 3),
    "CHALLENGE": (wamp_messages.Challenge, 4),
    "AUTHENTICATE": (wamp_messages.Authenticate, 5),
    "GOODBYE": (wamp_messages.Goodbye, 6),
    "ERROR": (wamp_messages.Error, 8),
    "PUBLISH": (wamp_messages.Publish, 16),
    "PUBLISHED": (wamp_messages.Published, 17),
    "SUBSCRIBE": (wamp_messages.Subscribe, 32),
    "SUBSCRIBED": (wamp_messages.Subscribed, 33),
    "UNSUBSCRIBE": (wamp_messages.Unsubscribe, 34),
    "UNSUBSCRIBED": (wamp_messages.Unsubscribed, 35),
    "EVENT": (wamp_messages.Event, 36),
    "CALL": (wamp_messages.Call, 48),
    "CANCEL": (wamp_messages.Cancel, 49),
    "RESULT": (wamp_messages.Result, 50),
    "REGISTER": (wamp_messages.Register, 64),
    "REGISTERED": (wamp_messages.Registered, 65),
    "UNREGISTER": (wamp_messages.Unregister, 66),
    "UNREGISTERED": (wamp_messages.Unregistered, 67),
    "INVOCATION": (wamp_messages.Invocation, 68),
    "INTERRUPT": (wamp_messages.Interrupt, 69),
    "YIELD": (wamp_messages.Yield, 70),
}


def create_message_from_attributes(message_type_name, attributes):
    """
    Create a WAMP message object from expected_attributes.

    :param message_type_name: WAMP message type name (e.g., "PUBLISHED")
    :param attributes: Expected attributes dict from test vector
    :return: WAMP message object
    """
    message_class, _ = MESSAGE_TYPE_MAP[message_type_name]

    # Session establishment messages
    if message_type_name == "HELLO":
        return message_class(realm=attributes["realm"], roles=attributes["roles"])
    elif message_type_name == "WELCOME":
        return message_class(
            session=attributes["session_id"], roles=attributes["roles"]
        )
    elif message_type_name == "ABORT":
        return message_class(
            reason=attributes["reason"], message=attributes.get("message")
        )
    elif message_type_name == "CHALLENGE":
        return message_class(
            method=attributes["method"], extra=attributes.get("extra", {})
        )
    elif message_type_name == "AUTHENTICATE":
        return message_class(
            signature=attributes["signature"], extra=attributes.get("extra", {})
        )
    elif message_type_name == "GOODBYE":
        return message_class(
            reason=attributes.get("reason", "wamp.close.normal"),
            message=attributes.get("message"),
        )

    # Error message
    elif message_type_name == "ERROR":
        return message_class(
            request_type=attributes["request_type"],
            request=attributes["request_id"],
            error=attributes["error"],
            args=attributes.get("args"),
            kwargs=attributes.get("kwargs"),
            payload=bytes.fromhex(attributes["payload"])
            if attributes.get("payload")
            else None,
        )

    # PubSub messages
    elif message_type_name == "PUBLISH":
        # Keep enc_algo and enc_serializer as strings (build() converts to enums)
        return message_class(
            request=attributes["request_id"],
            topic=attributes["topic"],
            args=attributes.get("args"),
            kwargs=attributes.get("kwargs"),
            payload=bytes.fromhex(attributes["payload"])
            if attributes.get("payload")
            else None,
            acknowledge=attributes.get("options", {}).get("acknowledge"),
            exclude_me=attributes.get("options", {}).get("exclude_me"),
            retain=attributes.get("options", {}).get("retain"),
            forward_for=attributes.get("options", {}).get("forward_for"),
            enc_algo=attributes.get("options", {}).get("enc_algo"),
            enc_serializer=attributes.get("options", {}).get("enc_serializer"),
        )
    elif message_type_name == "PUBLISHED":
        return message_class(
            request=attributes["request_id"], publication=attributes["publication_id"]
        )
    elif message_type_name == "SUBSCRIBE":
        return message_class(
            request=attributes["request_id"],
            topic=attributes["topic"],
            match=attributes.get("options", {}).get("match"),
            get_retained=attributes.get("options", {}).get("get_retained"),
            forward_for=attributes.get("options", {}).get("forward_for"),
        )
    elif message_type_name == "SUBSCRIBED":
        return message_class(
            request=attributes["request_id"], subscription=attributes["subscription_id"]
        )
    elif message_type_name == "UNSUBSCRIBE":
        return message_class(
            request=attributes["request_id"],
            subscription=attributes["subscription_id"],
            forward_for=attributes.get("options", {}).get("forward_for"),
        )
    elif message_type_name == "UNSUBSCRIBED":
        return message_class(request=attributes["request_id"])
    elif message_type_name == "EVENT":
        # Keep enc_algo and enc_serializer as strings (build() converts to enums)
        return message_class(
            subscription=attributes["subscription"],
            publication=attributes["publication"],
            args=attributes.get("args"),
            kwargs=attributes.get("kwargs"),
            payload=bytes.fromhex(attributes["payload"])
            if attributes.get("payload")
            else None,
            publisher=attributes.get("details", {}).get("publisher"),
            publisher_authid=attributes.get("details", {}).get("publisher_authid"),
            publisher_authrole=attributes.get("details", {}).get("publisher_authrole"),
            topic=attributes.get("details", {}).get("topic"),
            retained=attributes.get("details", {}).get("retained"),
            forward_for=attributes.get("details", {}).get("forward_for"),
            enc_algo=attributes.get("details", {}).get("enc_algo"),
            enc_serializer=attributes.get("details", {}).get("enc_serializer"),
        )

    # RPC messages
    elif message_type_name == "CALL":
        return message_class(
            request=attributes["request_id"],
            procedure=attributes["procedure"],
            args=attributes.get("args"),
            kwargs=attributes.get("kwargs"),
            payload=bytes.fromhex(attributes["payload"])
            if attributes.get("payload")
            else None,
            timeout=attributes.get("options", {}).get("timeout"),
            receive_progress=attributes.get("options", {}).get("receive_progress"),
            forward_for=attributes.get("options", {}).get("forward_for"),
            enc_algo=attributes.get("options", {}).get("enc_algo"),
            enc_serializer=attributes.get("options", {}).get("enc_serializer"),
        )
    elif message_type_name == "CANCEL":
        return message_class(
            request=attributes["request_id"],
            mode=attributes.get("options", {}).get("mode"),
            forward_for=attributes.get("options", {}).get("forward_for"),
        )
    elif message_type_name == "RESULT":
        return message_class(
            request=attributes["request_id"],
            args=attributes.get("args"),
            kwargs=attributes.get("kwargs"),
            payload=bytes.fromhex(attributes["payload"])
            if attributes.get("payload")
            else None,
            progress=attributes.get("details", {}).get("progress"),
            enc_algo=attributes.get("details", {}).get("enc_algo"),
            enc_serializer=attributes.get("details", {}).get("enc_serializer"),
            callee=attributes.get("details", {}).get("callee"),
            callee_authid=attributes.get("details", {}).get("callee_authid"),
            callee_authrole=attributes.get("details", {}).get("callee_authrole"),
            forward_for=attributes.get("details", {}).get("forward_for"),
        )
    elif message_type_name == "REGISTER":
        return message_class(
            request=attributes["request_id"],
            procedure=attributes["procedure"],
            match=attributes.get("options", {}).get("match"),
            invoke=attributes.get("options", {}).get("invoke"),
            concurrency=attributes.get("options", {}).get("concurrency"),
            force_reregister=attributes.get("options", {}).get("force_reregister"),
            forward_for=attributes.get("options", {}).get("forward_for"),
        )
    elif message_type_name == "REGISTERED":
        return message_class(
            request=attributes["request_id"], registration=attributes["registration_id"]
        )
    elif message_type_name == "UNREGISTER":
        return message_class(
            request=attributes["request_id"],
            registration=attributes["registration_id"],
            forward_for=attributes.get("options", {}).get("forward_for"),
        )
    elif message_type_name == "UNREGISTERED":
        return message_class(request=attributes["request_id"])
    elif message_type_name == "INVOCATION":
        return message_class(
            request=attributes["request_id"],
            registration=attributes["registration_id"],
            args=attributes.get("args"),
            kwargs=attributes.get("kwargs"),
            payload=bytes.fromhex(attributes["payload"])
            if attributes.get("payload")
            else None,
            timeout=attributes.get("details", {}).get("timeout"),
            receive_progress=attributes.get("details", {}).get("receive_progress"),
            caller=attributes.get("details", {}).get("caller"),
            caller_authid=attributes.get("details", {}).get("caller_authid"),
            caller_authrole=attributes.get("details", {}).get("caller_authrole"),
            procedure=attributes.get("details", {}).get("procedure"),
            enc_algo=attributes.get("details", {}).get("enc_algo"),
            enc_serializer=attributes.get("details", {}).get("enc_serializer"),
            forward_for=attributes.get("details", {}).get("forward_for"),
        )
    elif message_type_name == "INTERRUPT":
        return message_class(
            request=attributes["request_id"],
            mode=attributes.get("options", {}).get("mode"),
            reason=attributes.get("options", {}).get("reason"),
            forward_for=attributes.get("options", {}).get("forward_for"),
        )
    elif message_type_name == "YIELD":
        return message_class(
            request=attributes["request_id"],
            args=attributes.get("args"),
            kwargs=attributes.get("kwargs"),
            payload=bytes.fromhex(attributes["payload"])
            if attributes.get("payload")
            else None,
            progress=attributes.get("options", {}).get("progress"),
            enc_algo=attributes.get("options", {}).get("enc_algo"),
            enc_serializer=attributes.get("options", {}).get("enc_serializer"),
            forward_for=attributes.get("options", {}).get("forward_for"),
        )

    else:
        raise NotImplementedError(
            f"Message creation not implemented for {message_type_name}"
        )


def generate_flatbuffers_bytes(message_obj):
    """
    Serialize a WAMP message to FlatBuffers and return hex string.

    :param message_obj: WAMP message object
    :return: Hex string of serialized bytes
    """
    import flatbuffers

    # Create a FlatBuffers builder
    builder = flatbuffers.Builder(1024)

    # Use the message's build() method to build the FlatBuffers message
    msg_offset = message_obj.build(builder)

    # Finish the buffer
    builder.Finish(msg_offset)

    # Get the serialized bytes
    serialized_bytes = bytes(builder.Output())

    return hexlify(serialized_bytes).decode("ascii")


def process_test_vector_file(json_path):
    """
    Process a single test vector JSON file and add FlatBuffers entries.

    :param json_path: Path to test vector JSON file
    """
    print(f"\nProcessing: {json_path.name}")

    # Load test vector
    with open(json_path, "r") as f:
        test_vector = json.load(f)

    message_type_name = test_vector["wamp_message_type"]

    if message_type_name not in MESSAGE_TYPE_MAP:
        print(f"  ⚠ Skipping {message_type_name} - not in MESSAGE_TYPE_MAP")
        return False

    modified = False

    # Process each sample
    for i, sample in enumerate(test_vector.get("samples", [])):
        if "serializers" not in sample:
            continue

        # Check if flatbuffers already exists - we'll update it
        updating = "flatbuffers" in sample["serializers"]
        if updating:
            print(f"  ↻ Sample {i + 1}: updating existing flatbuffers entry")

        # Check if we have expected_attributes
        if "expected_attributes" not in sample:
            print(f"  ⚠ Sample {i + 1}: no expected_attributes, skipping")
            continue

        try:
            # Create message object
            message_obj = create_message_from_attributes(
                message_type_name, sample["expected_attributes"]
            )

            # Generate FlatBuffers bytes
            bytes_hex = generate_flatbuffers_bytes(message_obj)

            # Add to test vector
            sample["serializers"]["flatbuffers"] = [
                {
                    "bytes_hex": bytes_hex,
                    "note": "Generated by autobahn-python FlatBuffers serializer",
                }
            ]

            modified = True
            action = "updated" if updating else "added"
            print(
                f"  ✓ Sample {i + 1}: {action} flatbuffers ({len(bytes_hex) // 2} bytes)"
            )

        except NotImplementedError as e:
            print(f"  ⚠ Sample {i + 1}: {e}")
            continue
        except Exception as e:
            print(f"  ✗ Sample {i + 1}: Error - {e}")
            continue

    # Save if modified
    if modified:
        with open(json_path, "w") as f:
            json.dump(test_vector, f, indent=2)
            f.write("\n")  # Add trailing newline
        print("  💾 Saved updated test vector")
        return True

    return False


def main():
    """Main entry point"""
    print("=" * 70)
    print("FlatBuffers Test Vector Generator")
    print("=" * 70)

    # Find wamp-proto testsuite directory
    autobahn_root = Path(__file__).parent.parent.parent
    wamp_proto_root = autobahn_root / ".proto"
    testsuite_dir = wamp_proto_root / "testsuite" / "singlemessage" / "basic"

    if not testsuite_dir.exists():
        print(f"\n❌ Error: testsuite directory not found: {testsuite_dir}")
        print("   Expected: .proto/testsuite/singlemessage/basic/")
        return 1

    print(f"\nTestsuite directory: {testsuite_dir}")

    # Process all JSON files
    json_files = sorted(testsuite_dir.glob("*.json"))
    print(f"Found {len(json_files)} test vector files")

    modified_count = 0
    for json_path in json_files:
        if process_test_vector_file(json_path):
            modified_count += 1

    print("\n" + "=" * 70)
    print(f"✅ Complete: {modified_count}/{len(json_files)} files modified")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
