# Architecture Strategy: Statically Typed Python with Region-Based Lifetimes

**Status:** Draft / Active
**Target:** SLSA Level 4 Compliance / WASM Compilation
**Applies to:** Crossbar.io, Autobahn, txaio

## 1. Abstract

This document defines the architectural constraints required to transition our Python codebase from a dynamic, reference-counted runtime model to a **Statically Typed, Region-Based Memory model**.

While the code remains valid Python 3.12+ runnable on CPython, it strictly adheres to a subset of the language that allows for **deterministic compilation to WebAssembly (WASM)** without a Garbage Collector (GC). This enables deployment in high-assurance environments (Defense, Aerospace, MCUs) and specifically targets **NXP MCUs** (via WAMR) and **Cloudflare Workers** (via V8).

## 2. The Core Philosophy

To achieve **SLSA Level 4** build integrity and execution safety, we treat Python as a **Source Language** rather than a Runtime.

We enforce two major pillars:
1.  **Strict Static Typing:** Every variable must have a known, computable memory layout at compile time.
2.  **Region-Based Lifetimes:** Memory is managed via hierarchical regions (Arenas). Objects are allocated in a specific scope and deallocated en-masse when that scope ends.

---

## 3. The Lifetime Hierarchy

In a Region-Based system, "Leaks" and "Use-After-Free" errors are prevented by strictly enforcing a hierarchical ownership model. An object belonging to a shorter-lived region **must never** leak into a longer-lived region.

The canonical hierarchy for our stack is defined as follows (Level 0 lives longest):

| Level | Scope / Region | Examples | Lifetime Description |
| :--- | :--- | :--- | :--- |
| **0** | **Worker / Process** | `Router`, `Node`, `TransportFactory` | Allocated at startup. Persists until process exit. |
| **1** | **Transport** | `TcpTransport`, `TlsTransport` | Exists for the duration of a TCP connection. |
| **2** | **Session** | `WampSession`, `ApplicationSession` | Exists while the WAMP session is active (over a transport). |
| **3** | **Operation** | `Call`, `Invocation`, `Subscription` | Exists for the duration of a specific RPC or PubSub flow. |
| **4** | **Message** | `CallMessage`, `EventMessage` | Ephemeral. Exists only while processing a single frame. |

### 3.1 The Golden Rule of Reference Directionality

> **A Reference Violation occurs if an object at Level $N$ holds a strong reference to an object at Level $M$ where $M > N$.**

*   **Allowed:** A `Session` (L2) holding a reference to its `Transport` (L1). (Child -> Parent).
*   **Allowed:** A `Session` (L2) holding a reference to a `Call` (L3). (Parent -> Child / Ownership).
*   **FORBIDDEN:** A `Session` (L2) storing a reference to a `Message` (L4).
    *   *Why:* The `Message` region is cleared after the handle loop. If the `Session` retains a pointer, it points to freed memory (Dangling Pointer).
    *   *Fix:* We must **Copy/Clone** the data from the Message into the Session's region.

---

## 4. Pillar 1: Enforcing Static Types

We move from "Type Hinting" (for IDEs) to "Type Definition" (for Compilation).

### 4.1 The Rules
1.  **No `Any`:** The type `Any` is banned in Core logic. It represents a memory layout that cannot be determined at compile time.
2.  **No `Unknown`:** If the type checker cannot infer a local variable's type, it must be explicitly annotated.
3.  **Modern Syntax:** Use `list[str]`, not `List[str]`. Use `x | y`, not `Union[x, y]`.

### 4.2 Tooling Configuration
We use **Pyright** (via `ty` or direct) as the authoritative compiler gate.

**`pyproject.toml` Compliance Profile:**
```toml
[tool.pyright]
typeCheckingMode = "strict"
reportUnknownVariableType = true    # Critical for WASM compilation
reportUnknownMemberType = true      # Critical for vtables/structs
reportUnknownArgumentType = true
```

