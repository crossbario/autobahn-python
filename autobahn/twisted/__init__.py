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
AutobahnPython library implementation (eg. "Autobahn/0.13.0-Twisted/15.5.0-CPython/3.5.1")
"""
