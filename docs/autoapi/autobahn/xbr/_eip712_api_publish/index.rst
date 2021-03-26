:mod:`autobahn.xbr._eip712_api_publish`
=======================================

.. py:module:: autobahn.xbr._eip712_api_publish


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_api_publish._create_eip712_api_publish
   autobahn.xbr._eip712_api_publish.sign_eip712_api_publish
   autobahn.xbr._eip712_api_publish.recover_eip712_api_publish


.. function:: _create_eip712_api_publish(chainId: int, verifyingContract: bytes, member: bytes, published: int, catalogId: bytes, apiId: bytes, schema: str, meta: Optional[str]) -> dict

   :param chainId:
   :param verifyingContract:
   :param member:
   :param published:
   :param catalogId:
   :param apiId:
   :param schema:
   :param meta:
   :return:


.. function:: sign_eip712_api_publish(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, published: int, catalogId: bytes, apiId: bytes, schema: str, meta: Optional[str]) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_api_publish(chainId: int, verifyingContract: bytes, member: bytes, published: int, catalogId: bytes, apiId: bytes, schema: str, meta: Optional[str], signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


