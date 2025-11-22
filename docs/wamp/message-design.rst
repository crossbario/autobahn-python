.. _wamp-message-design:

WAMP Message Class Design
==========================

This document describes the architectural design of WAMP message classes in Autobahn|Python, including the rationale for using multiple inheritance with mixin classes to handle application payload and router forwarding attributes.

Overview
--------

Autobahn|Python implements all 25 WAMP message types defined in the `WAMP specification <https://wamp-proto.org/wamp_latest_ietf.html>`_. Analysis of these message classes reveals a **perfect architectural pattern** governing two orthogonal concerns:

1. **Application Payload** - Messages carrying application data (args/kwargs) with optional E2E encryption
2. **Router Forwarding** - Messages that can traverse router-to-router links in distributed fabrics

This pattern is implemented using **multiple inheritance with mixin classes**, providing a clean separation of concerns that maps directly to the WAMP protocol architecture.

The Four Message Categories
----------------------------

Based on analysis documented in `WAMP Message Attributes: E2E Encryption & Router-to-Router Links <https://github.com/wamp-proto/wamp-proto/blob/master/wep/WIP_E2EE_AND_RLINKS.md>`_, all WAMP messages fall into exactly **four categories**:

Category 1: Neither Payload nor Forwarding (12 messages)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Messages**: Session lifecycle and acknowledgments

- ``Abort``, ``Authenticate``, ``Challenge``
- ``EventReceived``
- ``Goodbye``, ``Hello``
- ``Published``, ``Registered``, ``Subscribed``
- ``Unregistered``, ``Unsubscribed``
- ``Welcome``

**Characteristics**:

- Local to router-client connection
- Never forwarded across router boundaries
- No application payload (or payload not encryptable)
- Session management only

**Implementation**: Derive directly from ``Message`` base class

Category 2: Payload Only (0 messages)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Messages**: NONE - This category is **architecturally empty**

**Why Empty**: Messages with application payload that needs encryption (payload transparency) **must also** support forwarding (``forward_for``) because:

- E2E encrypted payloads are meant to cross router boundaries
- Multi-router topologies are a primary use case for E2EE
- Encrypted messages must be routable in distributed fabrics

**Architectural Insight**: Payload transparency without router forwarding is **meaningless** - if you're encrypting end-to-end, you inherently need multi-hop routing.

Category 3: Forwarding Only (6 messages)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Messages**: Control/management messages without application payload

- ``Cancel``, ``Interrupt``
- ``Register``, ``Unregister``
- ``Subscribe``, ``Unsubscribe``

**Characteristics**:

- Control plane operations
- No application payload to encrypt
- Must be forwarded across routers (R-Links)
- Carry metadata only (URIs, IDs, options)

**Implementation**: Derive from ``MessageWithForwardFor`` mixin

**Example**: A ``SUBSCRIBE`` message from Client A connected to Router 1 for a topic handled by Router 2:

.. code-block:: text

   Client A → Router 1 → Router 2

Router 1 forwards ``SUBSCRIBE`` to Router 2, adding itself to ``forward_for``. When an ``EVENT`` comes back, Router 2 knows to send it to Router 1 (following the ``forward_for`` chain in reverse).

Category 4: Both Payload and Forwarding (7 messages)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Messages**: Application data plane - ALL messages carrying application payload

- **PubSub**: ``PUBLISH``, ``EVENT``
- **RPC**: ``CALL``, ``RESULT``, ``INVOCATION``, ``YIELD``
- **Errors**: ``ERROR`` (can carry payload in args/kwargs)

**Characteristics**:

- Carry application payload (args/kwargs or opaque bytes)
- Support E2E encryption (payload transparency)
- Can be routed across multiple routers (R-Links)
- The **only** messages users interact with for data exchange

**Implementation**: Derive from both ``MessageWithAppPayload`` and ``MessageWithForwardFor`` mixins (multiple inheritance)

**Why**: These messages are the **core data plane** of WAMP. They:

1. Carry user application data that may need encryption
2. Must traverse router-to-router links in distributed topologies
3. Require both E2EE and R-Link capabilities

Architectural Design: Multiple Inheritance with Mixins
-------------------------------------------------------

