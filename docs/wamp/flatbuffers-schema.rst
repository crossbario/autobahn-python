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