### 4.3 Migration Workflow
For existing modules being ported to the "WASM Core":
1.  Add `# pyright: strict` to the top of the file.
2.  Run `pyright`.
3.  Resolve all `Unknown` errors by adding explicit hints.

---

## 5. Pillar 2: Enforcing Lifetimes

Since Python lacks a native Borrow Checker, we enforce lifetime hierarchy via two methods: **Static Phantom Types** (Compile Time) and **Runtime Poisoning** (Test Time).

### 5.1 Method A: Static Verification (Phantom Types)
We use Python Generics to tag objects with their Region. This allows Pyright to catch lifetime violations.

```python
from typing import TypeVar, Generic, NewType

# Phantom Types (No runtime representation)
class R_Worker: pass
class R_Session: pass
class R_Message: pass

# Generic Region Variable
R = TypeVar("R")

class Message(Generic[R]):
    payload: bytes

class Session(Generic[R]):
    last_error: str

    # BAD: Attempting to store a Message-scoped object in a Session
    # def store_bad(self, msg: Message[R_Message]):
    #     self.cache = msg  # Pyright Error: Type Mismatch

    # GOOD: Explicit Copy/Clone
    def store_good(self, msg: Message[R_Message]):
        self.last_error = msg.payload.decode() # Copied primitive
```

### 5.2 Method B: Runtime Verification (The "Poison" Check)
For the legacy codebase, we apply a runtime mixin during the test suite execution to detect hierarchy violations.

**The Logic:**
Every core class defines `_region_level: int`. If an attribute assignment is detected where `self.level < value.level`, the runtime raises a `MemoryError`.

```python
# autobahn/util/region.py

class RegionTracked:
    _region_level: int = 0

    def __setattr__(self, key, value):
        # Optimization: Only check generic objects, skip primitives (int/str are copy-by-value in WASM usually)
        if hasattr(value, "_region_level"):
            if self._region_level < value._region_level:
                 raise MemoryError(
                     f"LIFETIME VIOLATION: {self.__class__.__name__}(L{self._region_level}) "
                     f"cannot hold reference to shorter-lived {value.__class__.__name__}(L{value._region_level}). "
                     f"Attribute: '{key}'. Explicit copy required."
                 )
        super().__setattr__(key, value)
```

**Implementation Strategy:**
1.  Inherit `RegionTracked` in `Session`, `Transport`, `Message`.
2.  Set `_region_level` in `__init__`.
3.  Run the full test suite.
4.  Any crash represents a future segregation fault in WASM.

---

## 6. Implementation Checklist

### Phase 1: Preparation (Current)
- [ ] **CI:** Update `ruff` config to enforce `ANN` (annotations) and `UP` (modern syntax).
- [ ] **CI:** Add `pyright` job in non-strict mode globally.
- [ ] **Code:** Identify the "Core WAMP" modules targetable for WASM.

### Phase 2: Static Hardening
- [ ] **Code:** Add `# pyright: strict` to core modules one by one.
- [ ] **Refactor:** Eliminate all `Any` and `Unknown` in core modules.
- [ ] **Refactor:** Replace dynamic `__getattr__` or `kwargs` with explicit Dataclasses/Structs.

### Phase 3: Lifetime Auditing
- [ ] **Audit:** Apply `RegionTracked` mixin to key classes.
- [ ] **Test:** Run suite and fix "Leak" bugs (where long-lived objects hold message references).
- [ ] **Design:** Introduce `clone(scope=...)` methods for objects that need to move between regions.

---

## 7. FAQ

**Q: Do I have to write this for all code?**
A: No. Only code intended to run in the Secure Enclave (WASM) needs strictly typed regions. Test helpers, scripts, and legacy adapters can remain standard Python.

**Q: Why not just use Rust?**
A: We are preserving the semantic logic of Crossbar.io/Autobahn accumulated over 10 years. We are compiling the *logic*, not the interpreter.

