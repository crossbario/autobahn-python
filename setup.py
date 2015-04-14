###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
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

from __future__ import absolute_import

import re
import sys
import platform
from setuptools import setup
from setuptools.command.test import test as TestCommand

# remember if we already had six _before_ installation
try:
    import six  # noqa
    _HAD_SIX = True
except ImportError:
    _HAD_SIX = False

CPY = platform.python_implementation() == 'CPython'
PY3 = sys.version_info >= (3,)
PY33 = (3, 3) <= sys.version_info < (3, 4)

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

# get version string from "autobahn/__init__.py"
# See: http://stackoverflow.com/a/7071358/884770
#
VERSIONFILE = "autobahn/__init__.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


# Autobahn core packages
#
packages = [
    'autobahn',
    'autobahn.wamp',
    'autobahn.wamp.test',
    'autobahn.websocket',
    'autobahn.websocket.test',
    'autobahn.asyncio',
    'autobahn.twisted',
    'twisted.plugins'
]

# Twisted dependencies
#
extras_require_twisted = ["zope.interface>=3.6", "Twisted>=11.1"]

# asyncio dependencies
#
if PY3:
    if PY33:
        # "Tulip"
        extras_require_asyncio = ["asyncio>=0.2.1"]
    else:
        # Python 3.4+ has asyncio builtin
        extras_require_asyncio = []
else:
    # backport of asyncio
    extras_require_asyncio = ["trollius>=0.1.2", "futures>=2.1.5"]


# C-based WebSocket acceleration
#
extras_require_accelerate = ["wsaccel>=0.6.2", "ujson>=1.33"] if CPY else []

# non-standard WebSocket compression support
#
extras_require_compress = ["python-snappy>=0.5", "lz4>=0.2.1"]

# non-JSON WAMP serialization support (namely MsgPack)
#
extras_require_serialization = ["msgpack-python>=0.4.0"]

# everything
#
extras_require_all = extras_require_twisted + extras_require_asyncio + \
    extras_require_accelerate + extras_require_compress + extras_require_serialization

# development dependencies
#
extras_require_dev = ["pep8", "flake8", "mock>=1.0.1", "pytest>=2.6.4"]

# for testing by users with "python setup.py test" (not Tox, which we use)
#
test_requirements = ["pytest", "mock"]


# pytest integration for setuptools. see:
# http://pytest.org/latest/goodpractises.html#integration-with-setuptools-test-commands
# https://github.com/pyca/cryptography/pull/678/files
class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here because in module scope the eggs are not loaded.
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


# Now install Autobahn ..
#
setup(
    name='autobahn',
    version=verstr,
    description='WebSocket client & server library, WAMP real-time framework',
    long_description=LONGSDESC,
    license='MIT License',
    author='Tavendo GmbH',
    author_email='autobahnws@googlegroups.com',
    url='http://autobahn.ws/python',
    platforms='Any',
    install_requires=[
        'six>=1.6.1',
        'txaio>=1.0.0'
    ],
    extras_require={
        'all': extras_require_all,
        'asyncio': extras_require_asyncio,
        'twisted': extras_require_twisted,
        'accelerate': extras_require_accelerate,
        'compress': extras_require_compress,
        'serialization': extras_require_serialization,
        'dev': extras_require_dev,
    },
    tests_require=test_requirements,
    cmdclass={'test': PyTest},
    packages=packages,
    zip_safe=False,
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    #
    classifiers=["License :: OSI Approved :: MIT License",
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
    keywords='autobahn autobahn.ws websocket realtime rfc6455 wamp rpc pubsub twisted asyncio'
)


try:
    from twisted.internet import reactor
    print("Twisted found (default reactor is {0})".format(reactor.__class__))
except ImportError:
    # the user doesn't have Twisted, so skip
    pass
else:
    # Make Twisted regenerate the dropin.cache, if possible. This is necessary
    # because in a site-wide install, dropin.cache cannot be rewritten by
    # normal users.
    if _HAD_SIX:
        # only proceed if we had had six already _before_ installing AutobahnPython,
        # since it produces errs/warns otherwise
        try:
            from twisted.plugin import IPlugin, getPlugins
            list(getPlugins(IPlugin))
        except Exception as e:
            print("Failed to update Twisted plugin cache: {0}".format(e))
        else:
            print("Twisted dropin.cache regenerated.")
    else:
        print("Warning: regenerate of Twisted dropin.cache skipped (can't run when six wasn't there before)")
