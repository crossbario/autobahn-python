###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from setuptools import setup

LONGSDESC = """
Twisted-based WebSocket/WAMP client and server framework.

AutobahnPython provides a WebSocket (RFC6455, Hybi-10 to -17, Hixie-76)
framework for creating WebSocket-based clients and servers.

AutobahnPython also includes an implementation of WAMP
(The WebSockets Application Messaging Protocol), a light-weight,
asynchronous RPC/PubSub over JSON/WebSocket protocol.

More information:

   * http://autobahn.ws/python
   * http://wamp.ws

Source Code:

   * https://github.com/tavendo/AutobahnPython
"""

setup (
   name = 'autobahn',
   version = '0.5.9',
   description = 'AutobahnPython - WebSocket/WAMP implementation for Python/Twisted.',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'Tavendo GmbH',
   author_email = 'autobahnws@googlegroups.com',
   url = 'http://autobahn.ws/python',
   platforms = ('Any'),
   install_requires = ['setuptools', 'Twisted>=11.1'],
   packages = ['autobahn'],
   zip_safe = False,
   ## http://pypi.python.org/pypi?%3Aaction=list_classifiers
   ##
   classifiers = ["License :: OSI Approved :: Apache Software License",
                  "Development Status :: 5 - Production/Stable",
                  "Environment :: Console",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Topic :: Internet",
                  "Topic :: Software Development :: Libraries"],
   keywords = 'autobahn autobahn.ws websocket realtime rfc6455 wamp rpc pubsub'
)
