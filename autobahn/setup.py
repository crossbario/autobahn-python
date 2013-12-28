###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
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

import sys
PY3 = sys.version_info.major > 2

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

## get version string from "autobahn/_version.py"
## See: http://stackoverflow.com/a/7071358/884770
##
import re
VERSIONFILE="autobahn/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
   verstr = mo.group(1)
else:
   raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


#packages = find_packages()
packages = ['autobahn', 
            'autobahn/wamp',
            'autobahn/websocket']

## Twisted integration
##
try:
   import twisted
except:
   print("Twisted not installed - skipping Twisted support packages")
else:
   packages.append('autobahn/twisted')

## Asyncio integration
##
if PY3:
   try:
      import asyncio
   except:
      print("Asyncio not available - skipping Asyncio support packages")
   else:
      packages.append('autobahn/asyncio')
else:
   print("Python 2 detected - skipping Asyncio support packages")


setup(
   name = 'autobahn',
   version = verstr,
   description = 'AutobahnPython - WebSocket/WAMP implementation for Python/Twisted.',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'Tavendo GmbH',
   author_email = 'autobahnws@googlegroups.com',
   url = 'http://autobahn.ws/python',
   platforms = ('Any'),
   install_requires = ['setuptools', 'zope.interface>=4.0.2'],
   extras_require = {
      'twisted': ["Twisted>=11.1"],
      'accelerate': ["wsaccel>=0.6.2"],
      'compress': ["python-snappy>=0.5", "lz4>=0.2.1"],
      'binary': ["msgpack-python>=0.4.0"]
   },
   packages = packages,
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
