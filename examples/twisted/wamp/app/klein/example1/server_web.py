###############################################################################
##
# Copyright (C) 2014 Tavendo GmbH
##
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
##
# http://www.apache.org/licenses/LICENSE-2.0
##
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##
###############################################################################

from twisted.internet.defer import inlineCallbacks, returnValue
from klein import Klein
from autobahn.twisted.wamp import Application

app = Klein()
wampapp = Application()


@app.route('/square/submit', methods=['POST'])
@inlineCallbacks
def square_submit(request):
    x = int(request.args.get('x', [0])[0])
    res = yield wampapp.session.call('com.example.square', x)
    returnValue("{} squared is {}".format(x, res))


if __name__ == "__main__":
    import sys
    from twisted.python import log
    from twisted.web.server import Site
    from twisted.internet import reactor
    log.startLogging(sys.stdout)

    reactor.listenTCP(8080, Site(app.resource()))
    wampapp.run("ws://localhost:9000", "realm1", standalone=False)
