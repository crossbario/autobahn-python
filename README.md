# Autobahn|Python

WebSocket & WAMP for Python on Twisted and asyncio.

[![Version](https://img.shields.io/pypi/v/autobahn.svg)](https://pypi.python.org/pypi/autobahn)
[![Test](https://github.com/crossbario/autobahn-python/workflows/main/badge.svg)](https://github.com/crossbario/autobahn-python/actions?query=workflow%3Amain)
[![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)](https://autobahn.readthedocs.io/en/latest/)
<!--
[![CI Deploy Status](https://github.com/crossbario/autobahn-python/workflows/deploy/badge.svg)](https://github.com/crossbario/autobahn-python/actions?query=workflow%3Adeploy)
[![CI Docker Status](https://github.com/crossbario/autobahn-python/workflows/docker/badge.svg)](https://github.com/crossbario/autobahn-python/actions?query=workflow%3Adocker)
[![CI EXE Status](https://github.com/crossbario/autobahn-python/workflows/pyinstaller/badge.svg)](https://github.com/crossbario/autobahn-python/actions?query=workflow%3Apyinstaller)
[![Docker
Images](https://img.shields.io/badge/download-docker-blue.svg?style=flat)](https://hub.docker.com/r/crossbario/autobahn-python/)
-->

---

**Quick Links**:
[Source Code](https://github.com/crossbario/autobahn-python) -
[Documentation](https://autobahn.readthedocs.io/en/latest/) -
[WebSocket Examples](https://autobahn.readthedocs.io/en/latest/websocket/examples.html) -
[WAMP Examples](https://autobahn.readthedocs.io/en/latest/wamp/examples.html)
**Community**:
[Forum](https://crossbar.discourse.group/) -
[StackOverflow](https://stackoverflow.com/questions/tagged/autobahn) -
[Twitter](https://twitter.com/autobahnws) -
[IRC \#autobahn/chat.freenode.net](https://webchat.freenode.net/)
**Companion
Projects**:
[Autobahn|JS](https://github.com/crossbario/autobahn-js/) -
[Autobahn|Cpp](https://github.com/crossbario/autobahn-cpp) -
[Autobahn|Testsuite](https://github.com/crossbario/autobahn-testsuite) -
[Crossbar.io](https://crossbar.io) -
[WAMP](https://wamp-proto.org)

## Introduction

**Autobahn|Python** is a subproject of
[Autobahn](https://crossbar.io/autobahn) and provides open-source
implementations of

- [The WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [The Web Application Messaging Protocol (WAMP)](https://wamp-proto.org/)

for Python 3.7+ and running on
[Twisted](https://twistedmatrix.com/) and
[asyncio](https://docs.python.org/3/library/asyncio.html).

You can use **Autobahn|Python** to create clients and servers in
Python speaking just plain WebSocket or WAMP.

**WebSocket** allows
[bidirectional real-time messaging on the Web](https://crossbario.com/blog/post/websocket-why-what-can-i-use-it/)
and beyond, while [WAMP](https://wamp-proto.org/) adds real-time
application communication on top of WebSocket.

**WAMP** provides asynchronous **Remote Procedure Calls** and
**Publish & Subscribe** for applications in _one_ protocol
running over [WebSocket](https://tools.ietf.org/html/rfc6455).
WAMP is a _routed_ protocol, so you need a **WAMP Router** to
connect your **Autobahn|Python** based clients. We provide
[Crossbar.io](https://crossbar.io), but there are
[other options](https://wamp-proto.org/implementations.html#routers)
as well.

Note

**Autobahn|Python** up to version v19.11.2 supported Python 2 and
3.4+, and up to version v20.7.1 supported Python 3.5+, and up to
version v21.2.1 supported Python 3.6+.

## Features

- framework for [WebSocket](https://tools.ietf.org/html/rfc6455)
  and [WAMP](https://wamp-proto.org/) clients and servers
- runs on [CPython](https://python.org/) and
  <span class="title-ref">PyPy &lt;https://pypy.org/&gt;</span>
- runs under [Twisted](https://twistedmatrix.com/) and
  [asyncio](https://docs.python.org/3/library/asyncio.html) -
  implements WebSocket
  [RFC6455](https://tools.ietf.org/html/rfc6455) and Draft
  Hybi-10+
- implements
  [WebSocket compression](https://tools.ietf.org/html/draft-ietf-hybi-permessage-compression)
- implements [WAMP](https://wamp-proto.org/), the Web Application
  Messaging Protocol
- high-performance, fully asynchronous implementation
- best-in-class standards conformance (100% strict passes with
  [Autobahn Testsuite](https://crossbar.io/autobahn#testsuite):
  [Client](https://autobahn.ws/testsuite/reports/clients/index.html)
  [Server](https://autobahn.ws/testsuite/reports/servers/index.html))
- message-, frame- and streaming-APIs for WebSocket
- supports TLS (secure WebSocket) and proxies
- Open-source
  ([MIT license](https://github.com/crossbario/autobahn-python/blob/master/LICENSE))

---

## AI Policy

> **IMPORTANT: A Note on Upcoming Policy Changes Regarding AI-Assisted Content**
>
> Up to and including release **v25.6.1**, this project contains no code
> or documentation generated with the assistance of AI tools. This version
> represents the final release under our historical contribution policy.
> Starting with future versions (*after* release v25.6.1), our contribution policy
> will change. Subsequent releases **MAY** contain code or documentation
> created with AI assistance.

We urge all users and contributors to review our [AI
Policy](https://github.com/crossbario/autobahn-python/blob/master/AI_POLICY.md).
This document details:

-   The rules and warranties required for all future contributions.
-   The potential intellectual property implications for the project and
    its users.

This policy was established following an open community discussion,
which you can review on [GitHub issue
\#1663](https://github.com/crossbario/autobahn-python/issues/1663).

We are providing this transparent notice to enable you to make an
informed decision. If our new AI policy is incompatible with your own
(or your organization's) development practices or risk tolerance, please
take this into consideration when deciding whether to upgrade beyond
version v25.6.1.


## Show me some code

To give you a first impression, here are two examples. We have
lot more
[in the repo](https://github.com/crossbario/autobahn-python/tree/master/examples).

### WebSocket Echo Server

Here is a simple WebSocket Echo Server that will echo back any
WebSocket message received:

    from autobahn.twisted.websocket import WebSocketServerProtocol
    # or: from autobahn.asyncio.websocket import WebSocketServerProtocol

    class MyServerProtocol(WebSocketServerProtocol):

        def onConnect(self, request):
            print("Client connecting: {}".format(request.peer))

        def onOpen(self):
            print("WebSocket connection open.")

        def onMessage(self, payload, isBinary):
            if isBinary:
                print("Binary message received: {} bytes".format(len(payload)))
            else:
                print("Text message received: {}".format(payload.decode('utf8')))

            # echo back message verbatim
            self.sendMessage(payload, isBinary)

        def onClose(self, wasClean, code, reason):
            print("WebSocket connection closed: {}".format(reason))

To actually run above server protocol, you need some lines of
[boilerplate](https://autobahn.readthedocs.io/en/latest/websocket/programming.html#running-a-server).

### WAMP Application Component

Here is a WAMP Application Component that performs all four types
of actions that WAMP provides:

1.  **subscribe** to a topic
2.  **publish** an event
3.  **register** a procedure
4.  **call** a procedure

<!-- -->

    from autobahn.twisted.wamp import ApplicationSession
    # or: from autobahn.asyncio.wamp import ApplicationSession

    class MyComponent(ApplicationSession):

        @inlineCallbacks
        def onJoin(self, details):

            # 1. subscribe to a topic so we receive events
            def onevent(msg):
                print("Got event: {}".format(msg))

            yield self.subscribe(onevent, 'com.myapp.hello')

            # 2. publish an event to a topic
            self.publish('com.myapp.hello', 'Hello, world!')

            # 3. register a procedure for remote calling
            def add2(x, y):
                return x + y

            self.register(add2, 'com.myapp.add2')

            # 4. call a remote procedure
            res = yield self.call('com.myapp.add2', 2, 3)
            print("Got result: {}".format(res))

Above code will work on Twisted and asyncio by changing a single
line (the base class of `MyComponent`). To actually run above
application component, you need some lines of
[boilerplate](https://autobahn.readthedocs.io/en/latest/wamp/programming.html#running-components)
and a
[WAMP Router](https://autobahn.readthedocs.io/en/latest/wamp/programming.html#running-a-wamp-router).

## Packaging

The Autobahn|Python OSS project:

- build & publish *binary wheels* on [GitHub Releases](https://github.com/crossbario/autobahn-python/releases) and [PyPI](https://pypi.org/project/autobahn/)
- plans to publish on [pyx](https://astral.sh/blog/introducing-pyx) once that launches
- plans to support [WheelNext](https://wheelnext.dev/) once that launches (see also: https://lwn.net/Articles/1028299/, https://labs.quansight.org/blog/python-wheels-from-tags-to-variants)
- no longer bakes & publishes Docker images *
- no longer explicitly supports [PyInstaller](https://pyinstaller.org/) packaging

> *: for commercial users, *typedef int GmbH (Germany)*, original creator and active maintainer of Autobahn, Crossbar.io and WAMP provides production grade, optimized and supported Docker images based on RHEL 9 and Debian 12, including complete SBOM for both the base system and full Python application run-time environment based on [CycloneDX v1.6](https://cyclonedx.org/) in JSON format and as a audit-level PDF/A document fulfilling strict cybersecurity requirements addressing e.g. EU CRA and [BSI TR-03183](https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/Technische-Richtlinien/TR-nach-Thema-sortiert/tr03183/TR-03183_node.html).

## Package Releases

Autobahn|Python provides comprehensive binary wheel coverage for all major platforms and Python implementations.

### Generic

- **Source distribution**: `autobahn-25.9.1.tar.gz`
- **Pure Python 3 wheel**: `autobahn-25.9.1-py3-none-any.whl`

> **Note**: The pure Python wheel cannot include NVX (Native Vector Extensions) optimizations and will fall back to pure Python implementations. This provides maximum compatibility but slower performance compared to platform-specific wheels with native CFFI extensions.

### Linux

Available for x86_64 architecture with native CFFI extensions:

- `autobahn-25.9.1-cp311-cp311-linux_x86_64.whl`
- `autobahn-25.9.1-cp312-cp312-linux_x86_64.whl`
- `autobahn-25.9.1-cp313-cp313-linux_x86_64.whl`
- `autobahn-25.9.1-cp314-cp314-linux_x86_64.whl`
- `autobahn-25.9.1-pp311-pypy311_pp73-linux_x86_64.whl`

### macOS

Available for Apple Silicon (ARM64) architecture:

- `autobahn-25.9.1-cp312-cp312-macosx_15_0_arm64.whl`
- `autobahn-25.9.1-cp313-cp313-macosx_15_0_arm64.whl`
- `autobahn-25.9.1-cp314-cp314-macosx_11_0_arm64.whl`
- `autobahn-25.9.1-pp311-pypy311_pp73-macosx_11_0_arm64.whl`

### Windows

Available for x86_64 (AMD64) architecture:

- `autobahn-25.9.1-cp311-cp311-win_amd64.whl`
- `autobahn-25.9.1-cp312-cp312-win_amd64.whl`
- `autobahn-25.9.1-cp313-cp313-win_amd64.whl`
- `autobahn-25.9.1-cp314-cp314-win_amd64.whl`
- `autobahn-25.9.1-pp311-pypy311_pp73-win_amd64.whl`

All wheels include native CFFI extensions for optimal performance and are available from [PyPI](https://pypi.org/project/autobahn/) and [GitHub Releases](https://github.com/crossbario/autobahn-python/releases).

## Extensions

### Networking framework

Autobahn runs on both Twisted and asyncio. To select the
respective netoworking framework, install flavor:

- `asyncio`: Install asyncio (when on Python 2, otherwise it's
  included in the standard library already) and asyncio support
  in Autobahn
- `twisted`: Install Twisted and Twisted support in Autobahn

---

### WebSocket Acceleration and Compression

#### Acceleration (Deprecated)

The `accelerate` optional dependency is **no longer recommended**. Autobahn now includes **NVX** (Native Vector Extensions), which provides SIMD-accelerated native code for WebSocket operations (XOR masking and UTF-8 validation) using CFFI. See the [NVX section](#native-vector-extensions-nvx) below for details.

- ~~`accelerate`~~: Deprecated - Use NVX instead

#### Compression

Autobahn supports multiple WebSocket per-message compression algorithms via the `compress` optional dependency:

    pip install autobahn[compress]

**Compression Methods Available:**

| Method | Availability | Standard | Implementation | Notes |
|--------|--------------|----------|----------------|-------|
| **permessage-deflate** | Always | [RFC 7692](https://datatracker.ietf.org/doc/html/rfc7692) | Python stdlib (zlib) | Standard WebSocket compression |
| **permessage-brotli** | `[compress]` | [RFC 7932](https://datatracker.ietf.org/doc/html/rfc7932) | brotli / brotlicffi | **Recommended** - Best compression ratio |
| **permessage-bzip2** | Optional | Non-standard | Python stdlib (bz2) | Requires Python built with libbz2 |
| **permessage-snappy** | Manual install | Non-standard | python-snappy | Requires separate installation |

**Platform-Optimized Brotli Support:**

Autobahn includes **Brotli compression** with full binary wheel coverage optimized for both CPython and PyPy:

- **CPython**: Uses [brotli](https://github.com/google/brotli) (Google's official package, CPyExt)
- **PyPy**: Uses [brotlicffi](https://github.com/python-hyper/brotlicffi) (CFFI-based, optimized for PyPy)

**Advantages of Brotli:**
- **Superior compression ratio** compared to deflate or snappy
- **Binary wheels** for all major platforms (Linux x86_64/ARM64, macOS x86_64/ARM64, Windows x86_64)
- **IETF standard** ([RFC 7932](https://datatracker.ietf.org/doc/html/rfc7932)) for HTTP compression
- **Fast decompression** suitable for real-time applications
- **Widely adopted** by browsers and CDNs

**Resources:**
- [RFC 7932 - Brotli Compressed Data Format](https://datatracker.ietf.org/doc/html/rfc7932)
- [Google Brotli](https://github.com/google/brotli) - Official implementation
- [brotlicffi](https://github.com/python-hyper/brotlicffi) - CFFI bindings for PyPy
- [PyPI: brotlicffi](https://pypi.org/project/brotlicffi/)
- [WAMP Brotli Extension Discussion](https://github.com/wamp-proto/wamp-proto/issues/555)

**Note on Snappy:**

[Snappy](https://github.com/google/snappy) compression is available but requires manual installation of [python-snappy](https://pypi.org/project/python-snappy/) (no binary wheels):

    pip install python-snappy  # Requires libsnappy-dev system library

For most use cases, **Brotli is recommended** over Snappy due to better compression ratios and included binary wheels.

---

### Encryption and WAMP authentication

Autobahn supports running over TLS (for WebSocket and all WAMP
transports) as well as **WAMP-cryposign** authentication.

To install use this flavor:

- `encryption`: Installs TLS and WAMP-cryptosign dependencies

Autobahn also supports **WAMP-SCRAM** authentication. To install:

- `scram`: Installs WAMP-SCRAM dependencies

---

### Native vector extensions (NVX)

&gt; This is NOT yet complete - ALPHA!

Autobahn contains **NVX**, a network accelerator library that
provides SIMD accelerated native vector code for WebSocket (XOR
masking) and UTF-8 validation.

> NVX lives in namespace
> <span class="title-ref">autobahn.nvx</span> and currently
> requires a x86-86 CPU with at least SSE2 and makes use of
> SSE4.1 if available. The code is written using vector
> instrinsics, should compile with both GCC and Clang,and
> interfaces with Python using CFFI, and hence runs fast on PyPy.

---

### WAMP Serializers

**As of v25.11.1, all WAMP serializers are included by default** - batteries included!

Autobahn|Python now ships with full support for all WAMP serializers out-of-the-box:

- **JSON** (standard library) - always available
- **MessagePack** - high-performance binary serialization
- **CBOR** - IETF standard binary serialization (RFC 8949)
- **UBJSON** - Universal Binary JSON
- **Flatbuffers** - Google's zero-copy serialization (vendored)

#### Architecture & Performance

The serializer dependencies are optimized for both **CPython** and **PyPy**:

| Serializer | CPython | PyPy | Wheel Type | Notes |
|------------|---------|------|------------|-------|
| **json** | stdlib | stdlib | - | Always available |
| **msgpack** | Binary wheel (C extension) | u-msgpack-python (pure Python) | Native + Universal | PyPy JIT makes pure Python faster than C |
| **ujson** | Binary wheel | Binary wheel | Native | Available for both implementations |
| **cbor2** | Binary wheel | Pure Python fallback | Native + Universal | Binary wheels + py3-none-any |
| **ubjson** | Pure Python | Pure Python | Source | Set `PYUBJSON_NO_EXTENSION=1` to skip C build |
| **flatbuffers** | Vendored | Vendored | Included | Always available, no external dependency |

**Key Design Principles:**

1. **Batteries Included**: All serializers available without extra install steps
2. **PyPy Optimization**: Pure Python implementations leverage PyPy's JIT for superior performance
3. **Binary Wheels**: Native wheels for all major platforms (Linux x86_64/ARM64, macOS x86_64/ARM64, Windows x86_64)
4. **Zero System Pollution**: All dependencies install cleanly via wheels or pure Python
5. **WAMP Compliance**: Full protocol support out-of-the-box

**Total Additional Size**: ~590KB (negligible compared to full application install)

#### Platform Coverage

All serializer dependencies provide binary wheels for:
- **Linux**: x86_64, ARM64 (manylinux, musllinux)
- **macOS**: x86_64 (Intel), ARM64 (Apple Silicon)
- **Windows**: x86_64 (AMD64), ARM64
- **Python**: 3.11, 3.12, 3.13, 3.14 (including 3.14t free-threaded)
- **Implementations**: CPython, PyPy 3.11+

#### Backwards Compatibility

The `serialization` optional dependency is maintained for backwards compatibility:

    pip install autobahn[serialization]  # Still works, but now a no-op

#### ujson Acceleration

To speed up JSON on CPython using the faster `ujson`, set:

    AUTOBAHN_USE_UJSON=1

> **Warning**: Using `ujson` will break the ability of Autobahn to transport and translate binary application payloads in WAMP transparently. This ability depends on features of the standard library `json` module not available in `ujson`.

#### Recommendations

- **General use**: JSON (stdlib) or CBOR
- **High performance**: MessagePack or Flatbuffers
- **Strict standards**: CBOR (IETF RFC 8949)
- **Zero-copy**: Flatbuffers (for large payloads)
