# ANSWERS & DESIGN DECISIONS to/wrt: WAMP Enumeration Audit - Findings Report

**Author:** Tobias Oberstein
**Date:** 2025-11-23
**Report:** `ENUMERATION_AUDIT.md`

---

### 1. ✅ Topic/Procedure Matching Methods - ALIGNED

good!

### 2. 🔴 CRITICAL: Call Cancellation Modes - MISALIGNED

1. yes, agreed! FlatBuffers has wrong enum values: should be:`SKIP=0, KILL=1, KILLNOWAIT=2`

2. yes, ABORT doesn't exist in spec or Python: should be removed from Flatbuffers schema

3. yes, KILLNOWAIT missing from FlatBuffers: should be added to Flatbuffers schema (`KILLNOWAIT=2`)

so yes, I agree with Action Required!

### 3. 🔴 CRITICAL: RPC Invocation Policies - INCONSISTENT

`INVOKE_ALL = "all"` should be removed from Flatbuffers and Python in autobahn-python!

crucially, it is _not_ used in crossbar.io, here is a simple/quick check:

```
oberstet@asgard1:~/work/wamp/crossbar$ find crossbar/router/dealer.py -name "*.py" -exec grep -Hi "INVOKE_" {} \;
crossbar/router/dealer.py:    def __init__(self, invoke=message.Register.INVOKE_SINGLE):
crossbar/router/dealer.py:        # _add_invoke_request and _remove_invoke_request
crossbar/router/dealer.py:            # this needs to update all four places where we track invocations similar to _remove_invoke_request
crossbar/router/dealer.py:                if registration.extra.invoke == message.Register.INVOKE_SINGLE:
crossbar/router/dealer.py:            message.Register.INVOKE_SINGLE,
crossbar/router/dealer.py:            message.Register.INVOKE_FIRST,
crossbar/router/dealer.py:            message.Register.INVOKE_LAST,
crossbar/router/dealer.py:            if registration.extra.invoke == message.Register.INVOKE_SINGLE:
crossbar/router/dealer.py:            elif registration.extra.invoke == message.Register.INVOKE_FIRST:
crossbar/router/dealer.py:            elif registration.extra.invoke == message.Register.INVOKE_LAST:
crossbar/router/dealer.py:        elif registration.extra.invoke == message.Register.INVOKE_ROUNDROBIN:
crossbar/router/dealer.py:        elif registration.extra.invoke == message.Register.INVOKE_RANDOM:
crossbar/router/dealer.py:        self._add_invoke_request(
crossbar/router/dealer.py:    def _add_invoke_request(
crossbar/router/dealer.py:        invoke_request = InvocationRequest(
crossbar/router/dealer.py:        self._invocations[invocation_request_id] = invoke_request
crossbar/router/dealer.py:        self._invocations_by_call[session._session_id, call.request] = invoke_request
crossbar/router/dealer.py:        invokes.append(invoke_request)
crossbar/router/dealer.py:        invokes.append(invoke_request)
crossbar/router/dealer.py:                if _can_cancel(invoke_request.caller, "caller"):
crossbar/router/dealer.py:                        invoke_request.caller,
crossbar/router/dealer.py:                if _can_cancel(invoke_request.callee, "callee"):
crossbar/router/dealer.py:                        invoke_request.callee,
crossbar/router/dealer.py:                            invoke_request.id,
crossbar/router/dealer.py:                self._remove_invoke_request(invoke_request)
crossbar/router/dealer.py:            invoke_request.timeout_call = self._cancel_timers.call_later(timeout, _cancel_both_sides)
crossbar/router/dealer.py:        return invoke_request
crossbar/router/dealer.py:    def _remove_invoke_request(self, invocation_request):
crossbar/router/dealer.py:                self._remove_invoke_request(invocation_request)
crossbar/router/dealer.py:            self._remove_invoke_request(invoke)
oberstet@asgard1:~/work/wamp/crossbar$ 
```

so: **Option B: Remove from Python (if not used)**

### 4. 🟡 MEDIUM: Payload Passthru Mode - INCOMPLETE

