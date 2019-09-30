import sys
import argparse
import os
from binascii import b2a_hex, a2b_hex

import web3
from autobahn import xbr

import eth_keys
from eth_account import Account
from cfxdb import pack_uint256, unpack_uint256, pack_uint128, unpack_uint128


def main(accounts):
    from py_eth_sig_utils import signing, utils
    from autobahn.xbr import _util

    verifying_adr = a2b_hex('0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B'[2:])
    channel_adr = a2b_hex('0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B'[2:])

    data = _util._create_eip712_data(
        verifying_adr,
        channel_adr,
        39,
        2700,
        False
    )

    # use fixed or generate a new raw random private key
    if True:
        # maker_key
        pkey_raw = a2b_hex('a4985a2ed93107886e9a1f12c7b8e2e351cc1d26c42f3aab7f220f3a7d08fda6')
    else:
        pkey_raw = os.urandom(32)
    print('Using private key: {}'.format(b2a_hex(pkey_raw).decode()))

    # make a private key object from the raw private key bytes
    pkey = eth_keys.keys.PrivateKey(pkey_raw)

    # make a private account from the private key
    acct = Account.privateKeyToAccount(pkey)

    # get the public key of the account
    addr = pkey.public_key.to_canonical_address()
    print('Account address: {}'.format(b2a_hex(addr).decode()))

    # get the canonical address of the account
    caddr = web3.Web3.toChecksumAddress(addr)
    print('Account canonical address: {}'.format(caddr))

    # step-wise computation of signature
    msg_hash = signing.encode_typed_data(data)
    print('Ok, MSG_HASH = 0x{}'.format(b2a_hex(msg_hash).decode()))
    sig_vrs = utils.ecsign(msg_hash, pkey_raw)
    sig = signing.v_r_s_to_signature(*sig_vrs)

    signature = signing.v_r_s_to_signature(*signing.sign_typed_data(data, pkey_raw))
    assert len(signature) == 32 + 32 + 1
    #assert signature == sig
    print('Ok, signed typed data (using key {}):\nSIGNATURE = 0x{}'.format(caddr, b2a_hex(signature).decode()))

    signer_address = signing.recover_typed_data(data, *signing.signature_to_v_r_s(signature))
    assert signer_address == caddr
    print('Ok, verified signature was signed by {}'.format(signer_address))


if __name__ == '__main__':
    print('using web3.py v{}'.format(web3.__version__))

    parser = argparse.ArgumentParser()

    parser.add_argument('--gateway',
                        dest='gateway',
                        type=str,
                        default=None,
                        help='Ethereum HTTP gateway URL or None for auto-select (default: -, means let web3 auto-select).')

    args = parser.parse_args()

    if args.gateway:
        w3 = web3.Web3(web3.Web3.HTTPProvider(args.gateway))
    else:
        # using automatic provider detection:
        from web3.auto import w3

    # check we are connected, and check network ID
    if not w3.isConnected():
        print('could not connect to Web3/Ethereum at "{}"'.format(args.gateway or 'auto'))
        sys.exit(1)
    else:
        print('connected via provider "{}"'.format(args.gateway or 'auto'))

    # set new provider on XBR library
    xbr.setProvider(w3)

    # now enter main ..
    main(w3.eth.accounts)
