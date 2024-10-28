# FlatBuffers and WAMP

## WAMP payload transparency mode

### Motivation

**tldr:**

* performance (passthrough of app payloads, general zero copy)
* support end-to-end encryption
* carrying proprietary binary payloads (MQTT)
* strict static typing of interfaces

---

WAMP supports both positional and keyword based request arguments and returns.

For example, the WAMP `CALL` message allows for the following three alternative forms:

1. `[CALL, Request|id, Options|dict, Procedure|uri]`
2. `[CALL, Request|id, Options|dict, Procedure|uri, Arguments|list]`
3. `[CALL, Request|id, Options|dict, Procedure|uri, Arguments|list, ArgumentsKw|dict]`

The actual application payload hence can take **three variants of app payload (XX)**:

1. `-`
2. `Arguments|list`
3. `Arguments|list, ArgumentsKw|dict`

This pattern repeats across **all** WAMP messages that can carry application payload, namely the following 7 WAMP messages:

* `PUBLISH`
* `EVENT`
* `CALL`
* `INVOCATION`
* `YIELD`
* `RESULT`
* `ERROR`

> Note: should the proposed new WAMP messages `EVENT_RECEIVED` and `SUBSCRIBER_RECEIVED` be introduced,
these also carry application payload, and would follow the same approach.

The approach taken (**XX**) allows for a number of useful features:

1. flexible support of popular dynamically typed serializers, namely: JSON, MsgPack, CBOR and UBJSON
2. allow arbitrary adhoc extensibility (as the router basically does not care about new app payloads)
3. transparently translate the *application payload* between serialization formats used by different clients connected at the same time.
4. support optional router side application payload validation: both static, and dynamic (calling into user supplied payload validators)

However, a number of downsides have become apparent as well:

1. resource consumption: serialization/deserialization can eat significant chunks of CPU, and produce GC pressure
2. legacy (MQTT) and proprietary payloads that should simply be transported "as is" (passthrough, without ever touching)
3. as apps and systems get larger and more complex, the dynamic typing flexibility turns into a major problem: **the internal and external interfaces and APIs in a microservices based application must be relied upon and their evolution actively managed**

The latter does not mean an "either or" question. You can have important base APIs and external interfaces defined rigorously, using static, strict typing discipline, while at the same time have other parts of your system evolve more freely, basically allowing weakly and dynamically typed data exchange - for limited areas.

---


### Payload Transparency Mode

**Payload Transparency Mode (PTM)** adds a 4th application payload variant to above **XX**

4. `[CALL, Request|id, Options|dict, Procedure|uri, Payload|binary]`

where the actual application payload takes this form:

4. `Payload|binary`

**PTM** can be used on a *per message basis*.

If PTM is used, then the following two attributes MUST be present in the `Details|dict` or `Options|dict` of the respective WAMP message:

* `payload|string`: Application payload type:
    * `"plain"`: Plain WAMP application payload.
    * `"cryptobox"`: Encrypted WAMP application payload. This is using WAMP-cryptobox (Curve25519 / Cryptobox).
    * `"opaque"`: Raw pass-through of app payload, uninterpreted in any way.
* `serializer|string`: Application payload serializer type.
    * `"transport"`: Use same (dynamic) serializer for the app payload as on the transport. This will be one of JSON, MSGPACK, CBOR or UBJSON.
    * `"json"`: Use JSON serializer (for dynamically typed app payload).
    * `"msgpack"`: Use MsgPack serializer (for dynamically typed app payload).
    * `"cbor"`: Use CBOR serializer (for dynamically typed app payload).
    * `"ubjson"`: Use UBJSON serializer (for dynamically typed app payload).
    * `"opaque"`: Raw pass-through of app payload, uninterpreted in any way.
    * `"flatbuffers"`: Explicit use of FlatBuffers also for (statically typed) payload.
* `key|string`: When using end-to-end encryption (WAMP-cryptobox), the public key to which the payload is encrypted
---

#### Payload PLAIN

When PTM is in use, and `Details.payload=="plain"`, the original application payload, one of

* `-`
* `Arguments|list`
* `Arguments|list, ArgumentsKw|dict`

is serialized according to the (dynamically typed) serializer specified in `serializer`, one of

* `"transport"`
* `"msgpack"`
* `"json"`
* `"cbor"`
* `"ubjson"`