first, yes, this is a slight mess (historical reasons), and it is not fully completed in the spec, but it _is_ used in AutobahnPython, AutobahnJS and most importantly in Crossbar.io: the End-to-end Encryption, the MQTT and the XBR (Ethereum blockchain, WAMP in data markets) stuff!

we need to untangle this "without breaking things". "not breaking" things means we need to be able to "test it", and we will only come to that once we have modernized the crossbar repo, and respective examples!

on the other hand, I _do_ want to rectify autobahn-python including flatbuffers scheme and python code _now_ to what _is_ already described & defined in the WAMP spec in "14.1. Payload Passthru Mode"!

so "some" fallout is unavoidable in the short term.

to start with, this means the attributes related to "Payload Passthru Mode" should be renamed in the Flatbuffers schema to bring it in line with the spec:

- `enc_algo` => `ppt_scheme`
- `enc_serializer` => `ppt_serializer`
- NEW! => `ppt_cipher`
- `enc_key` => `ppt_keyid`

in this attribute order, and with docstrings/comments from the WAMP protocol spec, and most importantly the types from the spec (which are string for all 4 attributes)!

**sidenote: we do want the descriptions in Flatbuffers schemata from all types/pieces to show up in generated API docs (Doxygen-style documentation comments), and hence we want to use `///` _everywhere_!**

this means changes to:

- `autobahn/wamp/flatbuffers/pubsub.fbs`
- `autobahn/wamp/flatbuffers/rpc.fbs`

we should also clean up the enum types (names) accordingly, here is the complete desired target:

```
/// The specific scheme in use with Payload Passthru (PPT) mode for the application payload.
ppt_scheme: PPTScheme;

/// The specific serializer encoding the application payload with the Payload Passthru (PPT) scheme in use.
ppt_serializer: PPTSerializer;

/// The cryptographic algorithm ("cipher") encrypting the application payload with the Payload Passthru (PPT) scheme in use.
ppt_cipher: PPTCipher;

/// The identifier or reference to the encryption key that was used to encrypt the payload with the Payload Passthru (PPT) scheme and cipher in use.
ppt_keyid: string (ppt_keyid);
```

with (in `autobahn/wamp/flatbuffers/types.fbs`):

```
///WAMP Payload Passthru (PPT) encryption key id. Define custom attribute to hint a string subtype: The value can be a hex-encoded string, URI, DNS name, Ethereum address, UUID identifier - any meaningful value which allows the target peer to choose a private key without guessing. The format of the value may depend on the ppt_scheme attribute.
attribute "ppt_keyid";

/// WAMP Payload Passthru (PPT) scheme (renamed from `Payload`).
enum PPTScheme: uint8
{
    /// Unset (plain WAMP application payload)
    NONE = 0,

    /// WAMP-cryptobox end-to-end encrypted application payload
    CRYPTOBOX = 1,

    /// MQTT passthrough-mode application payload
    MQTT = 2,

    /// XBR end-to-end encrypted end and Ethereum anchored application payload
    XBR = 3,

    /// Raw pass-through of app payload, uninterpreted in any way.
    OPAQUE = 4    
}

/// WAMP Payload Passthru (PPT) application payload serializer (renamed from `Serializer`).
enum PPTSerializer: uint8
{
    /// Use same serializer (dynamically or statically typed) for the application payload as used on the transport for the WAMP message envelope.
    TRANSPORT = 0,

    /// Use JSON serializer for dynamically typed application payload.
    JSON = 1,

    /// Use MsgPack serializer for dynamically typed application payload.
    MSGPACK = 2,

    /// Use CBOR serializer for dynamically typed application payload.
    CBOR = 3,

    /// Use UBJSON serializer for dynamically typed application payload.
    UBJSON = 4,

    /// Raw pass-through of application payload, uninterpreted in any way.
    OPAQUE = 5,

    /// Use FlatBuffers serializer for statically typed application payload (https://google.github.io/flatbuffers/index.html).
    FLATBUFFERS = 6,

    /// Use FlexBuffers serializer dynamically typed application payload (https://google.github.io/flatbuffers/flexbuffers.html).
    FLEXBUFFERS = 7
}

/// WAMP Payload Passthru (PPT) application payload cipher (NEW!).
enum PPTCipher: uint8
{
    /// No valid cipher (unfilled)
    NULL = 0,
    
    /// Particular combination of Salsa20 and Poly1305 specified in Daniel J. Bernstein, "Cryptography in NaCl" (https://cr.yp.to/highspeed/naclcrypto-20090310.pdf), see NaCl (https://nacl.cr.yp.to/) "crypto_secretbox_xsalsa20poly1305" (aka WAMP "cryptobox").
    XSALSA20POLY1305 = 1,

    /// Galois/Counter Mode (GCM), see https://en.wikipedia.org/wiki/Galois/Counter_Mode.
    AES256GCM = 2
}
```

