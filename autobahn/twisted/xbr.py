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

try:
    from autobahn import xbr
    HAS_XBR = True
except ImportError:
    HAS_XBR = False


if HAS_XBR:
    import txaio
    txaio.use_twisted()
    from twisted.internet.threads import deferToThread
    from twisted.internet.task import LoopingCall
    from twisted.internet.defer import ensureDeferred

    import uuid

    from autobahn.xbr._util import hl
    from autobahn.xbr._interfaces import IProvider, ISeller, IConsumer, IBuyer

    class SimpleBlockchain(xbr.SimpleBlockchain):
        backgroundCaller = deferToThread

    class KeySeries(xbr.KeySeries):
        log = txaio.make_logger()

        def __init__(self, api_id, price, interval, on_rotate=None):
            super().__init__(api_id, price, interval, on_rotate)
            self.running = False
            self._run_loop = None
            self._started = None

        async def start(self):
            """
            Start offering and selling data encryption keys in the background.
            """
            assert self._run_loop is None

            self.log.info('Starting key rotation every {interval} seconds for api_id="{api_id}" ..',
                          interval=hl(self._interval), api_id=hl(uuid.UUID(bytes=self._api_id)))

            self.running = True

            self._run_loop = LoopingCall(lambda: ensureDeferred(self._rotate()))
            self._started = self._run_loop.start(self._interval)

            return self._started

        def stop(self):
            """
            Stop offering/selling data encryption keys.
            """
            if not self._run_loop:
                raise RuntimeError('cannot stop {} - not currently running'.format(self.__class__.__name__))

            self._run_loop.stop()
            self._run_loop = None

            return self._started

    class SimpleSeller(xbr.SimpleSeller):
        """
        Simple XBR seller component. This component can be used by a XBR seller delegate to
        handle the automated selling of data encryption keys to the XBR market maker.
        """
        xbr.SimpleSeller.KeySeries = KeySeries

    class SimpleBuyer(xbr.SimpleBuyer):
        pass

    ISeller.register(SimpleSeller)
    IProvider.register(SimpleSeller)
    IBuyer.register(SimpleBuyer)
    IConsumer.register(SimpleBuyer)
