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

from __future__ import absolute_import

from autobahn.xbr._abi import XBR_TOKEN_ABI, XBR_NETWORK_ABI, XBR_PAYMENT_CHANNEL_ABI
from autobahn.xbr._abi import XBR_DEBUG_TOKEN_ADDR, XBR_DEBUG_NETWORK_ADDR
from autobahn.xbr._buyer import SimpleBuyer
from autobahn.xbr._seller import SimpleSeller
from autobahn.xbr._interfaces import IMarketMaker, IProvider, IConsumer, ISeller, IBuyer


xbrtoken = None
"""
Contract instance of the token used in the XBR Network.
"""

xbrnetwork = None
"""
Contract instance of the XBR Network.
"""


def setProvider(_w3):
    """
    The XBR library must be initialized (once) first by setting the Web3 provider
    using this function.
    """
    global xbrtoken
    global xbrnetwork
    xbrtoken = _w3.eth.contract(address=XBR_DEBUG_TOKEN_ADDR, abi=XBR_TOKEN_ABI)
    xbrnetwork = _w3.eth.contract(address=XBR_DEBUG_NETWORK_ADDR, abi=XBR_NETWORK_ABI)


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
    'setProvider',

    'xbrtoken',
    'xbrnetwork',

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
