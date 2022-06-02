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

import traceback

try:
    # PyPy 7.3.3 lacks this
    from _hashlib import HASH  # noqa: F401
except ImportError:
    # monkey patch it:
    import _hashlib
    _hashlib.HASH = _hashlib.Hash

try:
    from mnemonic import Mnemonic
    from autobahn.xbr._mnemonic import mnemonic_to_private_key

    # monkey patch, see:
    # https://github.com/ethereum/web3.py/issues/1201
    # https://github.com/ethereum/eth-abi/pull/88
    from eth_abi import abi

    import eth_account

    from autobahn.xbr._abi import XBR_TOKEN_ABI, XBR_NETWORK_ABI, XBR_MARKET_ABI, XBR_CATALOG_ABI, XBR_CHANNEL_ABI  # noqa
    from autobahn.xbr._abi import XBR_DEBUG_TOKEN_ADDR, XBR_DEBUG_NETWORK_ADDR, XBR_DEBUG_MARKET_ADDR, XBR_DEBUG_CATALOG_ADDR, XBR_DEBUG_CHANNEL_ADDR  # noqa
    from autobahn.xbr._abi import XBR_DEBUG_TOKEN_ADDR_SRC, XBR_DEBUG_NETWORK_ADDR_SRC, XBR_DEBUG_MARKET_ADDR_SRC, XBR_DEBUG_CATALOG_ADDR_SRC, XBR_DEBUG_CHANNEL_ADDR_SRC  # noqa
    from autobahn.xbr._interfaces import IMarketMaker, IProvider, IConsumer, ISeller, IBuyer, IDelegate  # noqa
    from autobahn.xbr._util import make_w3, pack_uint256, unpack_uint256  # noqa
    from autobahn.xbr._eip712_member_register import sign_eip712_member_register, recover_eip712_member_register  # noqa
    from autobahn.xbr._eip712_member_login import sign_eip712_member_login, recover_eip712_member_login  # noqa
    from autobahn.xbr._eip712_market_create import sign_eip712_market_create, recover_eip712_market_create  # noqa
    from autobahn.xbr._eip712_market_join import sign_eip712_market_join, recover_eip712_market_join  # noqa
    from autobahn.xbr._eip712_catalog_create import sign_eip712_catalog_create, recover_eip712_catalog_create  # noqa
    from autobahn.xbr._eip712_api_publish import sign_eip712_api_publish, recover_eip712_api_publish  # noqa
    from autobahn.xbr._eip712_consent import sign_eip712_consent, recover_eip712_consent  # noqa
    from autobahn.xbr._eip712_channel_open import sign_eip712_channel_open, recover_eip712_channel_open  # noqa
    from autobahn.xbr._eip712_channel_close import sign_eip712_channel_close, recover_eip712_channel_close  # noqa
    from autobahn.xbr._eip712_market_member_login import sign_eip712_market_member_login, \
        recover_eip712_market_member_login  # noqa
    from autobahn.xbr._eip712_base import is_address, is_chain_id, is_block_number, is_signature, \
        is_cs_pubkey, is_bytes16, is_eth_privkey  # noqa
    from autobahn.xbr._blockchain import SimpleBlockchain  # noqa
    from autobahn.xbr._seller import SimpleSeller, KeySeries  # noqa
    from autobahn.xbr._buyer import SimpleBuyer  # noqa
    from autobahn.xbr._config import load_or_create_profile, UserConfig, Profile  # noqa
    from autobahn.xbr._schema import FbsSchema, FbsObject, FbsType, FbsRPCCall, FbsEnum, FbsService, FbsEnumValue, \
    FbsAttribute, FbsField, FbsRepository  # noqa
    from autobahn.xbr._wallet import stretch_argon2_secret, expand_argon2_secret, pkm_from_argon2_secret  # noqa

    HAS_XBR = True

    from autobahn.xbr._frealm import FederatedRealm, Seeder  # noqa
    from autobahn.xbr._secmod import EthereumKey  # noqa

    if not hasattr(abi, 'collapse_type'):

        def collapse_type(base, sub, arrlist):
            return base + sub + ''.join(map(repr, arrlist))

        abi.collapse_type = collapse_type

    if not hasattr(abi, 'process_type'):
        from eth_abi.grammar import (
            TupleType,
            normalize,
            parse,
        )

        def process_type(type_str):
            normalized_type_str = normalize(type_str)
            abi_type = parse(normalized_type_str)

            type_str_repr = repr(type_str)
            if type_str != normalized_type_str:
                type_str_repr = '{} (normalized to {})'.format(
                    type_str_repr,
                    repr(normalized_type_str),
                )

            if isinstance(abi_type, TupleType):
                raise ValueError("Cannot process type {}: tuple types not supported".format(type_str_repr, ))

            abi_type.validate()

            sub = abi_type.sub
            if isinstance(sub, tuple):
                sub = 'x'.join(map(str, sub))
            elif isinstance(sub, int):
                sub = str(sub)
            else:
                sub = ''

            arrlist = abi_type.arrlist
            if isinstance(arrlist, tuple):
                arrlist = list(map(list, arrlist))
            else:
                arrlist = []

            return abi_type.base, sub, arrlist

        abi.process_type = process_type

    xbrtoken = None
    """
    Contract instance of XBRToken.
    """

    xbrnetwork = None
    """
    Contract instance of XBRNetwork.
    """

    xbrmarket = None
    """
    Contract instance of XBRMarket.
    """

    xbrcatalog = None
    """
    Contract instance of XBRMarket.
    """

    xbrchannel = None
    """
    Contract instance of XBRMarket.
    """

    def setProvider(_w3):
        """
        The XBR library must be initialized (once) first by setting the Web3 provider
        using this function.
        """
        global xbrtoken
        global xbrnetwork
        global xbrmarket
        global xbrcatalog
        global xbrchannel

        # print('Provider set - xbrtoken={}'.format(XBR_DEBUG_TOKEN_ADDR))
        xbrtoken = _w3.eth.contract(address=XBR_DEBUG_TOKEN_ADDR, abi=XBR_TOKEN_ABI)

        # print('Provider set - xbrnetwork={}'.format(XBR_DEBUG_NETWORK_ADDR))
        xbrnetwork = _w3.eth.contract(address=XBR_DEBUG_NETWORK_ADDR, abi=XBR_NETWORK_ABI)

        # print('Provider set - xbrmarket={}'.format(XBR_DEBUG_MARKET_ADDR))
        xbrmarket = _w3.eth.contract(address=XBR_DEBUG_MARKET_ADDR, abi=XBR_MARKET_ABI)

        # print('Provider set - xbrcatalog={}'.format(XBR_DEBUG_CATALOG_ADDR))
        xbrcatalog = _w3.eth.contract(address=XBR_DEBUG_CATALOG_ADDR, abi=XBR_CATALOG_ABI)

        # print('Provider set - xbrchannel={}'.format(XBR_DEBUG_CHANNEL_ADDR))
        xbrchannel = _w3.eth.contract(address=XBR_DEBUG_CHANNEL_ADDR, abi=XBR_CHANNEL_ABI)

    class MemberLevel(object):
        """
        XBR Network member levels.
        """
        NONE = 0
        ACTIVE = 1
        VERIFIED = 2
        RETIRED = 3
        PENALTY = 4
        BLOCKED = 5

    class NodeType(object):
        """
        XBR Cloud node types.
        """
        NONE = 0
        MASTER = 1
        CORE = 2
        EDGE = 3

    class ChannelType(object):
        """
        Type of a XBR off-chain channel: paying channel (for provider delegates selling data services) or payment channel (for consumer delegates buying data services).
        """

        NONE = 0
        """
        Unset
        """

        PAYMENT = 1
        """
        Payment channel: from buyer/consumer delegate to maker maker.
        """

        PAYING = 2
        """
        Paying channel: from market maker to seller/provider delegate.
        """

    class ActorType(object):
        """
        XBR Market Actor type.
        """

        NONE = 0
        """
        Unset
        """

        PROVIDER = 1
        """
        Actor is a XBR Provider.
        """

        CONSUMER = 2
        """
        Actor is a XBR Consumer.
        """

        PROVIDER_CONSUMER = 3
        """
        Actor is both a XBR Provider and XBR Consumer.
        """

    def generate_seedphrase(strength=128, language='english') -> str:
        """
        Generate a new BIP-39 mnemonic seed phrase for use in Ethereum (Metamask, etc).

        See:
        * https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
        * https://github.com/trezor/python-mnemonic

        :param strength: Strength of seed phrase in bits, one of the following ``[128, 160, 192, 224, 256]``,
            generating seed phrase of 12 - 24 words inlength.

        :return: Newly generated seed phrase (in english).
        """
        return Mnemonic(language).generate(strength)

    def check_seedphrase(seedphrase: str, language: str = 'english'):
        """
        Check a BIP-39 mnemonic seed phrase.

        :param seedphrase: The BIP-39 seedphrase from which to derive the account.
        :param language: The BIP-39 user language to generate the seedphrase for.
        :return:
        """
        return Mnemonic(language).check(seedphrase)

    def account_from_seedphrase(seedphrase: str, index: int = 0) -> eth_account.account.Account:
        """
        Create an account from the given BIP-39 mnemonic seed phrase.

        :param seedphrase: The BIP-39 seedphrase from which to derive the account.
        :param index: The account index in account hierarchy defined by the seedphrase.
        :return: The new Eth account object
        """
        from web3.auto import w3

        derivation_path = "m/44'/60'/0'/0/{}".format(index)
        key = mnemonic_to_private_key(seedphrase, str_derivation_path=derivation_path)
        account = w3.eth.account.privateKeyToAccount(key)
        return account

    def account_from_ethkey(ethkey: bytes) -> eth_account.account.Account:
        """
        Create an account from the private key seed.

        :param ethkey: The Ethereum private key seed (32 octets).
        :return: The new Eth account object
        """
        from web3.auto import w3

        assert len(ethkey) == 32
        account = w3.eth.account.privateKeyToAccount(ethkey)
        return account

    ASCII_BOMB = r"""
            _ ._  _ , _ ._
            (_ ' ( `  )_  .__)
        ( (  (    )   `)  ) _)
        (__ (_   (_ . _) _) ,__)
            `~~`\ ' . /`~~`
                ;   ;
                /   \
    _____________/_ __ \_____________

    """

    __all__ = (
        'HAS_XBR',
        'XBR_TOKEN_ABI',
        'XBR_NETWORK_ABI',
        'XBR_MARKET_ABI',
        'XBR_CATALOG_ABI',
        'XBR_CHANNEL_ABI',
        'xbrtoken',
        'xbrnetwork',
        'xbrmarket',
        'xbrcatalog',
        'xbrchannel',

        'setProvider',
        'make_w3',
        'pack_uint256',
        'unpack_uint256',
        'generate_seedphrase',
        'check_seedphrase',
        'account_from_seedphrase',
        'ASCII_BOMB',

        'sign_eip712_member_register',
        'recover_eip712_member_register',
        'sign_eip712_member_login',
        'recover_eip712_member_login',
        'sign_eip712_market_create',
        'recover_eip712_market_create',
        'sign_eip712_market_join',
        'recover_eip712_market_join',
        'sign_eip712_catalog_create',
        'recover_eip712_catalog_create',
        'sign_eip712_api_publish',
        'recover_eip712_api_publish',
        'sign_eip712_consent',
        'recover_eip712_consent',
        'sign_eip712_channel_open',
        'recover_eip712_channel_open',
        'sign_eip712_channel_close',
        'recover_eip712_channel_close',
        'sign_eip712_market_member_login',
        'recover_eip712_market_member_login',

        'is_bytes16',
        'is_cs_pubkey',
        'is_signature',
        'is_chain_id',
        'is_eth_privkey',
        'is_block_number',
        'is_address',

        'load_or_create_profile',
        'UserConfig',
        'Profile',

        'MemberLevel',
        'ActorType',
        'ChannelType',
        'NodeType',

        'KeySeries',
        'SimpleBlockchain',
        'SimpleSeller',
        'SimpleBuyer',

        'IMarketMaker',
        'IProvider',
        'IConsumer',
        'ISeller',
        'IBuyer',
        'IDelegate',

        'FbsSchema',
        'FbsService',
        'FbsType',
        'FbsObject',
        'FbsEnum',
        'FbsEnumValue',
        'FbsRPCCall',
        'FbsAttribute',
        'FbsField',
        'stretch_argon2_secret',
        'expand_argon2_secret',
        'pkm_from_argon2_secret',

        'FederatedRealm',
        'Seeder',
        'EthereumKey',
    )

except (ImportError, FileNotFoundError) as e:
    import sys
    traceback.print_tb(e.__traceback__, file=sys.stderr)
    sys.stderr.write(str(e))
    sys.stderr.flush()
    HAS_XBR = False
    __all__ = ('HAS_XBR',)
