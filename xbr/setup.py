###############################################################################
#
# Copyright (c) Crossbar.io Technologies GmbH and contributors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.
#
###############################################################################

from __future__ import absolute_import
from setuptools import setup

# read version string
__version__ = None
with open('autobahn/xbr/_version.py') as f:
    exec(f.read())  # defines __version__

# read package long description
with open('README.rst') as f:
    docstr = f.read()

setup(
    name='xbr',
    version=__version__,
    description='The XBR Protocol - blockchain protocol for decentralized open data markets',
    long_description=docstr,
    license='Apache 2.0 License',
    author='Crossbar.io Technologies GmbH',
    author_email='support@crossbario.com',
    url='https://xbr.network',
    platforms='Any',
    install_requires=[
        'cbor2>=5.1.0',             # MIT license
        'zlmdb>=20.4.1',            # MIT license
        'twisted>=20.3.0',          # MIT license
        'autobahn>=20.4.3',        # MIT license
        'web3>=4.8.1',              # MIT license

        # the following is needed for EIP712 ("signed typed data"):
        'py-eth-sig-utils>=0.4.0',  # MIT license (https://github.com/rmeissner/py-eth-sig-utils)
        'py-ecc>=1.7.1',            # MIT license (https://github.com/ethereum/py_ecc)
        'eth-abi>=1.3.0',           # MIT license (https://github.com/ethereum/eth-abi)

        # the following is needed (at least) for BIP32/39 mnemonic processing
        'mnemonic>=0.13',           # MIT license (https://github.com/trezor/python-mnemonic)

        # py-multihash 0.2.3 has requirement base58<2.0,>=1.0.2 (https://github.com/crossbario/crossbarfx/issues/469)
        'base58<2.0,>=1.0.2',       # MIT license (https://github.com/keis/base58)
        'ecdsa>=0.13',              # MIT license (https://github.com/warner/python-ecdsa)
        'py-multihash>=0.2.3',      # MIT license (https://github.com/multiformats/py-multihash / https://pypi.org/project/py-multihash/)
    ],
    extras_require={},
    packages=[
        'autobahn.xbr',
        'autobahn.asyncio.xbr',
        'autobahn.twisted.xbr',
    ],
    package_data={'xbr': ['./xbr/contracts/*.json']},

    entry_points={
        "console_scripts": [
            "xbrnetwork = autobahn.xbr._cli:_main",
        ]
    },

    # this flag will make files from MANIFEST.in go into _source_ distributions only
    include_package_data=True,

    zip_safe=False,

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=["License :: OSI Approved :: Apache Software License",
                 "Development Status :: 3 - Alpha",
                 "Environment :: No Input/Output (Daemon)",
                 "Intended Audience :: Developers",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 3",
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
    keywords='xbr data-markets blockchain ethereum wamp autobahn crossbar'
)
