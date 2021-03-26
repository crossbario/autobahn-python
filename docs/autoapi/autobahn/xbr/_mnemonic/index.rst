:mod:`autobahn.xbr._mnemonic`
=============================

.. py:module:: autobahn.xbr._mnemonic


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._mnemonic.mnemonic_to_bip39seed
   autobahn.xbr._mnemonic.bip39seed_to_bip32masternode
   autobahn.xbr._mnemonic.derive_public_key
   autobahn.xbr._mnemonic.derive_bip32childkey
   autobahn.xbr._mnemonic.fingerprint
   autobahn.xbr._mnemonic.b58xprv
   autobahn.xbr._mnemonic.b58xpub
   autobahn.xbr._mnemonic.parse_derivation_path
   autobahn.xbr._mnemonic.mnemonic_to_private_key


.. data:: BIP39_PBKDF2_ROUNDS
   :annotation: = 2048

   

.. data:: BIP39_SALT_MODIFIER
   :annotation: = mnemonic

   

.. data:: BIP32_PRIVDEV
   :annotation: = 2147483648

   

.. data:: BIP32_CURVE
   

   

.. data:: BIP32_SEED_MODIFIER
   :annotation: = b'Bitcoin seed'

   

.. data:: LEDGER_ETH_DERIVATION_PATH
   :annotation: = m/44'/60'/0'/0

   

.. function:: mnemonic_to_bip39seed(mnemonic, passphrase)

   BIP39 seed from a mnemonic key.
   Logic adapted from https://github.com/trezor/python-mnemonic. 


.. function:: bip39seed_to_bip32masternode(seed)

   BIP32 master node derivation from a bip39 seed.
   Logic adapted from https://github.com/satoshilabs/slips/blob/master/slip-0010/testvectors.py. 


.. function:: derive_public_key(private_key)

   Public key from a private key.
   Logic adapted from https://github.com/satoshilabs/slips/blob/master/slip-0010/testvectors.py. 


.. function:: derive_bip32childkey(parent_key, parent_chain_code, i)

   Derives a child key from an existing key, i is current derivation parameter.
   Logic adapted from https://github.com/satoshilabs/slips/blob/master/slip-0010/testvectors.py. 


.. function:: fingerprint(public_key)

   BIP32 fingerprint formula, used to get b58 serialized key. 


.. function:: b58xprv(parent_fingerprint, private_key, chain, depth, childnr)

   Private key b58 serialization format. 


.. function:: b58xpub(parent_fingerprint, public_key, chain, depth, childnr)

   Public key b58 serialization format. 


.. function:: parse_derivation_path(str_derivation_path)

   Parses a derivation path such as "m/44'/60/0'/0" and returns
   list of integers for each element in path. 


.. function:: mnemonic_to_private_key(mnemonic, str_derivation_path=LEDGER_ETH_DERIVATION_PATH, passphrase='')

   Performs all convertions to get a private key from a mnemonic sentence, including:

       BIP39 mnemonic to seed
       BIP32 seed to master key
       BIP32 child derivation of a path provided

   Parameters:
       mnemonic -- seed wordlist, usually with 24 words, that is used for ledger wallet backup
       str_derivation_path -- string that directs BIP32 key derivation, defaults to path
           used by ledger ETH wallet


