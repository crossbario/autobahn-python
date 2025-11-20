# FlatBuffers Implementation - Remaining Work

## Status: 9/25 messages complete (36%)

Last updated: 2025-11-20
Branch: `fix_1764`

## What's Been Completed

### Architecture ✅
- Dual-serializer architecture implemented
- `PAYLOAD_SERIALIZER_ID` property added to `ISerializer` interface
- `serialize_payload()` helper method in Serializer base class
- Back-reference from `IObjectSerializer` to parent `ISerializer`
- `Message.build()` signature updated with `serializer` parameter
- Comprehensive documentation in `docs/wamp/flatbuffers-schema.rst`

### Messages with cast() and build() ✅ (9 complete)
1. **Error** - Error responses with payload
2. **Publish** - Event publication with payload
3. **Published** - Publication acknowledgment (simple: session, request, publication)
4. **Event** - Event delivery with payload
5. **Call** - RPC invocation with payload
6. **Result** - RPC result with payload
7. **Invocation** - RPC invocation to callee with payload
8. **Yield** - RPC yield from callee with payload
9. **Subscribed** - Subscription acknowledgment (simple: session, request, subscription)

## What Remains (16 messages)

### Group 1: Simple Acknowledgments (3 messages)
**Pattern:** Same as Published/Subscribed - just session, request, + one ID field

#### Unsubscribed
- Fields: `session`, `request`, `subscription`
- FlatBuffers: `message_fbs.Unsubscribed`, `UnsubscribedGen`
- Template: Copy Published, replace `publication` → `subscription`

#### Registered
- Fields: `session`, `request`, `registration`
- FlatBuffers: `message_fbs.Registered`, `RegisteredGen`
- Template: Copy Published, replace `publication` → `registration`

#### Unregistered
- Fields: `session`, `request`, `registration`
- FlatBuffers: `message_fbs.Unregistered`, `UnregisteredGen`
- Template: Copy Published, replace `publication` → `registration`

### Group 2: Request Messages (3 messages)
**Pattern:** request, topic/procedure URI, options dict

#### Subscribe
- Fields: `request`, `topic`, `match`, `get_retained`, `forward_for`
- FlatBuffers schema: `autobahn/wamp/flatbuffers/pubsub.fbs`
- Similar to Publish but simpler (no payload)
- Options: match (enum), get_retained (bool), forward_for

#### Unsubscribe
- Fields: `request`, `subscription`, `forward_for`
- FlatBuffers schema: `autobahn/wamp/flatbuffers/pubsub.fbs`
- Very simple - just IDs and optional forward_for

#### Register
- Fields: `request`, `procedure`, `match`, `invoke`, `concurrency`, `forward_for`
- FlatBuffers schema: `autobahn/wamp/flatbuffers/rpc.fbs`
- Options: match (enum), invoke (enum), concurrency (int), forward_for

### Group 3: Control Messages (3 messages)

#### EventReceived
- Fields: `subscription`, `publication`
- FlatBuffers schema: `autobahn/wamp/flatbuffers/pubsub.fbs`
- Very simple - just two IDs (no session or request!)
- Template: Simpler than Published (only 2 fields)

#### Cancel
- Fields: `request`, `mode`, `forward_for`
- FlatBuffers schema: `autobahn/wamp/flatbuffers/rpc.fbs`
- Options: mode (enum), forward_for

#### Interrupt
- Fields: `request`, `mode`, `forward_for`
- FlatBuffers schema: `autobahn/wamp/flatbuffers/rpc.fbs`
- Nearly identical to Cancel

### Group 4: Session Messages (6 messages)
**Pattern:** More complex with nested structures

#### Hello
- Fields: `realm`, `roles` (ClientRoles struct), `authmethods`, `authid`, `authrole`, `authextra`, `resumable`, `resume_session`, `resume_token`
- FlatBuffers schema: `autobahn/wamp/flatbuffers/session.fbs`
- **Complex:** roles is `ClientRoles` struct (publisher, subscriber, caller, callee features)
- Need to serialize/deserialize ClientRoles properly
- authmethods is `[AuthMethod]` enum array
- authextra is dict → needs serialization

#### Welcome
- Fields: `session`, `roles` (RouterRoles struct), `realm`, `authid`, `authrole`, `authmethod`, `authprovider`, `authextra`, `resumed`, `resumable`, `resume_token`
- FlatBuffers schema: `autobahn/wamp/flatbuffers/session.fbs`
- **Complex:** roles is `RouterRoles` struct (broker, dealer features)
- Similar to Hello but RouterRoles instead of ClientRoles

