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

from autobahn.util import public

import six
from six.moves import urllib
# The Python urlparse module currently does not contain the ws/wss
# schemes, so we add those dynamically (which is a hack of course).
# Since the urllib from six.moves does not seem to expose the stuff
# we monkey patch here, we do it manually.
#
# Important: if you change this stuff (you shouldn't), make sure
# _all_ our unit tests for WS URLs succeed
#
if not six.PY3:
    # Python 2
    import urlparse
else:
    # Python 3
    from urllib import parse as urlparse

wsschemes = ["ws", "wss"]
urlparse.uses_relative.extend(wsschemes)
urlparse.uses_netloc.extend(wsschemes)
urlparse.uses_params.extend(wsschemes)
urlparse.uses_query.extend(wsschemes)
urlparse.uses_fragment.extend(wsschemes)

__all__ = (
    "create_url",
    "parse_url",
)


@public
def create_url(hostname, port=None, isSecure=False, path=None, params=None):
    """
    Create a WebSocket URL from components.

    :param hostname: WebSocket server hostname (for TCP/IP sockets) or
        filesystem path (for Unix domain sockets).
    :type hostname: str

    :param port: For TCP/IP sockets, WebSocket service port or ``None`` (to select default
        ports ``80`` or ``443`` depending on ``isSecure``. When ``hostname=="unix"``,
        this defines the path to the Unix domain socket instead of a TCP/IP network socket.
    :type port: int or str

    :param isSecure: Set ``True`` for secure WebSocket (``wss`` scheme).
    :type isSecure: bool

    :param path: WebSocket URL path of addressed resource (will be
        properly URL escaped). Ignored for RawSocket.
    :type path: str

    :param params: A dictionary of key-values to construct the query
        component of the addressed WebSocket resource (will be properly URL
        escaped). Ignored for RawSocket.
    :type params: dict

    :returns: Constructed WebSocket URL.
    :rtype: str
    """
    # assert type(hostname) == six.text_type
    assert type(isSecure) == bool

    if hostname == 'unix':
        netloc = u"unix:%s" % port
    else:
        assert port is None or (type(port) in six.integer_types and port in range(0, 65535))

        if port is not None:
            netloc = u"%s:%d" % (hostname, port)
        else:
            if isSecure:
                netloc = u"%s:443" % hostname
            else:
                netloc = u"%s:80" % hostname

    if isSecure:
        scheme = u"wss"
    else:
        scheme = u"ws"

    if path is not None:
        ppath = urllib.parse.quote(path)
    else:
        ppath = u"/"

    if params is not None:
        query = urllib.parse.urlencode(params)
    else:
        query = None

    return urllib.parse.urlunparse((scheme, netloc, ppath, None, query, None))


@public
def parse_url(url):
    """
    Parses as WebSocket URL into it's components and returns a tuple:

     - ``isSecure`` is a flag which is ``True`` for ``wss`` URLs.
     - ``host`` is the hostname or IP from the URL.

    and for TCP/IP sockets:

     - ``tcp_port`` is the port from the URL or standard port derived from
       scheme (``rs`` => ``80``, ``rss`` => ``443``).

    or for Unix domain sockets:

     - ``uds_path`` is the path on the local host filesystem.

    :param url: A valid WebSocket URL, i.e. ``ws://localhost:9000`` for TCP/IP sockets or
        ``ws://unix:/tmp/file.sock`` for Unix domain sockets (UDS).
    :type url: str

    :returns: A 6-tuple ``(isSecure, host, tcp_port, resource, path, params)`` (TCP/IP) or
        ``(isSecure, host, uds_path, resource, path, params)`` (UDS).
    :rtype: tuple
    """
    parsed = urlparse.urlparse(url)

    if parsed.scheme not in ["ws", "wss"]:
        raise Exception("invalid WebSocket URL: protocol scheme '{}' is not for WebSocket".format(parsed.scheme))

    if not parsed.hostname or parsed.hostname == "":
        raise Exception("invalid WebSocket URL: missing hostname")

    if parsed.fragment is not None and parsed.fragment != "":
        raise Exception("invalid WebSocket URL: non-empty fragment '%s" % parsed.fragment)

    if parsed.path is not None and parsed.path != "":
        ppath = parsed.path
        path = urllib.parse.unquote(ppath)
    else:
        ppath = "/"
        path = ppath

    if parsed.query is not None and parsed.query != "":
        resource = ppath + "?" + parsed.query
        params = urlparse.parse_qs(parsed.query)
    else:
        resource = ppath
        params = {}

    if parsed.hostname == u"unix":
        # Unix domain sockets sockets

        # ws://unix:/tmp/file.sock => unix:/tmp/file.sock => /tmp/file.sock
        fp = parsed.netloc + parsed.path
        uds_path = fp.split(':')[1]

        # note: we don't interpret "path" in any further way: it needs to be
        # a path on the local host with a listening Unix domain sockets at the other end ..
        return parsed.scheme == "wss", parsed.hostname, uds_path, resource, path, params

    else:
        # TCP/IP sockets

        if parsed.port is None or parsed.port == "":
            if parsed.scheme == "ws":
                tcp_port = 80
            else:
                tcp_port = 443
        else:
            tcp_port = int(parsed.port)

        if tcp_port < 1 or tcp_port > 65535:
            raise Exception("invalid port {}".format(tcp_port))

        return parsed.scheme == "wss", parsed.hostname, tcp_port, resource, path, params
