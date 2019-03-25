###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
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

import os
import sys
import platform
from setuptools import setup
from setuptools.command.test import test as test_command

# remember if we already had six _before_ installation
try:
    import six  # noqa
    _HAD_SIX = True
except ImportError:
    _HAD_SIX = False

CPY = platform.python_implementation() == 'CPython'
PY3 = sys.version_info >= (3,)
PY33 = (3, 3) <= sys.version_info < (3, 4)

# read version string
with open('autobahn/_version.py') as f:
    exec(f.read())  # defines __version__

# read package long description
with open('README.rst') as f:
    docstr = f.read()

# Twisted dependencies (be careful bumping these minimal versions,
# as we make claims to support older Twisted!)
extras_require_twisted = [
    "zope.interface>=3.6.0",        # Zope Public License
    "Twisted >= 12.1.0"             # MIT license
]

# asyncio dependencies
if PY3:
    if PY33:
        # "Tulip"
        extras_require_asyncio = [
            "asyncio>=3.4.3"        # Apache 2.0
        ]
    else:
        # Python 3.4+ has asyncio builtin
        extras_require_asyncio = []
else:
    # backport of asyncio for Python 2
    extras_require_asyncio = [
        "trollius>=2.0",            # Apache 2.0
        "futures>=3.0.4"            # BSD license
    ]

# C-based WebSocket acceleration (only use on CPython, not PyPy!)
if CPY and sys.platform != 'win32':
    # wsaccel does not provide wheels: https://github.com/methane/wsaccel/issues/12
    extras_require_accelerate = [
        "wsaccel>=0.6.2"            # Apache 2.0
    ]
else:
    extras_require_accelerate = []

# non-standard WebSocket compression support (FIXME: consider removing altogether)
# Ubuntu: sudo apt-get install libsnappy-dev
# lz4: do we need that anyway?
extras_require_compress = [
    "python-snappy>=0.5",       # BSD license
    "lz4>=0.7.0"                # BSD license
]

# accelerated JSON and non-JSON WAMP serialization support (namely MessagePack, CBOR and UBJSON)
extras_require_serialization = []
if CPY:
    extras_require_serialization.extend([
        'msgpack>=0.6.1',       # Apache 2.0 license
        'ujson>=1.35',          # BSD license
    ])
else:
    os.environ['PYUBJSON_NO_EXTENSION'] = '1'  # enforce use of pure Python py-ubjson (no Cython)
    extras_require_serialization.extend([
        'u-msgpack-python>=2.1',    # MIT license
    ])

extras_require_serialization.extend([
    'cbor2>=4.1.2',             # MIT license
    'cbor>=1.0.0',              # Apache 2.0 license
    'py-ubjson>=0.8.4',         # Apache 2.0 license
    'flatbuffers>=1.10',        # Apache 2.0 license
])

# TLS transport encryption
# WAMP-cryptosign end-to-end encryption
# WAMP-cryptosign authentication
os.environ['SODIUM_INSTALL'] = 'bundled'  # enforce use of bundled libsodium
extras_require_encryption = [
    'pyopenssl>=16.2.0',            # Apache 2.0 license
    'service_identity>=16.0.0',     # MIT license
    'pynacl>=1.0.1',                # Apache license
    'pytrie>=0.2',                  # BSD license
    'pyqrcode>=1.1'                 # BSD license
]

# Support for WAMP-SCRAM authentication
extras_require_scram = [
    'cffi>=1.11.5',             # MIT license
    'argon2_cffi>=18.1.0',      # MIT license
    'passlib>=1.7.1',           # BSD license
]

# Support native vector (SIMD) acceleration included with Autobahn
extras_require_nvx = [
    'cffi>=1.11.5',             # MIT license
]

# cffi based extension modules to build, currently only NVX
cffi_modules = []
if 'AUTOBAHN_USE_NVX' in os.environ:
    # FIXME: building this extension will make the wheel
    # produced no longer universal (as in "autobahn-18.4.1-py2.py3-none-any.whl").
    # on the other hand, I don't know how to selectively include this
    # based on the install flavor the user has chosen (eg pip install autobahn[nvx]
    # should make the following be included)
    cffi_modules.append('autobahn/nvx/_utf8validator.py:ffi')

# everything
extras_require_all = extras_require_twisted + extras_require_asyncio + \
    extras_require_accelerate + extras_require_compress + \
    extras_require_serialization + extras_require_encryption + \
    extras_require_scram + extras_require_nvx

