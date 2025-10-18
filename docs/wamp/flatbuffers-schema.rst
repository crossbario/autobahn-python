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
   * - `session.fbs <https://github.com/crossbario/autobahn-python/blob/master/autobahn/wamp/flatbuffers/session.fbs>`_
     - Session lifecycle messages: Hello, Welcome, Abort, Challenge, Authenticate, Goodbye, Error
   * - `pubsub.fbs <https://github.com/crossbario/autobahn-python/blob/master/autobahn/wamp/flatbuffers/pubsub.fbs>`_
     - Publish/Subscribe messages: Subscribe, Subscribed, Unsubscribe, Unsubscribed, Publish, Published, Event, EventReceived
   * - `rpc.fbs <https://github.com/crossbario/autobahn-python/blob/master/autobahn/wamp/flatbuffers/rpc.fbs>`_
     - RPC messages: Register, Registered, Unregister, Unregistered, Call, Cancel, Result, Invocation, Interrupt, Yield
   * - `auth.fbs <https://github.com/crossbario/autobahn-python/blob/master/autobahn/wamp/flatbuffers/auth.fbs>`_
     - Authentication method details: WAMP-CRA, WAMP-Cryptosign, WAMP-SCRAM, WAMP-Ticket
   * - `roles.fbs <https://github.com/crossbario/autobahn-python/blob/master/autobahn/wamp/flatbuffers/roles.fbs>`_
     - WAMP roles and features: ClientRoles, RouterRoles, Broker/Dealer/Publisher/Subscriber/Caller/Callee features
   * - `types.fbs <https://github.com/crossbario/autobahn-python/blob/master/autobahn/wamp/flatbuffers/types.fbs>`_
     - Common types: Map, Void, enums (Serializer, Payload, MessageType, AuthMethod, Match)
   * - `wamp.fbs <https://github.com/crossbario/autobahn-python/blob/master/autobahn/wamp/flatbuffers/wamp.fbs>`_
     - Root WAMP message union type

Binary Schemas (.bfbs)
~~~~~~~~~~~~~~~~~~~~~

Compiled binary reflection schemas are located in ``autobahn/wamp/gen/schema/``:

