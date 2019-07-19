import argparse
from binascii import a2b_hex, b2a_hex
from autobahn import xbr
from twisted.internet.task import react
from twisted.internet.defer import inlineCallbacks


@inlineCallbacks
def main(reactor, gateway, adr):
    sbc = xbr.SimpleBlockchain(gateway)
    yield sbc.start()

    balances = yield sbc.get_balances(adr)
    print('balances for 0x{}: {}'.format(b2a_hex(adr).decode(), balances))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--gateway',
                        dest='gateway',
                        type=str,
                        default=None,
                        help='Ethereum HTTP gateway URL or None for auto-select (default: -, means let web3 auto-select).')

    parser.add_argument('--adr',
                        dest='adr',
                        type=str,
                        default=None,
                        help='Ethereum address to lookup.')

    args = parser.parse_args()

    react(main, (args.gateway, a2b_hex(args.adr[2:],)))
