# WAMP Enumeration Audit - Findings Report

**Date:** 2025-11-23
**Scope:** FlatBuffers schema vs Python implementation vs WAMP specification
**Purpose:** Ensure all enumeration-like WAMP Options & Details are consistently defined across all three sources

---

## Executive Summary

Conducted systematic audit of all enumeration-like values used in WAMP messages across:
1. **FlatBuffers schema** (`autobahn/wamp/flatbuffers/types.fbs`)
2. **Python implementation** (`autobahn/wamp/message.py`, `autobahn/wamp/types.py`)
3. **WAMP protocol specification** (`wamp-proto/rfc/`)

**Key Findings:**
- ✅ **1 fully aligned** enumeration type (Match)
- 🔴 **2 critical inconsistencies** requiring immediate fixes
- 🟡 **4 missing enumerations** worth adding
- 🟢 **Several nice-to-have enhancements**

---

## Detailed Findings

### 1. ✅ Topic/Procedure Matching Methods - ALIGNED

**Field:** `Subscribe.Options.match`, `Register.Options.match`

| Value | WAMP Spec | FlatBuffers (Match enum) | Python |
|-------|-----------|-------------------------|--------|
| `"exact"` | ✅ | ✅ EXACT = 0 | ✅ MATCH_EXACT |
| `"prefix"` | ✅ | ✅ PREFIX = 1 | ✅ MATCH_PREFIX |
| `"wildcard"` | ✅ | ✅ WILDCARD = 2 | ✅ MATCH_WILDCARD |

**Status:** ✅ Complete - All three sources perfectly aligned

---

### 2. 🔴 CRITICAL: Call Cancellation Modes - MISALIGNED

**Field:** `Cancel.Options.mode`

| Value | WAMP Spec | FlatBuffers (CancelMode enum) | Python (Cancel.*) |
|-------|-----------|------------------------------|-------------------|
| `"skip"` | ✅ rfc_call_canceling.md | ✅ SKIP = 0 | ✅ SKIP = "skip" |
| `"kill"` | ✅ rfc_call_canceling.md | ✅ KILL = 2 ❌ **Wrong value** | ✅ KILL = "kill" |
| `"killnowait"` | ✅ rfc_call_canceling.md | ❌ **MISSING** | ✅ KILLNOWAIT = "killnowait" |
| `"abort"` | ❌ **NOT in spec** | ✅ ABORT = 1 ❌ **Extra value** | ❌ NOT in Python |

**Issues:**
1. **FlatBuffers has wrong enum values:**
   - Should be: `SKIP=0, KILL=1, KILLNOWAIT=2`
   - Currently: `SKIP=0, ABORT=1, KILL=2`
2. **ABORT doesn't exist in spec or Python** - appears to be a mistake
3. **KILLNOWAIT missing from FlatBuffers** - needs to be added

**WAMP Spec Reference:** `/home/oberstet/work/wamp/wamp-proto/rfc/text/advanced/rpc_call_canceling.md:122`

**Action Required:**
- **Fix `types.fbs` CancelMode enum to:**
  ```fbs
  enum CancelMode: uint8 {
      SKIP = 0,
      KILL = 1,
      KILLNOWAIT = 2
  }
  ```
- **Regenerate FlatBuffers wrappers**
- **Update any code using ABORT or wrong enum values**

**GitHub Issue:** To be filed in `autobahn-python`

---

### 3. 🔴 CRITICAL: RPC Invocation Policies - INCONSISTENT

**Field:** `Register.Options.invoke`

| Value | WAMP Spec | FlatBuffers (InvocationPolicy) | Python (Register.INVOKE_*) |
|-------|-----------|--------------------------------|----------------------------|
| `"single"` | ✅ rfc_shared_registration.md | ✅ SINGLE = 0 | ✅ INVOKE_SINGLE |
| `"first"` | ✅ rfc_shared_registration.md | ✅ FIRST = 1 | ✅ INVOKE_FIRST |
| `"last"` | ✅ rfc_shared_registration.md | ✅ LAST = 2 | ✅ INVOKE_LAST |
| `"roundrobin"` | ✅ rfc_shared_registration.md | ✅ ROUNDROBIN = 3 | ✅ INVOKE_ROUNDROBIN |
| `"random"` | ✅ rfc_shared_registration.md | ✅ RANDOM = 4 | ✅ INVOKE_RANDOM |
| `"all"` | ❌ **NOT in spec** | ❌ MISSING | ✅ INVOKE_ALL = "all" |

