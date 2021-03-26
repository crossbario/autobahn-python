:mod:`autobahn.xbr._eip712_market_create`
=========================================

.. py:module:: autobahn.xbr._eip712_market_create


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_market_create._create_eip712_market_create
   autobahn.xbr._eip712_market_create.sign_eip712_market_create
   autobahn.xbr._eip712_market_create.recover_eip712_market_create


.. function:: _create_eip712_market_create(chainId: int, verifyingContract: bytes, member: bytes, created: int, marketId: bytes, coin: bytes, terms: str, meta: Optional[str], maker: bytes, providerSecurity: int, consumerSecurity: int, marketFee: int) -> dict

   :param chainId:
   :param verifyingContract:
   :param member:
   :param created:
   :param marketId:
   :param coin:
   :param terms:
   :param meta:
   :param maker:
   :param providerSecurity:
   :param consumerSecurity:
   :param marketFee:
   :return:


.. function:: sign_eip712_market_create(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, created: int, marketId: bytes, coin: bytes, terms: str, meta: str, maker: bytes, providerSecurity: int, consumerSecurity: int, marketFee: int) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_market_create(chainId: int, verifyingContract: bytes, member: bytes, created: int, marketId: bytes, coin: bytes, terms: str, meta: str, maker: bytes, providerSecurity: int, consumerSecurity: int, marketFee: int, signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


