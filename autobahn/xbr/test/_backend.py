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

from typing import Optional

from twisted.internet.task import LoopingCall
from twisted.internet.defer import inlineCallbacks

from autobahn.util import hltype, hlval
from autobahn.wamp import register
from autobahn.wamp.types import CallDetails, PublishOptions, SessionDetails, CloseDetails, RegisterOptions
from autobahn.twisted.wamp import ApplicationSession


class Backend(ApplicationSession):
    def __init__(self, config):
        super().__init__(config)
        self._counter = 0
        self._last_msg = 'Hello, world'
        self._background_loop = LoopingCall(self._run_in_background)

    @inlineCallbacks
    def onJoin(self, details: SessionDetails):
        self.log.info('{func} session joined with details {details}',
                      func=hltype(self.onJoin), details=details)

        regs = yield self.register(self, options=RegisterOptions(details=True))
        for reg in regs:
            self.log.info('{func} registered procedure with {reg}', func=hltype(self.onJoin), reg=str(reg))

        self._background_loop.start(1.)
        self.log.info('{func} ready!', func=hltype(self.onJoin))

    @inlineCallbacks
    def _run_in_background(self):
        if self.is_attached():
            self._counter += 1
            pub = yield self.publish('public.topic1', self._last_msg, self._counter,
                                     options=PublishOptions(acknowledge=True))
            if self._counter % 10 == 0:
                self.log.info('{func} published event with {pub}', func=hltype(self._run_in_background), pub=str(pub))

    def onLeave(self, details: CloseDetails):
        self._background_loop.stop()
        self.log.info('{func} session closed with details {details}',
                      func=hltype(self.onClose), details=details)

    @register('public.echo', check_types=True)
    def echo(self, msg: str, details: Optional[CallDetails] = None):
        self.log.info('{func} called with msg="{msg}", details={details}',
                      msg=hlval(msg), details=details, func=hltype(self.echo))
        self._last_msg = msg
        return msg

    @register('user.add2', check_types=True)
    def add2(self, x: int, y: int, details: Optional[CallDetails] = None):
        self.log.info('{func} called with x={x}, y={y}, details={details}',
                      x=hlval(x), y=hlval(y), details=details, func=hltype(self.add2))
        return x + y