### 5. 🟡 MEDIUM: Authentication Methods - NOT ENUMERATED

yes, we need to add to `autobahn/wamp/flatbuffers/types.fbs`:

```
/// WAMP authentication method (see: WAMP protocol spec, "13. Authentication Methods").
enum AuthMethod: uint8
{
    /// Not set / not authenticated: `anonymous`.
    NULL = 0,

    /// WAMP Ticket authentication: `ticket` (see: WAMP protocol spec, "13.1. Ticket-based Authentication").
    TICKET = 1,

    /// WAMP Challenge-Response authentication: `wampcra` (see: WAMP protocol spec, "13.2. Challenge Response Authentication").
    CRA = 1,

    /// WAMP Salted Challenge Response authentication: `wamp-scram` (see: WAMP protocol spec, "13.3. Salted Challenge Response Authentication").
    SCRAM = 1,

    /// WAMP Cryptosign authentication: `cryptosign` (see: WAMP protocol spec, "13.4. Cryptosign-based Authentication").
    CRYPTOSIGN = 1,
}
```

### 6. 🟢 LOW: Channel Binding Types - NOT ENUMERATED

yes, we need to add to `autobahn/wamp/flatbuffers/types.fbs`:

```
/// TLS channel binding type (see: RFC5929 https://www.rfc-editor.org/rfc/rfc5929 and RFC9266 https://www.rfc-editor.org/rfc/rfc9266).
enum TLSChannelBinding: uint8
{
    /// Not set / no channel binding.
    NULL = 0,

    // RFC 5929 `tls-unique`. Available for TLS connections; historically used as the default for many SASL/SCRAM uses over TLS ≤ 1.2. Care needed with renegotiation and with TLS versions where the triple-handshake / EMS issues apply (see RFCs).
    TLS_UNIQUE = 1,

    /// RFC 5929 `tls-unique-for-telnet`. Only relevant to TELNET / TELNET AUTH usage. See RFC 5929 for details and applicability guidance.
    TLS_UNIQUE_TELNET = 2,

    /// RFC 5929 `tls-server-end-point`. Only available when a server certificate is used (i.e., cipher suites that include the Certificate handshake message / PKIX). Not applicable to OpenPGP server certificates. Recommended for situations where server-side proxies must interoperate without changes.
    TLS_SERVER_ENDPOINT = 3,

    /// RFC 9266 `tls-exporter`. Defined to address TLS 1.3 (where the older tls-unique semantics are not reliably available). RFC 9266 updates defaults for TLS ≥ 1.3: when channel bindings are used for TLS 1.3, tls-exporter is the mandatory/expected mechanism. Not defined for connections where TLS renegotiation is enabled.
    TLS_EXPORTER = 4,
}
```

### 7. 🟢 LOW: Key Derivation Functions (WAMP-SCRAM) - NOT ENUMERATED

yes, we need to add to `autobahn/wamp/flatbuffers/types.fbs`:

```
/// Key Derivation Functions, e.g. WAMP SCRAM uses a password-based key derivation function (KDF) to hash user passwords. WAMP-SCRAM supports both Argon2 and PBKDF2 as the KDF (see: WAMP protocol specification, "SCRAM Algorithms").
enum KDF: uint8
{
    /// Not set / no TLS channel binding.
    NULL = 0,

    /// Argon2id variant of Argon2, version 1.3 - `argon2id13`.
    ARGON2ID13 = 1,

    /// PBKDF2 - `pbkdf2`.
    PBKDF2 = 2,
}
```

