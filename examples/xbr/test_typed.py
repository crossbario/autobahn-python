import sys
import argparse
import os
from binascii import b2a_hex, a2b_hex

import web3
from autobahn import xbr

import eth_keys
from eth_account import Account


def main (accounts):

    from py_eth_sig_utils import signing

    data = {
        'types': {
            'EIP712Domain': [
                { 'name': 'name', 'type': 'string' },
                { 'name': 'version', 'type': 'string' },
                { 'name': 'chainId', 'type': 'uint256' },
                { 'name': 'verifyingContract', 'type': 'address' },
            ],
            'Person': [
                { 'name': 'name', 'type': 'string' },
                { 'name': 'wallet', 'type': 'address' }
            ],
            'Mail': [
                { 'name': 'from', 'type': 'Person' },
                { 'name': 'to', 'type': 'Person' },
                { 'name': 'contents', 'type': 'string' }
            ]
        },
        'primaryType': 'Mail',
        'domain': {
            'name': 'Ether Mail',
            'version': '1',
            'chainId': 1,
            'verifyingContract': '0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC',
        },
        'message': {
            'from': {
                'name': 'Cow',
                'wallet': '0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826',
            },
            'to': {
                'name': 'Bob',
                'wallet': '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB',
            },
            'contents': 'Hello, Bob!',
        },
    }

    # generate a new raw random private key
    pkey_raw = os.urandom(32)

    # make a private key object from the raw private key bytes
    pkey = eth_keys.keys.PrivateKey(pkey_raw)

    # make a private account from the private key
    acct = Account.privateKeyToAccount(pkey)

    # get the public key of the account
    addr = pkey.public_key.to_canonical_address()

    # get the canonical address of the account
    caddr = web3.Web3.toChecksumAddress(addr)

    signature = signing.v_r_s_to_signature(*signing.sign_typed_data(data, pkey_raw))
    assert len(signature) == 32 + 32 + 1
    print('Ok, signed typed data using {}'.format(caddr))

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
        print('connected to network {} at provider "{}"'.format(w3.version.network, args.gateway or 'auto'))

    # set new provider on XBR library
    xbr.setProvider(w3)

    # now enter main ..
    main(w3.eth.accounts)