> Note that serializers `"opaque"` and `"flatbuffers"` are illegal for payload `"plain"`.

---

#### Payload CRYPTOBOX

Write me.

---

#### Payload OPAQUE

Write me.

---


## FlatBuffers

FlatBuffers is a zero-copy serialization format open-sourced by Google in 2014 under the Apache 2 license.

Supported operating systems include:

* Android
* Linux
* MacOS X
* Windows

Supported programming languages include:

* C++
* C#
* C
* Go
* Java
* JavaScript
* PHP
* Python

---

## Building

1. Get [cmake](https://cmake.org/)
2. Follow [Building with CMake](https://github.com/google/flatbuffers/blob/master/docs/source/Building.md#building-with-cmake)

Essentially:

```console
git clone https://github.com/google/flatbuffers.git
cd flatbuffers
cmake -G "Unix Makefiles"
make -j4
./flatc --version
```

---

### flatc patches

The following patches are required currently for flatc: [this PR](https://github.com/google/flatbuffers/pull/4713) adds pieces missing for reflection in the flatc compiler.

---


## Usage

This folder contains a [Makefile](Makefile) that allows to compile all WAMP FlatBuffers schemata and generate binding code in various languages using

```console
make clean build cloc
```

Here is example output (a total of 30k LOC generated from 500 LOC .fbs):

```console
cpy2714_1) oberstet@thinkpad-t430s:~/scm/wamp-proto/wamp-proto/flatbuffers$ make clean build cloc
rm -rf ./_build
/home/oberstet/scm/xbr/flatbuffers/flatc -o ./_build/schema/ --binary --schema --bfbs-comments --bfbs-builtin-attrs *.fbs
/home/oberstet/scm/xbr/flatbuffers/flatc -o ./_build/cpp/ --cpp *.fbs
/home/oberstet/scm/xbr/flatbuffers/flatc -o ./_build/csharp/ --csharp *.fbs
/home/oberstet/scm/xbr/flatbuffers/flatc -o ./_build/go/ --go *.fbs
/home/oberstet/scm/xbr/flatbuffers/flatc -o ./_build/java/ --java *.fbs
/home/oberstet/scm/xbr/flatbuffers/flatc -o ./_build/js/ --js *.fbs
/home/oberstet/scm/xbr/flatbuffers/flatc -o ./_build/php/ --php *.fbs
/home/oberstet/scm/xbr/flatbuffers/flatc -o ./_build/python/ --python *.fbs
/home/oberstet/scm/xbr/flatbuffers/flatc -o ./_build/ts/ --ts *.fbs
cloc --read-lang-def=cloc.def --exclude-dir=_build .
      11 text files.
      11 unique files.                              
       2 files ignored.

github.com/AlDanial/cloc v 1.76  T=0.01 s (774.6 files/s, 113640.1 lines/s)
---------------------------------------------------------------------------------------
Language                             files          blank        comment           code
---------------------------------------------------------------------------------------
FlatBuffers                              7            314            372            535
Markdown                                 1             64              0            119
make                                     1             20              8             30
Windows Module Definition                1              0              0              5
---------------------------------------------------------------------------------------
SUM:                                    10            398            380            689
---------------------------------------------------------------------------------------
cloc ./_build
     331 text files.
     331 unique files.                                          
       2 files ignored.

github.com/AlDanial/cloc v 1.76  T=0.35 s (942.1 files/s, 132452.9 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
C/C++ Header                     7            405              7           5629
PHP                             62            961           3206           5006
Go                              62            826             62           4815
TypeScript                       7            832           3430           3428
JavaScript                       7            896           3493           3177
Java                            62            439             62           2825
C#                              62            477            186           2800
Python                          62            616            454           2504
-------------------------------------------------------------------------------
SUM:                           331           5452          10900          30184
-------------------------------------------------------------------------------
```

---


## Notes

* FlatBuffers [currently lacks](https://github.com/google/flatbuffers/issues/4237) syntax highlighting on GitHub.

---

## References

* [FlatBuffers Homepage](https://google.github.io/flatbuffers/)
* [FlatBuffers Source](https://github.com/google/flatbuffers)
* [flatcc - a FlatBuffers Compiler and Library in C for C](https://github.com/dvidelabs/flatcc)


---
