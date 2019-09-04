import sys
import argparse

import web3

from autobahn import xbr

from test_accounts import hl


def main (accounts):
    print('\nTest accounts:')
    for acct in accounts:
        balance_eth = w3.eth.getBalance(acct)
        balance_xbr = xbr.xbrtoken.functions.balanceOf(acct).call()
        print('    balances of {}: {:>30} ETH, {:>30} XBR'.format(hl(acct), balance_eth, balance_xbr))

    print('\nXBR contracts:')
    for acct in [xbr.xbrtoken.address, xbr.xbrnetwork.address]:
        balance_eth = w3.eth.getBalance(acct)
        balance_xbr = xbr.xbrtoken.functions.balanceOf(acct).call()
        print('    balances of {}: {:>30} ETH, {:>30} XBR'.format(hl(acct), balance_eth, balance_xbr))

    print()


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
        print('could not connect to Web3/Ethereum at: {}'.format(args.gateway or 'auto'))
        sys.exit(1)
    else:
        print('connected via provider "{}"'.format(args.gateway or 'auto'))

    # set new provider on XBR library
    xbr.setProvider(w3)

    # now enter main ..
    main(w3.eth.accounts)
