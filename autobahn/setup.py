###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
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

from __future__ import absolute_import

from distutils import log

try:
   from ez_setup import use_setuptools
   use_setuptools()
except Exception as e:
   log.warn("ez_setup failed: {0}".format(e))
finally:
   from setuptools import setup

import platform
CPY = platform.python_implementation() == 'CPython'

import sys
PY3 = sys.version_info >= (3,)
PY33 = sys.version_info >= (3,3) and sys.version_info < (3,4)


LONGSDESC = """
.. |ab| replace:: **Autobahn**\|Python

|ab| is a networking library that is part of the `Autobahn <http://autobahn.ws>`__
project and provides implementations of

* `The WebSocket Protocol <http://tools.ietf.org/html/rfc6455>`__
* `The Web Application Messaging Protocol (WAMP) <http://wamp.ws>`__

for `Twisted <http://www.twistedmatrix.com/>`__ and
`asyncio <https://docs.python.org/3/library/asyncio.html>`__,
on Python 2 & 3 and for writing servers and clients.

WebSocket allows bidirectional real-time messaging on the Web and WAMP
adds asynchronous *Remote Procedure Calls* and *Publish & Subscribe* on
top of WebSocket.

More information:

* `Project Site <http://autobahn.ws/python>`__
* `Source Code <https://github.com/tavendo/AutobahnPython>`__
"""

## get version string from "autobahn/__init__.py"
## See: http://stackoverflow.com/a/7071358/884770
##
import re
VERSIONFILE="autobahn/__init__.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
   verstr = mo.group(1)
else:
   raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


## Autobahn core packages
##
packages = ['autobahn',
            'autobahn.wamp',
            'autobahn.wamp.test',
            'autobahn.websocket',
            'autobahn.websocket.test',
            'autobahn.asyncio',
            'autobahn.twisted',
            'twisted.plugins',
            'autobahn.wamp1', # WAMPv1 - remove this later
            ]

if PY3:
   if PY33:
      ## "Tulip"
      asyncio_packages = ["asyncio>=0.2.1"]
   else:
      ## Python 3.4+ has asyncio builtin
      asyncio_packages = []
else:
   ## backport of asyncio
   asyncio_packages = ["trollius>=0.1.2", "futures>=2.1.5"]


## Now install Autobahn ..
##
setup(
   name = 'autobahn',
   version = verstr,
   description = 'WebSocket client & server library, WAMP real-time framework',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'Tavendo GmbH',
   author_email = 'autobahnws@googlegroups.com',
   url = 'http://autobahn.ws/python',
   platforms = ('Any'),
   install_requires = ['six>=1.6.1'],
   extras_require = {
      ## asyncio is needed for Autobahn/asyncio
      'asyncio': asyncio_packages,

      ## you need Twisted for Autobahn/Twisted - obviously
      'twisted': ["Twisted>=11.1"],

      ## native WebSocket and JSON acceleration: this should ONLY be used on CPython
      'accelerate': ["wsaccel>=0.6.2", "ujson>=1.33"] if CPY else [],

      ## for (non-standard) WebSocket compression methods - not needed if you
      ## only want standard WebSocket compression ("permessage-deflate")
      'compress': ["python-snappy>=0.5", "lz4>=0.2.1"],

      ## needed if you want WAMPv2 binary serialization support
      'serialization': ["msgpack-python>=0.4.0"]
   },
   packages = packages,
   zip_safe = False,
   ## http://pypi.python.org/pypi?%3Aaction=list_classifiers
   ##
   classifiers = ["License :: OSI Approved :: Apache Software License",
                  "Development Status :: 5 - Production/Stable",
                  "Environment :: No Input/Output (Daemon)",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Programming Language :: Python :: 2",
                  "Programming Language :: Python :: 2.6",
                  "Programming Language :: Python :: 2.7",
                  "Programming Language :: Python :: 3",
                  "Programming Language :: Python :: 3.3",
                  "Programming Language :: Python :: 3.4",
                  "Programming Language :: Python :: Implementation :: CPython",
                  "Programming Language :: Python :: Implementation :: PyPy",
                  "Programming Language :: Python :: Implementation :: Jython",
                  "Topic :: Internet",
                  "Topic :: Internet :: WWW/HTTP",
                  "Topic :: Communications",
                  "Topic :: System :: Distributed Computing",
                  "Topic :: Software Development :: Libraries",
                  "Topic :: Software Development :: Libraries :: Python Modules",
                  "Topic :: Software Development :: Object Brokering"],
   keywords = 'autobahn autobahn.ws websocket realtime rfc6455 wamp rpc pubsub twisted asyncio'
)


try:
   from twisted.internet import reactor
except:
   pass
else:
   # Make Twisted regenerate the dropin.cache, if possible. This is necessary
   # because in a site-wide install, dropin.cache cannot be rewritten by
   # normal users.
   try:
      from twisted.plugin import IPlugin, getPlugins
      list(getPlugins(IPlugin))
   except Exception as e:
      log.warn("Failed to update Twisted plugin cache: {}".format(e))
   else:
      log.info("Twisted dropin.cache regenerated.")