### 8. 🟢 LOW: Transport Details - NOT IN FLATBUFFERS

preface/note: "transport" here refers to the _WAMP_ transport as in:

> WAMP can run over any Transport which is message-based, bidirectional, reliable and ordered.

the _underlying_ communication "raw transport" or "channel" is different, and might not be message-based but streaming, and if so, requires a "framing" (into messages).

this can be seen in the `WELCOME.Details.transport`, here is an example (from the WAMP spec):

```

WAMP-Receive(-, -) <<
  WELCOME::
    [2,
     7325966140445461,
     {'authextra': {'x_cb_node': 'intel-nuci7-49879',
                    'x_cb_peer': 'tcp4:127.0.0.1:54046',
                    'x_cb_pid': 49987,
                    'x_cb_worker': 'worker001'},
      'authid': 'client01@example.com',
      'authmethod': 'cryptosign',
      'authprovider': 'static',
      'authrole': 'device',
      'realm': 'devices',
      'roles': {'broker': {'features': {'event_retention': True,
                                        'pattern_based_subscription': True,
                                        'publisher_exclusion': True,
                                        'publisher_identification': True,
                                        'session_meta_api': True,
                                        'subscriber_blackwhite_listing': True,
                                        'subscription_meta_api': True,
                                        'subscription_revocation': True}},
                'dealer': {'features': {'call_canceling': True,
                                        'caller_identification': True,
                                        'pattern_based_registration': True,
                                        'progressive_call_results': True,
                                        'registration_meta_api': True,
                                        'registration_revocation': True,
                                        'session_meta_api': True,
                                        'shared_registration': True,
                                        'testament_meta_api': True}}},
      'x_cb_node': 'intel-nuci7-49879',
      'x_cb_peer': 'tcp4:127.0.0.1:54046',
      'x_cb_pid': 49987,
      'x_cb_worker': 'worker001'}]
<<
2022-07-13T17:38:29+0200 session joined: {'authextra': {'x_cb_node': 'intel-nuci7-49879',
               'x_cb_peer': 'tcp4:127.0.0.1:54046',
               'x_cb_pid': 49987,
               'x_cb_worker': 'worker001'},
 'authid': 'client01@example.com',
 'authmethod': 'cryptosign',
 'authprovider': 'static',
 'authrole': 'device',
 'realm': 'devices',
 'resumable': False,
 'resume_token': None,
 'resumed': False,
 'serializer': 'cbor.batched',
 'session': 7325966140445461,
 'transport': {'channel_framing': 'websocket',
               'channel_id': {'tls-unique': b'\xe9s\xbe\xe2M\xce\xa9\xe2'
                                            b'\x06%\xf9I\xc0\xe3\xcd('
                                            b'\xd62\xcc\xbe\xfeI\x07\xc2'
                                            b'\xfa\xc2r\x87\x10\xf7\xb1`'},
               'channel_serializer': None,
               'channel_type': 'tls',
               'http_cbtid': None,
               'http_headers_received': None,
               'http_headers_sent': None,
               'is_secure': True,
               'is_server': False,
               'own': None,
               'own_fd': -1,
               'own_pid': 50690,
               'own_tid': 50690,
               'peer': 'tcp4:127.0.0.1:8080',
               'peer_cert': None,
               'websocket_extensions_in_use': None,
               'websocket_protocol': None}}              
