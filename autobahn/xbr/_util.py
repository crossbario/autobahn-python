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

import inspect

import click
import web3


def make_w3(gateway_config=None):
    """
    Create a Web3 instance configured and ready-to-use gateway to the blockchain.

    :param gateway_config: Blockchain gateway configuration.
    :type gateway_config: dict

    :return: Configured Web3 instance.
    :rtype: :class:`web3.Web3`
    """
    if gateway_config is None or gateway_config['type'] == 'auto':
        w3 = web3.Web3()

    elif gateway_config['type'] == 'user':
        request_kwargs = gateway_config.get('http_options', {})
        w3 = web3.Web3(web3.Web3.HTTPProvider(gateway_config['http'], request_kwargs=request_kwargs))

    elif gateway_config['type'] == 'infura':
        request_kwargs = gateway_config.get('http_options', {})
        project_id = gateway_config['key']
        # project_secret = gateway_config['secret']

        http_url = 'https://{}.infura.io/v3/{}'.format(gateway_config['network'], project_id)
        w3 = web3.Web3(web3.Web3.HTTPProvider(http_url, request_kwargs=request_kwargs))

        # https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority
        if gateway_config.get('network', None) == 'rinkeby':
            # This middleware is required to connect to geth --dev or the Rinkeby public network.
            from web3.middleware import geth_poa_middleware

            # inject the poa compatibility middleware to the innermost layer
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    else:
        raise RuntimeError('invalid blockchain gateway type "{}"'.format(gateway_config['type']))

    return w3


def unpack_uint128(data):
    assert data is None or type(data) == bytes, 'data must by bytes, was {}'.format(type(data))
    if data and type(data) == bytes:
        assert len(data) == 16, 'data must be bytes[16], but was bytes[{}]'.format(len(data))

    if data:
        return web3.Web3.toInt(data)
    else:
        return 0


def pack_uint128(value):
    assert value is None or (type(value) == int and value >= 0 and value < 2**128)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (16 - len(data)) + data
    else:
        return b'\x00' * 16


def unpack_uint256(data):
    assert data is None or type(data) == bytes, 'data must by bytes, was {}'.format(type(data))
    if data and type(data) == bytes:
        assert len(data) == 32, 'data must be bytes[32], but was bytes[{}]'.format(len(data))

    if data:
        return int(web3.Web3.toInt(data))
    else:
        return 0


def pack_uint256(value):
    assert value is None or (type(value) == int and value >= 0 and value < 2**256), 'value must be uint256, but was {}'.format(value)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (32 - len(data)) + data
    else:
        return b'\x00' * 32


def hl(text, bold=False, color='yellow'):
    if not isinstance(text, str):
        text = '{}'.format(text)
    return click.style(text, fg=color, bold=bold)


def _qn(obj):
    if inspect.isclass(obj) or inspect.isfunction(obj) or inspect.ismethod(obj):
        qn = '{}.{}'.format(obj.__module__, obj.__qualname__)
    else:
        qn = 'unknown'
    return qn


def hltype(obj):
    qn = _qn(obj).split('.')
    text = hl(qn[0], color='yellow', bold=True) + hl('.' + '.'.join(qn[1:]), color='yellow', bold=False)
    return '<' + text + '>'


def hlid(oid):
    return hl('{}'.format(oid), color='blue', bold=True)


def hluserid(oid):
    if not isinstance(oid, str):
        oid = '{}'.format(oid)
    return hl('"{}"'.format(oid), color='yellow', bold=True)


def hlval(val, color='green'):
    return hl('{}'.format(val), color=color, bold=True)


def hlcontract(oid):
    if not isinstance(oid, str):
        oid = '{}'.format(oid)
    return hl('<{}>'.format(oid), color='magenta', bold=True)


def with_0x(address):
    if address and not address.startswith('0x'):
        return '0x{address}'.format(address=address)
    return address


def without_0x(address):
    if address and address.startswith('0x'):
        return address[2:]
    return address
