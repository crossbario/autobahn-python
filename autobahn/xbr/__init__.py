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

try:
    from mnemonic import Mnemonic
    from autobahn.xbr._mnemonic import mnemonic_to_private_key

    # monkey patch, see:
    # https://github.com/ethereum/web3.py/issues/1201
    # https://github.com/ethereum/eth-abi/pull/88
    from eth_abi import abi

    from autobahn.xbr._abi import XBR_TOKEN_ABI, XBR_NETWORK_ABI, XBR_CHANNEL_ABI  # noqa
    from autobahn.xbr._abi import XBR_DEBUG_TOKEN_ADDR, XBR_DEBUG_NETWORK_ADDR  # noqa
    from autobahn.xbr._interfaces import IMarketMaker, IProvider, IConsumer, ISeller, IBuyer  # noqa
    from autobahn.xbr._util import sign_eip712_data, recover_eip712_signer, pack_uint256, unpack_uint256  # noqa
    from autobahn.xbr._blockchain import SimpleBlockchain  # noqa
    from autobahn.xbr._seller import SimpleSeller, KeySeries  # noqa
    from autobahn.xbr._buyer import SimpleBuyer  # noqa

    HAS_XBR = True

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
    Contract instance of the token used in the XBR Network.
    """

    xbrnetwork = None
    """
    Contract instance of the XBR Network.
    """

    def setProvider(_w3):
        """
        The XBR library must be initialized (once) first by setting the Web3 provider
        using this function.
        """
        global xbrtoken
        global xbrnetwork

        # print('Provider set - xbrtoken={}'.format(XBR_DEBUG_TOKEN_ADDR))
        xbrtoken = _w3.eth.contract(address=XBR_DEBUG_TOKEN_ADDR, abi=XBR_TOKEN_ABI)

        # print('Provider set - xbrnetwork={}'.format(XBR_DEBUG_NETWORK_ADDR))
        xbrnetwork = _w3.eth.contract(address=XBR_DEBUG_NETWORK_ADDR, abi=XBR_NETWORK_ABI)

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

    class ActorType(object):
        """
        XBR Market actor types.
        """
        NONE = 0
        NETWORK = 1
        MARKET = 2
        PROVIDER = 3
        CONSUMER = 4

    def generate_seedphrase(strength=128, language='english'):
        """
        Generate a new BIP-39 mnemonic seed phrase for use in Ethereum (Metamask, etc).

        :param strength: Strength of seed phrase in bits, one of the following ``[128, 160, 192, 224, 256]``,
            generating seed phrase of 12 - 24 words inlength.

        :return: Newly generated seed phrase (in english).
        :rtype: string
        """
        return Mnemonic(language).generate(strength)

    def check_seedphrase(seedphrase, language='english'):
        return Mnemonic(language).check(seedphrase)

    def account_from_seedphrase(seephrase, index=0):
        from web3.auto import w3

        derivation_path = "m/44'/60'/0'/0/{}".format(index)
        key = mnemonic_to_private_key(seephrase, str_derivation_path=derivation_path)
        account = w3.eth.account.privateKeyToAccount(key)
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
        'setProvider',

        'xbrtoken',
        'xbrnetwork',
        'sign_eip712_data',
        'recover_eip712_signer',
        'pack_uint256',
        'unpack_uint256',

        'KeySeries',
        'SimpleBlockchain',
        'SimpleSeller',
        'SimpleBuyer',

        'generate_seedphrase',
        'check_seedphrase',
        'account_from_seedphrase',

        'MemberLevel',
        'ActorType',
        'NodeType',

        'XBR_TOKEN_ABI',
        'XBR_NETWORK_ABI',
        'XBR_CHANNEL_ABI',
        'ASCII_BOMB',

        'IMarketMaker',
        'IProvider',
        'IConsumer',
        'ISeller',
        'IBuyer',
    )

except ImportError:
    HAS_XBR = False
    __all__ = ('HAS_XBR',)
