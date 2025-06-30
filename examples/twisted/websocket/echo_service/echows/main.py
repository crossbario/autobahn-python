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

import twisted
from twisted.python import log, usage
from twisted.application.service import MultiService

from echoservice import EchoService


class AppService(MultiService):
    """
    Our application service hierarchy.
    """

    def startService(self):
        # create WebSocket echo service and make it a child of our app service
        svc = EchoService(self.port)
        svc.setName("EchoService")
        svc.setServiceParent(self)

        MultiService.startService(self)


class Options(usage.Options):
    optParameters = [
        [
            "port",
            "p",
            8080,
            "Listening port (for both Web and WebSocket) - default 8080.",
        ]
    ]


def makeService(options):
    """
    This will be called from twistd plugin system and we are supposed to
    create and return our application service.
    """

    # create application service and forward command line options ..
    service = AppService()
    service.port = int(options["port"])

    return service
