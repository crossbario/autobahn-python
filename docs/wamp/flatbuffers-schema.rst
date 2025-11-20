.. _wamp-flatbuffers-schema:

FlatBuffers Schema Reference
=============================

Autobahn|Python includes comprehensive FlatBuffers schema definitions for WAMP messages and application payloads. This page documents the schemas, their purpose, and how they enable both high-performance serialization and static typing for WAMP applications.

Why FlatBuffers for WAMP?
--------------------------

FlatBuffers serve **two fundamental purposes** in the WAMP ecosystem:

**1. Zero-Copy Serialization (WEP006)**

FlatBuffers provide a high-performance, zero-copy binary serialization format particularly well-suited for network protocols like WAMP:

* **Zero-copy deserialization** - Messages can be accessed directly from wire buffers without parsing overhead
* **Smaller message size** - Typically 20-30% smaller than JSON for WAMP messages
* **Faster processing** - Up to 10x faster than JSON for complex messages, crucial for high-throughput applications
* **PyPy compatibility** - Pure Python fallback ensures excellent performance on PyPy's JIT compiler

See `WEP006 - Zero-copy WAMP Serialization with Flatbuffers <https://github.com/wamp-proto/wamp-proto/blob/master/wep/wep006/README.md>`_ and `issue #72 <https://github.com/wamp-proto/wamp-proto/issues/72>`_.

**2. WAMP IDL for Static Typing (WEP007)**

FlatBuffers IDL enables **WAMP Interface Description Language (WAMP IDL)** for statically typing WAMP application interfaces:

* **Type-safe WAMP APIs** - Define typed contracts for procedures and topics
* **Interface declarations** - Group related procedures and topics into named interfaces with UUIDs
* **Code generation** - Generate type-safe client/server code from interface definitions
* **API documentation** - Machine-readable API catalogs for discovery and tooling
* **Payload validation** - Runtime validation of call arguments and results against schemas

WAMP IDL uses FlatBuffers custom attributes (``wampid``, ``wampuri``, ``arg``, ``kwarg``, etc.) to map WAMP concepts to FlatBuffers types, enabling rich interface definitions like the `WAMP Meta API <https://github.com/wamp-proto/wamp-proto/blob/master/catalog/src/wamp-meta.fbs>`_.

See `WEP007 - WAMP API Schema Definition with Flatbuffers <https://github.com/wamp-proto/wamp-proto/blob/master/wep/wep007/README.md>`_, the `WAMP specification on WAMP IDL <https://wamp-proto.org/wamp_latest_ietf.html#name-wamp-idl>`_, and `issue #355 <https://github.com/wamp-proto/wamp-proto/issues/355>`_.

**Performance Benchmarks**

Comprehensive benchmarks demonstrating FlatBuffers performance advantages exist in a separate repository. These sophisticated benchmarks use `vmprof <https://vmprof.readthedocs.io/>`_ for PyPy-compatible profiling (including GC analysis) and generate flamegraphs for detailed performance visualization. These benchmarks should be integrated into this repository in the future.

Overview
--------

The WAMP FlatBuffers schemas define all WAMP message types using Google's `FlatBuffers <https://google.github.io/flatbuffers/>`_ Interface Definition Language (IDL). These schemas are:

* **Compiled to binary reflection schemas** (.bfbs files) for runtime schema introspection
* **Auto-generated to Python wrapper classes** for type-safe message construction and parsing
* **Mapped to WAMP message classes** in :mod:`autobahn.wamp.message` for seamless integration
* **Used in WAMP IDL** for declaring typed WAMP interfaces, procedures, and topics

Schema Files
------------

Source Schemas (.fbs)
~~~~~~~~~~~~~~~~~~~~~

FlatBuffers IDL source files are located in ``autobahn/wamp/flatbuffers/``:

.. list-table:: Source Schema Files
   :header-rows: 1
   :widths: 30 70

   * - File
     - Description
   * - `session.fbs <../_static/flatbuffers/session.fbs>`_
     - Session lifecycle messages: Hello, Welcome, Abort, Challenge, Authenticate, Goodbye, Error
   * - `pubsub.fbs <../_static/flatbuffers/pubsub.fbs>`_
     - Publish/Subscribe messages: Subscribe, Subscribed, Unsubscribe, Unsubscribed, Publish, Published, Event, EventReceived
   * - `rpc.fbs <../_static/flatbuffers/rpc.fbs>`_
     - RPC messages: Register, Registered, Unregister, Unregistered, Call, Cancel, Result, Invocation, Interrupt, Yield
   * - `auth.fbs <../_static/flatbuffers/auth.fbs>`_
     - Authentication method details: WAMP-CRA, WAMP-Cryptosign, WAMP-SCRAM, WAMP-Ticket
   * - `roles.fbs <../_static/flatbuffers/roles.fbs>`_
     - WAMP roles and features: ClientRoles, RouterRoles, Broker/Dealer/Publisher/Subscriber/Caller/Callee features
   * - `types.fbs <../_static/flatbuffers/types.fbs>`_
     - Common types: Map, Void, enums (Serializer, Payload, MessageType, AuthMethod, Match)
   * - `wamp.fbs <../_static/flatbuffers/wamp.fbs>`_
     - Root WAMP message union type