The Problem: Code Duplication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Without mixins, the original design duplicated attribute handling across multiple message classes:

- **Application payload attributes** (``args``, ``kwargs``, ``payload``, ``enc_algo``, ``enc_key``, ``enc_serializer``) duplicated across 7 Category 4 messages
- **Forwarding attribute** (``forward_for``) duplicated across 13 messages (6 Category 3 + 7 Category 4)
- Lazy FlatBuffers deserialization logic duplicated in each message class

This violated the **DRY principle** (Don't Repeat Yourself) and made maintenance difficult.

The Solution: Mixin Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We introduce two mixin classes that encapsulate orthogonal concerns:

1. ``MessageWithAppPayload`` - Handles application payload attributes
2. ``MessageWithForwardFor`` - Handles router forwarding attributes

These mixins are **orthogonal** (no overlapping attributes) and can be composed using multiple inheritance.

Class Hierarchy
~~~~~~~~~~~~~~~~

.. code-block:: text

   Message (base)
   │
   ├─ MessageWithAppPayload (mixin)
   │  ├─ args
   │  ├─ kwargs
   │  ├─ payload
   │  ├─ enc_algo
   │  ├─ enc_key
   │  └─ enc_serializer
   │
   ├─ MessageWithForwardFor (mixin)
   │  └─ forward_for
   │
   └─ Concrete message classes:
      ├─ Category 1 (12): Message only
      │  └─ Hello, Welcome, Abort, ...
      ├─ Category 3 (6): MessageWithForwardFor only
      │  └─ Subscribe, Register, Cancel, ...
      └─ Category 4 (7): MessageWithAppPayload + MessageWithForwardFor
         └─ Publish, Event, Call, Result, ...

Why Multiple Inheritance?
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Advantages**:

1. **Separation of Concerns**: Each mixin handles exactly one orthogonal concern
2. **DRY Principle**: Payload logic in one place, forwarding logic in one place
3. **Type Safety**: Mixins can be type-hinted for better IDE support
4. **Direct Mapping**: Maps perfectly to the 4 architectural categories
5. **Pythonic Pattern**: Standard approach in frameworks like Django, Flask
6. **Maintainability**: Changes to payload handling affect only ``MessageWithAppPayload``

**Method Resolution Order (MRO)**:

Python's C3 linearization ensures predictable method resolution:

.. code-block:: python

   class Publish(MessageWithAppPayload, MessageWithForwardFor):
       pass

   # MRO: Publish → MessageWithAppPayload → MessageWithForwardFor → Message → object

Since mixins are orthogonal (no overlapping methods), MRO conflicts cannot occur.

Technical Implementation: ``__slots__`` and Initialization
-----------------------------------------------------------

The implementation uses sophisticated Python patterns to combine multiple inheritance with ``__slots__`` for memory efficiency.

The ``__slots__`` Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Challenge**: Python's ``__slots__`` mechanism has strict rules for multiple inheritance.

**Rule**: You cannot have multiple base classes that both define non-empty, non-overlapping ``__slots__``.

Attempting this causes: ``TypeError: multiple bases have instance lay-out conflict``

**Solution**: Mixins use **empty** ``__slots__ = ()`` while the concrete message class defines all slots.

Empty ``__slots__ = ()`` vs No ``__slots__``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This distinction is **critical**:

**Empty slots** (``__slots__ = ()``):

.. code-block:: python

   class MessageWithAppPayload(object):
       __slots__ = ()  # ✓ "I add no new slots, but use slots from derived classes"

**Effect**:

- Class has NO ``__dict__`` (memory efficient)
- Class adds NO new slot attributes
- Derived classes can still use ``__slots__``
- Acts as a "pure mixin" for methods only

**No slots defined**:

.. code-block:: python

   class MessageWithAppPayload(object):
       # No __slots__ defined  # ✗ "I use __dict__ for attributes"

**Effect**:

- Class gets a ``__dict__`` for dynamic attributes
- Breaks the ``__slots__`` chain
- Derived classes can't benefit from slots
- Wastes memory with unnecessary ``__dict__``

**DO NOT REMOVE** the ``__slots__ = ()`` from mixin classes!

How It Works
^^^^^^^^^^^^

The pattern combines three elements:

1. **Message base class**: Defines ``__slots__`` for base attributes (``_from_fbs``, ``_serialized``, etc.)
2. **Mixin classes**: Have ``__slots__ = ()`` (empty) and provide methods only
3. **Concrete classes**: Define ``__slots__`` for their own attributes PLUS mixin attributes

Example with ``Publish``:

.. code-block:: python

   class Message(object):
       __slots__ = ('_from_fbs', '_serialized', ...)  # Base slots

   class MessageWithAppPayload(object):
       __slots__ = ()  # Empty - adds no storage

   class MessageWithForwardFor(object):
       __slots__ = ()  # Empty - adds no storage

   class Publish(MessageWithAppPayload, MessageWithForwardFor, Message):
       __slots__ = (
           # From Message base (inherited, not redefined)
           # Publish-specific slots
           '_request',
           '_topic',
           '_acknowledge',
           # ... other Publish attributes
           # From MessageWithAppPayload mixin (storage defined here, methods in mixin)
           '_args',
           '_kwargs',
           '_payload',
           '_enc_algo',
           '_enc_key',
           '_enc_serializer',
           # From MessageWithForwardFor mixin (storage defined here, methods in mixin)
           '_forward_for',
       )

**Memory layout**: All slots from ``Message`` and ``Publish`` are allocated in the instance. The mixins provide the **methods** (properties) to access their logical slots, but the **storage** is defined in the concrete class.

**Why this works**:

- Only ONE class in the inheritance chain (``Message``) defines actual base slots
- Mixins have empty ``__slots__``, so no conflict
- ``Publish`` adds more slots for itself and the mixins
- Mixins provide property accessors for "their" slots
- No ``__dict__`` anywhere - pure slot-based storage

Method Resolution Order (MRO):

.. code-block:: python

   >>> Publish.__mro__
   (<class 'Publish'>,
    <class 'MessageWithAppPayload'>,    # ← Provides args/kwargs/payload properties
    <class 'MessageWithForwardFor'>,    # ← Provides forward_for property
    <class 'Message'>,                  # ← Base functionality
    <class 'object'>)

When accessing ``publish_instance.args``:

1. Python looks in ``Publish`` → not found
2. Looks in ``MessageWithAppPayload`` → **found** (the ``@property`` method)
3. That property accesses ``self._args`` which exists in ``Publish.__slots__``

Initialization Pattern
~~~~~~~~~~~~~~~~~~~~~~

**Challenge**: Cannot use ``__init__()`` in mixins with multiple inheritance.

**Problem with mixin ``__init__()``**:

.. code-block:: python

   class MessageWithAppPayload(object):
       def __init__(self, args=None, kwargs=None, ...):
           super().__init__(...)  # ✗ Complicated MRO chain!
           self._args = args

Issues:

- ``super().__init__()`` follows MRO, causing ``Message.__init__()`` to be called multiple times
- Confusing initialization order
- Hard to debug and reason about

**Solution: Explicit initialization methods**:

.. code-block:: python

   class MessageWithAppPayload(object):
       def _init_app_payload(self, args=None, kwargs=None, ...):
           """Initialize application payload attributes (no super() call)."""
           self._args = args
           self._kwargs = kwargs
           # ...

   class Publish(...):
       def __init__(self, request, topic, args=None, ...):
           # Call Message.__init__() exactly once
           Message.__init__(self, from_fbs=from_fbs)

           # Call mixin initialization methods explicitly
           self._init_app_payload(args=args, kwargs=kwargs, ...)
           self._init_forward_for(forward_for=forward_for)

           # Initialize Publish-specific attributes
           self._request = request
           self._topic = topic

**Benefits**:

- Clear, explicit initialization order
- ``Message.__init__()`` called exactly once
- No confusing ``super()`` chains
- Easy to debug and understand
- Each initialization step is explicit and traceable

**Why not use ``super()``?**

With multiple inheritance, ``super()`` follows the MRO chain. For ``Publish``:

.. code-block:: python

   # If mixins used __init__ with super():
   Publish.__init__()
     → super().__init__()  # Calls MessageWithAppPayload.__init__()
       → super().__init__()  # Calls MessageWithForwardFor.__init__()
         → super().__init__()  # Calls Message.__init__()

This works, but requires ALL classes in the chain to properly use ``super()`` and accept ``**kwargs`` to pass along unknown arguments. It's fragile and hard to maintain.

Our explicit pattern is more verbose but much clearer:

.. code-block:: python

   Publish.__init__()
     → Message.__init__(from_fbs=from_fbs)  # Explicit, called once
     → self._init_app_payload(...)          # Explicit
     → self._init_forward_for(...)          # Explicit

The MessageWithAppPayload Mixin
--------------------------------

Purpose
~~~~~~~

Encapsulates the "6-set" of application payload attributes that **always co-occur** in Category 4 messages.

The "6-set" Attributes
~~~~~~~~~~~~~~~~~~~~~~

These six attributes form an **inseparable unit**:

1. ``args`` (list) - Positional arguments for procedures/events
2. ``kwargs`` (dict) - Keyword arguments for procedures/events
3. ``payload`` (bytes) - Opaque encrypted payload (for E2EE)
4. ``enc_algo`` (str) - Encryption/encoding algorithm identifier
5. ``enc_key`` (str) - Key identifier for decryption
6. ``enc_serializer`` (str) - Payload serializer ID

**Co-occurrence Rule**: In E2EE mode, attributes 3-6 **must all be present** or **all be None**. In normal mode, all are None except ``args``/``kwargs``.

Payload Serialization Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The mixin handles a **three-level architecture**:

1. **Transport Serializer** - Serializes the WAMP message envelope (JSON/msgpack/CBOR/ubjson/FlatBuffers)
2. **Payload Mode** - Normal (args/kwargs) vs Transparent (E2EE with opaque payload)
3. **Payload Serializer** - Serializes application data within the envelope

**Supported Payload Serializers**:

Per ``enum Serializer`` in `types.fbs <https://github.com/crossbario/autobahn-python/blob/master/autobahn/wamp/flatbuffers/types.fbs>`_:

- ``TRANSPORT = 0`` - Use same serializer as transport (default for FlatBuffers)
- ``JSON = 1`` - Explicit JSON serialization
- ``MSGPACK = 2`` - Explicit MessagePack serialization
- ``CBOR = 3`` - Explicit CBOR serialization (default)
- ``UBJSON = 4`` - Explicit UBJSON serialization
- ``OPAQUE = 5`` - Raw pass-through (no serialization)
- ``FLATBUFFERS = 6`` - FlatBuffers with static schema
- ``FLEXBUFFERS = 7`` - FlexBuffers with quasi-dynamic typing

**Important**: ``enc_serializer`` specifies **payload** serialization, not transport serialization. The name "enc" stands for **encoding**, not encryption (though it's also used in E2EE contexts).

Implementation Details
~~~~~~~~~~~~~~~~~~~~~~

The mixin provides:

**Lazy Deserialization**:

When a FlatBuffers-serialized message is received, ``args``/``kwargs`` are deserialized on first access using the serializer specified by ``enc_serializer``.

.. code-block:: python

   @property
   def args(self):
       """Lazy deserialization of args from FlatBuffers"""
       if self._args is None and self._from_fbs:
           if self._from_fbs.ArgsLength():
               ser_id = self.enc_serializer or "cbor"  # Default to CBOR
               args_bytes = self._from_fbs.ArgsAsBytes()  # Returns memoryview!
               self._args = self._deserialize_with_memoryview(args_bytes, ser_id)
       return self._args

**Zero-Copy Optimization**:

The helper ``_deserialize_with_memoryview()`` uses memoryview (zero-copy) for serializers that support it:

- ✓ **Zero-copy**: CBOR (``cbor2``), MessagePack (``msgpack``), UBJSON (``ubjson``)
- ✗ **Requires bytes()**: JSON (``json``), FlexBuffers (``flatbuffers.flexbuffers``)

.. code-block:: python

   def _deserialize_with_memoryview(self, data_bytes, ser_id):
       """
       Deserialize with memoryview where possible for zero-copy efficiency.
       Converts to bytes only for JSON/FlexBuffers.
       """
       if ser_id == "json" or ser_id == "flexbuffers":
           data = bytes(data_bytes)  # One copy needed
       else:
           data = data_bytes  # Keep as memoryview (zero-copy)

       serializer = self._get_payload_serializer(ser_id)
       return serializer.unserialize(data)[0]

**FlexBuffers Support**:

FlexBuffers provides schema-less, quasi-dynamic typing using FlatBuffers infrastructure:

.. code-block:: python

   if ser_id == "flexbuffers":
       import flatbuffers.flexbuffers as flexbuffers
       root = flexbuffers.GetRoot(bytes(args_bytes))
       self._args = root.AsVector.Value  # Returns Python list
       # For kwargs: root.AsMap.Value returns Python dict

The MessageWithForwardFor Mixin
--------------------------------

Purpose
~~~~~~~

Encapsulates router-to-router forwarding metadata for messages that can traverse distributed router fabrics.

The forward_for Attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Type**: ``list[dict]`` - Forwarding chain metadata

**Structure**: Each entry is a dictionary with:

.. code-block:: python

   {
       'session': int,      # WAMP session ID
       'authid': str,       # Authentication ID
       'authrole': str      # Authentication role
   }

**Semantics**:

- Each router that forwards a message adds its own entry to ``forward_for``
- The chain tracks the complete routing path
- Prevents routing loops (routers check if they're already in the chain)
- Enables reverse routing (responses follow the chain backward)

Implementation Details
~~~~~~~~~~~~~~~~~~~~~~

The mixin provides:

**Lazy Deserialization**:

When a FlatBuffers-serialized message is received, ``forward_for`` is deserialized on first access from the FlatBuffers ``Principal`` objects:

.. code-block:: python

   @property
   def forward_for(self):
       """Lazy deserialization of forward_for from FlatBuffers"""
       if self._forward_for is None and self._from_fbs:
           if self._from_fbs.ForwardForLength():
               forward_for = []
               for j in range(self._from_fbs.ForwardForLength()):
                   principal = self._from_fbs.ForwardFor(j)
                   authid = principal.Authid()
                   if authid:
                       authid = authid.decode('utf-8')
                   authrole = principal.Authrole()
                   if authrole:
                       authrole = authrole.decode('utf-8')
                   forward_for.append({
                       'session': principal.Session(),
                       'authid': authid,
                       'authrole': authrole,
                   })
               self._forward_for = forward_for
       return self._forward_for

**Helper Methods** (future):

The mixin could provide utility methods like:

- ``_validate_forward_chain()`` - Check for routing loops
- ``_add_hop(session, authid, authrole)`` - Append router to chain
- ``_reverse_chain()`` - Get return path for responses

Concrete Message Classes
-------------------------

Category 4 Example: Publish
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``Publish`` message demonstrates multiple inheritance combining both mixins:

.. code-block:: python

   class Publish(MessageWithAppPayload, MessageWithForwardFor):
       """
       WAMP PUBLISH message.

       Combines:
       - Application payload (args/kwargs/payload/enc_*)
       - Router forwarding (forward_for)
       - Publish-specific attributes (request, topic, options)
       """
       MESSAGE_TYPE = 16

       def __init__(self, request, topic, args=None, kwargs=None,
                    payload=None, enc_algo=None, enc_key=None,
                    enc_serializer=None, acknowledge=None,
                    retain=None, exclude_me=None, exclude=None,
                    exclude_authid=None, exclude_authrole=None,
                    eligible=None, eligible_authid=None,
                    eligible_authrole=None, forward_for=None):
           # Initialize mixins
           MessageWithAppPayload.__init__(
               self, args=args, kwargs=kwargs, payload=payload,
               enc_algo=enc_algo, enc_key=enc_key,
               enc_serializer=enc_serializer
           )
           MessageWithForwardFor.__init__(self, forward_for=forward_for)

           # Publish-specific attributes
           self.request = request
           self.topic = topic
           self.acknowledge = acknowledge
           self.retain = retain
           # ... other options

**Method Resolution Order**:

.. code-block:: python

   >>> Publish.__mro__
   (<class 'autobahn.wamp.message.Publish'>,
    <class 'autobahn.wamp.message.MessageWithAppPayload'>,
    <class 'autobahn.wamp.message.MessageWithForwardFor'>,
    <class 'autobahn.wamp.message.Message'>,
    <class 'object'>)

Category 3 Example: Subscribe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``Subscribe`` message uses only the forwarding mixin:

.. code-block:: python

   class Subscribe(MessageWithForwardFor):
       """
       WAMP SUBSCRIBE message.

       Combines:
       - Router forwarding (forward_for)
       - Subscribe-specific attributes (request, topic, match)
       """
       MESSAGE_TYPE = 32

       def __init__(self, request, topic, match=None,
                    get_retained=None, forward_for=None):
           MessageWithForwardFor.__init__(self, forward_for=forward_for)

           self.request = request
           self.topic = topic
           self.match = match
           self.get_retained = get_retained

Validation Rules
----------------

The "6-set" Co-occurrence Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Rule**: In messages with application payload, the E2EE attributes must follow all-or-none semantics:

- If ``payload`` is not None, then ``enc_algo``, ``enc_key``, and ``enc_serializer`` **must all be present**
- If ``payload`` is None, then ``enc_algo``, ``enc_key``, and ``enc_serializer`` **must all be None**

**Mutual Exclusivity**:

- If ``payload`` is not None (E2EE mode), then ``args`` and ``kwargs`` **must be None**
- If ``args`` or ``kwargs`` is not None (normal mode), then ``payload`` **must be None**

**Future Implementation**:

These validation rules should be implemented in ``MessageWithAppPayload.__init__()`` or as a separate validation method:

.. code-block:: python

   def _validate_payload_attributes(self):
       """Validate "6-set" co-occurrence rules"""
       has_payload = self._payload is not None
       has_enc_algo = self._enc_algo is not None
       has_enc_key = self._enc_key is not None
       has_enc_serializer = self._enc_serializer is not None

       # All-or-none for E2EE attributes
       if has_payload:
           if not (has_enc_algo and has_enc_key and has_enc_serializer):
               raise ValueError(
                   "E2EE mode: payload requires enc_algo, enc_key, "
                   "and enc_serializer"
               )
       else:
           if has_enc_algo or has_enc_key or has_enc_serializer:
               raise ValueError(
                   "Normal mode: enc_algo/enc_key/enc_serializer "
                   "require payload"
               )

       # Mutual exclusivity
       has_args = self._args is not None
       has_kwargs = self._kwargs is not None

       if has_payload and (has_args or has_kwargs):
           raise ValueError(
               "Cannot have both payload (E2EE) and args/kwargs (normal)"
           )

Migration Notes
---------------

API Compatibility
~~~~~~~~~~~~~~~~~

This refactoring is **internal only** - the public API remains unchanged:

- All message classes still have the same ``__init__()`` signatures
- All attributes remain accessible with the same names
- Serialization/deserialization behavior is identical

No user code changes are required.

Internal Changes
~~~~~~~~~~~~~~~~

For Autobahn|Python developers:

1. Message classes now use multiple inheritance (Category 3 & 4 only)
2. Attribute initialization delegates to mixin ``__init__()`` methods
3. Lazy deserialization logic moved to mixins (DRY)
4. FlatBuffers ``build()`` methods will use mixin helpers

Benefits
~~~~~~~~

- **Maintainability**: Changes to payload/forwarding logic in one place
- **Testability**: Mixins can be unit-tested independently
- **Extensibility**: New payload serializers added in one place
- **Type Safety**: Better IDE support with mixin type hints
- **Performance**: Zero-copy optimizations benefit all messages automatically

References
----------

- `WAMP Specification <https://wamp-proto.org/wamp_latest_ietf.html>`_
- `WAMP Message Attributes: E2E Encryption & Router-to-Router Links <https://github.com/wamp-proto/wamp-proto/blob/master/wep/WIP_E2EE_AND_RLINKS.md>`_
- `WEP006 - Zero-copy WAMP Serialization with FlatBuffers <https://github.com/wamp-proto/wamp-proto/blob/master/wep/wep006/README.md>`_
- `FlatBuffers Schema Reference <flatbuffers-schema.html>`_
- :mod:`autobahn.wamp.message` - Message class implementations
- :mod:`autobahn.wamp.serializer` - Serializer implementations

---

*This architectural design ensures Autobahn|Python's WAMP message implementation remains maintainable, performant, and aligned with the WAMP protocol specification.*
