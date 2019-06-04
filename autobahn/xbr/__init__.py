###############################################################################
#
# Copyright (c) Crossbar.io Technologies GmbH and contributors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.
#
###############################################################################

from __future__ import absolute_import

from xbr._version import __version__
from xbr._abi import XBR_TOKEN_ABI, XBR_NETWORK_ABI, XBR_PAYMENT_CHANNEL_ABI
from xbr._abi import XBR_DEBUG_TOKEN_ADDR, XBR_DEBUG_NETWORK_ADDR
from xbr._buyer import SimpleBuyer
from xbr._seller import SimpleSeller
from xbr._interfaces import IMarketMaker, IProvider, IConsumer, ISeller, IBuyer


version = __version__
"""
XBR library version.
"""

xbrToken = None
"""
Contract instance of the token used in the XBR Network.
"""

xbrNetwork = None
"""
Contract instance of the XBR Network.
"""


def setProvider(_w3):
    """
    The XBR library must be initialized (once) first by setting the Web3 provider
    using this function.
    """
    global xbrToken
    global xbrNetwork
    xbrToken = _w3.eth.contract(address=XBR_DEBUG_TOKEN_ADDR, abi=XBR_TOKEN_ABI)
    xbrNetwork = _w3.eth.contract(address=XBR_DEBUG_NETWORK_ADDR, abi=XBR_NETWORK_ABI)


class MemberLevel(object):
    """
    XBR Network member levels.
    """
    NONE = 0
    ACTIVE = 1
    VERIFIED = 2
    RETIRED = 3
    PENALTY = 4
    BLOCKED = 5


class NodeType(object):
    """
    XBR Cloud node types.
    """
    NONE = 0
    MASTER = 1
    CORE = 2
    EDGE = 3


class ActorType(object):
    """
    XBR Market actor types.
    """
    NONE = 0
    NETWORK = 1
    MARKET = 2
    PROVIDER = 3
    CONSUMER = 4


ASCII_BOMB = r"""
          _ ._  _ , _ ._
        (_ ' ( `  )_  .__)
      ( (  (    )   `)  ) _)
     (__ (_   (_ . _) _) ,__)
         `~~`\ ' . /`~~`
              ;   ;
              /   \
_____________/_ __ \_____________

"""


__all__ = (
    'version',
    'setProvider',

    'xbrToken',
    'xbrNetwork',

    'MemberLevel',
    'ActorType',
    'NodeType',

    'XBR_TOKEN_ABI',
    'XBR_NETWORK_ABI',
    'XBR_PAYMENT_CHANNEL_ABI',
    'ASCII_BOMB',

    'IMarketMaker',
    'IProvider',
    'IConsumer',
    'ISeller',
    'IBuyer',

    'SimpleBuyer',
    'SimpleSeller',
)
