:mod:`autobahn.xbr._eip712_domain_create`
=========================================

.. py:module:: autobahn.xbr._eip712_domain_create


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_domain_create._create_eip712_domain_create
   autobahn.xbr._eip712_domain_create.sign_eip712_domain_create
   autobahn.xbr._eip712_domain_create.recover_eip712_domain_create


.. function:: _create_eip712_domain_create(chainId: int, verifyingContract: bytes, member: bytes, created: int, domainId: bytes, domainKey: bytes, license: str, terms: str, meta: Optional[str]) -> dict

   :param chainId:
   :param verifyingContract:
   :param member:
   :param created:
   :param domainId:
   :param domainKey:
   :param license:
   :param terms:
   :param meta:
   :return:


.. function:: sign_eip712_domain_create(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, created: int, domainId: bytes, domainKey: bytes, license: str, terms: str, meta: str) -> bytes

   :param eth_privkey: Ethereum address of member (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_domain_create(chainId: int, verifyingContract: bytes, member: bytes, created: int, domainId: bytes, domainKey: bytes, license: str, terms: str, meta: str, signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


