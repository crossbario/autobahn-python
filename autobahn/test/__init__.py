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

from __future__ import absolute_import, print_function


class FakeTransport(object):
    _written = b""
    _open = True

    def __init__(self):
        self._abort_calls = []

    def abortConnection(self, *args, **kw):
        self._abort_calls.append((args, kw))

    def write(self, msg):
        if not self._open:
            raise Exception("Can't write to a closed connection")
        self._written = self._written + msg

    def loseConnection(self):
        self._open = False

    def registerProducer(self, producer, streaming):
        # https://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IConsumer.html
        raise NotImplementedError

    def unregisterProducer(self):
        # do nothing is correct! until we fake implement registerProducer ..;)
        pass

    def getPeer(self):
        # for Twisted, this would be an IAddress
        class _FakePeer(object):
            pass
        return _FakePeer()

    def getHost(self):
        # for Twisted, this would be an IAddress
        class _FakeHost(object):
            pass
        return _FakeHost()

    def abort_called(self):
        return len(self._abort_calls) > 0
