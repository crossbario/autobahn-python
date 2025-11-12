# WAMP Serialization & Deserialization (SerDes) - Comprehensive Plan

## Vision & Goals

This document outlines a comprehensive approach to **validating correctness** and **measuring performance** of WAMP message serialization and deserialization in Autobahn|Python.

**Key Principle**: Performance matters, but **correctness is foundational**. We must prove that WAMP messages are correctly serialized, deserialized, and preserve all attributes before optimizing for speed.

---

## Dimensions of Testing

### Dimension 1: Performance (✅ Completed - `examples/benchmarks/serialization/`)

**Status**: Basic infrastructure complete with flamegraph generation

**What it measures**:
- Throughput (messages/second) per serializer
- Memory usage patterns (via vmprof profiling)
- Performance characteristics across payload sizes
- CPython vs PyPy comparison

**Current coverage**:
- 7 serializers: JSON, msgpack, CBOR, ubjson, ujson, flatbuffers, cbor2
- 2 payload modes: normal, transparent (passthru)
- 6 payload sizes: empty, small, medium, large, xl, xxl
- Full flamegraph visualization

**Limitations**: Performance tests alone don't prove correctness!

---

### Dimension 2: Single-Serializer Roundtrip Correctness ⚠️ **TODO**

**Goal**: Prove that for each WAMP serializer, the following holds:

```
WAMP Message Object → serialize() → bytes → deserialize() → WAMP Message Object'
```

Where `Object == Object'` for **all attributes**:
- WAMP message type
- All WAMP metadata fields (Options, Details, etc.)
- Complete application payload (args, kwargs)

**Must cover**:
- ✅ All WAMP message types (see below)
- ✅ All WAMP advanced features (publisher exclusion, pattern subscriptions, etc.)
- ✅ Edge cases (empty args, null values, binary data, nested structures)
- ✅ Both payload modes: normal and transparent

**WAMP Message Types to Test**:

**Session Lifecycle**:
- `HELLO` (1)
- `WELCOME` (2)
- `ABORT` (3)
- `GOODBYE` (6)

**Publish & Subscribe**:
- `PUBLISH` (16) - with various Options (exclude_me, eligible, etc.)
- `PUBLISHED` (17)
- `SUBSCRIBE` (32) - with match policies
- `SUBSCRIBED` (33)
- `UNSUBSCRIBE` (34)
- `UNSUBSCRIBED` (35)
- `EVENT` (36) - with various Details

**Remote Procedure Calls**:
- `CALL` (48) - with timeout, progressive results
- `RESULT` (50) - simple and progressive
- `REGISTER` (64) - with invocation policies
- `REGISTERED` (65)
- `UNREGISTER` (66)
- `UNREGISTERED` (67)
- `INVOCATION` (68)
- `YIELD` (70) - simple and progressive
- `ERROR` (8) - for all error contexts

---

### Dimension 3: Cross-Serializer Preservation ⚠️ **TODO**

**Goal**: Prove that WAMP message representation in Autobahn|Python preserves all attributes when crossing serializers.

**Test Pattern**:
```
Object → serialize(json) → bytes_json → deserialize(json) → Object_json
Object → serialize(msgpack) → bytes_msgpack → deserialize(msgpack) → Object_msgpack

Assert: Object_json == Object_msgpack (at Python object level)
```

**Why this matters**: This tests the **abstraction layer** in the WAMP library, not just the serializers. Ensures that the internal representation doesn't lose or corrupt data during serialize/deserialize cycles.

**Must verify**:
- All WAMP metadata preserved
- Application payload preserved (including binary data)
- Works across all 7 serializers
- Works in both normal and transparent modes

---

## "Going Down" - Protocol Specification Foundation

### Machine-Readable Test Vectors ⚠️ **TODO**

**Vision**: Create comprehensive, machine-readable test vectors that become part of the WAMP specification itself.

**Location**: Could live in `wamp-proto` repository as a new appendix

