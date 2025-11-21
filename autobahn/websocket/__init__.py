###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import logging
import os
import warnings

log = logging.getLogger(__name__)

# ============================================================================
# NVX (Native Vector Extensions) Runtime Configuration
# ============================================================================
#
# This section determines whether to use native acceleration (NVX) for
# performance-critical WebSocket operations (UTF-8 validation, XOR masking).
#
# Public API exported: HAS_NVX, USES_NVX
# ============================================================================

# Step 1: Probe for NVX availability (was it built and can we import it?)
_has_nvx = False
try:
    # Try importing the actual CFFI extension modules directly
    # (not just the Python wrappers which are always importable)
    # This correctly detects if NVX was actually built at install time
    import _nvx_utf8validator  # noqa: F401
    import _nvx_xormasker  # noqa: F401

    _has_nvx = True
except ImportError:
    # NVX not available (not built or CFFI compilation failed)
    pass

HAS_NVX = _has_nvx
"""
Boolean flag indicating whether NVX (Native Vector Extensions) native acceleration
modules are available in this installation.

This is a build-time capability check - it's ``True`` if the NVX native extensions
were successfully compiled and can be imported, ``False`` otherwise.

NVX provides native implementations for performance-critical WebSocket operations:

* UTF-8 validation using SIMD instructions
* XOR masking using vectorized operations

The value of ``HAS_NVX`` is independent of the runtime setting ``AUTOBAHN_USE_NVX``.
To check if NVX is actually being used at runtime, see :data:`USES_NVX`.

:type: bool

Example::

    from autobahn.websocket import HAS_NVX

    if HAS_NVX:
        print("NVX native acceleration is available")
    else:
        print("NVX not built - using pure Python implementations")

See Also:
    :data:`USES_NVX` - Whether NVX is actually enabled at runtime
"""

# Step 2: Parse AUTOBAHN_USE_NVX environment variable
env_val = os.environ.get("AUTOBAHN_USE_NVX", "").strip().lower()

if env_val in ("0", "no", "false"):
    # Case 2.2: Explicit disable
    explicit_disable = True
    explicit_enable = False
elif env_val in ("1", "yes", "true"):
    # Case 2.3: Explicit enable
    explicit_enable = True
    explicit_disable = False
else:
    # Case 2.4: Not set or empty/invalid value
    explicit_enable = False
    explicit_disable = False

# Step 3: Validate and determine runtime usage
if explicit_enable and not HAS_NVX:
    # Case 3: User explicitly requested NVX but it's not available
    raise RuntimeError(
        "NVX native acceleration explicitly requested via AUTOBAHN_USE_NVX=1, "
        "but NVX modules are not available. Either NVX was not built "
        "(build with AUTOBAHN_USE_NVX=1) or CFFI compilation failed."
    )

if explicit_disable and HAS_NVX:
    # Case 4: NVX available but user explicitly disabled it at runtime
    log.info(
        "NVX native acceleration is available but explicitly disabled via "
        "AUTOBAHN_USE_NVX=0. Falling back to pure Python implementations."
    )
    USES_NVX = False
else:
    # Case 5: Default behavior - use NVX if available
    USES_NVX = HAS_NVX

"""
Boolean flag indicating whether NVX (Native Vector Extensions) native acceleration
is actually being used at runtime.

This reflects the runtime configuration after considering both:

* **Build-time availability** (:data:`HAS_NVX`) - Were NVX modules compiled?
* **Runtime configuration** (``AUTOBAHN_USE_NVX`` environment variable) - Is NVX enabled?

Possible scenarios:

* ``USES_NVX = True``: NVX is built AND enabled (default when available)
* ``USES_NVX = False``: Either NVX not built OR explicitly disabled via ``AUTOBAHN_USE_NVX=0``

Control NVX at runtime using the ``AUTOBAHN_USE_NVX`` environment variable:

* ``AUTOBAHN_USE_NVX=1`` - Force enable (raises error if not built)
* ``AUTOBAHN_USE_NVX=0`` - Force disable (falls back to pure Python)
* Unset or empty - Auto-enable if available (default)

:type: bool

Example::

    from autobahn.websocket import USES_NVX, HAS_NVX

    if USES_NVX:
        print("Using NVX native acceleration for WebSocket operations")
    elif HAS_NVX:
        print("NVX available but disabled (AUTOBAHN_USE_NVX=0)")
    else:
        print("NVX not built - using pure Python implementations")

See Also:
    :data:`HAS_NVX` - Whether NVX was built and is available
"""

# ============================================================================
# End of NVX Runtime Configuration
# ============================================================================


from autobahn.websocket.interfaces import IWebSocketChannel
from autobahn.websocket.types import (
    ConnectionAccept,
    ConnectionDeny,
    ConnectionRequest,
    ConnectionResponse,
    IncomingMessage,
    Message,
    OutgoingMessage,
)

__all__ = (
    "ConnectionAccept",
    "ConnectionDeny",
    "ConnectionRequest",
    "ConnectionResponse",
    "HAS_NVX",
    "IWebSocketChannel",
    "IncomingMessage",
    "Message",
    "OutgoingMessage",
    "USES_NVX",
)