**Q: What happens if I violate the region rule?**
A: In Python CRuntime: Nothing (it works). In WASM: The allocator panics or the device crashes. We treat these as **Critical Security Bugs**.

## 8. Runtime Implementation: Async Regions & 1:N Concurrency

We need to address the critical complexity that separates a simple "Function Call Stack" from an "Async Protocol Machine."

A pure LIFO (Stack) allocator works for nested functions `A() -> B() -> C()`.
It **fails** for Async Concurrency, where `Session` starts `RPC_A`, then `RPC_B`, and `RPC_A` might finish *after* `RPC_B`, or vice versa. One cannot "pop" the stack for A without destroying B.

To map this to WASM/WAMR while keeping the "Region" safety, we must move from a **Single Stack Allocator** to a **Forest of Arenas (Pool Allocator)**.

### 8.1 The Concurrency Challenge
The WAMP hierarchy is strictly logical (`Worker -> Session -> Operation`), but the **temporal execution** is concurrent.
*   A `Session` is a 1:N container. It owns multiple active `Operations` (RPC calls, subscriptions) simultaneously.
*   These Operations complete in non-deterministic order.
*   Therefore, a single "Bump Pointer Stack" is insufficient for the **Session Layer**, as we cannot free Operation A's memory while Operation B is still active on top of it.

### 8.2 The Hybrid Allocator Model
To solve this in WASM without a GC, the Runtime Shim implements a **Hybrid Allocator** consisting of two strategies:

#### A. The Slab Allocator (For Long-Lived Roots)
Used for **Level 0 (Worker)**, **Level 1 (Transport)**, and **Level 2 (Session)**.
*   **Mechanism:** The runtime pre-allocates fixed-size "slots" (Slabs) for these structures.
*   **Behavior:** When a new TCP connection comes in, we grab a free `SessionSlab` from the pool. When it disconnects, we mark it free.
*   **Fragmentation:** Zero. Slabs are uniform.

#### B. The "Arena-per-Task" (For Operations & Messages)
Used for **Level 3 (Operations)** and **Level 4 (Messages)**.
*   **Mechanism:** Every Async Operation (e.g., a pending `Call`) is assigned its own dedicated **Linear Memory Arena** (e.g., a 4KB or 16KB Page).
*   **Binding:** The WAMP `RequestID` acts as the handle to this Arena.
    *   `Map<RequestID, ArenaPointer>`
*   **Behavior:**
    1.  **Start:** `Call(ID=100)` starts. Runtime grabs a clean Page. All local variables and outgoing messages for this call are allocated via bump-pointer *inside this Page*.
    2.  **Suspend:** The Page stays in memory while we await the network.
    3.  **Resume:** When `RESULT(ID=100)` arrives, the Router looks up `ID=100`, finds the Page, switches the "Active Allocator" to that Page, and deserializes the Result message *into that Page*.
    4.  **End:** When the logic completes, the **Entire Page** is released back to the free list.

### 8.3 Context Switching & Correlation
In this model, "Memory Management" is tied directly to "Async Context Switching."

**The Flow:**

1.  **Network Ingress (The Router Loop):**
    *   The Transport reads raw bytes into a generic **IO Buffer** (Level 1 Region).
    *   Parser decodes the WAMP Header to find `RequestID`.

2.  **Context Lookup:**
    *   **Case A (New Op):** It's a `CALL`. Runtime allocates a **New Arena**.
    *   **Case B (Existing Op):** It's a `RESULT` for `ID=100`. Runtime looks up `Arena(100)`.

3.  **The "Region Switch":**
    *   The Runtime sets the global `CURRENT_ALLOCATOR` pointer to `Arena(100)`.
    *   The Parser deserializes the rest of the message payload. The memory lands physically inside `Arena(100)`.

4.  **Execution:**
    *   The Python logic `on_result(res)` runs. Any temporary variables it creates land in `Arena(100)`.

