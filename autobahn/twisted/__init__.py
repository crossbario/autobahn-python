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
import twisted
from autobahn.twisted.choosereactor import install_reactor
from autobahn.websocket import USES_NVX

# Twisted specific utilities (these should really be in Twisted, but
# they aren't, and we use these in example code, so it must be part of
# the public API)
from autobahn.twisted.util import sleep

# Twisted Web support - FIXME: these imports trigger import of Twisted reactor!
# from autobahn.twisted.resource import WebSocketResource, WSGIRootResource
# WAMP support
from autobahn.twisted.wamp import ApplicationSession

# WebSocket protocol support
# support for running Twisted stream protocols over WebSocket
from autobahn.twisted.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
    WebSocketServerFactory,
    WebSocketServerProtocol,
    WrappingWebSocketClientFactory,
    WrappingWebSocketServerFactory,
)

__all__ = (
    "ApplicationSession",
    "WebSocketClientFactory",
    "WebSocketClientProtocol",
    "WebSocketServerFactory",
    "WebSocketServerProtocol",
    "WrappingWebSocketServerFactory",
    "install_reactor",
    "sleep",
)

# Build identification string with optional NVX acceleration indicator
if USES_NVX:
    import cffi

    __ident__ = "Autobahn/{}-NVXCFFI/{}-Twisted/{}-{}/{}".format(
        autobahn.__version__,
        cffi.__version__,
        twisted.__version__,
        platform.python_implementation(),
        platform.python_version(),
    )
else:
    __ident__ = "Autobahn/{}-Twisted/{}-{}/{}".format(
        autobahn.__version__,
        twisted.__version__,
        platform.python_implementation(),
        platform.python_version(),
    )

"""
Identification string for the Autobahn|Python Twisted backend.

This string identifies the library version, networking framework, and runtime
environment. It's commonly used in protocol handshakes (e.g., WebSocket Upgrade
headers, WAMP HELLO metadata) to identify the client/server implementation.

Format with NVX acceleration enabled::

    "Autobahn/{version}-NVXCFFI/{cffi_version}-Twisted/{twisted_version}-{python_impl}/{python_version}"

Format without NVX acceleration::

    "Autobahn/{version}-Twisted/{twisted_version}-{python_impl}/{python_version}"

The presence of ``NVXCFFI`` in the identification string indicates that NVX
(Native Vector Extensions) native acceleration is enabled, providing high-performance
UTF-8 validation and XOR masking using SIMD instructions.

:type: str

Example values::

    # With NVX acceleration on CPython
    "Autobahn/25.10.2-NVXCFFI/1.15.1-Twisted/24.7.0-CPython/3.11.9"

    # Without NVX acceleration on PyPy
    "Autobahn/25.10.2-Twisted/24.7.0-PyPy/7.3.16"

See Also:
    :data:`autobahn.asyncio.__ident__` - Identification string for asyncio backend
    :data:`autobahn.websocket.USES_NVX` - Whether NVX acceleration is enabled
"""
