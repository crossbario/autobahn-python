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

from flask import Flask
from crochet import setup, run_in_reactor, wait_for

# this MUST be called _before_ any Autobahn or Twisted imports!
setup()

from autobahn.twisted.wamp import Application  # noqa


# our WAMP app
#
wapp = Application()

# this is a synchronous wrapper around the asynchronous WAMP code
#


@wait_for(timeout=1)
def publish(topic, *args, **kwargs):
    return wapp.session.publish(topic, *args, **kwargs)


# our Flask app
#
app = Flask(__name__)
app._visits = 0


@app.route("/")
def index():
    app._visits += 1
    publish("com.example.on_visit", app._visits, msg="hello from flask")
    return "Visit {}".format(app._visits)


if __name__ == "__main__":
    import sys
    import logging

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    # this will start the WAMP app on a background thread and setup communication
    # with the main thread that runs a (blocking) Flask server
    #
    @run_in_reactor
    def start_wamp():
        wapp.run("ws://127.0.0.1:8080/ws", "realm1", start_reactor=False)

    start_wamp()

    # now start the Flask dev server (which is a regular blocking WSGI server)
    #
    app.run(port=8050)