5.  **Teardown:**
    *   The logic finishes. The Runtime calls `arena_free(Arena(100))`.
    *   **Safety:** All temporary objects, the incoming message, and the operation state vanish instantly.

This is the exact insight that turns a generic memory model into a **Domain-Driven Architecture**.

In the Router (Crossbar.io), the **`Observation`** class is the natural "Lifecycle Owner" of the PubSub payload. It is the standard-bearer for the 1:N distribution.

By tying the memory region to the `Observation`, we solve the hardest problem in zero-copy networking: **"When is it safe to free the payload?"**

### 8.4 The "Observation Arena" (Solving 1:N PubSub)

In the Router (Crossbar.io), a `PUBLISH` message triggers a 1:N fan-out to subscribers. We must avoid copying the payload (Arguments/KwArgs) $N$ times.

We map the Crossbar.io `Observation` abstraction directly to a **Reference-Counted Memory Arena**.

1.  **Ingress (The Publish):**
    *   When the Broker processes a `PUBLISH`, it allocates a new **Observation Arena**.
    *   The payload (application data) is deserialized *once* directly into this Arena.
    *   The `Observation` object (living in the Broker/Worker region) holds the pointer to this Arena.

2.  **Dispatch (The Fan-Out):**
    *   The Broker iterates matching subscriptions.
    *   For each match, it queues an `EVENT` message to the subscriber's Transport.
    *   **Crucial Optimization:** The `EVENT` message struct does *not* contain the payload data. It contains a **View (Pointer)** into the Observation Arena.
    *   **Ref-Counting:** The `Observation` increments a counter: `pending_deliveries += 1`.

3.  **Egress (The Flush):**
    *   As each Transport writes the packet to the wire (or fills the Kernel TCP buffer), it triggers a callback.
    *   The callback decrements `pending_deliveries -= 1`.

4.  **Teardown (The Drop):**
    *   When `pending_deliveries == 0`, the Router knows that *every* subscriber has received the data (or it has been handed off to the OS kernel).
    *   The **Observation Arena** is freed.

*Note: This creates a "Zero-Copy" path from Ingress Socket -> Observation Arena -> Egress Socket.*

### 8.5 Handling Router-to-Router (R2R) Federation

Router-to-Router links introduce complexity (latency, buffering), but they map cleanly to the **Observation Arena** model.

*   **The R2R Link as a "Subscriber":**
    *   To the Broker, an Uplink/Downlink is just another subscriber with a Transport.
    *   It holds a reference to the `Observation Arena` just like a local WebSocket client.
*   **The Difference:**
    *   R2R links might have significant buffering or "Store and Forward" behavior.
    *   The `Observation Arena` persists as long as the R2R link is holding the reference.
*   **Safety:**
    *   Because the `Observation` is decoupled from the original *Publisher's* Session, the Publisher can disconnect immediately after sending. The `Observation` (and its memory) stays alive until the R2R link confirms transmission.

---

### 8.6 Technical Note on Crossbar.io Implementation

This mapping validates the existing Python implementation choices:

*   **`crossbar.router.observation.Observation`**: This class effectively becomes the "Handle" for the Arena.
*   **`crossbar.router.broker.Broker`**: The Broker manages the lifetime of the Handle.

When compiling the Typed Python to WASM:
*   The `Observation` class logic remains Python (orchestrating the logic).
*   The `self.payload` attribute inside `Observation` is transformed by the compiler into a **WASM Pointer** to the `Observation Arena`.
*   Passing `self.payload` to `session.send()` passes that pointer, not a copy.

This confirms that the architecture is robust enough to handle the transition to WASM without redesigning the protocol flow.
***

