"""
Utility functions for WAMP serdes tests
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


def get_wamp_proto_path() -> Path:
    """
    Get path to wamp-proto repository.

    Assumes wamp-proto is a sibling directory to autobahn-python:
    ~/work/wamp/autobahn-python/
    ~/work/wamp/wamp-proto/
    """
    current_file = Path(__file__).resolve()
    # Go up from tests/ -> serdes/ -> examples/ -> autobahn-python/ -> wamp/
    autobahn_root = current_file.parent.parent.parent.parent
    wamp_proto = autobahn_root.parent / "wamp-proto"

    if not wamp_proto.exists():
        raise FileNotFoundError(
            f"wamp-proto repository not found at {wamp_proto}. "
            "Please ensure wamp-proto is in the same parent directory as autobahn-python."
        )

    return wamp_proto


def load_test_vector(relative_path: str) -> Dict[str, Any]:
    """
    Load a test vector JSON file from wamp-proto/testsuite/

    Args:
        relative_path: Path relative to testsuite/, e.g. "singlemessage/basic/publish.json"

    Returns:
        Parsed JSON test vector
    """
    wamp_proto = get_wamp_proto_path()
    test_vector_path = wamp_proto / "testsuite" / relative_path

    if not test_vector_path.exists():
        raise FileNotFoundError(f"Test vector not found: {test_vector_path}")

    with open(test_vector_path, 'r') as f:
        return json.load(f)


def get_serializer_ids() -> List[str]:
    """
    Get list of all WAMP serializer IDs to test.

    Returns:
        List of serializer IDs (e.g., ["json", "msgpack", "cbor", ...])
    """
    from autobahn.wamp.serializer import SERID_TO_OBJSER
    return sorted(SERID_TO_OBJSER.keys())


def bytes_from_hex(hex_string: str) -> bytes:
    """Convert hex string to bytes"""
    return bytes.fromhex(hex_string)


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string"""
    return data.hex()


def validate_message_with_code(msg: Any, validation_code: str) -> None:
    """
    Validate a message using embedded Python code.

    The validation code is executed with 'msg' in scope.
    Any assertion failures will raise AssertionError.

    Args:
        msg: Deserialized WAMP message object
        validation_code: Python code string with assertions
    """
    # Create namespace with msg available
    namespace = {'msg': msg}

    # Execute validation code
    try:
        exec(validation_code, namespace)
    except AssertionError as e:
        # Re-raise with line number context if possible
        if not str(e):
            # Empty assertion - add context
            import traceback
            tb_lines = traceback.format_exc().split('\n')
            # Find the line that failed
            for line in tb_lines:
                if 'assert' in line.lower():
                    raise AssertionError(f"Assertion failed: {line.strip()}") from e
        raise


def construct_message_with_code(construction_code: str) -> Any:
    """
    Construct a WAMP message using embedded Python code.

    The construction code should create a variable named 'msg'.

    Args:
        construction_code: Python code string that creates 'msg'

    Returns:
        Constructed WAMP message object
    """
    namespace = {}

    # Execute construction code
    exec(construction_code, namespace)

    # Extract the constructed message
    if 'msg' not in namespace:
        raise ValueError("Construction code must create a variable named 'msg'")

    return namespace['msg']


def matches_any_byte_representation(
    actual_bytes: bytes,
    expected_variants: List[Dict[str, str]]
) -> bool:
    """
    Check if actual bytes match any of the expected byte representations.

    This implements the "at least one" semantics for non-bijective serialization.

    Args:
        actual_bytes: Serialized bytes to check
        expected_variants: List of byte representations (each with 'bytes' or 'bytes_hex')

    Returns:
        True if actual_bytes matches at least one expected variant
    """
    for variant in expected_variants:
        if 'bytes_hex' in variant:
            expected = bytes_from_hex(variant['bytes_hex'])
            if actual_bytes == expected:
                return True

        if 'bytes' in variant:
            # For JSON serializer, the 'bytes' field is the string representation
            # We need to encode it to bytes for comparison
            expected = variant['bytes'].encode('utf-8')
            if actual_bytes == expected:
                return True

    return False


def validates_with_any_code(
    msg: Any,
    validation_codes: List[str]
) -> Optional[str]:
    """
    Try to validate message with any of the validation code blocks.

    This implements the "at least one" semantics for validation.

    Args:
        msg: Deserialized WAMP message object
        validation_codes: List of validation code strings

    Returns:
        None if validation passed with at least one code block,
        or error message string if all validations failed
    """
    errors = []

    for idx, code in enumerate(validation_codes):
        try:
            validate_message_with_code(msg, code)
            return None  # Success!
        except AssertionError as e:
            # Include code snippet for debugging
            code_preview = code[:200] + "..." if len(code) > 200 else code
            errors.append(f"Validation block {idx}: {e}\n  Code: {code_preview}")
        except Exception as e:
            code_preview = code[:200] + "..." if len(code) > 200 else code
            errors.append(f"Validation block {idx} error: {e}\n  Code: {code_preview}")

    # All validation attempts failed
    return "; ".join(errors)
