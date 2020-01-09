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


from autobahn.util import public

# The Python urlparse module currently does not contain the rs/rss
# schemes, so we add those dynamically (which is a hack of course).
#
# Important: if you change this stuff (you shouldn't), make sure
# _all_ our unit tests for WS URLs succeed
#
from urllib import parse as urlparse

wsschemes = ["rs", "rss"]
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
def create_url(hostname, port=None, isSecure=False):
    """
    Create a RawSocket URL from components.

    :param hostname: RawSocket server hostname (for TCP/IP sockets) or
        filesystem path (for Unix domain sockets).
    :type hostname: str

    :param port: For TCP/IP sockets, RawSocket service port or ``None`` (to select default
        ports ``80`` or ``443`` depending on ``isSecure``. When ``hostname=="unix"``,
        this defines the path to the Unix domain socket instead of a TCP/IP network socket.
    :type port: int or str

    :param isSecure: Set ``True`` for secure RawSocket (``rss`` scheme).
    :type isSecure: bool

    :returns: Constructed RawSocket URL.
    :rtype: str
    """
    # assert type(hostname) == str
    assert type(isSecure) == bool

    if hostname == 'unix':

        netloc = "unix:%s" % port
    else:
        assert port is None or (type(port) == int and port in range(0, 65535))

        if port is not None:
            netloc = "%s:%d" % (hostname, port)
        else:
            if isSecure:
                netloc = "{}:443".format(hostname)
            else:
                netloc = "{}:80".format(hostname)

    if isSecure:
        scheme = "rss"
    else:
        scheme = "rs"

    return "{}://{}".format(scheme, netloc)


@public
def parse_url(url):
    """
    Parses as RawSocket URL into it's components and returns a tuple:

     - ``isSecure`` is a flag which is ``True`` for ``rss`` URLs.
     - ``host`` is the hostname or IP from the URL.

    and for TCP/IP sockets:

     - ``tcp_port`` is the port from the URL or standard port derived from
       scheme (``rs`` => ``80``, ``rss`` => ``443``).

    or for Unix domain sockets:

     - ``uds_path`` is the path on the local host filesystem.

    :param url: A valid RawSocket URL, i.e. ``rs://localhost:9000`` for TCP/IP sockets or
        ``rs://unix:/tmp/file.sock`` for Unix domain sockets (UDS).
    :type url: str

    :returns: A 3-tuple ``(isSecure, host, tcp_port)`` (TCP/IP) or ``(isSecure, host, uds_path)`` (UDS).
    :rtype: tuple
    """
    parsed = urlparse.urlparse(url)

    if parsed.scheme not in ["rs", "rss"]:
        raise Exception("invalid RawSocket URL: protocol scheme '{}' is not for RawSocket".format(parsed.scheme))

    if not parsed.hostname or parsed.hostname == "":
        raise Exception("invalid RawSocket URL: missing hostname")

    if parsed.query is not None and parsed.query != "":
        raise Exception("invalid RawSocket URL: non-empty query '{}'".format(parsed.query))

    if parsed.fragment is not None and parsed.fragment != "":
        raise Exception("invalid RawSocket URL: non-empty fragment '{}'".format(parsed.fragment))

    if parsed.hostname == "unix":
        # Unix domain sockets sockets

        # rs://unix:/tmp/file.sock => unix:/tmp/file.sock => /tmp/file.sock
        fp = parsed.netloc + parsed.path
        uds_path = fp.split(':')[1]

        # note: we don't interpret "uds_path" in any further way: it needs to be
        # a path on the local host with a listening Unix domain sockets at the other end ..

        return parsed.scheme == "rss", parsed.hostname, uds_path

    else:
        # TCP/IP sockets

        if parsed.path is not None and parsed.path != "":
            raise Exception("invalid RawSocket URL: non-empty path '{}'".format(parsed.path))

        if parsed.port is None or parsed.port == "":
            if parsed.scheme == "rs":
                tcp_port = 80
            else:
                tcp_port = 443
        else:
            tcp_port = int(parsed.port)

        if tcp_port < 1 or tcp_port > 65535:
            raise Exception("invalid port {}".format(tcp_port))

        return parsed.scheme == "rss", parsed.hostname, tcp_port