### How this maps to our code
*   **`session.call(..., request_id=123)`**: This Python line triggers the creation of `Arena(123)`.
*   **`await future`**: This suspends the Python stack. The `Arena(123)` sits dormant in WASM linear memory.
*   **`msg = Transport.read()`**: This happens in a Transport/IO buffer.
*   **`future.resolve(msg)`**: The runtime identifies `msg` belongs to `Arena(123)`, performs a `memcpy` (or move) of the data into `Arena(123)`, and resumes the Python stack using that arena as the heap.

Here is the text for **Section 9** to be added to our architecture document. It formalizes the "Defense in Depth" strategy regarding lifetime enforcement.

## 9. Static Verification vs. Runtime Instrumentation

While Pyright's strict static analysis is the primary mechanism for developer guidance, it is **insufficient** on its own to guarantee the rigorous memory safety required for the WASM Secure Enclave. We employ a dual-strategy (Static + Runtime) to eliminate blind spots inherent in the Python language.

### 9.1 The "Viral Generics" Problem
Static verification relies on **complete coverage**. If a single helper function in the call stack is not typed as `Generic[R]` (or is typed loosely), the region constraint is lost.

*   **The Risk:** Passing a `Message[R_Message]` into a generic helper `def utils.cache(item: Any)` allows the item to be stored in a global variable, bypassing the static checker.
*   **The Runtime Fix:** The `RegionTracked` runtime mixin carries the region level (`_region_level: int`) on the object instance itself. Even if the type system "forgets" the region, the object remembers.

### 9.2 Container and Dynamic Blind Spots
Python allows operations that are difficult to statically analyze for ownership transfer.

1.  **Container Mutation:** Appending a strictly-typed item to a loosely-typed list (e.g., `list[object]`) is often permitted by type checkers but violates region safety.
2.  **Dynamic Attributes:** Using `setattr(self, name, value)` bypasses property type checks.
3.  **Type Ignores:** Developers may use `# type: ignore` to bypass CI errors during crunch times.

### 9.3 Defense in Depth Strategy
To satisfy **SLSA Level 4** and high-assurance audit requirements, we treat these two methods as complementary layers:

1.  **Layer 1: Static Phantom Types (Guard Rails)**
    *   **Role:** Developer Guidance.
    *   **Effect:** Prevents bugs during coding (IDE feedback).
    *   **Constraint:** Can be bypassed by `Any` or `type: ignore`.

2.  **Layer 2: Runtime Poisoning (Land Mines)**
    *   **Role:** Architectural Enforcement.
    *   **Effect:** Detects actual architectural violations during the test suite execution.
    *   **Constraint:** Cannot catch code paths not covered by tests.
    *   **Mechanism:** The `__setattr__` hook in `RegionTracked` compares `self._region_level` vs `value._region_level` and raises a `MemoryError` immediately if a shorter-lived object is assigned to a longer-lived parent.

**Verdict:** We require **both**. Static types prove we *intended* to follow the rules; Runtime checks prove we *actually* followed them.

## 10. Handling Dynamic WAMP Payloads (`args` & `kwargs`)

A fundamental characteristic of WAMP is that `args` (positional) and `kwargs` (keyword) arguments are application-defined and arbitrary. While traditional Python types them as `list[Any] | None` or `dict[str, Any] | None`, our strict static typing requirement bans `Any`.

To resolve this conflict while enabling high-performance routing, we employ a **Split-View Strategy**: a recursive union type for Application Logic (Core 1 / SDK) and an opaque zero-copy handle for Router Logic (Core 0).

### 10.1 The SDK View: Recursive Typed Unions
For application code (Autobahn SDK) where inspection of arguments is required, we define the closed set of all valid WAMP-serializable types. This provides static safety without resorting to `Any`.

```python
from typing import TypeAlias

# 1. Primitives (Fixed set of WAMP-compatible scalars)
WampScalar: TypeAlias = int | float | str | bool | bytes | None

# 2. Recursive Containers
WampList: TypeAlias = list["WampValue"]
WampDict: TypeAlias = dict[str, "WampValue"]

# 3. The Closed Union (Replaces 'Any')
WampValue: TypeAlias = WampScalar | WampList | WampDict
```

