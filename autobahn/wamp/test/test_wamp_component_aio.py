###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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
import unittest.mock as mock
import pytest
import txaio

if os.environ.get('USE_ASYNCIO', False):
    from autobahn.asyncio.component import Component

    @pytest.mark.skipif(sys.version_info < (3, 5), reason="requires Python 3.5+")
    @pytest.mark.asyncio(forbid_global_loop=True)
    def test_asyncio_component(event_loop):
        orig_loop = txaio.config.loop
        txaio.config.loop = event_loop

        comp = Component(
            transports=[
                {
                    "url": "ws://localhost:12/bogus",
                    "max_retries": 1,
                    "max_retry_delay": 0.1,
                }
            ]
        )

        # if having trouble, try starting some logging (and use
        # "py.test -s" to get real-time output)
        # txaio.start_logging(level="debug")
        f = comp.start(loop=event_loop)
        txaio.config.loop = event_loop
        finished = txaio.create_future()

        def fail():
            finished.set_exception(AssertionError("timed out"))
            txaio.config.loop = orig_loop
        txaio.call_later(4.0, fail)

        def done(f):
            try:
                f.result()
                finished.set_exception(AssertionError("should get an error"))
            except RuntimeError as e:
                if 'Exhausted all transport connect attempts' not in str(e):
                    finished.set_exception(AssertionError("wrong exception caught"))
            finished.set_result(None)
            txaio.config.loop = orig_loop
            assert comp._done_f is None
        f.add_done_callback(done)
        return finished

    @pytest.mark.skipif(sys.version_info < (3, 5), reason="requires Python 3.5+")
    @pytest.mark.asyncio(forbid_global_loop=True)
    def test_asyncio_component_404(event_loop):
        """
        If something connects but then gets aborted, it should still try
        to re-connect (in real cases this could be e.g. wrong path,
        TLS failure, WebSocket handshake failure, etc)
        """
        orig_loop = txaio.config.loop
        txaio.config.loop = event_loop

        class FakeTransport(object):
            def close(self):
                pass

            def write(self, data):
                pass

        fake_transport = FakeTransport()
        actual_protocol = [None]  # set in a closure below

        def create_connection(protocol_factory=None, server_hostname=None, host=None, port=None, ssl=False):
            if actual_protocol[0] is None:
                protocol = protocol_factory()
                actual_protocol[0] = protocol
                protocol.connection_made(fake_transport)
                return txaio.create_future_success((fake_transport, protocol))
            else:
                return txaio.create_future_error(RuntimeError("second connection fails completely"))

        with mock.patch.object(event_loop, 'create_connection', create_connection):
            event_loop.create_connection = create_connection

            comp = Component(
                transports=[
                    {
                        "url": "ws://localhost:12/bogus",
                        "max_retries": 1,
                        "max_retry_delay": 0.1,
                    }
                ]
            )

            # if having trouble, try starting some logging (and use
            # "py.test -s" to get real-time output)
            # txaio.start_logging(level="debug")
            f = comp.start(loop=event_loop)
            txaio.config.loop = event_loop

            # now that we've started connecting, we *should* be able
            # to connetion_lost our transport .. but we do a
            # call-later to ensure we're after the setup stuff in the
            # event-loop (because asyncio doesn't synchronously
            # process already-completed Futures like Twisted does)

            def nuke_transport():
                if actual_protocol[0] is not None:
                    actual_protocol[0].connection_lost(None)  # asyncio can call this with None
            txaio.call_later(0.1, nuke_transport)

            finished = txaio.create_future()

            def fail():
                finished.set_exception(AssertionError("timed out"))
                txaio.config.loop = orig_loop
            txaio.call_later(1.0, fail)

            def done(f):
                try:
                    f.result()
                    finished.set_exception(AssertionError("should get an error"))
                except RuntimeError as e:
                    if 'Exhausted all transport connect attempts' not in str(e):
                        finished.set_exception(AssertionError("wrong exception caught"))
                finished.set_result(None)
                txaio.config.loop = orig_loop
            f.add_done_callback(done)
            return finished
