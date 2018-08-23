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

import os
import pytest
import txaio

if os.environ.get('USE_ASYNCIO', False):
    from autobahn.asyncio.component import Component

    @pytest.mark.asyncio(forbid_global_loop=True)
    async def test_asyncio_component(event_loop):
        txaio.config.loop = event_loop

        comp = Component(
            transports=[
                {
                    u"url": u"ws://localhost:9999/bogus",
                    u"max_retries": 1,
                    u"max_retry_delay": 0.1,
                }
            ]
        )

        # if having trouble, try starting some logging (and use
        # "py.test -s" to get real-time output)
        # txaio.start_logging(level="debug")
        try:
            await comp.start(loop=event_loop)
            assert False, "should get an error"
        except RuntimeError as e:
            assert 'Exhausted all transport connect attempts' in str(e)
