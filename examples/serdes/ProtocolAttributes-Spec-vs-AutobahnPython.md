# WAMP Protocol Attributes: Spec vs Autobahn-Python Implementation

This document compares WAMP protocol message attributes as defined in the WAMP specification
against their implementation in Autobahn-Python.

## Summary Matrix

| Message Type | Matched | Spec-Only | Implementation-Only | Naming Differences |
|--------------|---------|-----------|---------------------|-------------------|
| PUBLISH.Options      | 9  | 1 (+4 ppt_*) | 2 (+3 enc_*) | E2EE: ppt_* vs enc_* |
| EVENT.Details        | 5  | 1 (+4 ppt_*) | 3 (+3 enc_*) | E2EE: ppt_* vs enc_* |
| SUBSCRIBE.Options    | 2  | 0           | 1            | None |
| SUBSCRIBED           | N/A | N/A         | N/A          | No Options/Details |
| PUBLISHED            | N/A | N/A         | N/A          | No Options/Details |
| UNSUBSCRIBE.Options  | 0  | 0           | 1            | None |
| UNSUBSCRIBED         | N/A | N/A         | N/A          | No Details (basic) |

## PUBLISH.Options

### Matched Attributes (9)

These attributes appear in both the spec and implementation with consistent naming and types:

| Attribute | Type | Spec Section | Implementation |
|-----------|------|--------------|----------------|
| acknowledge | bool | Basic Profile: publish_subscribe.md | message.py:2792-2801 |
| exclude_me | bool | Advanced: pubsub_publisher_exclusion.md | message.py:2803-2812 |
| exclude | list[int] | Advanced: pubsub_subscriber_blackwhite_listing.md | message.py:2814-2833 |
| exclude_authid | list[string] | Advanced: pubsub_subscriber_blackwhite_listing.md | message.py:2835-2858 |
| exclude_authrole | list[string] | Advanced: pubsub_subscriber_blackwhite_listing.md | message.py:2860-2883 |
| eligible | list[int] | Advanced: pubsub_subscriber_blackwhite_listing.md | message.py:2885-2904 |
| eligible_authid | list[string] | Advanced: pubsub_subscriber_blackwhite_listing.md | message.py:2906-2929 |
| eligible_authrole | list[string] | Advanced: pubsub_subscriber_blackwhite_listing.md | message.py:2931-2954 |
| retain | bool | Advanced: pubsub_event_retention.md | message.py:2956-2964 |

### Spec-Only Attributes (1)

These attributes are defined in the spec but NOT implemented in Autobahn-Python:

| Attribute | Type | Spec Section | Notes |
|-----------|------|--------------|-------|
| disclose_me | bool | Advanced: pubsub_publisher_identification.md | NOT implemented |

### Implementation-Only Attributes (2)

These attributes are implemented in Autobahn-Python but NOT defined in the WAMP spec:

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| transaction_hash | str | message.py:2966-2976 | Application-level transaction ID for throttling/deduplication |
| forward_for | list[dict] | message.py:2978-2988 | Router-to-router forwarding chain |

### Naming Differences: Payload Passthru Mode (E2EE)

The spec defines 4 attributes with `ppt_*` prefix (Payload Passthru), while
Autobahn-Python implements 3 attributes with `enc_*` prefix (Encryption).

**WAMP Spec (Advanced: payload_passthru_mode.md):**
- `ppt_scheme|string` - Required: Payload schema identifier (e.g., "wamp", "mqtt")
- `ppt_serializer|string` - Optional: Serializer used (e.g., "cbor", "flatbuffers", "native")
- `ppt_cipher|string` - Optional: Encryption cipher (e.g., "xsalsa20poly1305", "aes256gcm")
- `ppt_keyid|string` - Optional: Encryption key identifier

**Autobahn-Python Implementation (message.py:2737-2759):**
- `enc_algo|str` - Encryption algorithm (mapped to ppt_cipher?)
- `enc_key|str` - Encryption key (mapped to ppt_keyid?)
- `enc_serializer|str` - Payload serializer (mapped to ppt_serializer?)

**Analysis:**
- Implementation predates current spec terminology
- Missing `ppt_scheme` (required in spec)
- `enc_algo` likely maps to `ppt_cipher`
- `enc_key` likely maps to `ppt_keyid`
- `enc_serializer` likely maps to `ppt_serializer`

## EVENT.Details

### Matched Attributes (5)

These attributes appear in both the spec and implementation with consistent naming and types:

| Attribute | Type | Spec Section | Implementation |
|-----------|------|--------------|----------------|
| publisher | int | Advanced: pubsub_publisher_identification.md | message.py:4203-4212 |
| publisher_authid | str | Advanced: pubsub_publisher_identification.md | message.py:4214-4223 |
| publisher_authrole | str | Advanced: pubsub_publisher_identification.md | message.py:4225-4234 |
| topic | uri | Advanced: pubsub_pattern_based_subscription.md | message.py:4236-4245 |
| retained | bool | Advanced: pubsub_event_retention.md | message.py:4247-4254 |