Binary Schemas (.bfbs)
~~~~~~~~~~~~~~~~~~~~~~

Compiled binary reflection schemas are located in ``autobahn/wamp/gen/schema/``:

* `session.bfbs <../_static/flatbuffers/schema/session.bfbs>`_ - Compiled from session.fbs
* `pubsub.bfbs <../_static/flatbuffers/schema/pubsub.bfbs>`_ - Compiled from pubsub.fbs
* `rpc.bfbs <../_static/flatbuffers/schema/rpc.bfbs>`_ - Compiled from rpc.fbs
* `auth.bfbs <../_static/flatbuffers/schema/auth.bfbs>`_ - Compiled from auth.fbs
* `roles.bfbs <../_static/flatbuffers/schema/roles.bfbs>`_ - Compiled from roles.fbs
* `types.bfbs <../_static/flatbuffers/schema/types.bfbs>`_ - Compiled from types.fbs
* `wamp.bfbs <../_static/flatbuffers/schema/wamp.bfbs>`_ - Compiled from wamp.fbs

These files are included in the Python package distribution and can be accessed programmatically:

.. code-block:: python

   from importlib.resources import files

   # Access binary schema files
   schema_pkg = files('autobahn.wamp.gen.schema')
   wamp_schema = schema_pkg.joinpath('wamp.bfbs').read_bytes()

   # Access source schema files
   fbs_pkg = files('autobahn.wamp.flatbuffers')
   wamp_fbs = fbs_pkg.joinpath('wamp.fbs').read_text()

Schema Design Patterns
----------------------

The FlatBuffers schemas follow consistent design patterns for application payload handling and router-to-router message forwarding. These patterns ensure compatibility, consistency, and correct behavior across all WAMP message types.

Application Payload Handling (6-Field Set)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All WAMP message types that carry **application payload** (Publish, Event, Call, Result, Invocation, Yield, Error) consistently include a **6-field set** that supports both normal mode and transparent mode payload handling:

.. code-block:: fbs

   /// Positional values for application-defined payload.
   args: [uint8];

   /// Keyword values for application-defined payload.
   kwargs: [uint8];

   /// Alternative, transparent payload. If given, ``args`` and ``kwargs`` must be left unset.
   payload: [uint8];

   // The encoding algorithm that was used to encode the payload.
   enc_algo: Payload;

   // The payload object serializer that was used encoding the payload.
   enc_serializer: Serializer;

   // When using Payload.CRYPTOBOX, the public Cryptobox key of the key pair used for encrypting the payload.
   enc_key: [uint8];

**Two Operational Modes:**

1. **Normal Mode** (Dynamic Typing)

   * Uses ``args`` and ``kwargs`` fields
   * ``payload`` field must be empty/unset
   * Each field (args, kwargs) is independently serialized using ``enc_serializer``
   * Supports JSON, MessagePack, CBOR, UBJSON serializers
   * Enables dynamic, schema-less application payloads

   Example:

   .. code-block:: python

      # Publishing with args/kwargs (CBOR-serialized)
      publish = Publish(
          topic='com.example.topic',
          args=[1, 2, 3],
          kwargs={'key': 'value'},
          enc_serializer='cbor'  # Serializer used for args/kwargs
      )

2. **Transparent Mode** (Static Typing / E2EE)

   * Uses ``payload`` field
   * ``args`` and ``kwargs`` fields must be empty/unset
   * Payload is opaque bytes, potentially encrypted or statically typed
   * Supports end-to-end encryption (E2EE) via Payload.CRYPTOBOX
   * Supports embedded FlatBuffers for static typing (ENC_SER_FLATBUFFERS)

   Example:

   .. code-block:: python

      # Publishing with encrypted payload
      publish = Publish(
          topic='com.example.topic',
          payload=encrypted_bytes,
          enc_algo=Payload.CRYPTOBOX,
          enc_serializer='cbor',  # Serializer of original data before encryption
          enc_key=public_key
      )

      # Publishing with embedded FlatBuffers (static typing)
      result = Result(
          request=12345,
          payload=flatbuffers_bytes,  # Pre-serialized FlatBuffers data
          enc_serializer='flatbuffers'  # ENC_SER_FLATBUFFERS
      )

**The "FlatBuffers-CBOR" Pattern:**

The most common pattern is using FlatBuffers for WAMP message structure while using CBOR (or other serializers) for application payload:

* **WAMP message envelope**: FlatBuffers (zero-copy, high performance)
* **Application payload (args/kwargs)**: CBOR-encoded bytes in args/kwargs fields
* **Configurable**: Can use JSON, MessagePack, UBJSON instead of CBOR via ``enc_serializer``
* **Extensible**: Can embed statically-typed FlatBuffers payloads via ENC_SER_FLATBUFFERS

This composition provides flexibility while maintaining high performance.

Router-to-Router Message Forwarding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All WAMP message types that carry application payload also support **Router-to-Router (R2R) link message forwarding** via the ``forward_for`` field:

