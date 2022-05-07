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

from typing import Optional, List, Dict, Any

import web3
from web3.contract import Contract
from ens.main import ENS

from twisted.internet.threads import deferToThread

from autobahn.wamp.message import identity_realm_name_category


def make_w3(gateway_config=None):
    """
    Create a Web3 instance configured and ready-to-use gateway to the blockchain.

    :param gateway_config: Blockchain gateway configuration.
    :type gateway_config: dict

    :return: Configured Web3 instance.
    :rtype: :class:`web3.Web3`
    """
    if gateway_config is None or gateway_config['type'] == 'auto':
        w3 = web3.Web3()

    elif gateway_config['type'] == 'user':
        request_kwargs = gateway_config.get('http_options', {})
        w3 = web3.Web3(web3.Web3.HTTPProvider(gateway_config['http'], request_kwargs=request_kwargs))

    elif gateway_config['type'] == 'infura':
        request_kwargs = gateway_config.get('http_options', {})
        project_id = gateway_config['key']
        # project_secret = gateway_config['secret']

        http_url = 'https://{}.infura.io/v3/{}'.format(gateway_config['network'], project_id)
        w3 = web3.Web3(web3.Web3.HTTPProvider(http_url, request_kwargs=request_kwargs))

        # https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority
        if gateway_config.get('network', None) == 'rinkeby':
            # This middleware is required to connect to geth --dev or the Rinkeby public network.
            from web3.middleware import geth_poa_middleware

            # inject the poa compatibility middleware to the innermost layer
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    else:
        raise RuntimeError('invalid blockchain gateway type "{}"'.format(gateway_config['type']))

    return w3


def unpack_uint128(data):
    assert data is None or type(data) == bytes, 'data must by bytes, was {}'.format(type(data))
    if data and type(data) == bytes:
        assert len(data) == 16, 'data must be bytes[16], but was bytes[{}]'.format(len(data))

    if data:
        return web3.Web3.toInt(data)
    else:
        return 0


def pack_uint128(value):
    assert value is None or (type(value) == int and value >= 0 and value < 2**128)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (16 - len(data)) + data
    else:
        return b'\x00' * 16


def unpack_uint256(data):
    assert data is None or type(data) == bytes, 'data must by bytes, was {}'.format(type(data))
    if data and type(data) == bytes:
        assert len(data) == 32, 'data must be bytes[32], but was bytes[{}]'.format(len(data))

    if data:
        return int(web3.Web3.toInt(data))
    else:
        return 0


def pack_uint256(value):
    assert value is None or (type(value) == int and value >= 0 and value < 2**256), 'value must be uint256, but was {}'.format(value)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (32 - len(data)) + data
    else:
        return b'\x00' * 32


class Seeder(object):
    __slots__ = (
        '_label',
        '_url',
        '_operator',
        '_country',
    )

    def __init__(self):
        self._label: Optional[str] = None
        self._url: Optional[str] = None
        self._operator: Optional[str] = None
        self._country: Optional[str] = None


class Datapool(object):
    """
    A datapool is a WAMP application realm with a trust anchor rooted in Ethereum, and
    which can be shared between multiple parties.

    A datapool is globally identified on an Ethereum chain (e.g. on Mainnet or Rinkeby)
    by an Ethereum address associated to a datapool owner by an on-chain record stored
    in the WAMP Network contract. The datapool address thus only needs to exist as an
    identifier of the datapool-owner record.
    """
    # FIXME
    CONTRACT_ADDRESS = web3.Web3.toChecksumAddress('0xF7acf1C4CB4a9550B8969576573C2688B48988C2')
    CONTRACT_ABI: str = ''

    def __init__(self, name_or_address: str, gateway_config: Optional[Dict[str, Any]] = None):
        """
        Instantiate a datapool from a datapool ENS name (which is resolved to an Ethereum
        address) or Ethereum address.

        :param name_or_address: Ethereum ENS name or address.
        :param gateway_config: If provided, use this Ethereum gateway. If not provided,
            connect via Infura to Ethereum Mainnet, which requires an environment variable
            ``WEB3_INFURA_PROJECT_ID`` with your Infura project ID.
        """
        self._name_or_address = name_or_address
        self._gateway_config = gateway_config

        # status, will change to 'RUNNING' after initialize() has completed
        self._status = 'STOPPED'

        self._name_category: Optional[str] = identity_realm_name_category(self._name_or_address)
        if self._name_category not in ['eth', 'ens', 'reverse_ens']:
            raise ValueError('name_or_address "{}" not an Ethereum address or ENS name'.format(self._name_or_address))

        # will be filled once initialize()'ed
        self._w3 = None
        self._ens = None

        # address identifying the datapool
        self._address: Optional[str] = None

        # will be initialized with a Datapool contract instance
        self._contract: Optional[Contract] = None

        # cache of datapool seeders, filled once in status running
        self._seeders: List[Seeder] = []

    @property
    def status(self) -> str:
        return self._status

    @property
    def name_or_address(self) -> str:
        return self._name_or_address

    @property
    def gateway_config(self) -> Optional[Dict[str, Any]]:
        return self._gateway_config

    @property
    def name_category(self) -> Optional[str]:
        return self._name_category

    @property
    def address(self):
        return self._address

    @property
    def seeders(self) -> List[Seeder]:
        return self._seeders

    def initialize(self):
        """

        :return:
        """
        if self._status != 'STOPPED':
            raise RuntimeError('cannot start in status "{}"'.format(self._status))
        d = deferToThread(self._initialize_background)
        return d

    def _initialize_background(self):
        self._status = 'STARTING'

        if self._gateway_config:
            self._w3 = make_w3(self._gateway_config)
        else:
            from web3.auto.infura import w3
            self._w3 = w3
        self._ens = ENS.fromWeb3(self._w3)

        if self._name_category in ['ens', 'reverse_ens']:
            if self._name_category == 'reverse_ens':
                name = ''.join(reversed(self._name_or_address.split('.')))
            else:
                name = self._name_or_address
            self._address = self._ens.address(name)
        elif self._name_category == 'eth':
            self._address = self._w3.toChecksumAddress(self._name_or_address)
        else:
            assert False, 'should not arrive here'

        # https://web3py.readthedocs.io/en/stable/contracts.html#web3.contract.Contract
        # https://web3py.readthedocs.io/en/stable/web3.eth.html#web3.eth.Eth.contract
        # self._contract = self._w3.eth.contract(address=self.CONTRACT_ADDRESS, abi=self.CONTRACT_ABI)

        # FIXME: get IPFS hash, download file, unzip seeders

        self._status = 'RUNNING'
