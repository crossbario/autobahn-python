"""
WAMP Serialization/Deserialization (SerDes) Tests

This test suite validates WAMP message serialization and deserialization
correctness using machine-readable test vectors from the wamp-proto repository.

Test Dimensions:
1. Performance - Measured by benchmarks (see examples/benchmarks/serialization/)
2. Single-serializer roundtrip correctness - Each serializer preserves message attributes
3. Cross-serializer preservation - Message attributes preserved across different serializers

Test vectors are loaded from: wamp-proto/testsuite/
"""
