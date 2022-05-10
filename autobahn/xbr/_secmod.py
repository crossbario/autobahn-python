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

import txaio

from typing import Optional, Union, Dict, Any

from eth_account.account import Account
from eth_account.signers.local import LocalAccount

from py_eth_sig_utils.eip712 import encode_typed_data
from py_eth_sig_utils.utils import ecsign, ecrecover_to_pub, checksum_encode, sha3
from py_eth_sig_utils.signing import v_r_s_to_signature, signature_to_v_r_s

from autobahn.wamp.interfaces import ISecurityModule, IEthereumKey
from autobahn.xbr._mnemonic import mnemonic_to_private_key

__all__ = ('EthereumKey', )


class EthereumKey(object):
    """
    Base class to implement :class:`autobahn.wamp.interfaces.IEthereumKey`.
    """

    def __init__(self, key_or_address: Union[LocalAccount, str, bytes], can_sign: bool, security_module: Optional[ISecurityModule] = None,
                 key_id: Optional[str] = None) -> None:
        if can_sign:
            # https://eth-account.readthedocs.io/en/latest/eth_account.html#eth_account.account.Account
            assert type(key_or_address) == LocalAccount
            self._key = key_or_address
            self._address = key_or_address.address
        else:
            assert type(key_or_address) in (str, bytes)
            self._key = None
            self._address = key_or_address
        self._can_sign = can_sign
        self._security_module = security_module
        self._key_id = key_id

    @property
    def security_module(self) -> Optional['ISecurityModule']:
        """
        Implements :meth:`autobahn.wamp.interfaces.ISigningKey.security_module`.
        """
        return self._security_module

    @property
    def key_id(self) -> Optional[str]:
        """
        Implements :meth:`autobahn.wamp.interfaces.ISigningKey.key_id`.
        """
        return self._key_id

    @property
    def key_type(self) -> str:
        """
        Implements :meth:`autobahn.wamp.interfaces.ISigningKey.key_type`.
        """
        return 'eth'

    def public_key(self, binary: bool = False) -> Union[str, bytes]:
        """
        Implements :meth:`autobahn.wamp.interfaces.ISigningKey.public_key`.
        """
        raise NotImplementedError()

    def can_sign(self) -> bool:
        """
        Implements :meth:`autobahn.wamp.interfaces.ISigningKey.can_sign`.
        """
        return self._can_sign

    def address(self, binary: bool = False) -> Union[str, bytes]:
        """
        Implements :meth:`autobahn.wamp.interfaces.IEthereumKey.address`.
        """
        # FIXME: implement "binary"
        return self._address

    def sign(self, data: bytes) -> bytes:
        """
        Implements :meth:`autobahn.wamp.interfaces.ISigningKey.sign`.
        """
        # FIXME: implement signing of raw data
        raise NotImplementedError()

    def recover(self, data: bytes, signature: bytes) -> bytes:
        """
        Implements :meth:`autobahn.wamp.interfaces.ISigningKey.recover`.
        """
        # FIXME: implement signing address recovery from signature of raw data
        raise NotImplementedError()

    def sign_typed_data(self, data: Dict[str, Any]) -> bytes:
        """
        Implements :meth:`autobahn.wamp.interfaces.IEthereumKey.sign_typed_data`.
        """
        try:
            # encode typed data dict and return message hash
            msg_hash = encode_typed_data(data)

            # ECDSA signatures in Ethereum consist of three parameters: v, r and s.
            # The signature is always 65-bytes in length.
            #     r = first 32 bytes of signature
            #     s = second 32 bytes of signature
            #     v = final 1 byte of signature
            signature_vrs = ecsign(msg_hash, self._key.key)

            # concatenate signature components into byte string
            signature = v_r_s_to_signature(*signature_vrs)
        except Exception as e:
            return txaio.create_future_error(e)
        else:
            return txaio.create_future_success(signature)

    def verify_typed_data(self, data: Dict[str, Any], signature: bytes) -> bool:
        """
        Implements :meth:`autobahn.wamp.interfaces.IEthereumKey.verify_typed_data`.
        """
        try:
            msg_hash = encode_typed_data(data)
            signature_vrs = signature_to_v_r_s(signature)
            public_key = ecrecover_to_pub(msg_hash, *signature_vrs)
            address_bytes = sha3(public_key)[-20:]
            address = checksum_encode(address_bytes)
        except Exception as e:
            return txaio.create_future_error(e)
        else:
            return txaio.create_future_success(address == self._address)

    @classmethod
    def from_address(cls, address: Union[str, bytes]) -> 'EthereumKey':
        """
        Create a public key from an address, which can be used to verify signatures.

        :param key: The Ethereum private key seed (32 octets).
        :return: New instance of :class:`EthereumKey`
        """
        return EthereumKey(key_or_address=address, can_sign=False)

    @classmethod
    def from_bytes(cls, key: bytes) -> 'EthereumKey':
        """
        Create a private key from seed bytes, which can be used to sign and create signatures.

        :param key: The Ethereum private key seed (32 octets).
        :return: New instance of :class:`EthereumKey`
        """
        if type(key) != bytes:
            raise ValueError("invalid seed type {} (expected binary)".format(type(key)))

        if len(key) != 32:
            raise ValueError("invalid seed length {} (expected 32)".format(len(key)))

        account: LocalAccount = Account.from_key(key)
        return EthereumKey(key_or_address=account, can_sign=True)

    @classmethod
    def from_seedphrase(cls, seedphrase: str, index: int = 0) -> 'EthereumKey':
        """
        Create a private key from the given BIP-39 mnemonic seed phrase and index,
        which can be used to sign and create signatures.

        :param seedphrase: The BIP-39 seedphrase ("Mnemonic") from which to derive the account.
        :param index: The account index in account hierarchy defined by the seedphrase.
        :return: New instance of :class:`EthereumKey`
        """
        # Base HD Path:  m/44'/60'/0'/0/{account_index}
        derivation_path = "m/44'/60'/0'/0/{}".format(index)

        key = mnemonic_to_private_key(seedphrase, str_derivation_path=derivation_path)
        assert type(key) == bytes
        assert len(key) == 32

        account: LocalAccount = Account.from_key(key)
        return EthereumKey(key_or_address=account, can_sign=True)


IEthereumKey.register(EthereumKey)