```

since this is WAMP-over-WebSocket, `websocket_protocol` in above should actually be one of (see "2.3.1. WebSocket Transport" and "15.2. Message Batching"):

- `wamp.2.json`
- `wamp.2.msgpack`
- `wamp.2.cbor`
- `wamp.2.json.batched`
- `wamp.2.msgpack.batched`
- `wamp.2.cbor.batched`

and `websocket_extensions_in_use` should be e.g. `permessage-deflate` if WebSocket compression is active.

Both of these _are_ supported in AutobahnPython _and_ Crossbar.io, e.g. look at:

```
oberstet@amd-ryzen5:~/work/wamp/crossbar$ find crossbar -name "*.py" -exec grep -Hi "websocket_extensions_in_use" {} \;
crossbar/router/service.py:                                         'websocket_extensions_in_use': [{'client_max_window_bits': 13,
crossbar/router/service.py:                           'websocket_extensions_in_use': None,
crossbar/router/protocol.py:            self._transport_details.websocket_extensions_in_use = None
crossbar/router/protocol.py:        self._transport_details.websocket_extensions_in_use = [e.__json__() for e in self.websocket_extensions_in_use]
oberstet@amd-ryzen5:~/work/wamp/crossbar$ find crossbar -name "*.py" -exec grep -Hi "websocket_protocol" {} \;
crossbar/router/service.py:                                         'websocket_protocol': 'wamp.2.json'},
crossbar/router/service.py:                           'websocket_protocol': 'wamp.2.cbor'}}
crossbar/router/protocol.py:            self._transport_details.websocket_protocol = protocol
crossbar/router/protocol.py:        self._transport_details.websocket_protocol = "wamp.2.{}".format(self._serializer.SERIALIZER_ID)
oberstet@amd-ryzen5:~/work/wamp/crossbar$ 
```

but yes, we should add to `autobahn/wamp/flatbuffers/types.fbs`:

```
/// WAMP transport channel type (`channel_type`). WAMP can run over any Transport which is message-based (requiring no WAMP transport channel framing) or stream-based (requiring WAMP transport channel framing), and bidirectional, reliable and ordered.
enum TransportChannelType: uint8
{
    /// Not set or applicable.
    NULL = 0,

    /// Host language native function call transport, e.g. inherently message-based already (function call).
    FUNCTION = 1,

    /// Host run-time / OS level in-memory transport, e.g. (unframed / stream-based) memory buffer.
    MEMORY = 2,

    /// Serial (UART) based transport (unframed / stream-based).
    SERIAL = 3,

    /// TCP (non-TLS) based transport (unframed / stream-based).
    TCP = 4,

    /// TLS (over TCP) based transport (unframed / stream-based).
    TLS = 5,

    /// FUTURE (?):
    /// - add WireGuard (over UDP) based transport.
    /// - add QUIC (over UDP; using TLS 1.3 handshake messages; WebTransport browser API) based transport.
    /// - add WebRTC data channels (SCTP over DTLS; RTCDataChannel browser API) based transport.
    /// - add VirtIO (in-memory queues) based transport.
}
```

and

```
/// WAMP transport channel framing (`channel_framing`).
enum TransportChannelFraming: uint8
{
    /// Not set.
    NULL = 0,

    /// Raw transport itself is inherently message-based already (e.g. FUNCTION or VIRTIO).
    NATIVE = 1,

    /// Raw transport itself (e.g. TCP) is stream-based and channel framing applied is WebSocket (RFC6455).
    WEBSOCKET = 2,

    /// Raw transport itself (e.g. TCP) is stream-based and channel framing applied is RawSocket (WAMP).
    RAWSOCKET = 3,
}
```

and

```
/// WAMP transport channel serializer (`channel_serializer`).
enum TransportChannelSerializer: uint8
{
    /// Not set or applicable.
    NULL = 0,

    /// Use JSON serializer (for dynamically typed app payload).
    JSON = 1,

    /// Use MsgPack serializer (for dynamically typed app payload).
    MSGPACK = 2,

    /// Use CBOR serializer (for dynamically typed app payload).
    CBOR = 3,

    /// Use UBJSON serializer (for dynamically typed app payload).
    UBJSON = 4,

    /// Raw pass-through of app payload, uninterpreted in any way.
    OPAQUE = 5,

    /// Use FlatBuffers serialized (statically typed) payload (https://google.github.io/flatbuffers/index.html).
    FLATBUFFERS = 6,

    /// Use FlexBuffers serialized (dynamically typed) payload (https://google.github.io/flatbuffers/flexbuffers.html).
    FLEXBUFFERS = 7
}
```
