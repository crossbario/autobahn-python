# WAMP Protocol Attributes: Spec vs Autobahn-Python Implementation

This document compares WAMP protocol message attributes as defined in the WAMP specification
against their implementation in Autobahn-Python.

## Table of Contents

### Summary
- [Summary Matrix](#summary-matrix)
  - [Phase 1: Pub/Sub Messages (Complete)](#phase-1-pubsub-messages-complete)
  - [Phase 2: RPC Messages (Complete)](#phase-2-rpc-messages-complete)
  - [Phase 3: Shared Messages (Complete)](#phase-3-shared-messages-complete)
  - [Overall Summary](#overall-summary)

### Phase 1: Pub/Sub Messages
- [PUBLISH.Options](#publishoptions)
- [EVENT.Details](#eventdetails)
- [SUBSCRIBE.Options](#subscribeoptions)
- [SUBSCRIBED](#subscribed)
- [PUBLISHED](#published)
- [UNSUBSCRIBE.Options](#unsubscribeoptions)
- [UNSUBSCRIBED](#unsubscribed)

### Phase 2: RPC Messages
- [CALL.Options](#calloptions)
- [RESULT.Details](#resultdetails)
- [REGISTER.Options](#registeroptions)
- [REGISTERED](#registered)
- [UNREGISTER.Options](#unregisteroptions)
- [UNREGISTERED](#unregistered)
- [INVOCATION.Details](#invocationdetails)
- [YIELD.Options](#yieldoptions)
- [ERROR.Details](#errordetails)

### Appendix
- [Recommendations](#recommendations)
- [Version Information](#version-information)

---

## Summary Matrix

### Phase 1: Pub/Sub Messages (Complete)

| Message Type | Matched | Spec-Only | Implementation-Only | Naming Differences |
|--------------|---------|-----------|---------------------|-------------------|
| PUBLISH.Options      | 9  | 1 (+4 ppt_*) | 2 (+3 enc_*) | E2EE: ppt_* vs enc_* |
| EVENT.Details        | 5  | 1 (+4 ppt_*) | 3 (+3 enc_*) | E2EE: ppt_* vs enc_* |
| SUBSCRIBE.Options    | 2  | 0           | 1            | None |
| SUBSCRIBED           | N/A | N/A         | N/A          | No Options/Details |
| PUBLISHED            | N/A | N/A         | N/A          | No Options/Details |
| UNSUBSCRIBE.Options  | 0  | 0           | 1            | None |
| UNSUBSCRIBED         | N/A | N/A         | N/A          | No Details (basic) |

### Phase 2: RPC Messages (Complete)

| Message Type | Matched | Spec-Only | Implementation-Only | Naming Differences |
|--------------|---------|-----------|---------------------|-------------------|
| CALL.Options         | 2  | 1 (+4 ppt_*) | 5 (+3 enc_*) | E2EE: ppt_* vs enc_* |
| RESULT.Details       | 1  | 0 (+4 ppt_*) | 4 (+3 enc_*) | E2EE: ppt_* vs enc_* |
| REGISTER.Options     | 2  | 0           | 3            | None |
| REGISTERED           | N/A | N/A         | N/A          | No Options/Details |
| UNREGISTER.Options   | 0  | 0           | 1            | None |
| UNREGISTERED         | 2  | 0           | 0            | None |
| INVOCATION.Details   | 6  | 1 (+4 ppt_*) | 2 (+3 enc_*) | E2EE: ppt_* vs enc_* |
| YIELD.Options        | 1  | 0 (+4 ppt_*) | 4 (+3 enc_*) | E2EE: ppt_* vs enc_* |

### Phase 3: Shared Messages (Complete)

| Message Type | Matched | Spec-Only | Implementation-Only | Naming Differences |
|--------------|---------|-----------|---------------------|-------------------|
| ERROR.Details        | 0  | 0 (+4 ppt_*) | 4 (+3 enc_*) | E2EE: ppt_* vs enc_* |

### Overall Summary

**Spec Compliance:**
- ✅ Core functionality: All basic profile features implemented
- ⚠️  Missing disclosure initiation: `disclose_me` not implemented (PUBLISH, CALL)
- ⚠️  E2EE naming: Uses `enc_*` prefix instead of spec's `ppt_*` prefix
- ⚠️  Missing E2EE: `ppt_scheme` not implemented (required in spec)
- ⚠️  Missing trustlevel: `EVENT.Details.trustlevel` not implemented

**Implementation Extensions:**
- ✅ Router-to-router forwarding: `forward_for` (all messages with Options/Details)
- ✅ Transaction deduplication: `transaction_hash` (PUBLISH, CALL)
- ✅ Disclosure metadata: Router-added `publisher*`, `caller*`, `callee*` attributes
- ✅ Event acknowledgement: `x_acknowledged_delivery` (EVENT - needs naming review)

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

---

# Phase 2: RPC Messages

## CALL.Options

CALL is a message from Caller to Dealer to invoke a remote procedure.

**Message Format**:
- `[CALL, Request|id, Options|dict, Procedure|uri]`
- `[CALL, Request|id, Options|dict, Procedure|uri, Arguments|list]`
- `[CALL, Request|id, Options|dict, Procedure|uri, Arguments|list, ArgumentsKw|dict]`
- `[CALL, Request|id, Options|dict, Procedure|uri, Payload|binary]`

**WAMP Spec** (Advanced Profile):
- `timeout|int` - Advanced: rpc_call_timeout.md
- `receive_progress|bool` - Advanced: rpc_progressive_call_results.md
- `disclose_me|bool` - Advanced: rpc_caller_identification.md

**Autobahn-Python Implementation** (message.py:4468-4869):
- `timeout|int` - Call timeout in milliseconds
- `receive_progress|bool` - Caller wants progressive results
- `transaction_hash|str` - Application-level transaction ID for deduplication
- `enc_algo|str` - Encryption algorithm for payload transparency
- `enc_key|str` - Encryption key for payload transparency
- `enc_serializer|str` - Payload serializer for payload transparency
- `caller|int` - Caller session ID (when disclosed)
- `caller_authid|str` - Caller auth ID (when disclosed)
- `caller_authrole|str` - Caller auth role (when disclosed)
- `forward_for|list[dict]` - Router-to-router forwarding chain

### Matched Attributes (2)

| Attribute | Type | Spec Section | Implementation |
|-----------|------|--------------|----------------|
| timeout | int | Advanced: rpc_call_timeout.md | message.py:4474, 4687-4703, 4803-4804 |
| receive_progress | bool | Advanced: rpc_progressive_call_results.md | message.py:4475, 4705-4714, 4806-4807 |

### Spec-Only Attributes (1)

| Attribute | Type | Spec Section | Notes |
|-----------|------|--------------|-------|
| disclose_me | bool | Advanced: rpc_caller_identification.md | NOT implemented |

### Implementation-Only Attributes (3)

These attributes are implemented in Autobahn-Python but NOT defined in the WAMP spec:

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| transaction_hash | str | message.py:4476, 4716-4725, 4809-4810 | Application-level transaction ID for deduplication (see wamp-proto#391) |
| caller | int | message.py:4480, 4727-4736, 4820-4821 | Caller session ID - router-added when caller discloses |
| caller_authid | str | message.py:4481, 4738-4747, 4822-4823 | Caller auth ID - router-added when caller discloses |
| caller_authrole | str | message.py:4482, 4749-4758, 4824-4825 | Caller auth role - router-added when caller discloses |
| forward_for | list[dict] | message.py:4483, 4760-4778, 4827-4828 | Router-to-router forwarding chain |

**Note**: The `caller`, `caller_authid`, and `caller_authrole` options are set by the router when the caller uses `disclose_me=true`. These are router-added metadata, not caller-provided options.

### Naming Differences: Payload Passthru Mode (E2EE)

Same pattern as PUBLISH.Options and EVENT.Details - the spec uses `ppt_*` prefix while implementation uses `enc_*` prefix.

**WAMP Spec** (Advanced: payload_passthru_mode.md):
- `ppt_scheme|string`
- `ppt_serializer|string`
- `ppt_cipher|string`
- `ppt_keyid|string`

**Autobahn-Python Implementation** (message.py:4477-4479, 4642-4662, 4812-4818):
- `enc_algo|str`
- `enc_key|str`
- `enc_serializer|str`

### Analysis

CALL.Options has similar compliance issues as PUBLISH.Options:
- ✅ Core RPC options implemented (`timeout`, `receive_progress`)
- ❌ Missing `disclose_me` (caller identification initiation)
- ✅ Router-added caller disclosure metadata (`caller`, `caller_authid`, `caller_authrole`)
- ⚠️  E2EE uses `enc_*` prefix instead of `ppt_*` prefix from spec
- ⚠️  Missing `ppt_scheme` (required in spec)
- ✅ Implementation-specific extensions (`transaction_hash`, `forward_for`)

## RESULT.Details

RESULT is a message from Dealer to Caller returning the result of a remote procedure call.

**Message Format**:
- `[RESULT, CALL.Request|id, Details|dict]`
- `[RESULT, CALL.Request|id, Details|dict, YIELD.Arguments|list]`
- `[RESULT, CALL.Request|id, Details|dict, YIELD.Arguments|list, YIELD.ArgumentsKw|dict]`
- `[RESULT, CALL.Request|id, Details|dict, Payload|binary]`

**WAMP Spec** (Advanced Profile):
- `progress|bool` - Advanced: rpc_progressive_call_results.md

**Autobahn-Python Implementation** (message.py:5030-5346):
- `progress|bool` - Progressive result indicator
- `enc_algo|str` - Encryption algorithm for payload transparency
- `enc_key|str` - Encryption key for payload transparency
- `enc_serializer|str` - Payload serializer for payload transparency
- `callee|int` - Callee session ID (when disclosed)
- `callee_authid|str` - Callee auth ID (when disclosed)
- `callee_authrole|str` - Callee auth role (when disclosed)
- `forward_for|list[dict]` - Router-to-router forwarding chain

### Matched Attributes (1)

| Attribute | Type | Spec Section | Implementation |
|-----------|------|--------------|----------------|
| progress | bool | Advanced: rpc_progressive_call_results.md | message.py:5035, 5224-5233, 5314-5315 |

### Spec-Only Attributes (0)

All spec-defined RESULT.Details attributes are implemented in Autobahn-Python.

### Implementation-Only Attributes (4)

These attributes are implemented in Autobahn-Python but NOT defined in the WAMP spec:

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| callee | int | message.py:5039, 5235-5244, 5317-5318 | Callee session ID - router-added when callee discloses |
| callee_authid | str | message.py:5040, 5246-5255, 5319-5320 | Callee auth ID - router-added when callee discloses |
| callee_authrole | str | message.py:5041, 5257-5266, 5321-5322 | Callee auth role - router-added when callee discloses |
| forward_for | list[dict] | message.py:5042, 5268-5286, 5323-5324 | Router-to-router forwarding chain |

**Note**: The `callee`, `callee_authid`, and `callee_authrole` details are set by the router when the callee uses disclosure. These are router-added metadata, not callee-provided details.

### Naming Differences: Payload Passthru Mode (E2EE)

Same pattern as CALL.Options - the spec uses `ppt_*` prefix while implementation uses `enc_*` prefix.

**WAMP Spec** (Advanced: payload_passthru_mode.md):
- `ppt_scheme|string`
- `ppt_serializer|string`
- `ppt_cipher|string`
- `ppt_keyid|string`

**Autobahn-Python Implementation** (message.py:5036-5038, 5187-5207, 5326-5332):
- `enc_algo|str`
- `enc_key|str`
- `enc_serializer|str`

### Analysis

RESULT.Details has similar patterns as CALL.Options:
- ✅ Core RPC detail implemented (`progress`)
- ✅ Router-added callee disclosure metadata (`callee`, `callee_authid`, `callee_authrole`)
- ⚠️  E2EE uses `enc_*` prefix instead of `ppt_*` prefix from spec
- ⚠️  Missing `ppt_scheme` (required in spec)
- ✅ Implementation-specific extension (`forward_for`)

## REGISTER.Options

REGISTER is a message from Callee to Dealer to register a procedure endpoint.

**Message Format**:
- `[REGISTER, Request|id, Options|dict, Procedure|uri]`

**WAMP Spec** (Advanced Profile):
- `match|string` - Advanced: rpc_pattern_based_registration.md
- `invoke|string` - Advanced: rpc_shared_registration.md

**Autobahn-Python Implementation** (message.py:5372-5637):
- `match|str` - Pattern matching policy ("exact", "prefix", "wildcard")
- `invoke|str` - Invocation policy ("single", "first", "last", "roundrobin", "random")
- `concurrency|int` - Maximum concurrency for the registration
- `force_reregister|bool` - Force re-registration
- `forward_for|list[dict]` - Router-to-router forwarding chain

### Matched Attributes (2)

| Attribute | Type | Spec Section | Implementation |
|-----------|------|--------------|----------------|
| match | str | Advanced: rpc_pattern_based_registration.md | message.py:5375, 5477-5497, 5608-5609 |
| invoke | str | Advanced: rpc_shared_registration.md | message.py:5376, 5521-5543, 5611-5612 |

### Spec-Only Attributes (0)

All spec-defined REGISTER.Options attributes are implemented in Autobahn-Python.

### Implementation-Only Attributes (3)

These attributes are implemented in Autobahn-Python but NOT defined in the WAMP spec:

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| concurrency | int | message.py:5377, 5545-5561, 5614-5615 | Maximum concurrency (>0) - controls concurrent invocations |
| force_reregister | bool | message.py:5378, 5563-5571, 5617-5618 | Force re-registration even if already registered |
| forward_for | list[dict] | message.py:5379, 5573-5591, 5620-5621 | Router-to-router forwarding chain |

### Analysis

REGISTER.Options has excellent spec compliance:
- ✅ All spec-defined attributes implemented (`match`, `invoke`)
- ✅ Defaults properly handled (match="exact", invoke="single")
- ✅ Pattern-based registration supported (prefix, wildcard)
- ✅ Shared registration policies supported (first, last, roundrobin, random)
- ✅ Implementation extensions (`concurrency`, `force_reregister`, `forward_for`)
- ✅ No E2EE complexity (unlike CALL/RESULT)

## REGISTERED

REGISTERED is an acknowledgment message sent by a Dealer to a Callee to confirm a registration.

**Message Format**: `[REGISTERED, REGISTER.Request|id, Registration|id]`

**WAMP Spec** (Basic Profile: remote_procedure_calls.md):
- `REGISTER.Request|id` (int) - The ID from the original REGISTER request
- `Registration|id` (int) - The registration ID assigned by the Dealer

**Autobahn-Python Implementation** (message.py:5640-5705):
- `request` (int) - The request ID of the original REGISTER request
- `registration` (int) - The registration ID for the registered procedure

### Analysis

REGISTERED has perfect spec compliance:
- ✅ Simple acknowledgment message with no Options or Details dictionaries
- ✅ Only contains two ID fields as defined in spec
- ✅ Attribute names match spec semantics exactly
- ✅ No implementation-specific extensions
- ✅ Message format: `[65, request_id, registration_id]`

---

## UNREGISTER.Options

UNREGISTER allows a Callee to unregister a previously registered procedure endpoint.

**Message Format**: `[UNREGISTER, Request|id, REGISTERED.Registration|id]` (basic) or
`[UNREGISTER, Request|id, REGISTERED.Registration|id, Options|dict]` (with Options)

**WAMP Spec** (Basic Profile: remote_procedure_calls.md):
- No Options defined in basic or advanced profile

**Autobahn-Python Implementation** (message.py:5708-5814):
- `forward_for` (list[dict]) - Router-to-router forwarding chain metadata

### Implementation-Only Attributes (1)

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| forward_for | list[dict] | message.py:5726, 5775-5794, 5807-5810 | Router-to-router forwarding chain |

### Analysis

UNREGISTER.Options analysis:
- ✅ No spec-defined Options (basic or advanced profile)
- ✅ Only implementation-specific attribute is `forward_for` (consistent with other messages)
- ✅ Simple request-response pattern with no complexity
- ✅ No E2EE attributes needed for this message type

---

## UNREGISTERED

UNREGISTERED is an acknowledgment message sent by a Dealer to a Callee to confirm an unregistration,
or can be sent unsolicited by the Dealer to indicate a registration has been revoked.

**Message Format**:
- Basic acknowledgment: `[UNREGISTERED, UNREGISTER.Request|id]`
- Router-initiated revocation: `[UNREGISTERED, 0, Details|dict]` (Advanced profile)

**WAMP Spec** (Basic Profile: remote_procedure_calls.md, Advanced: rpc_registration_revocation.md):
- Basic: `UNREGISTER.Request|id` (int) - The ID from the original UNREGISTER request
- Advanced (registration_revocation feature):
  - `Details.registration|int` - Required: The registration ID being revoked
  - `Details.reason|string` - Optional: Reason why the registration was revoked

**Autobahn-Python Implementation** (message.py:5816-5923):
- `request` (int) - The request ID of the original UNREGISTER request (or 0 for router-initiated)
- `registration` (int|None) - If unregister was actively triggered by router, the ID of the registration revoked
- `reason` (str|None) - The reason (a URI) for revocation

### Matched Attributes (2)

| Attribute | Type | Spec Section | Implementation |
|-----------|------|--------------|----------------|
| registration | int | Advanced: rpc_registration_revocation.md | message.py:5833, 5882-5896, 5918 |
| reason | str | Advanced: rpc_registration_revocation.md | message.py:5834, 5898-5901, 5916-5917 |

### Analysis

UNREGISTERED has excellent spec compliance:
- ✅ All spec-defined attributes implemented correctly
- ✅ Supports both basic acknowledgment and advanced router-initiated revocation
- ✅ `registration` and `reason` match advanced profile specification
- ✅ Correctly uses request=0 for router-initiated revocations
- ✅ No implementation-specific extensions
- ✅ Attribute names match spec semantics

---

## INVOCATION.Details

INVOCATION is sent by a Dealer to a Callee to invoke a registered procedure, forwarding the call from a Caller.

**Message Format**: `[INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict]` (basic) with optional args/kwargs or payload

**WAMP Spec** (Basic and Advanced Profiles):
- Basic: Empty Details `{}` (basic/remote_procedure_call.md)
- Advanced attributes from various features:
  - `caller|int` - Caller's session ID (advanced/rpc_caller_identification.md)
  - `caller_authid|str` - Caller's authid (advanced/rpc_caller_identification.md)
  - `caller_authrole|str` - Caller's authrole (advanced/rpc_caller_identification.md)
  - `procedure|str` - Actual procedure URI for pattern-based registrations (advanced/rpc_pattern_based_registration.md)
  - `timeout|int` - Call timeout in ms (advanced/rpc_call_timeout.md)
  - `receive_progress|bool` - Callee should produce progressive results (advanced/rpc_progressive_call_results.md)
  - `trustlevel|int` - Trustlevel of caller (advanced/rpc_call_trustlevels.md)
  - `ppt_scheme|str`, `ppt_serializer|str`, `ppt_cipher|str`, `ppt_keyid|str` - Payload passthru mode (advanced/payload_passthru_mode.md)

**Autobahn-Python Implementation** (message.py:5925-6400):
- `timeout` (int) - Call timeout in ms
- `receive_progress` (bool) - Indicates if callee should produce progressive results
- `caller` (int) - Caller's session ID
- `caller_authid` (str) - Caller's authid
- `caller_authrole` (str) - Caller's authrole
- `procedure` (str) - Actual procedure for pattern-based registrations
- `transaction_hash` (str) - Application-level transaction ID
- `enc_algo` (str) - Encryption algorithm (maps to ppt_cipher)
- `enc_key` (str) - Encryption key (maps to ppt_keyid)
- `enc_serializer` (str) - Payload serializer (maps to ppt_serializer)
- `forward_for` (list[dict]) - Router-to-router forwarding chain

### Matched Attributes (6)

| Attribute | Type | Spec Section | Implementation |
|-----------|------|--------------|----------------|
| caller | int | Advanced: rpc_caller_identification.md | message.py:6198-6207 |
| caller_authid | str | Advanced: rpc_caller_identification.md | message.py:6209-6218 |
| caller_authrole | str | Advanced: rpc_caller_identification.md | message.py:6220-6229 |
| procedure | str | Advanced: rpc_pattern_based_registration.md | message.py:6231-6240 |
| timeout | int | Advanced: rpc_call_timeout.md | message.py:6169-6185 |
| receive_progress | bool | Advanced: rpc_progressive_call_results.md | message.py:6187-6196 |

### Spec-Only Attributes (1)

| Attribute | Type | Spec Section | Notes |
|-----------|------|--------------|-------|
| trustlevel | int | Advanced: rpc_call_trustlevels.md | NOT implemented |

### Implementation-Only Attributes (2)

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| transaction_hash | str | message.py:6242-6251 | Application-level transaction ID for throttling/deduplication |
| forward_for | list[dict] | message.py:6253-6271 | Router-to-router forwarding chain |

### Naming Differences: Payload Passthru Mode (E2EE)

**WAMP Spec** uses `ppt_*` prefix while **Autobahn-Python** uses `enc_*` prefix (same as CALL, RESULT):
- Missing: `ppt_scheme` (required in spec)
- `enc_algo` maps to `ppt_cipher`
- `enc_key` maps to `ppt_keyid`
- `enc_serializer` maps to `ppt_serializer`

### Analysis

INVOCATION.Details has excellent spec compliance for most attributes:
- ✅ All major spec-defined attributes implemented (caller identification, pattern-based, progressive calls, timeout)
- ⚠️  Missing `trustlevel` (advanced feature for call trust levels)
- ⚠️  E2EE naming mismatch: uses `enc_*` instead of spec's `ppt_*` prefix
- ⚠️  Missing `ppt_scheme` (required in spec for payload passthru)
- ✅ Implementation-only: `transaction_hash` for deduplication (useful feature)
- ✅ Implementation-only: `forward_for` for router-to-router scenarios

---

## YIELD.Options

YIELD is sent by a Callee to a Dealer to return results from a procedure invocation.

**Message Format**: `[YIELD, INVOCATION.Request|id, Options|dict]` (basic) with optional args/kwargs or payload

**WAMP Spec** (Basic and Advanced Profiles):
- Basic: Empty Options `{}` (basic/remote_procedure_call.md)
- Advanced attributes:
  - `progress|bool` - Indicates progressive result (advanced/rpc_progressive_call_results.md)
  - `ppt_scheme|str`, `ppt_serializer|str`, `ppt_cipher|str`, `ppt_keyid|str` - Payload passthru mode (advanced/payload_passthru_mode.md)

**Autobahn-Python Implementation** (message.py:6530-6900):
- `progress` (bool) - Progressive invocation result indicator
- `enc_algo` (str) - Encryption algorithm (maps to ppt_cipher)
- `enc_key` (str) - Encryption key (maps to ppt_keyid)
- `enc_serializer` (str) - Payload serializer (maps to ppt_serializer)
- `callee` (int) - Callee's session ID (router-added disclosure)
- `callee_authid` (str) - Callee's authid (router-added disclosure)
- `callee_authrole` (str) - Callee's authrole (router-added disclosure)
- `forward_for` (list[dict]) - Router-to-router forwarding chain

### Matched Attributes (1)

| Attribute | Type | Spec Section | Implementation |
|-----------|------|--------------|----------------|
| progress | bool | Advanced: rpc_progressive_call_results.md | message.py:6552, 6806-6815, 6884-6885 |

### Implementation-Only Attributes (4)

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| callee | int | message.py:6556, 6816-6825 | Router-added callee disclosure (session ID) |
| callee_authid | str | message.py:6557, 6827-6836 | Router-added callee disclosure (authid) |
| callee_authrole | str | message.py:6558, 6838-6847 | Router-added callee disclosure (authrole) |
| forward_for | list[dict] | message.py:6849-6867 | Router-to-router forwarding chain |

### Naming Differences: Payload Passthru Mode (E2EE)

**WAMP Spec** uses `ppt_*` prefix while **Autobahn-Python** uses `enc_*` prefix (same pattern as CALL, RESULT, INVOCATION):
- Missing: `ppt_scheme` (required in spec)
- `enc_algo` maps to `ppt_cipher`
- `enc_key` maps to `ppt_keyid`
- `enc_serializer` maps to `ppt_serializer`

### Analysis

YIELD.Options has good spec compliance with useful router extensions:
- ✅ Core `progress` attribute implemented correctly for progressive call results
- ⚠️  E2EE naming mismatch: uses `enc_*` instead of spec's `ppt_*` prefix
- ⚠️  Missing `ppt_scheme` (required in spec for payload passthru)
- ✅ Implementation-only: `callee*` attributes for router-added disclosure (mirrors `caller*` in RESULT)
- ✅ Implementation-only: `forward_for` for router-to-router scenarios

---

## ERROR.Details

ERROR is a universal error response message used by both Pub/Sub and RPC patterns to indicate failures.

**Message Format**: `[ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri]` (basic) with optional args/kwargs or payload

**WAMP Spec** (Basic and Advanced Profiles):
- Basic: Empty Details `{}` (basic/messages.md)
- Advanced attributes:
  - `ppt_scheme|str`, `ppt_serializer|str`, `ppt_cipher|str`, `ppt_keyid|str` - Payload passthru mode (advanced/payload_passthru_mode.md)

**Autobahn-Python Implementation** (message.py:1602-1900):
- `enc_algo` (str) - Encryption algorithm (maps to ppt_cipher)
- `enc_key` (str) - Encryption key (maps to ppt_keyid)
- `enc_serializer` (str) - Payload serializer (maps to ppt_serializer)
- `callee` (int) - Callee's session ID (router-added disclosure)
- `callee_authid` (str) - Callee's authid (router-added disclosure)
- `callee_authrole` (str) - Callee's authrole (router-added disclosure)
- `forward_for` (list[dict]) - Router-to-router forwarding chain

**Request Types** that ERROR can respond to:
- Pub/Sub: SUBSCRIBE (32), UNSUBSCRIBE (34), PUBLISH (16)
- RPC: CALL (48), REGISTER (64), UNREGISTER (66), INVOCATION (68)

### Implementation-Only Attributes (4)

| Attribute | Type | Implementation | Notes |
|-----------|------|----------------|-------|
| callee | int | message.py:1629, 1830-1839 | Router-added callee disclosure (session ID) |
| callee_authid | str | message.py:1630, 1841-1850 | Router-added callee disclosure (authid) |
| callee_authrole | str | message.py:1631, 1852-1861 | Router-added callee disclosure (authrole) |
| forward_for | list[dict] | message.py:1632, 1863-1881 | Router-to-router forwarding chain |

### Naming Differences: Payload Passthru Mode (E2EE)

**WAMP Spec** uses `ppt_*` prefix while **Autobahn-Python** uses `enc_*` prefix (consistent with all other message types):
- Missing: `ppt_scheme` (required in spec)
- `enc_algo` maps to `ppt_cipher`
- `enc_key` maps to `ppt_keyid`
- `enc_serializer` maps to `ppt_serializer`

### Analysis

ERROR.Details has minimal spec-defined attributes with useful router extensions:
- ✅ Universal error response for both Pub/Sub and RPC
- ✅ No spec-defined Details in basic profile (empty dict)
- ⚠️  E2EE naming mismatch: uses `enc_*` instead of spec's `ppt_*` prefix
- ⚠️  Missing `ppt_scheme` (required in spec for payload passthru)
- ✅ Implementation-only: `callee*` attributes for router-added disclosure (consistent with RESULT and YIELD)
- ✅ Implementation-only: `forward_for` for router-to-router scenarios
- ✅ Clean and consistent implementation across all error scenarios

---

## Recommendations

### For Autobahn-Python Implementation

1. **Add missing spec-defined attributes:**
   - `PUBLISH.Options.disclose_me|bool`
   - `EVENT.Details.trustlevel|int`
   - `CALL.Options.disclose_me|bool`

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

### Analysis Status

**Phase 1: Pub/Sub Messages** ✅ **COMPLETE**
- PUBLISH.Options ✅
- EVENT.Details ✅
- SUBSCRIBE.Options ✅
- SUBSCRIBED ✅
- PUBLISHED ✅
- UNSUBSCRIBE.Options ✅
- UNSUBSCRIBED ✅

**Phase 2: RPC Messages** ✅ **COMPLETE**
- CALL.Options ✅
- RESULT.Details ✅
- REGISTER.Options ✅
- REGISTERED ✅
- UNREGISTER.Options ✅
- UNREGISTERED ✅
- INVOCATION.Details ✅
- YIELD.Options ✅

**Phase 3: Shared Messages** ✅ **COMPLETE**
- ERROR.Details ✅ (used in both Pub/Sub and RPC)

### Test Coverage

**SerDes Conformance Tests:**
- Total: 338 passed, 56 skipped ✅ ALL PHASES COMPLETE
- Phase 1 (Pub/Sub): 218 tests (8 message types × ~27 tests/type avg) ✅ COMPLETE
- Phase 2 (RPC): 96 tests (8 message types × 12 tests/type) ✅ COMPLETE
- Phase 3 (Shared): 12 tests (1 message type × 12 tests/type) ✅ COMPLETE
- Serializers tested: JSON, MsgPack, CBOR, UBJSON (FlatBuffers skipped)
- Coverage: 17 out of 17 WAMP message types tested! 🎉

### Source Information

- **WAMP Spec**: /home/oberstet/work/wamp/wamp-proto/rfc/text/
- **Autobahn-Python**: /home/oberstet/work/wamp/autobahn-python/autobahn/wamp/message.py
- **Test Vectors**: /home/oberstet/work/wamp/wamp-proto/testsuite/singlemessage/basic/
- **Analysis Date**: 2025-11-17
- **Last Updated**: ALL PHASES COMPLETE - All 17 WAMP message types analyzed and tested

### Related Issues

- **wamp-proto#556**: Add comprehensive test vectors for all WAMP message types
- **autobahn-python#1764**: Add SerDes conformance tests using wamp-proto test vectors
