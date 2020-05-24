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
import sys
import binascii
import configparser

import click
import web3
from eth_utils.conversions import hexstr_if_str, to_hex

from txaio import make_logger
from autobahn.websocket.util import parse_url
from autobahn.xbr._util import hlval, hltype


_HAS_COLOR_TERM = False
try:
    import colorama

    # https://github.com/tartley/colorama/issues/48
    term = None
    if sys.platform == 'win32' and 'TERM' in os.environ:
        term = os.environ.pop('TERM')

    colorama.init()
    _HAS_COLOR_TERM = True

    if term:
        os.environ['TERM'] = term

except ImportError:
    pass


class Profile(object):

    log = make_logger()

    def __init__(self,
                 path=None,
                 name=None,
                 ethkey=None,
                 cskey=None,
                 market_url=None,
                 market_realm=None,
                 infura_url=None,
                 infura_network=None,
                 infura_key=None,
                 infura_secret=None):
        self.path = path
        self.name = name
        self.ethkey = ethkey
        self.cskey = cskey
        self.market_url = market_url
        self.market_realm = market_realm
        self.infura_url = infura_url
        self.infura_network = infura_network
        self.infura_key = infura_key
        self.infura_secret = infura_secret

    @staticmethod
    def parse(path, name, items):
        ethkey = None
        cskey = None
        market_url = None
        market_realm = None
        infura_network = None
        infura_key = None
        infura_secret = None
        infura_url = None
        for k, v in items:
            if k == 'market_url':
                market_url = str(v)
            elif k == 'market_realm':
                market_realm = str(v)
            elif k == 'ethkey':
                ethkey = binascii.a2b_hex(v[2:])
            elif k == 'cskey':
                cskey = binascii.a2b_hex(v[2:])
            elif k == 'infura_network':
                infura_network = str(v)
            elif k == 'infura_key':
                infura_key = str(v)
            elif k == 'infura_secret':
                infura_secret = str(v)
            elif k == 'infura_url':
                infura_url = str(v)
            else:
                # skip unknown attribute
                Profile.log.warn('unprocessed config attribute "{}"'.format(k))

        return Profile(path, name, ethkey, cskey, market_url, market_realm, infura_url, infura_network, infura_key, infura_secret)


class UserConfig(object):

    log = make_logger()

    def __init__(self, config_path):
        self._config_path = os.path.abspath(config_path)

        config = configparser.ConfigParser()
        config.read(config_path)

        self.config = config

        profiles = {}
        for profile_name in config.sections():
            profile = Profile.parse(config_path, profile_name, config.items(profile_name))
            profiles[profile_name] = profile

        self.profiles = profiles

        self.log.debug('profiles loaded: {profiles}',
                       func=hltype(self.__init__),
                       profiles=', '.join(hlval(x) for x in sorted(self.profiles.keys())))


if 'CROSSBAR_FABRIC_URL' in os.environ:
    _DEFAULT_CFC_URL = os.environ['CROSSBAR_FABRIC_URL']
else:
    _DEFAULT_CFC_URL = u'wss://master.xbr.network/ws'


def style_error(text):
    if _HAS_COLOR_TERM:
        return click.style(text, fg='red', bold=True)
    else:
        return text


def style_ok(text):
    if _HAS_COLOR_TERM:
        return click.style(text, fg='green', bold=True)
    else:
        return text


class WampUrl(click.ParamType):
    """
    WAMP transport URL validator.
    """

    name = 'WAMP transport URL'

    def __init__(self):
        click.ParamType.__init__(self)

    def convert(self, value, param, ctx):
        try:
            parse_url(value)
        except Exception as e:
            self.fail(style_error(str(e)))
        else:
            return value


def prompt_for_wamp_url(msg):
    """
    Prompt user for WAMP transport URL (eg "wss://planet.xbr.network/ws").
    """
    value = click.prompt(msg, type=WampUrl())
    return value


class EthereumAddress(click.ParamType):
    """
    Ethereum address validator.
    """

    name = 'Ethereum address'

    def __init__(self):
        click.ParamType.__init__(self)

    def convert(self, value, param, ctx):
        try:
            value = web3.Web3.toChecksumAddress(value)
            adr = binascii.a2b_hex(value[2:])
            if len(value) != 20:
                raise ValueError('Ethereum addres must be 20 bytes (160 bit), but was {} bytes'.format(len(adr)))
        except Exception as e:
            self.fail(style_error(str(e)))
        else:
            return value


def prompt_for_ethereum_address(msg):
    """
    Prompt user for an Ethereum (public) address.
    """
    value = click.prompt(msg, type=EthereumAddress())
    return value


class PrivateKey(click.ParamType):
    """
    Private key (32 bytes in HEX) validator.
    """

    name = 'Private key'

    def __init__(self, key_len):
        click.ParamType.__init__(self)
        self._key_len = key_len

    def convert(self, value, param, ctx):
        try:
            value = hexstr_if_str(to_hex, value)
            key = binascii.a2b_hex(value[2:])
            if len(key) != self._key_len:
                raise ValueError('key length must be {} bytes, but was {} bytes'.format(self._key_len, len(key)))
        except Exception as e:
            self.fail(style_error(str(e)))
        else:
            return value


def prompt_for_key(msg, key_len):
    """
    Prompt user for a binary key of given length (in HEX).
    """
    value = click.prompt(msg, type=PrivateKey(key_len))
    return value


# default configuration stored in $HOME/.xbrnetwork/config.ini
_DEFAULT_CONFIG = """[default]

# user private Ethereum key
ethkey={ethkey}

# user private WAMP client key
cskey={cskey}

# default XBR market URL to connect to
market_url={market_url}

# Infura blockchain gateway configuration
infura_url={infura_url}
infura_network={infura_network}
infura_key={infura_key}
infura_secret={infura_secret}
"""


def load_or_create_profile(dotdir=None, profile=None):
    dotdir = dotdir or '~/.xbrnetwork'
    profile = profile or 'default'

    config_dir = os.path.expanduser(dotdir)
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
        click.echo('created new local user directory {}'.format(style_ok(config_dir)))

    config_path = os.path.join(config_dir, 'config.ini')
    if not os.path.isfile(config_path):
        click.echo('creating new user profile "{}"'.format(style_ok(profile)))
        with open(config_path, 'w') as f:
            market_url = prompt_for_wamp_url('enter a XBR data market URL')
            market_realm = click.prompt('enter the WAMP realm of the XBR data market', type=str)
            ethkey = prompt_for_key('your private Etherum key', 32)
            cskey = prompt_for_key('your private WAMP client key', 32)
            infura_network = click.prompt('enter Ethereum network to use', type=str, default='rinkeby')
            infura_url = click.prompt('enter Infura gateway URL', type=str)
            infura_key = click.prompt('your Infura gateway key', type=str)
            infura_secret = click.prompt('your Infura gateway secret', type=str)
            f.write(_DEFAULT_CONFIG.format(market_url=market_url, market_realm=market_realm, ethkey=ethkey,
                                           cskey=cskey, infura_url=infura_url, infura_network=infura_network,
                                           infura_key=infura_key, infura_secret=infura_secret))
            click.echo('created new local user configuration {}'.format(style_ok(config_path)))

    config_obj = UserConfig(config_path)
    profile_obj = config_obj.profiles.get(profile, None)

    if not profile_obj:
        raise click.ClickException('no such profile: "{}"'.format(profile))

    return profile_obj