### Spec-Only Attributes (1)

These attributes are defined in the spec but NOT implemented in Autobahn-Python:

| Attribute | Type | Spec Section | Notes |
|-----------|------|--------------|-------|
| trustlevel | int | Advanced: pubsub_publication_trustlevels.md | NOT implemented |

### Implementation-Only Attributes (3)

These attributes are implemented in Autobahn-Python but NOT defined in the WAMP spec:

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| transaction_hash | str | message.py:4256-4265 | Application-level transaction ID |
| x_acknowledged_delivery | bool | message.py:4267-4274 | Event acknowledgement flag (FIXME comment in code) |
| forward_for | list[dict] | message.py:4276-4294 | Router-to-router forwarding chain |

### Naming Differences: Payload Passthru Mode (E2EE)

Same as PUBLISH.Options - the spec uses `ppt_*` prefix while implementation uses `enc_*` prefix.

**WAMP Spec (Advanced: payload_passthru_mode.md):**
- `ppt_scheme|string`
- `ppt_serializer|string`
- `ppt_cipher|string`
- `ppt_keyid|string`

**Autobahn-Python Implementation (message.py:4158-4178):**
- `enc_algo|str`
- `enc_key|str`
- `enc_serializer|str`

## SUBSCRIBE.Options

### Matched Attributes (2)

These attributes appear in both the spec and implementation with consistent naming and types:

| Attribute | Type | Spec Section | Implementation |
|-----------|------|--------------|----------------|
| match | string | Advanced: pubsub_pattern_based_subscription.md | message.py:3232-3252 |
| get_retained | bool | Advanced: pubsub_event_retention.md | message.py:3254-3262 |

**match values:**
- `"exact"` (default) - Exact topic match
- `"prefix"` - Prefix-based pattern matching
- `"wildcard"` - Wildcard-based pattern matching

**get_retained:**
- Requests retained message if available when subscribing

### Spec-Only Attributes (0)

All spec-defined SUBSCRIBE.Options attributes are implemented in Autobahn-Python.

### Implementation-Only Attributes (1)

These attributes are implemented in Autobahn-Python but NOT defined in the WAMP spec:

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| forward_for | list[dict] | message.py:3264-3282 | Router-to-router forwarding chain |

**forward_for structure:**
```python
[{
    "session": int,      # Session ID
    "authid": str,       # Authentication ID
    "authrole": str      # Authentication role
}]
```

### Analysis

SUBSCRIBE.Options has excellent spec compliance:
- ✅ All spec-defined attributes implemented
- ✅ Consistent naming with spec
- ✅ Only 1 implementation-specific attribute (`forward_for` for router-to-router links)
- ✅ No E2EE complexity (unlike PUBLISH/EVENT)

## SUBSCRIBED

SUBSCRIBED is an acknowledgment message sent by a Router to a Client to confirm a subscription.

**Message Format**: `[SUBSCRIBED, SUBSCRIBE.Request|id, Subscription|id]`

**WAMP Spec** (Basic Profile: publish_subscribe.md):
- `SUBSCRIBE.Request|id` (int) - The ID from the original SUBSCRIBE request
- `Subscription|id` (int) - The subscription ID assigned by the Broker

**Autobahn-Python Implementation** (message.py:3323-3372):
- `request` (int) - The request ID of the original SUBSCRIBE request
- `subscription` (int) - The subscription ID for the subscribed topic

### Analysis

SUBSCRIBED has perfect spec compliance:
- ✅ Simple acknowledgment message with no Options or Details dictionaries
- ✅ Only contains two ID fields as defined in spec
- ✅ Attribute names match spec semantics exactly
- ✅ No implementation-specific extensions
- ✅ Message format: `[33, request_id, subscription_id]`

**Example** (from test vectors):
```json
{
  "description": "SUBSCRIBED acknowledgment",
  "wmsg": [33, 713845233, 5512315355],
  "expected_attributes": {
    "message_type": 33,
    "request_id": 713845233,
    "subscription_id": 5512315355
  }
}
```

## PUBLISHED

PUBLISHED is an acknowledgment message sent by a Router to a Client to confirm a publication (when `PUBLISH.Options.acknowledge` is true).

**Message Format**: `[PUBLISHED, PUBLISH.Request|id, Publication|id]`

**WAMP Spec** (Basic Profile: publish_subscribe.md):
- `PUBLISH.Request|id` (int) - The ID from the original PUBLISH request
- `Publication|id` (int) - The publication ID assigned by the Broker

**Autobahn-Python Implementation** (message.py:3067-3116):
- `request` (int) - The request ID of the original PUBLISH request
- `publication` (int) - The publication ID for the published event

### Analysis

PUBLISHED has perfect spec compliance:
- ✅ Simple acknowledgment message with no Options or Details dictionaries
- ✅ Only contains two ID fields as defined in spec
- ✅ Attribute names match spec semantics exactly
- ✅ No implementation-specific extensions
- ✅ Message format: `[17, request_id, publication_id]`