**Structure**:
```
wamp-proto/test-vectors/
├── basic/
│   ├── hello.json
│   ├── welcome.json
│   ├── subscribe.json
│   ├── event.json
│   ├── publish.json
│   ├── call.json
│   ├── result.json
│   └── ...
└── advanced/
    ├── publisher_exclusion.json
    ├── publisher_identification.json
    ├── pattern_based_subscription.json
    ├── progressive_call_results.json
    ├── shared_registration.json
    └── ...
```

**Test Vector Format**:
```json
{
  "description": "EVENT with publisher exclusion disabled",
  "wamp_message_type": "EVENT",
  "wamp_message_code": 36,
  "feature": "basic.pubsub",
  "serialization": "json",
  "bytes": "[36, 5512315355, 4429313566, {}, [], {\"color\": \"orange\", \"sizes\": [23, 42, 7]}]",
  "canonical_bytes_hex": "5b33362c20353531323331353335352c2e2e2e",
  "expected_attributes": {
    "message_type": 36,
    "subscription_id": 5512315355,
    "publication_id": 4429313566,
    "details": {},
    "args": [],
    "kwargs": {
      "color": "orange",
      "sizes": [23, 42, 7]
    }
  },
  "language_checks": {
    "python": "assert msg.subscription == 5512315355 and msg.kwargs['color'] == 'orange'",
    "javascript": "assert(msg.subscription === 5512315355 && msg.kwargs.color === 'orange')"
  }
}
```

**Benefits**:
- Cross-implementation compatibility testing
- Prevents regressions
- Guides new implementers
- Forces specification precision
- Enables automated conformance testing

**Example: Publisher Exclusion Test Vector**:
```json
{
  "description": "PUBLISH with publisher exclusion disabled",
  "wamp_message_type": "PUBLISH",
  "wamp_message_code": 16,
  "feature": "advanced.pubsub.publisher_exclusion",
  "serialization": "json",
  "bytes": "[16, 239714735, {\"exclude_me\": false}, \"com.myapp.mytopic1\", [\"Hello, world!\"]]",
  "expected_attributes": {
    "request_id": 239714735,
    "exclude_me": false,
    "topic": "com.myapp.mytopic1",
    "args": ["Hello, world!"]
  },
  "semantic_note": "When exclude_me=false, the publisher WILL receive EVENT if it is subscribed to the topic"
}
```

### Multi-Message Semantic Test Vectors 🔮 **Future**

**Beyond single messages**: WAMP semantics often span multiple messages across sessions.

**Example: Publisher Exclusion Semantics**:
```json
{
  "description": "Publisher Exclusion - Disabled (exclude_me=false)",
  "feature": "advanced.pubsub.publisher_exclusion",
  "sessions": [
    {
      "session_id": "session_1",
      "role": "publisher_and_subscriber"
    }
  ],
  "sequence": [
    {
      "from": "session_1",
      "to": "router",
      "message": {
        "type": "SUBSCRIBE",
        "topic": "com.myapp.topic1"
      }
    },
    {
      "from": "router",
      "to": "session_1",
      "message": {
        "type": "SUBSCRIBED"
      }
    },
    {
      "from": "session_1",
      "to": "router",
      "message": {
        "type": "PUBLISH",
        "options": {"exclude_me": false},
        "topic": "com.myapp.topic1"
      }
    },
    {
      "from": "router",
      "to": "session_1",
      "message": {
        "type": "EVENT",
        "expected": true,
        "assertion": "Publisher MUST receive EVENT because exclude_me=false"
      }
    }
  ]
}
```

**This tests**: Router behavior, not just client library serialization!

---

## "Going Up" - Implementation-Level Concerns

### Advanced Feature Testing ⚠️ **TODO**

#### 1. Message Batching (`transport_batched_websocket.md`)

**What it is**: Multiple WAMP messages sent in single WebSocket frame

**Testing requirements**:
- ✅ Message boundaries preserved
- ✅ Serialization correctness maintained across batch
- ✅ Performance: batching reduces overhead
- ✅ Works with all serializers

**Test pattern**:
```python
messages = [SUBSCRIBE(...), PUBLISH(...), CALL(...)]
batched_bytes = batch_serialize(messages)
parsed_messages = batch_deserialize(batched_bytes)
assert messages == parsed_messages
```