#### Abort
- Fields: `reason` (URI), `message` (string)
- FlatBuffers schema: `autobahn/wamp/flatbuffers/session.fbs`
- **Simple:** just reason and message strings

#### Challenge
- Fields: `method` (string), `extra` (dict)
- FlatBuffers schema: `autobahn/wamp/flatbuffers/session.fbs`
- extra dict needs serialization (CBOR-encoded in FlatBuffers)

#### Authenticate
- Fields: `signature` (string), `extra` (dict)
- FlatBuffers schema: `autobahn/wamp/flatbuffers/session.fbs`
- extra dict needs serialization

#### Goodbye
- Fields: `reason` (URI), `message` (string)
- FlatBuffers schema: `autobahn/wamp/flatbuffers/session.fbs`
- Nearly identical to Abort

## Implementation Pattern

Each message needs:

### 1. Update `__init__` to support `from_fbs`
```python
def __init__(self, field1=None, field2=None, ..., from_fbs=None):
    assert field1 is None or type(field1) == expected_type
    # ... assertions for all fields

    Message.__init__(self, from_fbs=from_fbs)
    self._field1 = field1
    self._field2 = field2
```

### 2. Add lazy deserialization properties
```python
@property
def field1(self):
    if self._field1 is None and self._from_fbs:
        self._field1 = self._from_fbs.Field1()
    return self._field1
```

### 3. Add `cast()` static method
```python
@staticmethod
def cast(buf):
    return MessageName(from_fbs=message_fbs.MessageName.GetRootAsMessageName(buf, 0))
```

### 4. Add `build()` method
```python
def build(self, builder, serializer=None):
    # Serialize string fields
    field_str = self.field_str
    if field_str:
        field_str = builder.CreateString(field_str)

    # Serialize byte vector fields (payload, args, kwargs)
    field_bytes = self.field_bytes
    if field_bytes:
        if serializer:
            field_bytes = builder.CreateByteVector(serializer.serialize_payload(field_bytes))
        else:
            field_bytes = builder.CreateByteVector(cbor2.dumps(field_bytes))

    # Start message
    message_fbs.MessageNameGen.MessageNameStart(builder)

    # Add fields
    if self.session:
        message_fbs.MessageNameGen.MessageNameAddSession(builder, self.session)
    if field_str:
        message_fbs.MessageNameGen.MessageNameAddFieldStr(builder, field_str)
    # ... add all fields

    # End and return
    msg = message_fbs.MessageNameGen.MessageNameEnd(builder)
    return msg
```

## Testing Strategy

After implementation, test with:

```bash
# Run SerDes conformance tests
.venvs/cpy311/bin/pytest examples/serdes/tests/ -v

# Test specific messages
.venvs/cpy311/bin/pytest examples/serdes/tests/test_publish.py -v
.venvs/cpy311/bin/pytest examples/serdes/tests/test_event.py -v

# Add new tests for all message types
# Copy pattern from test_publish.py and test_event.py
```

## Files to Modify

1. **autobahn/wamp/message.py** - Add cast() and build() to 16 message classes
2. **examples/serdes/tests/** - Add comprehensive test coverage for all message types

## Key Reference Files

- **Existing implementations:** Search for `def cast(buf):` and `def build(self, builder` in message.py to see examples
- **FlatBuffers schemas:** `autobahn/wamp/flatbuffers/*.fbs`
- **Generated FlatBuffers Python:** `autobahn/wamp/gen/wamp/proto/*.py`
- **Documentation:** `docs/wamp/flatbuffers-schema.rst`

## Systematic Approach

1. **Implement Groups 1-3 first (9 messages):** Simple, template-based
   - Can batch-generate implementations using script
   - Test as a group

2. **Then Group 4 (6 messages):** More complex
   - Require careful handling of nested structures
   - Test individually

3. **Comprehensive testing:**
   - Create test files for all message types
   - Verify serialization round-trip
   - Test with different payload serializers (CBOR, JSON, FlatBuffers)

## Success Criteria

- ✅ All 25 WAMP message types have cast() and build() methods
- ✅ All messages support from_fbs lazy deserialization
- ✅ All messages can serialize to/from FlatBuffers correctly
- ✅ Comprehensive test coverage in examples/serdes/tests/
- ✅ All tests pass for CPython and PyPy
- ✅ CI/CD passes on GitHub

## Notes

- The architecture is proven and working for 9 messages
- The pattern is systematic and clear
- Groups 1-3 can be implemented quickly (similar patterns)
- Group 4 needs more care (nested structures like ClientRoles/RouterRoles)
- Consider creating a code generation script for Groups 1-3 to ensure consistency