**Compiler Implication:** In the WASM build, `WampValue` lowers to a **Tagged Union** (Variant). Attempts to pass non-serializable objects (e.g., a `datetime` or `socket`) will trigger a static type error in Pyright, preventing runtime serialization failures.

### 10.2 The Router View: Opaque Zero-Copy Blobs
The Crossbar.io Router (Core 0) performs routing based strictly on the URI (`procedure` or `topic`). It **does not** inspect application payloads.

To avoid the overhead of allocating and deserializing recursive structures that the Router will never read, the compiler treats `args` and `kwargs` differently in the **Router Build Profile**.

**Router Message Definition:**
```python
class Call(Message[R]):
    request_id: int
    procedure: str
    
    # In Router Profile, the compiler maps these to 'RawPayloadHandle'
    # instead of deserializing into 'list[WampValue]'
    args: WampRawPayload | None  
    kwargs: WampRawPayload | None
```

**Operational Flow:**
1.  **Ingress:** The Transport reads the WAMP frame.
2.  **Parsing:** The parser decodes the header (Type, ID, URI).
3.  **Bypass:** When the parser encounters the `Arguments` or `ArgumentsKw` fields, it **stops deserializing**. It records the pointer and length of the raw serialized bytes (e.g., the MessagePack map/array slice) into a `WampRawPayload` handle.
4.  **Forwarding:** The Router passes this opaque handle to the outgoing Transport.
5.  **Egress:** The outgoing Transport writes the header and simply `memcpy`s the raw payload bytes.

**Benefit:**
*   **Zero Allocation:** No complex recursive structs are allocated in the heap.
*   **Zero Garbage:** No cleanup required for deep object trees.
*   **Security:** Malformed payloads (e.g., deeply nested JSON bombs) are not parsed by the Router, protecting the Core 0 control plane from parsing vulnerabilities.

---

### 10.3 Are they "New"?

*Recursive type aliases are fully supported in Python 3.11+ and PyPy 3.11+**, but the **syntax** changes slightly depending on whether we are on 3.11 or the newer 3.12.

Here is the breakdown of how "New" they are and how to write them for our specific target (3.11+).

While we could always "hack" recursive types using forward references (strings) in older Python, official support for **Recursive Type Aliases** where the type checker actually understands the recursion depth and structural equality was formalized in **Python 3.10** (PEP 613) and perfected in **Python 3.12** (PEP 695).

#### 10.3.1. How to write it in Python 3.11 (CPython & PyPy)
In Python 3.11, we **must** use `from typing import TypeAlias` and we **must** use string quotes for the self-reference.

```python
from typing import TypeAlias

# 1. Primitives
WampScalar: TypeAlias = int | float | str | bool | bytes | None

# 2. Recursive definition
# NOTE: we MUST use quotes "WampValue" inside the definition 
# because WampValue isn't fully defined yet when the interpreter reads this line.
WampValue: TypeAlias = WampScalar | list["WampValue"] | dict[str, "WampValue"]
```

*   **Supported by Pyright/Ty:** Yes, fully.
*   **Runtime:** The interpreter sees a string `"WampValue"`. `ty`/Pyright resolves it statically.

### 10.3.2. How to write it in Python 3.12+ (The "New" Way)
Python 3.12 introduced the `type` keyword (PEP 695). This is the "neat" syntax we might have seen. It handles the forward reference automatically (no quotes needed).

```python
# Python 3.12+ only
type WampScalar = int | float | str | bool | bytes | None
type WampValue = WampScalar | list[WampValue] | dict[str, WampValue]
```

#### 10.3.3. PyPy Support
**PyPy 3.10+ (and the upcoming 3.11 releases) supports the `TypeAlias` syntax perfectly.**

