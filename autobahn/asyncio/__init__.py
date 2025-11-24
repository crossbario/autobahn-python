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

import platform

import autobahn
from autobahn.websocket import USES_NVX

# WAMP support
from autobahn.asyncio.wamp import ApplicationSession

# WebSocket protocol support
from autobahn.asyncio.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
    WebSocketServerFactory,
    WebSocketServerProtocol,
)

__all__ = (
    "ApplicationSession",
    "WebSocketClientFactory",
    "WebSocketClientProtocol",
    "WebSocketServerFactory",
    "WebSocketServerProtocol",
)

# Build identification string with optional NVX acceleration indicator
if USES_NVX:
    import cffi

    __ident__ = "Autobahn/{}-NVXCFFI/{}-asyncio-{}/{}".format(
        autobahn.__version__,
        cffi.__version__,
        platform.python_implementation(),
        platform.python_version(),
    )
else:
    __ident__ = "Autobahn/{}-asyncio-{}/{}".format(
        autobahn.__version__,
        platform.python_implementation(),
        platform.python_version(),
    )

"""
Identification string for the Autobahn|Python asyncio backend.

This string identifies the library version, networking framework, and runtime
environment. It's commonly used in protocol handshakes (e.g., WebSocket Upgrade
headers, WAMP HELLO metadata) to identify the client/server implementation.

Format with NVX acceleration enabled::

    "Autobahn/{version}-NVXCFFI/{cffi_version}-asyncio-{python_impl}/{python_version}"

Format without NVX acceleration::

    "Autobahn/{version}-asyncio-{python_impl}/{python_version}"

The presence of ``NVXCFFI`` in the identification string indicates that NVX
(Native Vector Extensions) native acceleration is enabled, providing high-performance
UTF-8 validation and XOR masking using SIMD instructions.

Note that asyncio is built into Python's standard library (since Python 3.4),
so no separate asyncio version is included in the identification string (unlike
the Twisted backend which includes the Twisted version).

:type: str

Example values::

    # With NVX acceleration on CPython
    "Autobahn/25.10.2-NVXCFFI/1.15.1-asyncio-CPython/3.11.9"

    # Without NVX acceleration on PyPy
    "Autobahn/25.10.2-asyncio-PyPy/7.3.16"

See Also:
    :data:`autobahn.twisted.__ident__` - Identification string for Twisted backend
    :data:`autobahn.websocket.USES_NVX` - Whether NVX acceleration is enabled
"""
