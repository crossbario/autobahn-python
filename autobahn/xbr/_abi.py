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
import pkg_resources

os.environ['ETH_HASH_BACKEND'] = 'pycryptodome'

import web3


# from eth_hash.backends.pycryptodome import keccak256  # noqa
# print('Using eth_hash backend {}'.format(keccak256))


XBR_TOKEN_FN = pkg_resources.resource_filename('autobahn', 'xbr/contracts/XBRToken.json')
XBR_NETWORK_FN = pkg_resources.resource_filename('autobahn', 'xbr/contracts/XBRNetwork.json')
XBR_CHANNEL_FN = pkg_resources.resource_filename('autobahn', 'xbr/contracts/XBRChannel.json')


if 'XBR_DEBUG_TOKEN_ADDR' in os.environ:
    XBR_DEBUG_TOKEN_ADDR = web3.Web3.toChecksumAddress(os.environ['XBR_DEBUG_TOKEN_ADDR'])
else:
    XBR_DEBUG_TOKEN_ADDR = '0x0'
    print('WARNING: The XBR smart contracts are not yet deployed to public networks. Please set XBR_DEBUG_TOKEN_ADDR manually.')

if 'XBR_DEBUG_NETWORK_ADDR' in os.environ:
    XBR_DEBUG_NETWORK_ADDR = web3.Web3.toChecksumAddress(os.environ['XBR_DEBUG_NETWORK_ADDR'])
else:
    XBR_DEBUG_NETWORK_ADDR = '0x0'
    print('WARNING: The XBR smart contracts are not yet deployed to public networks. Please set XBR_DEBUG_NETWORK_ADDR manually.')


def _load_json(contract_name):
    fn = pkg_resources.resource_filename('autobahn', 'xbr/contracts/{}.json'.format(contract_name))
    # fn = os.path.join(os.path.dirname(__file__), '../build/contracts/{}.json'.format(contract_name))
    with open(fn) as f:
        data = json.loads(f.read())
    return data


XBR_TOKEN_ABI = _load_json('XBRToken')['abi']
XBR_NETWORK_ABI = _load_json('XBRNetwork')['abi']
XBR_CHANNEL_ABI = _load_json('XBRChannel')['abi']