* ``session.bfbs`` - Compiled from session.fbs
* ``pubsub.bfbs`` - Compiled from pubsub.fbs
* ``rpc.bfbs`` - Compiled from rpc.fbs
* ``auth.bfbs`` - Compiled from auth.fbs
* ``roles.bfbs`` - Compiled from roles.fbs
* ``types.bfbs`` - Compiled from types.fbs
* ``wamp.bfbs`` - Compiled from wamp.fbs

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
   * - ``table Hello``
     - :class:`autobahn.wamp.gen.wamp.proto.Hello.Hello`
     - :class:`autobahn.wamp.message.Hello`
   * - ``table Welcome``
     - :class:`autobahn.wamp.gen.wamp.proto.Welcome.Welcome`
     - :class:`autobahn.wamp.message.Welcome`
   * - ``table Abort``
     - :class:`autobahn.wamp.gen.wamp.proto.Abort.Abort`
     - :class:`autobahn.wamp.message.Abort`
   * - ``table Challenge``
     - :class:`autobahn.wamp.gen.wamp.proto.Challenge.Challenge`
     - :class:`autobahn.wamp.message.Challenge`
   * - ``table Authenticate``
     - :class:`autobahn.wamp.gen.wamp.proto.Authenticate.Authenticate`
     - :class:`autobahn.wamp.message.Authenticate`
   * - ``table Goodbye``
     - :class:`autobahn.wamp.gen.wamp.proto.Goodbye.Goodbye`
     - :class:`autobahn.wamp.message.Goodbye`
   * - ``table Error``
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
   * - ``table Subscribe``
     - :class:`autobahn.wamp.gen.wamp.proto.Subscribe.Subscribe`
     - :class:`autobahn.wamp.message.Subscribe`
   * - ``table Subscribed``
     - :class:`autobahn.wamp.gen.wamp.proto.Subscribed.Subscribed`
     - :class:`autobahn.wamp.message.Subscribed`
   * - ``table Unsubscribe``
     - :class:`autobahn.wamp.gen.wamp.proto.Unsubscribe.Unsubscribe`
     - :class:`autobahn.wamp.message.Unsubscribe`
   * - ``table Unsubscribed``
     - :class:`autobahn.wamp.gen.wamp.proto.Unsubscribed.Unsubscribed`
     - :class:`autobahn.wamp.message.Unsubscribed`
   * - ``table Publish``
     - :class:`autobahn.wamp.gen.wamp.proto.Publish.Publish`
     - :class:`autobahn.wamp.message.Publish`
   * - ``table Published``
     - :class:`autobahn.wamp.gen.wamp.proto.Published.Published`
     - :class:`autobahn.wamp.message.Published`
   * - ``table Event``
     - :class:`autobahn.wamp.gen.wamp.proto.Event.Event`
     - :class:`autobahn.wamp.message.Event`
   * - ``table EventReceived``
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
   * - ``table Register``
     - :class:`autobahn.wamp.gen.wamp.proto.Register.Register`
     - :class:`autobahn.wamp.message.Register`
   * - ``table Registered``
     - :class:`autobahn.wamp.gen.wamp.proto.Registered.Registered`
     - :class:`autobahn.wamp.message.Registered`
   * - ``table Unregister``
     - :class:`autobahn.wamp.gen.wamp.proto.Unregister.Unregister`
     - :class:`autobahn.wamp.message.Unregister`
   * - ``table Unregistered``
     - :class:`autobahn.wamp.gen.wamp.proto.Unregistered.Unregistered`
     - :class:`autobahn.wamp.message.Unregistered`
   * - ``table Call``
     - :class:`autobahn.wamp.gen.wamp.proto.Call.Call`
     - :class:`autobahn.wamp.message.Call`
   * - ``table Cancel``
     - :class:`autobahn.wamp.gen.wamp.proto.Cancel.Cancel`
     - :class:`autobahn.wamp.message.Cancel`
   * - ``table Result``
     - :class:`autobahn.wamp.gen.wamp.proto.Result.Result`
     - :class:`autobahn.wamp.message.Result`
   * - ``table Invocation``
     - :class:`autobahn.wamp.gen.wamp.proto.Invocation.Invocation`
     - :class:`autobahn.wamp.message.Invocation`
   * - ``table Interrupt``
     - :class:`autobahn.wamp.gen.wamp.proto.Interrupt.Interrupt`
     - :class:`autobahn.wamp.message.Interrupt`
   * - ``table Yield``
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
   * - ``table AuthCraChallenge``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCraChallenge.AuthCraChallenge`
     - WAMP-CRA challenge details
   * - ``table AuthCraRequest``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCraRequest.AuthCraRequest`
     - WAMP-CRA authentication request
   * - ``table AuthCraWelcome``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCraWelcome.AuthCraWelcome`
     - WAMP-CRA welcome details
   * - ``table AuthCryptosignChallenge``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCryptosignChallenge.AuthCryptosignChallenge`
     - WAMP-Cryptosign challenge
   * - ``table AuthCryptosignRequest``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCryptosignRequest.AuthCryptosignRequest`
     - WAMP-Cryptosign auth request
   * - ``table AuthCryptosignWelcome``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthCryptosignWelcome.AuthCryptosignWelcome`
     - WAMP-Cryptosign welcome
   * - ``table AuthScramChallenge``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthScramChallenge.AuthScramChallenge`
     - WAMP-SCRAM challenge
   * - ``table AuthScramRequest``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthScramRequest.AuthScramRequest`
     - WAMP-SCRAM auth request
   * - ``table AuthScramWelcome``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthScramWelcome.AuthScramWelcome`
     - WAMP-SCRAM welcome
   * - ``table AuthTicketChallenge``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthTicketChallenge.AuthTicketChallenge`
     - WAMP-Ticket challenge
   * - ``table AuthTicketRequest``
     - :class:`autobahn.wamp.gen.wamp.proto.AuthTicketRequest.AuthTicketRequest`
     - WAMP-Ticket auth request
   * - ``table AuthTicketWelcome``
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
   * - ``table ClientRoles``
     - :class:`autobahn.wamp.gen.wamp.proto.ClientRoles.ClientRoles`
     - Client role capabilities
   * - ``table RouterRoles``
     - :class:`autobahn.wamp.gen.wamp.proto.RouterRoles.RouterRoles`
     - Router role capabilities
   * - ``table PublisherFeatures``
     - :class:`autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeatures`
     - Publisher role features
   * - ``table SubscriberFeatures``
     - :class:`autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeatures`
     - Subscriber role features
   * - ``table CallerFeatures``
     - :class:`autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeatures`
     - Caller role features
   * - ``table CalleeFeatures``
     - :class:`autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeatures`
     - Callee role features
   * - ``table BrokerFeatures``
     - :class:`autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeatures`
     - Broker role features
   * - ``table DealerFeatures``
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
   * - ``table Map``
     - :class:`autobahn.wamp.gen.wamp.Map.Map`
     - Generic key-value map
   * - ``table Void``
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

Related Documentation
---------------------

* :ref:`WAMP Programming Guide <wamp-programming>`
* :class:`autobahn.wamp.message` - WAMP message classes
* :class:`autobahn.wamp.serializer` - WAMP serializers
* `FlatBuffers Documentation <https://google.github.io/flatbuffers/>`_
* `WAMP Protocol Specification <https://wamp-proto.org/>`_
