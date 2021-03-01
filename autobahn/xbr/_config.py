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

    def __init__(self,
                 path=None,
                 name=None,
                 ethkey=None,
                 cskey=None,
                 username=None,
                 email=None,
                 network_url=None,
                 network_realm=None,
                 market_url=None,
                 market_realm=None,
                 infura_url=None,
                 infura_network=None,
                 infura_key=None,
                 infura_secret=None):
        from txaio import make_logger
        self.log = make_logger()
        self.path = path
        self.name = name
        self.ethkey = ethkey
        self.cskey = cskey
        self.username = username
        self.email = email
        self.network_url = network_url
        self.network_realm = network_realm
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
        username = None
        email = None
        network_url = None
        network_realm = None
        market_url = None
        market_realm = None
        infura_network = None
        infura_key = None
        infura_secret = None
        infura_url = None
        for k, v in items:
            if k == 'network_url':
                network_url = str(v)
            elif k == 'network_realm':
                network_realm = str(v)
            elif k == 'market_url':
                market_url = str(v)
            elif k == 'market_realm':
                market_realm = str(v)
            elif k == 'ethkey':
                ethkey = binascii.a2b_hex(v[2:])
            elif k == 'cskey':
                cskey = binascii.a2b_hex(v[2:])
            elif k == 'username':
                username = str(v)
            elif k == 'email':
                email = str(v)
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
                print('unprocessed config attribute "{}"'.format(k))

        return Profile(path, name, ethkey, cskey, username, email, network_url, network_realm, market_url, market_realm,
                       infura_url, infura_network, infura_key, infura_secret)


class UserConfig(object):

    def __init__(self, config_path):
        from txaio import make_logger
        self.log = make_logger()

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


def prompt_for_wamp_url(msg, default=None):
    """
    Prompt user for WAMP transport URL (eg "wss://planet.xbr.network/ws").
    """
    value = click.prompt(msg, type=WampUrl(), default=default)
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
            if value[:2] in ['0x', '\\x']:
                key = binascii.a2b_hex(value[2:])
            else:
                key = binascii.a2b_hex(value)
            if len(key) != self._key_len:
                raise ValueError('key length must be {} bytes, but was {} bytes'.format(self._key_len, len(key)))
        except Exception as e:
            self.fail(style_error(str(e)))
        else:
            return value


def prompt_for_key(msg, key_len, default=None):
    """
    Prompt user for a binary key of given length (in HEX).
    """
    value = click.prompt(msg, type=PrivateKey(key_len), default=default)
    return value


# default configuration stored in $HOME/.xbrnetwork/config.ini
_DEFAULT_CONFIG = """[default]
# username used with this profile
username={username}

# user email used with the profile (e.g. for verification emails)
email={email}

# XBR network node used as a directory server and gateway to XBR smart contracts
network_url={network_url}

# WAMP realm on network node, usually "xbrnetwork"
network_realm={network_realm}

# user private WAMP-cryptosign key (for client authentication)
cskey={cskey}

# user private Ethereum key (for signing transactions and e2e data encryption)
ethkey={ethkey}
"""

# # default XBR market URL to connect to
# market_url={market_url}
# market_realm={market_realm}
# # Infura blockchain gateway configuration
# infura_url={infura_url}
# infura_network={infura_network}
# infura_key={infura_key}
# infura_secret={infura_secret}


def load_or_create_profile(dotdir=None, profile=None, default_url=None, default_realm=None, default_email=None, default_username=None):
    dotdir = dotdir or '~/.xbrnetwork'
    profile = profile or 'default'
    default_url = default_url or 'wss://planet.xbr.network/ws'
    default_realm = default_realm or 'xbrnetwork'

    config_dir = os.path.expanduser(dotdir)
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
        click.echo('created new local user directory {}'.format(style_ok(config_dir)))

    config_path = os.path.join(config_dir, 'config.ini')
    if not os.path.isfile(config_path):
        click.echo('creating new user profile "{}"'.format(style_ok(profile)))
        with open(config_path, 'w') as f:
            network_url = prompt_for_wamp_url('enter the WAMP router URL of the network directory node', default=default_url)
            network_realm = click.prompt('enter the WAMP realm to join on the network directory node', type=str, default=default_realm)
            cskey = prompt_for_key('your private WAMP client key', 32, default='0x' + binascii.b2a_hex(os.urandom(32)).decode())
            ethkey = prompt_for_key('your private Etherum key', 32, default='0x' + binascii.b2a_hex(os.urandom(32)).decode())
            email = click.prompt('user email used for with profile', type=str, default=default_email)
            username = click.prompt('user name used with this profile', type=str, default=default_username)
            f.write(_DEFAULT_CONFIG.format(network_url=network_url, network_realm=network_realm, ethkey=ethkey,
                                           cskey=cskey, email=email, username=username))
            click.echo('created new local user configuration {}'.format(style_ok(config_path)))

    config_obj = UserConfig(config_path)
    profile_obj = config_obj.profiles.get(profile, None)

    if not profile_obj:
        raise click.ClickException('no such profile: "{}"'.format(profile))

    return profile_obj