# development dependencies
extras_require_dev = [
    # flake8 will install the version "it needs"
    # "pep8>=1.6.2",                      # MIT license
    "pep8-naming>=0.3.3",               # MIT license
    "flake8>=2.5.1",                    # MIT license
    "pyflakes>=1.0.0",                  # MIT license
    "mock>=1.3.0",                      # BSD license

    # pytest 3.3.0 has dropped support for Python 3.3
    # https://docs.pytest.org/en/latest/changelog.html#pytest-3-3-0-2017-11-23
    "pytest>=2.8.6,<3.3.0",             # MIT license

    "twine>=1.6.5",                     # Apache 2.0
    'sphinx>=1.2.3',                    # BSD
    'pyenchant>=1.6.6',                 # LGPL
    'sphinxcontrib-spelling>=2.1.2',    # BSD
    'sphinx_rtd_theme>=0.1.9',          # BSD

    'awscli',                           # Apache 2.0
    'qualname',                         # BSD
    'passlib',                          # BSD license
    'wheel',                            # MIT license
]

if PY3:
    extras_require_dev.extend([
        # pytest-asyncio 0.6 has dropped support for Py <3.5
        # https://github.com/pytest-dev/pytest-asyncio/issues/57
        'pytest_asyncio<0.6',               # Apache 2.0
        'pytest-aiohttp',                   # Apache 2.0
    ])

# for testing by users with "python setup.py test" (not Tox, which we use)
test_requirements = [
    "pytest>=2.8.6,<3.3.0",             # MIT license
    "mock>=1.3.0",                      # BSD license
]


class PyTest(test_command):
    """
    pytest integration for setuptools.

    see:
      - http://pytest.org/latest/goodpractises.html#integration-with-setuptools-test-commands
      - https://github.com/pyca/cryptography/pull/678/files
    """

    def finalize_options(self):
        test_command.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here because in module scope the eggs are not loaded.
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='autobahn',
    version=__version__,
    description='WebSocket client & server library, WAMP real-time framework',
    long_description=docstr,
    license='MIT License',
    author='Crossbar.io Technologies GmbH',
    url='http://crossbar.io/autobahn',
    platforms='Any',
    install_requires=[
        'six>=1.11.0',      # MIT license
        'txaio>=18.8.1',    # MIT license
    ],
    extras_require={
        'all': extras_require_all,
        'asyncio': extras_require_asyncio,
        'twisted': extras_require_twisted,
        'accelerate': extras_require_accelerate,
        'compress': extras_require_compress,
        'serialization': extras_require_serialization,
        'encryption': extras_require_encryption,
        'scram': extras_require_scram,
        'nvx': extras_require_nvx,
        'dev': extras_require_dev,
    },
    tests_require=test_requirements,
    cmdclass={
        'test': PyTest
    },
    packages=[
        'autobahn',
        'autobahn.test',
        'autobahn.wamp',
        'autobahn.wamp.gen',
        'autobahn.wamp.gen.wamp',
        'autobahn.wamp.gen.wamp.proto',
        'autobahn.wamp.test',
        'autobahn.websocket',
        'autobahn.websocket.test',
        'autobahn.rawsocket',
        'autobahn.rawsocket.test',
        'autobahn.asyncio',
        'autobahn.twisted',
        'twisted.plugins',
        'autobahn.nvx',
        'autobahn.nvx.test',
    ],
    package_data={'autobahn.asyncio': ['test/*']},
    cffi_modules=cffi_modules,

    entry_points={
        "console_scripts": [
            "wamp = autobahn.__main__:_main",
        ]
    },

    # this flag will make files from MANIFEST.in go into _source_ distributions only
    include_package_data=True,

    zip_safe=False,

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=["License :: OSI Approved :: MIT License",
                 "Development Status :: 5 - Production/Stable",
                 "Environment :: No Input/Output (Daemon)",
                 "Framework :: Twisted",
                 "Intended Audience :: Developers",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2",
                 "Programming Language :: Python :: 2.7",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3.4",
                 "Programming Language :: Python :: 3.5",
                 "Programming Language :: Python :: 3.6",
                 "Programming Language :: Python :: 3.7",
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
    keywords='autobahn crossbar websocket realtime rfc6455 wamp rpc pubsub twisted asyncio'
)


# regenerate Twisted plugin cache
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