.. code-block:: fbs

   // R2R-link message forwarding route that was taken.
   forward_for: [Principal];

Where ``Principal`` is defined as:

.. code-block:: fbs

   struct Principal
   {
       // WAMP session ID.
       session: uint64;

       // Note: authid and authrole are commented out in schema due to
       // FlatBuffers struct limitation (structs can only contain scalars)
   }

**Message Types with forward_for:**

The following message types include the ``forward_for`` field for R2R routing:

**Messages with Application Payload:**

* Publish - Events published by clients, forwarded through routers
* Event - Events delivered to subscribers, may traverse multiple routers
* Call - RPC calls from callers, routed to callees
* Result - RPC results from callees, routed back to callers
* Invocation - RPC invocations to callees, may be forwarded
* Yield - RPC yields from callees, routed back through intermediaries
* Error - Error messages from any role, must be routed back to originator

**Control Messages (No Application Payload):**

* Cancel - Call cancellation requests, routed through R2R links
* Interrupt - Invocation interruption requests, routed through R2R links

**Purpose:**

The ``forward_for`` field tracks the routing path taken by a message as it traverses multiple WAMP routers in distributed deployments. Each intermediate router appends its principal (session information) to the array, enabling:

* **Message provenance tracking** - Know which routers handled the message
* **Loop detection** - Prevent circular routing in complex topologies
* **Audit trails** - Security and compliance logging of message paths
* **Federation support** - Essential for router-to-router federation scenarios

**Example:**

.. code-block:: python

   # Error with forwarding information
   error = Error(
       request_type=MessageType.CALL,
       request=12345,
       error='wamp.error.runtime_error',
       args=['Callee encountered an error'],
       forward_for=[
           {'session': 9876543210, 'authid': None, 'authrole': None},  # Router 1
           {'session': 1234567890, 'authid': None, 'authrole': None},  # Router 2
       ]
   )

Python Implementation Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Python message classes in :mod:`autobahn.wamp.message` implement lazy deserialization patterns for FlatBuffers support:

**1. Initialization Pattern:**

.. code-block:: python

   def __init__(self,
                request=None,
                topic=None,
                args=None,
                kwargs=None,
                # ... other parameters ...
                from_fbs=None):  # FlatBuffers support parameter
       """
       Constructor supports both direct instantiation and lazy FlatBuffers deserialization.

       :param from_fbs: Optional FlatBuffers message object for lazy deserialization
       """
       Message.__init__(self, from_fbs=from_fbs)  # Pass to parent

       # Use underscore-prefixed private attributes
       self._request = request
       self._topic = topic
       self._args = args
       self._kwargs = _validate_kwargs(kwargs)
       # ... initialize all attributes with underscore prefix

**2. Lazy Property Pattern:**

Properties provide lazy deserialization from FlatBuffers when accessed:

.. code-block:: python

   @property
   def args(self):
       """Lazy deserialize args from FlatBuffers."""
       if self._args is None and self._from_fbs:
           if self._from_fbs.ArgsLength():
               # Deserialize using CBOR (respects enc_serializer in future)
               self._args = cbor2.loads(bytes(self._from_fbs.ArgsAsBytes()))
       return self._args

   @args.setter
   def args(self, value):
       assert value is None or type(value) in [list, tuple]
       self._args = value

**3. __slots__ Pattern:**

All attributes use underscore-prefixed names to match private storage:

.. code-block:: python

   __slots__ = (
       '_request',
       '_topic',
       '_args',
       '_kwargs',
       '_payload',
       # ... all attributes with underscore prefix
   )

**4. Equality Pattern:**

Comparison uses property getters (not direct attribute access) to support lazy deserialization:

.. code-block:: python

   def __eq__(self, other):
       if not isinstance(other, self.__class__):
           return False
       if not Message.__eq__(self, other):
           return False
       # Use property getters, not self._args
       if other.args != self.args:
           return False
       if other.kwargs != self.kwargs:
           return False
       # ... compare all attributes via properties
       return True

These patterns ensure that:

* Messages can be constructed directly (normal mode) or from FlatBuffers (lazy mode)
* Deserialization only occurs when attributes are actually accessed (zero-copy benefits)
* All message operations (equality, serialization, etc.) work correctly in both modes

Serialization Architecture
---------------------------

Autobahn|Python's FlatBuffers implementation uses a **dual-serializer architecture** that separates envelope serialization from application payload serialization. This architecture enables flexible composition patterns while maintaining clean separation of concerns.

Protocol-Level Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the WAMP protocol level, messages have two conceptually distinct parts:

**Message Envelope (Fixed Structure)**
   The WAMP message structure itself with fixed fields defined by the protocol specification:

   * Message type code (PUBLISH, CALL, RESULT, etc.)
   * Request/session IDs
   * URIs (topics, procedures, error URIs)
   * Options and details dictionaries
   * Metadata (forwarding info, caller disclosure, etc.)

**Application Payload (Dynamic Content)**
   The actual application data being transmitted:

   * ``args`` - Positional arguments (list)
   * ``kwargs`` - Keyword arguments (dict)
   * ``payload`` - Transparent payload (bytes, for E2EE or embedded FlatBuffers)

