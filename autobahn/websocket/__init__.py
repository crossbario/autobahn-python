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

import os
import warnings

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
HAS_NVX = False
try:
    # Try importing both NVX modules to verify they're available
    from autobahn.nvx._xormasker import create_xor_masker as _nvx_xor_test  # noqa: F401
    from autobahn.nvx._utf8validator import Utf8Validator as _nvx_utf8_test  # noqa: F401
    HAS_NVX = True
except ImportError:
    # NVX not available (not built or CFFI compilation failed)
    pass

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
    warnings.warn(
        "NVX native acceleration is available but explicitly disabled via "
        "AUTOBAHN_USE_NVX=0. Falling back to pure Python implementations.",
        RuntimeWarning,
        stacklevel=2
    )
    USES_NVX = False
else:
    # Case 5: Default behavior - use NVX if available
    USES_NVX = HAS_NVX

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