Since type hints are primarily a **static analysis** feature (erased or stored in `__annotations__` at runtime), PyPy has no trouble with them. The performance impact is zero because the recursion is resolved by `ty`/Pyright at compile/check time, not by PyPy at runtime.

#### 10.3.4. Summary Recommendation

Since we are targeting **3.11+**, we stick to the **Standard 3.11 Syntax**:

```python
from typing import TypeAlias

WampValue: TypeAlias = int | float | str | bool | bytes | None | list["WampValue"] | dict[str, "WampValue"]
```

This is:
1.  **Compatible** with CPython 3.11 and PyPy 3.11.
2.  **Understood** by `ty` / Pyright (Strict Mode).
3.  **Compilable** by our future WASM frontend (it sees the recursive graph).

### 10.3 Summary
*   **Client/SDK Code** sees `list[WampValue]` (Type Safe, Recursive).
*   **Router Code** sees `WampRawPayload` (Fast, Opaque).
*   **Type Checker** enforces `WampValue` compliance, preventing `Any`.

## 11. Risk Assessment

The risk to end-users is **extremely low**, bordering on zero, provided we follow the standard "Pythonic" implementation pattern.

Here is the risk assessment breakdown for our stakeholders/users:

### 11.1. Risk of Static Typing (Type Hints)
**Risk Level: None / Positive.**

*   **Runtime Impact:** Python ignores type hints at runtime (mostly). They are comments to the interpreter. There is no performance penalty and no change in behavior for existing code.
*   **User Experience:** This is a pure **upgrade** for users.
    *   Users with modern IDEs (VS Code, PyCharm) will suddenly get working auto-completion and "red squigglies" if they pass the wrong arguments to `session.publish()`.
    *   Users without type checkers will notice nothing.

### 11.2. Risk of Region Markers (Runtime Checks)
**Risk Level: Low (Manageable via Configuration).**

The only real risk here is **Performance**, not stability.
*   **The Concern:** If we add a `__setattr__` hook to every `Message` class to check `_region_level`, we introduce Python function call overhead on every attribute assignment. In a high-throughput router (Crossbar.io), this adds up.
*   **The Solution:** Make the Runtime Instrumentation **Conditional**.

**Implementation Strategy (The "Debug Mode" Pattern):**

Do not bake the `RegionTracked` mixin logic into the production class permanently. Use a conditional inheritance or a runtime toggle.

```python
# autobahn/util/region.py

# Default: No-op (Zero Overhead for Production Users)
class RegionTracked:
    _region_level: int = 0

# Debug/CI/WASM-Prep Mode: Active Checks
if __debug__ or os.environ.get("AUTOBAHN_DEBUG_LIFETIMES"):
    class RegionTracked:
        _region_level: int = 0
        def __setattr__(self, key, value):
            # ... perform the expensive check ...
            super().__setattr__(key, value)
```

**Result:**
*   **Standard User (`pip install autobahn`):** Gets the "fast" version. `RegionTracked` does nothing.
*   **CI / Test Suite:** Runs with `AUTOBAHN_DEBUG_LIFETIMES=1`. Catches the violations.
*   **WASM Compiler:** Sees the `_region_level` annotation and uses it to generate the memory management code.

### 11.3. API Stability (Breaking Changes?)
**Risk Level: Low.**

*   we are not changing the public API methods (e.g., `publish`, `call`).
*   we are only formalizing the *internal* contracts.
*   **Edge Case:** If a user was doing something "illegal" before (like monkey-patching a `Message` object onto a `Session` object manually), their code might break *if* they run in strict mode. **This is acceptable.** That user was relying on undefined behavior that would have caused memory leaks or bugs anyway.

### 11.4 Summary Verdict

*   **For the "Standard" Python User:** The libraries get better (typed) and stay fast (checks disabled by default).
*   **For the "Defense" Customer:** They get the mathematically proven, hardened artifact.
*   **For us (Maintainer):** we get a single codebase that serves both masters.

It is a very safe migration path.