These two parts can be serialized using **different formats** to optimize for different requirements:

* **Envelope**: Benefits from FlatBuffers' zero-copy deserialization and static typing
* **Payload**: May use dynamic serializers (JSON/CBOR/MsgPack) for flexibility or embedded FlatBuffers for static typing

Implementation-Level Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The implementation uses three key abstractions to support dual serialization:

**ISerializer (Transport Serializer)**
   Responsible for serializing the complete WAMP message (envelope + payload).

   Key properties:

   * ``SERIALIZER_ID`` - Transport format ID (e.g., ``"flatbuffers"``, ``"json"``, ``"cbor"``)
   * ``PAYLOAD_SERIALIZER_ID`` - Application payload format ID (may differ from ``SERIALIZER_ID``)
   * ``serialize(msg)`` - Serialize complete WAMP message to bytes
   * ``serialize_payload(data)`` - Serialize application payload (args/kwargs) to bytes

   Implementations:

   * ``JsonSerializer`` - Both envelope and payload use JSON
   * ``CBORSerializer`` - Both envelope and payload use CBOR
   * ``MsgPackSerializer`` - Both envelope and payload use MessagePack
   * ``FlatBuffersSerializer`` - Envelope uses FlatBuffers, payload is **configurable**

**IObjectSerializer (Format-Specific Serializer)**
   Low-level serializer for a specific format (JSON, CBOR, etc.).

   Properties:

   * ``NAME`` - Format name (e.g., ``"json"``, ``"cbor"``)
   * ``BINARY`` - Whether format requires binary-clean transport
   * ``serialize(obj)`` / ``unserialize(bytes)`` - Format conversion

   Implementations:

   * ``JsonObjectSerializer`` - JSON format serialization
   * ``CBORObjectSerializer`` - CBOR format serialization
   * ``MsgPackObjectSerializer`` - MessagePack format serialization
   * ``FlatBuffersObjectSerializer`` - FlatBuffers format serialization

**Message.build(builder, serializer)**
   Builds FlatBuffers representation of a WAMP message.

   * ``builder`` - FlatBuffers builder instance
   * ``serializer`` - ISerializer instance for payload serialization
   * Uses ``serializer.serialize_payload()`` to serialize args/kwargs according to ``PAYLOAD_SERIALIZER_ID``

Serialization Flow
~~~~~~~~~~~~~~~~~~

The complete serialization flow for a WAMP message with FlatBuffers envelope:

.. code-block:: text

   User creates message:
      msg = Publish(topic="com.example.topic", args=[1, 2, 3])

   User calls serializer:
      data = serializer.serialize(msg)
      ↓
   ISerializer (FlatBuffersSerializer):
      - SERIALIZER_ID = "flatbuffers" (envelope format)
      - PAYLOAD_SERIALIZER_ID = "cbor" (payload format, configurable)
      ↓
   Message.serialize(object_serializer):
      - Receives IObjectSerializer (FlatBuffersObjectSerializer)
      - Accesses parent ISerializer via _parent_serializer back-reference
      - Creates FlatBuffers builder
      - Calls self.build(builder, parent_serializer)
      ↓
   Message.build(builder, serializer):
      - Serializes message envelope to FlatBuffers
      - Calls serializer.serialize_payload(args) for args
      - Calls serializer.serialize_payload(kwargs) for kwargs
      - ISerializer uses configured payload serializer (e.g., CBOR)
      ↓
   Result:
      - WAMP message envelope: FlatBuffers (zero-copy, static typing)
      - Application payload: CBOR (dynamic typing, compact)

Composition Patterns
~~~~~~~~~~~~~~~~~~~~

The dual-serializer architecture supports multiple composition patterns:

**Traditional (Homogeneous Serialization)**
   Envelope and payload use the same format:

   .. code-block:: python

      # JSON for everything
      serializer = JsonSerializer()
      # SERIALIZER_ID = "json"
      # PAYLOAD_SERIALIZER_ID = "json"

      # CBOR for everything
      serializer = CBORSerializer()
      # SERIALIZER_ID = "cbor"
      # PAYLOAD_SERIALIZER_ID = "cbor"

**FlatBuffers-CBOR (Default Composition)**
   FlatBuffers envelope with CBOR payload (optimal for most use cases):

   .. code-block:: python

      serializer = FlatBuffersSerializer(payload_serializer="cbor")
      # SERIALIZER_ID = "flatbuffers"
      # PAYLOAD_SERIALIZER_ID = "cbor"

   Benefits:

   * Zero-copy envelope parsing (FlatBuffers)
   * Compact, flexible payload (CBOR)
   * Best general-purpose performance

**FlatBuffers-JSON**
   FlatBuffers envelope with JSON payload (debugging, browser compatibility):

   .. code-block:: python

      serializer = FlatBuffersSerializer(payload_serializer="json")
      # SERIALIZER_ID = "flatbuffers"
      # PAYLOAD_SERIALIZER_ID = "json"

   Benefits:

   * Zero-copy envelope parsing (FlatBuffers)
   * Human-readable payload (JSON)
   * Useful for debugging and web applications