#### 2. Payload Passthru Mode (`payload_passthru_mode.md`)

**What it is**: Router treats `args`/`kwargs` as opaque bytes, doesn't deserialize application payload

**Key distinction**:
- **Normal mode**: Router deserializes entire WAMP message including payload
- **Transparent mode**: Router only deserializes WAMP metadata, payload stays as bytes

**Why it matters**:
- Performance: Router doesn't pay deserialization cost for payload
- Enables E2E encryption (router can't read encrypted payload)
- Different code paths in implementation

**Testing requirements**:
- ✅ Router correctly parses WAMP metadata (Options, Details)
- ✅ Router does NOT parse application payload
- ✅ Payload bytes preserved exactly: `PUBLISH.args → EVENT.args` (memcpy)
- ✅ WAMP routing logic still works (exclude_me, eligible, etc.)

**Test pattern**:
```python
# Client 1: Publish with passthru mode
payload_bytes = b'\x00\x01\x02...'  # Opaque bytes
publish = Publish(
    topic="com.test",
    args_bytes=payload_bytes,  # Not deserialized args
    options=PublishOptions(exclude_me=False)
)

# Router: Should NOT deserialize payload_bytes
# Router: MUST parse options.exclude_me

# Client 2: Receives EVENT
event = receive_event()
assert event.args_bytes == payload_bytes  # Byte-for-byte match
```

#### 3. Payload End-to-End Encryption (`e2e_encryption.md`)

**What it is**: Application payload encrypted by publisher, decrypted by subscriber. Router cannot read it.

**Built on**: Payload passthru mode

**Implementation requirements**:
- Router processes WAMP metadata (for routing)
- Router NEVER deserializes encrypted payload
- Encrypted bytes copied directly: `PUBLISH.args → EVENT.args`

**Testing requirements**:
- ✅ Encrypted payload survives router transit unmodified (byte-for-byte)
- ✅ Router still applies routing logic (exclusions, eligible lists)
- ✅ Subscriber can decrypt payload
- ✅ Performance: Router doesn't pay crypto or deserialization cost

**Test pattern**:
```python
# Publisher
plaintext = {"secret": "data"}
encrypted = encrypt(plaintext, key)
publish = Publish(topic="com.secure", args_bytes=encrypted)

# Router (should not decrypt or deserialize)
# Routing logic still works based on Options

# Subscriber
event = receive_event()
decrypted = decrypt(event.args_bytes, key)
assert decrypted == plaintext
```

#### 4. FlatBuffers Dual Usage

**Two orthogonal uses**:

**Level 1**: FlatBuffers as WAMP message serializer
- Serializes entire WAMP message (like JSON, msgpack do)
- Used in transport serializer negotiation

**Level 2**: FlatBuffers for application payload
- User's application data uses FlatBuffers schema
- Orthogonal to WAMP message serializer choice
- Can use FlatBuffers payload with JSON message serializer (and vice versa)

**Testing requirements**:
- ✅ FlatBuffers message serializer works correctly
- ✅ FlatBuffers payload works with all message serializers
- ✅ Zero-copy optimizations work (FlatBuffers main benefit)
- ✅ Performance benchmarks show zero-copy advantage

**Test pattern**:
```python
# Level 1: FlatBuffers as message serializer
serializer = FlatBuffersSerializer()
msg = Publish(...)
bytes = serializer.serialize(msg)
msg2 = serializer.deserialize(bytes)
assert msg == msg2

# Level 2: FlatBuffers payload with different message serializers
fb_payload = FlatBufferObject(...)
publish = Publish(topic="com.test", args=[fb_payload])

# Try with all message serializers
for serializer in [JsonSerializer(), MsgPackSerializer(), FlatBuffersSerializer()]:
    bytes = serializer.serialize(publish)
    msg = serializer.deserialize(bytes)
    assert msg.args[0] == fb_payload  # Payload preserved
```

---

## Implementation Plan

### Strategic Approach: Vertical Slice Methodology

**Philosophy**: Prove the entire pipeline end-to-end with ONE example before scaling horizontally.

**Why Vertical Slice?**
1. **Early Validation**: Discover design issues with real implementation
2. **Fast Feedback**: Working tests provide immediate value
3. **Template Creation**: First example becomes the pattern for all others
4. **Risk Reduction**: Find problems before investing in full coverage
5. **Iterative Refinement**: Adjust based on lessons learned

**Vertical Slice Definition**:
- Pick ONE WAMP message type (e.g., PUBLISH)
- Implement ENTIRE pipeline:
  - Test vector in wamp-proto repository ✅
  - Test framework in autobahn-python ✅
  - All three test dimensions ✅
  - Local pytest execution ✅
  - GitHub Actions CI/CD integration (next)
- Get it working, polished, and reviewed
- THEN scale to all other message types

### Phase 1: Foundation ✅ COMPLETED
- [x] Performance benchmarking infrastructure (`examples/benchmarks/serialization/`)
- [x] Flamegraph visualization
- [x] Multi-serializer testing
- [x] Normal vs Transparent mode benchmarks

### Phase 2: Vertical Slice - PUBLISH Message ✅ COMPLETED

**Rationale**: PUBLISH is a good starting point because:
- Representative complexity (Options dict, args, kwargs)
- Used in common workflows
- Tests both basic and advanced features (publisher exclusion, etc.)

**Implementation**:
- [x] Create test vector schema in wamp-proto (Issue #556, PR #557)
- [x] Implement testsuite/singlemessage/basic/publish.json ✅
- [x] Design test framework structure in autobahn-python ✅
- [x] Implement examples/serdes/tests/ directory ✅
  - [x] conftest.py - pytest fixtures and configuration
  - [x] utils.py - helper functions (load_test_vector, validate_message, etc.)
  - [x] test_publish.py - complete test suite
- [x] Implement all three test dimensions:
  - [x] Dimension 2: Single-serializer roundtrip correctness
    - [x] test_publish_deserialize_from_bytes
    - [x] test_publish_serialize_to_bytes
    - [x] test_publish_roundtrip
  - [x] Dimension 3: Cross-serializer preservation
    - [x] test_publish_cross_serializer_preservation
  - [x] Expected attributes validation
    - [x] test_publish_expected_attributes
- [x] Validate locally with pytest (20/20 tests passing)
- [x] Document design decisions and lessons learned

**Key Technical Discoveries**:
1. **txaio initialization required**: Must call `txaio.use_asyncio()` before importing autobahn serializers
2. **Autobahn serializer API**: `serialize()` returns `(bytes, is_binary)`, `unserialize()` returns `List[IMessage]`
3. **Publish message structure**: No `options` attribute - individual option fields instead
4. **Non-bijective serialization**: JSON has multiple valid representations (whitespace variations)
5. **"At least one" semantics**: Critical for handling serialization variants

**Test Results**:
- ✅ 20 tests passing (JSON, msgpack serializers)
- ✅ All three dimensions validated
- ✅ Template established for other message types

### Phase 3: Horizontal Scaling - All Basic Message Types ⚠️ **IN PROGRESS**

**Approach**: Now that the vertical slice is proven, scale horizontally using the established template.

**Priority Order** (by usage frequency and complexity):
1. [x] PUBLISH (16) - ✅ Complete (vertical slice)
2. [ ] EVENT (36) - Subscriber receives
3. [ ] SUBSCRIBE (32) - Simple subscription
4. [ ] SUBSCRIBED (33) - Subscription confirmed
5. [ ] CALL (48) - RPC invocation
6. [ ] RESULT (50) - RPC result
7. [ ] REGISTER (64) - Procedure registration
8. [ ] REGISTERED (65) - Registration confirmed
9. [ ] INVOCATION (68) - Callee receives
10. [ ] YIELD (70) - Callee responds
11. [ ] HELLO (1) - Session establishment
12. [ ] WELCOME (2) - Session accepted
13. [ ] UNSUBSCRIBE (34), UNSUBSCRIBED (35)
14. [ ] UNREGISTER (66), UNREGISTERED (67)
15. [ ] GOODBYE (6) - Session close
16. [ ] ABORT (3) - Session rejected
17. [ ] ERROR (8) - Generic error (all contexts)
18. [ ] PUBLISHED (17) - Acknowledgment (if requested)

**For Each Message Type**:
1. Create test vector in wamp-proto: `testsuite/singlemessage/basic/<message>.json`
2. Add tests in autobahn-python: `examples/serdes/tests/test_<message>.py`
3. Run pytest locally
4. Commit and push

### Phase 4: Advanced Features & Edge Cases ⚠️ **TODO**
- [ ] Multiple samples per message type (args only, kwargs only, both, payload)
- [ ] Advanced profile options:
  - [ ] Publisher exclusion/inclusion (PUBLISH options)
  - [ ] Pattern-based subscriptions (SUBSCRIBE match policies)
  - [ ] Shared registration (REGISTER invocation policies)
  - [ ] Progressive call results (CALL/RESULT)
  - [ ] Caller/publisher identification (Details)
- [ ] Edge cases:
  - [ ] Empty args/kwargs
  - [ ] Null values
  - [ ] Binary data in payload
  - [ ] Deeply nested structures
  - [ ] Unicode handling
  - [ ] Large payloads

### Phase 5: Additional Serializers ⚠️ **TODO**
- [ ] Add CBOR byte representations to test vectors
- [ ] Add UBJSON byte representations to test vectors
- [ ] Test flatbuffers (if applicable to test vector format)
- [ ] Ensure all serializers pass all tests

### Phase 6: CI/CD Integration ⚠️ **TODO**
- [ ] Add GitHub Actions workflow for serdes tests
- [ ] Test on CPython 3.9, 3.10, 3.11, 3.12, 3.13
- [ ] Test on PyPy 3.9, 3.10, 3.11
- [ ] Test on multiple platforms (Linux, macOS, Windows)
- [ ] Add coverage reporting
- [ ] Badge in README

### Phase 7: Protocol Test Vectors Expansion 🔮 **Future**
- [ ] Multi-message sequences (singlesession/)
- [ ] Multi-session interactions (multisession/)
- [ ] Router behavior validation (requires Crossbar.io)
- [ ] Advanced feature semantics (publisher exclusion, pattern matching, etc.)

### Phase 5: Advanced Features ⚠️ **TODO**
- [ ] Message batching tests
- [ ] Payload passthru mode validation
- [ ] E2E encryption roundtrip tests
- [ ] FlatBuffers dual-usage testing

### Phase 6: Multi-Message Semantics 🔮 **Future**
- [ ] Design multi-message test framework
- [ ] Implement session simulation
- [ ] Test router behavior (requires Crossbar.io integration)
- [ ] Validate all advanced feature semantics

---

## Success Criteria

### Correctness ✅
- All WAMP message types roundtrip correctly in all serializers
- All WAMP metadata preserved across serializers
- Application payload preserved bit-for-bit
- Passthru mode verified (router doesn't deserialize payload)
- E2E encryption works correctly

### Performance 📊
- Benchmarks show expected characteristics
- Flamegraphs identify optimization opportunities
- Zero-copy implementations (FlatBuffers) show measurable benefit
- Passthru mode shows performance advantage

### Spec Conformance 📖
- Test vectors match WAMP spec examples
- All advanced features tested
- Multi-message semantics validated (future)

### Engineering Rigor 🔧
- Automated test suite prevents regressions
- Clear documentation of coverage
- Reproducible benchmarks
- Cross-implementation compatibility (future)

---

## Next Steps

1. **Immediate**: Complete this planning document with user feedback
2. **Short-term**: Implement Phase 2 (single-serializer correctness)
3. **Medium-term**: Implement Phase 3 (cross-serializer correctness)
4. **Long-term**: Contribute test vectors to WAMP spec

---

## Questions & Discussion

- Is the test vector format appropriate?
- Should we prioritize specific WAMP message types or features?
- How should we handle router behavior testing (requires Crossbar.io)?
- Should test vectors live in wamp-proto or autobahn-python first?