**Example** (from test vectors):
```json
{
  "description": "PUBLISHED acknowledgment",
  "wmsg": [17, 239714735, 4429313566],
  "expected_attributes": {
    "message_type": 17,
    "request_id": 239714735,
    "publication_id": 4429313566
  }
}
```

## UNSUBSCRIBE.Options

UNSUBSCRIBE is a message from Subscriber to Broker to unsubscribe from a topic.

**Message Format**:
- `[UNSUBSCRIBE, Request|id, SUBSCRIBED.Subscription|id]`
- `[UNSUBSCRIBE, Request|id, SUBSCRIBED.Subscription|id, Options|dict]`

**WAMP Spec** (Basic Profile: publish_subscribe.md):
- No Options defined in spec

**Autobahn-Python Implementation** (message.py:3391-3505):
- `forward_for` (list[dict]) - Router-to-router forwarding chain

### Matched Attributes (0)

No attributes defined in spec.

### Spec-Only Attributes (0)

All spec-defined UNSUBSCRIBE attributes are implemented in Autobahn-Python (none in spec).

### Implementation-Only Attributes (1)

These attributes are implemented in Autobahn-Python but NOT defined in the WAMP spec:

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| forward_for | list[dict] | message.py:3409, 3466-3485 | Router-to-router forwarding chain |

**forward_for structure:**
```python
[{
    "session": int,      # Session ID
    "authid": str,       # Authentication ID
    "authrole": str      # Authentication role
}]
```

### Analysis

UNSUBSCRIBE.Options has consistent implementation:
- ✅ No spec-defined Options (WAMP spec defines no Options for UNSUBSCRIBE)
- ✅ Only 1 implementation-specific attribute (`forward_for` for router-to-router links)
- ✅ Consistent with SUBSCRIBE.Options (both have only `forward_for`)
- ✅ Optional Options dictionary (message works without it)

## UNSUBSCRIBED

UNSUBSCRIBED is an acknowledgment message sent by a Router to a Client to confirm an unsubscription.

**Message Format**: `[UNSUBSCRIBED, UNSUBSCRIBE.Request|id]` or `[UNSUBSCRIBED, UNSUBSCRIBE.Request|id, Details|dict]`

**WAMP Spec** (Basic Profile: publish_subscribe.md):
- `UNSUBSCRIBE.Request|id` (int) - The ID from the original UNSUBSCRIBE request

**Autobahn-Python Implementation** (message.py:3507-3615):
- `request` (int) - The request ID of the original UNSUBSCRIBE request
- `subscription` (int or None) - For router-triggered unsubscribe (router revocation signaling)
- `reason` (str or None) - Reason URI for router-initiated revocation

### Analysis

UNSUBSCRIBED has perfect spec compliance for basic form:
- ✅ Simple acknowledgment message with just one ID field in basic form
- ✅ Attribute names match spec semantics exactly
- ✅ Basic message format: `[35, request_id]`
- ✅ Optional Details dict for advanced features (router-initiated revocation)
- ⚠️  Implementation extends spec with router revocation signaling (when request=0, subscription and reason are set)

**Example** (from test vectors):
```json
{
  "description": "UNSUBSCRIBED acknowledgment",
  "wmsg": [35, 85346237],
  "expected_attributes": {
    "message_type": 35,
    "request_id": 85346237
  }
}
```

**Note**: The implementation supports advanced router-initiated unsubscribe ("router revocation signaling") where `request=0` and `subscription` and `reason` fields are used. This is an implementation-specific extension not yet in the spec.

## Recommendations

### For Autobahn-Python Implementation

1. **Add missing spec-defined attributes:**
   - `PUBLISH.Options.disclose_me|bool`
   - `EVENT.Details.trustlevel|int`

2. **Consider renaming E2EE attributes** to match current spec:
   - `enc_algo` → `ppt_cipher`
   - `enc_key` → `ppt_keyid`
   - `enc_serializer` → `ppt_serializer`
   - Add `ppt_scheme` (required in spec)

3. **Document implementation-only attributes:**
   - Clarify purpose and usage of `transaction_hash`
   - Document `forward_for` structure and use case
   - Resolve FIXME for `x_acknowledged_delivery` naming

### For WAMP Specification

1. **Consider adding to spec:**
   - `transaction_hash` for call/publish deduplication (see [wamp-proto#391](https://github.com/wamp-proto/wamp-proto/issues/391))
   - `forward_for` for router-to-router link tracking

## Version Information

- **WAMP Spec**: /home/oberstet/work/wamp/wamp-proto/rfc/text/
- **Autobahn-Python**: /home/oberstet/work/wamp/autobahn-python/autobahn/wamp/message.py
- **Analysis Date**: 2025-11-17 (Phase 1 complete: all Pub/Sub messages analyzed)