**FlatBuffers-FlatBuffers (Static Typing)**
   Both envelope and payload use FlatBuffers (maximum performance and type safety):

   .. code-block:: python

      serializer = FlatBuffersSerializer(payload_serializer="flatbuffers")
      # SERIALIZER_ID = "flatbuffers"
      # PAYLOAD_SERIALIZER_ID = "flatbuffers"

   Benefits:

   * Complete zero-copy deserialization
   * Static typing for both envelope and payload
   * Maximum performance for typed APIs
   * Enables WAMP IDL with embedded FlatBuffers schemas

This pattern enables **WAMP IDL** where procedure arguments and results are defined using FlatBuffers schemas, providing compile-time type checking and runtime validation.

Configuration and Usage
~~~~~~~~~~~~~~~~~~~~~~~

Creating serializers with different payload formats:

.. code-block:: python

   from autobahn.wamp.serializer import FlatBuffersSerializer

   # Default: FlatBuffers envelope + CBOR payload
   ser1 = FlatBuffersSerializer()

   # FlatBuffers envelope + JSON payload
   ser2 = FlatBuffersSerializer(payload_serializer="json")

   # FlatBuffers envelope + MessagePack payload
   ser3 = FlatBuffersSerializer(payload_serializer="msgpack")

   # FlatBuffers envelope + FlatBuffers payload (WAMP IDL)
   ser4 = FlatBuffersSerializer(payload_serializer="flatbuffers")

   # Access serializer properties
   print(ser1.SERIALIZER_ID)          # "flatbuffers"
   print(ser1.PAYLOAD_SERIALIZER_ID)  # "cbor"
   print(ser2.PAYLOAD_SERIALIZER_ID)  # "json"

Using serializers with WAMP sessions:

.. code-block:: python

   from autobahn.wamp.serializer import create_transport_serializers

   # Configure transport with FlatBuffers-CBOR
   transport = {
       'serializers': ['flatbuffers']  # Uses CBOR payload by default
   }
   serializers = create_transport_serializers(transport)

   # Use with ApplicationSession
   session = ApplicationSession()
   session._transport.serializers = serializers

Design Benefits
~~~~~~~~~~~~~~~

This dual-serializer architecture provides several key benefits:

**Explicit Separation of Concerns**
   * Envelope serialization (protocol structure) is decoupled from payload serialization (application data)
   * Each can be optimized independently for its specific requirements
   * Clear architectural boundaries match protocol semantics

**Flexible Composition**
   * Mix and match envelope and payload formats
   * Optimize for different use cases (debugging, performance, type safety)
   * Smooth migration path from traditional to FlatBuffers serialization

**Performance Optimization**
   * FlatBuffers envelope: Zero-copy deserialization of protocol structure
   * CBOR payload: Compact encoding of dynamic application data
   * Best of both worlds: Static typing where needed, dynamic typing where useful

**WAMP IDL Support**
   * FlatBuffers-FlatBuffers enables typed WAMP APIs
   * Embedded schemas provide runtime validation
   * Code generation from interface definitions
   * Type-safe RPC and pub/sub

**Backwards Compatibility**
   * Traditional serializers (JSON, CBOR, MsgPack) continue to work unchanged
   * ``PAYLOAD_SERIALIZER_ID`` defaults to ``SERIALIZER_ID`` for traditional serializers
   * Smooth adoption path for existing applications

Message Type Mapping
--------------------

The following table shows the mapping from FlatBuffers schema types to Python wrapper classes to WAMP message classes:

