###############################################################################
##
# Copyright (C) 2012-2013 Tavendo GmbH
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

import uuid
import sys

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from flask import Flask, render_template

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource, \
    WSGIRootResource, \
    HTTPChannelHixie76Aware


##
# Our WebSocket Server protocol
##
class EchoServerProtocol(WebSocketServerProtocol):

    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)


##
# Our WSGI application .. in this case Flask based
##
app = Flask(__name__)
app.secret_key = str(uuid.uuid4())


@app.route('/')
def page_home():
    return render_template('index.html')


if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    app.debug = debug
    if debug:
        log.startLogging(sys.stdout)

    ##
    # create a Twisted Web resource for our WebSocket server
    ##
    wsFactory = WebSocketServerFactory("ws://localhost:8080",
                                       debug=debug,
                                       debugCodePaths=debug)

    wsFactory.protocol = EchoServerProtocol
    wsFactory.setProtocolOptions(allowHixie76=True)  # needed if Hixie76 is to be supported

    wsResource = WebSocketResource(wsFactory)

    ##
    # create a Twisted Web WSGI resource for our Flask server
    ##
    wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), app)

    ##
    # create a root resource serving everything via WSGI/Flask, but
    # the path "/ws" served by our WebSocket stuff
    ##
    rootResource = WSGIRootResource(wsgiResource, {'ws': wsResource})

    ##
    # create a Twisted Web Site and run everything
    ##
    site = Site(rootResource)
    site.protocol = HTTPChannelHixie76Aware  # needed if Hixie76 is to be supported

    reactor.listenTCP(8080, site)
    reactor.run()