**Issues:**
1. **Python defines `Register.INVOKE_ALL = "all"`** but it's NOT in WAMP spec
2. **Internal Python inconsistency:** `RegisterOptions` in `types.py:1070` validates against `["single", "first", "last", "roundrobin", "random"]` (doesn't include `"all"`)

**WAMP Spec Reference:** `/home/oberstet/work/wamp/wamp-proto/rfc/text/advanced/rpc_shared_registration.md:14-23`

**Action Required - Choose one:**

**Option A: Add to spec (if functionally needed)**
- Propose adding `invoke="all"` to WAMP spec
- Add to FlatBuffers after spec acceptance
- Fix Python validation in types.py

**Option B: Remove from Python (if not used)**
- Remove `Register.INVOKE_ALL` constant
- Verify no code uses this value
- Document as unsupported

**GitHub Issues:**
- `autobahn-python`: Document the inconsistency
- `wamp-proto`: Clarify if `"all"` should be in spec (if choosing Option A)

---

### 4. 🟡 MEDIUM: Payload Passthru Mode - INCOMPLETE

**Spec defines three related enumerations for end-to-end encryption:**

#### 4a. Encryption Schemes (`ppt_scheme`)

**WAMP Spec:**
- `"wamp"` (E2E encryption)
- `"mqtt"` (MQTT payload gateway)
- Custom schemes with `"x_"` prefix

**Python (`message.py`):**
- `ENC_ALGO_CRYPTOBOX = 1` → `"cryptobox"`
- `ENC_ALGO_MQTT = 2` → `"mqtt"`
- `ENC_ALGO_XBR = 3` → `"xbr"`

**FlatBuffers (`types.fbs`):**
- `Payload` enum: `PLAIN, CRYPTOBOX, OPAQUE`

**Issues:**
- Terminology mismatch: spec says "scheme", Python says "algo", FlatBuffers says "Payload"
- XBR exists in Python but not explicitly in spec - clarify if spec should include it
- MQTT: mapping unclear between spec and Python

#### 4b. Payload Serializers (`ppt_serializer`)

**WAMP Spec:**
- `"native"`, `"json"`, `"msgpack"`, `"cbor"`, `"ubjson"`, `"flatbuffers"`

**Python (`message.py`):**
- `ENC_SER_JSON = 1`, `ENC_SER_MSGPACK = 2`, `ENC_SER_CBOR = 3`, `ENC_SER_UBJSON = 4`, `ENC_SER_FLATBUFFERS = 6`, `ENC_SER_OPAQUE = 5`

**FlatBuffers (`types.fbs`):**
- `Serializer` enum: `TRANSPORT, JSON, MSGPACK, CBOR, UBJSON, OPAQUE, FLATBUFFERS, FLEXBUFFERS`

**Issues:**
- Spec uses `"native"`, Python/FlatBuffers use `"TRANSPORT"` - clarify equivalence
- FlatBuffers has `FLEXBUFFERS` not in spec or Python

#### 4c. Encryption Ciphers (`ppt_cipher`)

**WAMP Spec:**
- `"xsalsa20poly1305"`
- `"aes256gcm"`

**Python:** ❌ No enumeration (string values only)
**FlatBuffers:** ❌ **MISSING entirely**

**WAMP Spec Reference:** `/home/oberstet/work/wamp/wamp-proto/rfc/text/advanced/payload_passthru_mode.md`

**Action Required:**
1. **Add `Cipher` enum to `types.fbs`:**
   ```fbs
   enum Cipher: uint8 {
       XSALSA20POLY1305 = 0,
       AES256GCM = 1
   }
   ```
2. **Harmonize terminology** across spec/Python/FlatBuffers
3. **Clarify XBR status** - should it be in spec?

**GitHub Issues:**
- `autobahn-python`: Add Cipher enum to FlatBuffers, harmonize naming
- `wamp-proto`: Clarify XBR encryption scheme status

---

### 5. 🟡 MEDIUM: Authentication Methods - NOT ENUMERATED

**WAMP Spec defines:**
- `"anonymous"`
- `"ticket"`
- `"wampcra"`
- `"cryptosign"`
- `"wamp-scram"`

**Python/FlatBuffers:** ❌ These are string values in `HELLO.Details.authmethods`, no enum defined

**WAMP Spec References:**
- `/home/oberstet/work/wamp/wamp-proto/rfc/text/advanced/authentication_*.md`

**Action Required (Optional):**
- Consider adding `AuthMethod` enum to FlatBuffers for type safety
- Would enable compile-time checking of auth methods

**GitHub Issue:** `autobahn-python` - Enhancement: Add AuthMethod enum

---

### 6. 🟢 LOW: Channel Binding Types - NOT ENUMERATED

**WAMP Spec (for Cryptosign/SCRAM):**
- `"tls-unique"`
- `"tls-exporter"`
- `"tls-server-end-point"` (SCRAM only)

**Python/FlatBuffers:** ❌ String values only, no enum

**Action:** Low priority - could add for completeness

---

### 7. 🟢 LOW: Key Derivation Functions (WAMP-SCRAM) - NOT ENUMERATED

**WAMP Spec:**
- `"argon2id13"`
- `"pbkdf2"`

**Python/FlatBuffers:** ❌ String values only, no enum

**Action:** Low priority - could add for completeness

---

### 8. 🟢 LOW: Transport Details - NOT IN FLATBUFFERS

**Python (`types.py` - TransportDetails class):**
- Channel types: `FUNCTION, MEMORY, SERIAL, TCP, TLS, UDP, DTLS`
- Channel framing: `NATIVE, WEBSOCKET, RAWSOCKET`
- Channel serializers: `JSON, MSGPACK, CBOR, UBJSON, FLATBUFFERS`

**FlatBuffers:** ❌ No enums for transport details

**Action:** Evaluate if transport metadata should be in FlatBuffers schema

---

## Summary by Priority

### 🔴 CRITICAL - Must Fix

| Issue | Component | Action | GitHub Repo |
|-------|-----------|--------|-------------|
| CancelMode enum wrong | FlatBuffers schema | Fix enum values, add KILLNOWAIT | autobahn-python |
| InvocationPolicy "all" | Python + maybe Spec | Decide: add to spec OR remove from Python | Both repos |
| RegisterOptions validation | Python types.py | Make consistent with message.py | autobahn-python |

### 🟡 MEDIUM - Should Add

| Issue | Component | Action | GitHub Repo |
|-------|-----------|--------|-------------|
| Cipher enum missing | FlatBuffers schema | Add XSALSA20POLY1305, AES256GCM | autobahn-python |
| Payload terminology | All | Harmonize naming (scheme/algo/payload) | Both repos |
| XBR encryption scheme | Spec | Clarify if should be standardized | wamp-proto |
| AuthMethod enum | FlatBuffers schema | Add for type safety | autobahn-python |

### 🟢 LOW - Nice to Have

| Issue | Component | Action | GitHub Repo |
|-------|-----------|--------|-------------|
| ChannelBinding enum | FlatBuffers | Add for completeness | autobahn-python |
| KDF enum | FlatBuffers | Add for completeness | autobahn-python |
| Transport enums | FlatBuffers | Evaluate usefulness | autobahn-python |

---

## Recommended Next Steps

1. **Review this audit with project maintainers**
2. **File GitHub issues** for critical items (template below)
3. **Fix CancelMode enum** in types.fbs (breaking change - needs version bump)
4. **Decide on InvocationPolicy "all"** value
5. **Add missing Cipher enum**
6. **Consider harmonizing terminology** across spec/implementations

---

## GitHub Issue Templates

### Template: CancelMode Enum Fix (autobahn-python)

```markdown
## Issue: CancelMode enum in FlatBuffers schema is incorrect

**Priority:** Critical (breaking change required)

**Problem:**
The `CancelMode` enum in `autobahn/wamp/flatbuffers/types.fbs` does not match the WAMP specification or Python implementation:

- FlatBuffers has: `SKIP=0, ABORT=1, KILL=2`
- Should be: `SKIP=0, KILL=1, KILLNOWAIT=2`

**WAMP Spec:** https://wamp-proto.org/wamp_latest.html#rpc-call-canceling
(Also: `wamp-proto/rfc/text/advanced/rpc_call_canceling.md:122`)

**Impact:**
- FlatBuffers messages using CancelMode cannot represent "killnowait"
- "ABORT" value doesn't exist in spec and is not used in Python

**Proposed Fix:**
```fbs
enum CancelMode: uint8 {
    SKIP = 0,
    KILL = 1,
    KILLNOWAIT = 2
}
```

**Breaking Change:** Yes - existing FlatBuffers binary messages using ABORT or KILL will be incompatible

**Related:** Full audit in `ENUMERATION_AUDIT.md`
```

---

### Template: InvocationPolicy "all" Clarification (wamp-proto)

```markdown
## Question: Should `invoke="all"` be in WAMP spec for shared registrations?

**Context:**
Autobahn|Python defines `Register.INVOKE_ALL = "all"` constant, but this value is NOT in the WAMP specification for shared registrations.

**WAMP Spec Currently Defines:**
- `single`, `first`, `last`, `roundrobin`, `random`

**Reference:** https://wamp-proto.org/wamp_latest.html#rpc-shared-registrations
(Also: `wamp-proto/rfc/text/advanced/rpc_shared_registration.md:14-23`)

**Questions:**
1. Should `invoke="all"` be added to the spec?
2. What would the semantics be? (invoke ALL registered callees, collect all results?)
3. Or should this be removed from Autobahn|Python as non-standard?

**Note:** Autobahn|Python's `RegisterOptions` validation in `types.py:1070` does NOT include `"all"`, creating an internal inconsistency.

**Related:** Full audit in `autobahn-python/ENUMERATION_AUDIT.md`
```

---

## Files Examined

**FlatBuffers:**
- `autobahn/wamp/flatbuffers/types.fbs`

**Python:**
- `autobahn/wamp/message.py`
- `autobahn/wamp/types.py`

**WAMP Spec:**
- `wamp-proto/rfc/text/advanced/rpc_call_canceling.md`
- `wamp-proto/rfc/text/advanced/rpc_shared_registration.md`
- `wamp-proto/rfc/text/advanced/pubsub_pattern_based_subscription.md`
- `wamp-proto/rfc/text/advanced/rpc_pattern_based_registration.md`
- `wamp-proto/rfc/text/advanced/payload_passthru_mode.md`
- `wamp-proto/rfc/text/advanced/authentication_*.md`
- `wamp-proto/rfc/text/advanced/transport_rawsocket.md`

---

**End of Report**