Session Messages
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - FlatBuffers Table
     - Python Wrapper Class
     - WAMP Message Class
   * - ``table Hello`` (`session.fbs <../_static/flatbuffers/session.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Hello.Hello`
     - :class:`autobahn.wamp.message.Hello`
   * - ``table Welcome`` (`session.fbs <../_static/flatbuffers/session.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Welcome.Welcome`
     - :class:`autobahn.wamp.message.Welcome`
   * - ``table Abort`` (`session.fbs <../_static/flatbuffers/session.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Abort.Abort`
     - :class:`autobahn.wamp.message.Abort`
   * - ``table Challenge`` (`session.fbs <../_static/flatbuffers/session.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Challenge.Challenge`
     - :class:`autobahn.wamp.message.Challenge`
   * - ``table Authenticate`` (`session.fbs <../_static/flatbuffers/session.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Authenticate.Authenticate`
     - :class:`autobahn.wamp.message.Authenticate`
   * - ``table Goodbye`` (`session.fbs <../_static/flatbuffers/session.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Goodbye.Goodbye`
     - :class:`autobahn.wamp.message.Goodbye`
   * - ``table Error`` (`session.fbs <../_static/flatbuffers/session.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Error.Error`
     - :class:`autobahn.wamp.message.Error`

Publish/Subscribe Messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - FlatBuffers Table
     - Python Wrapper Class
     - WAMP Message Class
   * - ``table Subscribe`` (`pubsub.fbs <../_static/flatbuffers/pubsub.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Subscribe.Subscribe`
     - :class:`autobahn.wamp.message.Subscribe`
   * - ``table Subscribed`` (`pubsub.fbs <../_static/flatbuffers/pubsub.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Subscribed.Subscribed`
     - :class:`autobahn.wamp.message.Subscribed`
   * - ``table Unsubscribe`` (`pubsub.fbs <../_static/flatbuffers/pubsub.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Unsubscribe.Unsubscribe`
     - :class:`autobahn.wamp.message.Unsubscribe`
   * - ``table Unsubscribed`` (`pubsub.fbs <../_static/flatbuffers/pubsub.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Unsubscribed.Unsubscribed`
     - :class:`autobahn.wamp.message.Unsubscribed`
   * - ``table Publish`` (`pubsub.fbs <../_static/flatbuffers/pubsub.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Publish.Publish`
     - :class:`autobahn.wamp.message.Publish`
   * - ``table Published`` (`pubsub.fbs <../_static/flatbuffers/pubsub.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Published.Published`
     - :class:`autobahn.wamp.message.Published`
   * - ``table Event`` (`pubsub.fbs <../_static/flatbuffers/pubsub.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Event.Event`
     - :class:`autobahn.wamp.message.Event`
   * - ``table EventReceived`` (`pubsub.fbs <../_static/flatbuffers/pubsub.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.EventReceived.EventReceived`
     - :class:`autobahn.wamp.message.EventReceived`

RPC Messages
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - FlatBuffers Table
     - Python Wrapper Class
     - WAMP Message Class
   * - ``table Register`` (`rpc.fbs <../_static/flatbuffers/rpc.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Register.Register`
     - :class:`autobahn.wamp.message.Register`
   * - ``table Registered`` (`rpc.fbs <../_static/flatbuffers/rpc.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Registered.Registered`
     - :class:`autobahn.wamp.message.Registered`
   * - ``table Unregister`` (`rpc.fbs <../_static/flatbuffers/rpc.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Unregister.Unregister`
     - :class:`autobahn.wamp.message.Unregister`
   * - ``table Unregistered`` (`rpc.fbs <../_static/flatbuffers/rpc.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Unregistered.Unregistered`
     - :class:`autobahn.wamp.message.Unregistered`
   * - ``table Call`` (`rpc.fbs <../_static/flatbuffers/rpc.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Call.Call`
     - :class:`autobahn.wamp.message.Call`
   * - ``table Cancel`` (`rpc.fbs <../_static/flatbuffers/rpc.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Cancel.Cancel`
     - :class:`autobahn.wamp.message.Cancel`
   * - ``table Result`` (`rpc.fbs <../_static/flatbuffers/rpc.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Result.Result`
     - :class:`autobahn.wamp.message.Result`
   * - ``table Invocation`` (`rpc.fbs <../_static/flatbuffers/rpc.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Invocation.Invocation`
     - :class:`autobahn.wamp.message.Invocation`
   * - ``table Interrupt`` (`rpc.fbs <../_static/flatbuffers/rpc.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Interrupt.Interrupt`
     - :class:`autobahn.wamp.message.Interrupt`
   * - ``table Yield`` (`rpc.fbs <../_static/flatbuffers/rpc.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.Yield.Yield`
     - :class:`autobahn.wamp.message.Yield`

Authentication Messages
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - FlatBuffers Table
     - Python Wrapper Class
     - Purpose
   * - ``table AuthCraChallenge`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCraChallenge.AuthCraChallenge`
     - WAMP-CRA challenge details
   * - ``table AuthCraRequest`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCraRequest.AuthCraRequest`
     - WAMP-CRA authentication request
   * - ``table AuthCraWelcome`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCraWelcome.AuthCraWelcome`
     - WAMP-CRA welcome details
   * - ``table AuthCryptosignChallenge`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCryptosignChallenge.AuthCryptosignChallenge`
     - WAMP-Cryptosign challenge
   * - ``table AuthCryptosignRequest`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCryptosignRequest.AuthCryptosignRequest`
     - WAMP-Cryptosign auth request
   * - ``table AuthCryptosignWelcome`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCryptosignWelcome.AuthCryptosignWelcome`
     - WAMP-Cryptosign welcome
   * - ``table AuthScramChallenge`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallenge`
     - WAMP-SCRAM challenge
   * - ``table AuthScramRequest`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthScramRequest.AuthScramRequest`
     - WAMP-SCRAM auth request
   * - ``table AuthScramWelcome`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthScramWelcome.AuthScramWelcome`
     - WAMP-SCRAM welcome
   * - ``table AuthTicketChallenge`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthTicketChallenge.AuthTicketChallenge`
     - WAMP-Ticket challenge
   * - ``table AuthTicketRequest`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthTicketRequest.AuthTicketRequest`
     - WAMP-Ticket auth request
   * - ``table AuthTicketWelcome`` (`auth.fbs <../_static/flatbuffers/auth.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.AuthTicketWelcome.AuthTicketWelcome`
     - WAMP-Ticket welcome

Roles and Features
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - FlatBuffers Table
     - Python Wrapper Class
     - Purpose
   * - ``table ClientRoles`` (`roles.fbs <../_static/flatbuffers/roles.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.ClientRoles.ClientRoles`
     - Client role capabilities
   * - ``table RouterRoles`` (`roles.fbs <../_static/flatbuffers/roles.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.RouterRoles.RouterRoles`
     - Router role capabilities
   * - ``table PublisherFeatures`` (`roles.fbs <../_static/flatbuffers/roles.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeatures`
     - Publisher role features
   * - ``table SubscriberFeatures`` (`roles.fbs <../_static/flatbuffers/roles.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeatures`
     - Subscriber role features
   * - ``table CallerFeatures`` (`roles.fbs <../_static/flatbuffers/roles.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeatures`
     - Caller role features
   * - ``table CalleeFeatures`` (`roles.fbs <../_static/flatbuffers/roles.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeatures`
     - Callee role features
   * - ``table BrokerFeatures`` (`roles.fbs <../_static/flatbuffers/roles.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeatures`
     - Broker role features
   * - ``table DealerFeatures`` (`roles.fbs <../_static/flatbuffers/roles.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeatures`
     - Dealer role features

Common Types
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - FlatBuffers Table
     - Python Wrapper Class
     - Purpose
   * - ``table Map`` (`types.fbs <../_static/flatbuffers/types.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.Map.Map`
     - Generic key-value map
   * - ``table Void`` (`types.fbs <../_static/flatbuffers/types.fbs>`_)
     - :class:`autobahn.wamp.gen.wamp.Void.Void`
     - Empty/void type

Using FlatBuffers Serialization
--------------------------------

To use FlatBuffers serialization with WAMP, install the optional dependency:

.. code-block:: bash

   pip install autobahn[serialization]

Then configure your WAMP session to use FlatBuffers:

.. code-block:: python

   from autobahn.wamp import serializer
   from autobahn.wamp.types import ComponentConfig

   # Configure FlatBuffers serializer
   config = ComponentConfig(
       realm='realm1',
       extra=dict(serializer='flatbuffers')
   )

   # The serializer will automatically use the FlatBuffers schemas
   # for encoding/decoding WAMP messages

Performance Characteristics
---------------------------

FlatBuffers serialization offers several advantages for WAMP:

* **Zero-copy deserialization** - Messages can be accessed directly from the wire buffer without parsing
* **Smaller message size** - Typically 20-30% smaller than JSON for WAMP messages
* **Faster serialization** - Up to 10x faster than JSON for complex messages
* **Schema validation** - Compile-time and runtime schema validation
* **Forward/backward compatibility** - Schema evolution without breaking existing code

Schema Generation
-----------------

The Python wrapper classes are automatically generated from the FlatBuffers schemas using the ``flatc`` compiler. If you modify the schemas, regenerate the wrappers:

.. code-block:: bash

   # Requires flatc compiler
   just wamp-flatbuffers-build

This command:

1. Compiles all .fbs files to .bfbs binary schemas
2. Generates Python wrapper classes in ``autobahn/wamp/gen/``
3. Validates schema compatibility

WAMP Protocol & Autobahn|Python Design Notes
---------------------------------------------

FlatBuffers integration in Autobahn|Python serves **three orthogonal use cases**, each addressing different architectural layers:

1. **WAMP Protocol Base Serializer** - Serializing WAMP message frames (the protocol envelope)
2. **WAMP Payload Serializer** - Serializing application payloads within WAMP messages
3. **WAMP Catalogs/IDL** - Static typing of interfaces using FlatBuffers schemas

This multi-layered design separates protocol serialization from payload serialization, enabling flexible composition.

FlatBuffers as Protocol Serializer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FlatBuffers is integrated as one of several WAMP protocol base serializers in :mod:`autobahn.wamp.serializer`, alongside JSON, MessagePack, CBOR, and UBJSON.

**Serializer Registration** (:file:`autobahn/wamp/serializer.py` lines 991-1093):

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Identifier
     - Value
   * - **SERIALIZER_ID**
     - ``"flatbuffers"`` (WebSocket subprotocol: ``wamp.2.flatbuffers``)
   * - **RAWSOCKET_SERIALIZER_ID**
     - ``5`` (RawSocket handshake byte)
   * - **MIME_TYPE**
     - ``"application/x-flatbuffers"`` (HTTP long-poll)

**Transport Serializer Creation**:

The :func:`create_transport_serializer` function (:file:`serializer.py` line 1096) instantiates serializers from string IDs:

.. code-block:: python

   # Parse serializer ID with optional batching mode
   serializer = create_transport_serializer("flatbuffers")
   # Returns FlatBuffersSerializer instance

   # For content-type negotiation during WAMP handshake
   serializers = create_transport_serializers(transport)
   # Creates list of all supported serializers from transport config

Zero-Copy Lazy Loading Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``from_fbs`` integration pattern (:file:`autobahn/wamp/message.py` lines 2262-2323) enables true zero-copy deserialization:

.. code-block:: python

   class Event(Message):
       def __init__(self, from_fbs=None, ...):
           # Store FlatBuffers message reference (zero-copy)
           self._from_fbs = from_fbs

       @property
       def args(self):
           if self._args is None and self._from_fbs:
               # Lazily decode CBOR bytes from FlatBuffers on first access
               self._args = cbor2.loads(bytes(self._from_fbs.ArgsAsBytes()))
           return self._args

**Key Design Insight**: Application payloads (``args``/``kwargs``) are stored as **CBOR-encoded bytes** inside the FlatBuffers message structure and decoded only when accessed. This provides:

* **Zero-copy transport** - FlatBuffers envelope can be accessed without parsing
* **Lazy payload deserialization** - Application data decoded only if needed
* **Hybrid serialization** - FlatBuffers for protocol, CBOR for payloads (currently)

In the future, payloads could be FlatBuffers-typed objects defined via WAMP IDL, enabling full zero-copy throughout the entire message processing pipeline.

Custom Message Type Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FlatBuffers messages bypass the standard list-based WAMP message parsing (:file:`serializer.py` lines 303-305):

.. code-block:: python

   def unserialize(self, payload, isBinary=None):
       raw_msgs = self._serializer.unserialize(payload)

       if self._serializer.NAME == "flatbuffers":
           # FlatBuffers messages already parsed - skip list processing
           msgs = raw_msgs
       else:
           # Standard path: parse list-based WAMP messages
           msgs = []
           for raw_msg in raw_msgs:
               # Parse [MESSAGE_TYPE, ...] format
               ...

This special handling recognizes that FlatBuffers messages are already structured objects, not raw lists.

Current Implementation Status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**⚠️ Experimental - Read-Only Implementation**

The current FlatBuffers integration is **experimental** and has significant limitations:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Status
     - Details
   * - **Serialization**
     - ❌ ``serialize()`` raises ``NotImplementedError`` - cannot send FlatBuffers messages
   * - **Deserialization**
     - ✅ ``unserialize()`` works - can receive FlatBuffers messages
   * - **Message Coverage**
     - ⚠️ Only 2 of 24 WAMP message types implemented: EVENT (type 36) and PUBLISH (type 8)
   * - **Batching**
     - ❌ Explicitly disabled - FlatBuffers does not support message batching currently
   * - **Use Case**
     - Read-only: Can receive FlatBuffers messages from advanced routers, but cannot send them

**Implementation in** :file:`autobahn/wamp/serializer.py`:

.. code-block:: python

   class FlatBuffersObjectSerializer(object):
       MESSAGE_TYPE_MAP = {
           message_fbs.MessageType.EVENT: (message_fbs.Event, message.Event),
           message_fbs.MessageType.PUBLISH: (message_fbs.Publish, message.Publish),
       }

       def serialize(self, obj):
           # Not implemented - cannot send FlatBuffers messages yet
           raise NotImplementedError()

       def unserialize(self, payload):
           # Can receive FlatBuffers messages
           union_msg = message_fbs.Message.Message.GetRootAsMessage(payload, 0)
           msg_type = union_msg.MsgType()

           if msg_type in self.MESSAGE_TYPE_MAP:
               # Parse known message types
               ...

**Future Development**: Full bidirectional FlatBuffers support requires:

1. Implementing ``serialize()`` for all 24 WAMP message types
2. Adding FlatBuffers builders to WAMP message classes
3. Supporting batched message delivery
4. Integrating WAMP IDL-typed payloads for end-to-end zero-copy

Payload Serialization Layers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The current implementation uses a **hybrid approach**:

.. code-block:: text

   ┌─────────────────────────────────────────────────┐
   │  FlatBuffers Message Envelope (Protocol Layer)  │
   │  ┌───────────────────────────────────────────┐  │
   │  │ Message Type: EVENT                       │  │
   │  │ Subscription ID: 12345                    │  │
   │  │ Publication ID: 67890                     │  │
   │  │                                           │  │
   │  │ args:   [CBOR bytes] ◄── Payload Layer   │  │
   │  │ kwargs: [CBOR bytes] ◄── Payload Layer   │  │
   │  └───────────────────────────────────────────┘  │
   └─────────────────────────────────────────────────┘

**Current**: FlatBuffers for envelope, CBOR for application payloads

**Future with WAMP IDL**: FlatBuffers for both envelope AND payloads (full zero-copy)

Integration with WAMP Machinery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FlatBuffers serializers integrate seamlessly with the WAMP protocol stack:

1. **Transport Configuration** - Serializers specified in transport options during connection setup
2. **Content Negotiation** - WebSocket subprotocol negotiation selects ``wamp.2.flatbuffers`` if both peers support it
3. **Message Routing** - Router forwards FlatBuffers messages to compatible peers, transcodes for others
4. **Backward Compatibility** - Routers can transcode between FlatBuffers and JSON/MessagePack/CBOR

See :mod:`autobahn.wamp.serializer` for the complete serializer implementation and :mod:`autobahn.wamp.message` for the message class integration.

Related Documentation
---------------------

* :class:`autobahn.wamp.message` - WAMP message classes
* :class:`autobahn.wamp.serializer` - WAMP serializers
* `FlatBuffers Documentation <https://google.github.io/flatbuffers/>`_
* `WAMP Protocol Specification <https://wamp-proto.org/>`_
