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

import os
import json
import binascii
import pkg_resources

os.environ['ETH_HASH_BACKEND'] = 'pycryptodome'

# from eth_hash.backends.pycryptodome import keccak256  # noqa
# print('Using eth_hash backend {}'.format(keccak256))
import web3

XBR_TOKEN_FN = pkg_resources.resource_filename('autobahn', 'xbr/contracts/XBRToken.json')
XBR_NETWORK_FN = pkg_resources.resource_filename('autobahn', 'xbr/contracts/XBRNetwork.json')
XBR_MARKET_FN = pkg_resources.resource_filename('autobahn', 'xbr/contracts/XBRMarket.json')
XBR_CATALOG_FN = pkg_resources.resource_filename('autobahn', 'xbr/contracts/XBRCatalog.json')
XBR_CHANNEL_FN = pkg_resources.resource_filename('autobahn', 'xbr/contracts/XBRChannel.json')


if 'XBR_DEBUG_TOKEN_ADDR' in os.environ:
    _token_adr = os.environ['XBR_DEBUG_TOKEN_ADDR']
    try:
        _token_adr = binascii.a2b_hex(_token_adr[2:])
        _token_adr = web3.Web3.toChecksumAddress(_token_adr)
    except Exception as e:
        raise RuntimeError('could not parse Ethereum address for XBR_DEBUG_TOKEN_ADDR={} - {}'.format(_token_adr, e))
    XBR_DEBUG_TOKEN_ADDR = _token_adr
else:
    XBR_DEBUG_TOKEN_ADDR = '0x0000000000000000000000000000000000000000'
    print('WARNING: The XBR smart contracts are not yet deployed to public networks. Please set XBR_DEBUG_TOKEN_ADDR manually.')

if 'XBR_DEBUG_NETWORK_ADDR' in os.environ:
    _netw_adr = os.environ['XBR_DEBUG_NETWORK_ADDR']
    try:
        _netw_adr = binascii.a2b_hex(_netw_adr[2:])
        _netw_adr = web3.Web3.toChecksumAddress(_netw_adr)
    except Exception as e:
        raise RuntimeError('could not parse Ethereum address for XBR_DEBUG_NETWORK_ADDR={} - {}'.format(_netw_adr, e))
    XBR_DEBUG_NETWORK_ADDR = _netw_adr
else:
    XBR_DEBUG_NETWORK_ADDR = '0x0000000000000000000000000000000000000000'
    print('WARNING: The XBR smart contracts are not yet deployed to public networks. Please set XBR_DEBUG_NETWORK_ADDR manually.')

if 'XBR_DEBUG_MARKET_ADDR' in os.environ:
    _mrkt_adr = os.environ['XBR_DEBUG_MARKET_ADDR']
    try:
        _mrkt_adr = binascii.a2b_hex(_mrkt_adr[2:])
        _mrkt_adr = web3.Web3.toChecksumAddress(_mrkt_adr)
    except Exception as e:
        raise RuntimeError('could not parse Ethereum address for XBR_DEBUG_MARKET_ADDR={} - {}'.format(_mrkt_adr, e))
    XBR_DEBUG_MARKET_ADDR = _mrkt_adr
else:
    XBR_DEBUG_MARKET_ADDR = '0x0000000000000000000000000000000000000000'
    print('WARNING: The XBR smart contracts are not yet deployed to public networks. Please set XBR_DEBUG_MARKET_ADDR manually.')

if 'XBR_DEBUG_CATALOG_ADDR' in os.environ:
    _ctlg_adr = os.environ['XBR_DEBUG_CATALOG_ADDR']
    try:
        _ctlg_adr = binascii.a2b_hex(_ctlg_adr[2:])
        _ctlg_adr = web3.Web3.toChecksumAddress(_ctlg_adr)
    except Exception as e:
        raise RuntimeError('could not parse Ethereum address for XBR_DEBUG_CATALOG_ADDR={} - {}'.format(_ctlg_adr, e))
    XBR_DEBUG_CATALOG_ADDR = _ctlg_adr
else:
    XBR_DEBUG_CATALOG_ADDR = '0x0000000000000000000000000000000000000000'
    print('WARNING: The XBR smart contracts are not yet deployed to public networks. Please set XBR_DEBUG_CATALOG_ADDR manually.')

if 'XBR_DEBUG_CHANNEL_ADDR' in os.environ:
    _chnl_adr = os.environ['XBR_DEBUG_CHANNEL_ADDR']
    try:
        _chnl_adr = binascii.a2b_hex(_chnl_adr[2:])
        _chnl_adr = web3.Web3.toChecksumAddress(_chnl_adr)
    except Exception as e:
        raise RuntimeError('could not parse Ethereum address for XBR_DEBUG_CHANNEL_ADDR={} - {}'.format(_chnl_adr, e))
    XBR_DEBUG_CHANNEL_ADDR = _chnl_adr
else:
    XBR_DEBUG_CHANNEL_ADDR = '0x0000000000000000000000000000000000000000'
    print('WARNING: The XBR smart contracts are not yet deployed to public networks. Please set XBR_DEBUG_CHANNEL_ADDR manually.')


def _load_json(contract_name):
    fn = pkg_resources.resource_filename('autobahn', 'xbr/contracts/{}.json'.format(contract_name))
    # fn = os.path.join(os.path.dirname(__file__), '../build/contracts/{}.json'.format(contract_name))
    with open(fn) as f:
        data = json.loads(f.read())
    return data


XBR_TOKEN_ABI = _load_json('XBRToken')['abi']
XBR_NETWORK_ABI = _load_json('XBRNetwork')['abi']
XBR_MARKET_ABI = _load_json('XBRMarket')['abi']
XBR_CATALOG_ABI = _load_json('XBRCatalog')['abi']
XBR_CHANNEL_ABI = _load_json('XBRChannel')['abi']
