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

from typing import Optional, Dict, Any, List

import web3
from ens import ENS
from twisted.internet.threads import deferToThread
from web3.contract import Contract

from autobahn.wamp.message import identity_realm_name_category
from autobahn.xbr import make_w3


class Seeder(object):
    """

    """
    __slots__ = (
        '_frealm',
        '_operator',
        '_label',
        '_country',
        '_legal',
        '_endpoint',
        '_bandwidth_requested',
        '_bandwidth_offered',
    )

    def __init__(self,
                 frealm: 'FederatedRealm',
                 operator: Optional[str] = None,
                 label: Optional[str] = None,
                 country: Optional[str] = None,
                 legal: Optional[str] = None,
                 endpoint: Optional[str] = None,
                 bandwidth_requested: Optional[int] = None,
                 bandwidth_offered: Optional[int] = None,
                 ):
        """

        :param frealm:
        :param operator:
        :param label:
        :param country:
        :param legal:
        :param endpoint:
        :param bandwidth_requested:
        :param bandwidth_offered:
        """
        self._frealm: FederatedRealm = frealm
        self._operator: Optional[str] = operator
        self._label: Optional[str] = label
        self._country: Optional[str] = country
        self._legal: Optional[str] = legal
        self._endpoint: Optional[str] = endpoint
        self._bandwidth_requested: Optional[str] = bandwidth_requested
        self._bandwidth_offered: Optional[str] = bandwidth_offered

    @property
    def frealm(self) -> 'FederatedRealm':
        """

        :return:
        """
        return self._frealm

    @property
    def operator(self) -> Optional[str]:
        """
        Operator address, e.g. ``"0xe59C7418403CF1D973485B36660728a5f4A8fF9c"``.

        :return: The Ethereum address of the endpoint operator.
        """
        return self._operator

    @property
    def label(self) -> Optional[str]:
        """
        Operator endpoint label.

        :return: A human readable label for the operator or specific operator endpoint.
        """
        return self._label

    @property
    def country(self) -> Optional[str]:
        """
        Operator country (ISO 3166-1 alpha-2), e.g. ``"US"``.

        :return: ISO 3166-1 alpha-2 country code.
        """
        return self._country

    @property
    def legal(self) -> Optional[str]:
        """

        :return:
        """
        return self._legal

    @property
    def endpoint(self) -> Optional[str]:
        """
        Public WAMP endpoint of seeder. Secure WebSocket URL resolving to a public IPv4
        or IPv6 listening url accepting incoming WAMP-WebSocket connections,
        e.g. ``wss://service1.example.com/ws``.

        :return: The endpoint URL.
        """
        return self._endpoint

    @property
    def bandwidth_requested(self) -> Optional[int]:
        """

        :return:
        """
        return self._bandwidth_requested

    @property
    def bandwidth_offered(self) -> Optional[int]:
        """

        :return:
        """
        return self._bandwidth_offered


class FederatedRealm(object):
    """
    A federated realm is a WAMP application realm with a trust anchor rooted in Ethereum, and
    which can be shared between multiple parties.

    A federated realm is globally identified on an Ethereum chain (e.g. on Mainnet or Rinkeby)
    by an Ethereum address associated to a federated realm owner by an on-chain record stored
    in the WAMP Network contract. The federated realm address thus only needs to exist as an
    identifier of the federated realm-owner record.
    """
    # FIXME
    CONTRACT_ADDRESS = web3.Web3.toChecksumAddress('0xF7acf1C4CB4a9550B8969576573C2688B48988C2')
    CONTRACT_ABI: str = ''

    def __init__(self, name_or_address: str, gateway_config: Optional[Dict[str, Any]] = None):
        """
        Instantiate a federated realm from a federated realm ENS name (which is resolved to an Ethereum
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

        # address identifying the federated realm
        self._address: Optional[str] = None

        # will be initialized with a FederatedRealm contract instance
        self._contract: Optional[Contract] = None

        # cache of federated realm seeders, filled once in status running
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
