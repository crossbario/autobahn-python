###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################


from flask import Flask, request
from crochet import setup, run_in_reactor, wait_for

## this MUST be called _before_ any Autobahn or Twisted imports!
setup()

from twisted.internet.defer import returnValue
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import Application


## our WAMP app
##
wapp = Application()

@wapp.register('com.example.square')
def square(x):
   print("square() called with {}".format(x))
   return x * x

@wapp.register('com.example.slowsquare')
def slowsquare(x):
   print("slowsquare() called with {}".format(x))
   yield sleep(2)
   returnValue(x * x)


## the following are synchronous wrappers around the asynchronous WAMP code
##
@wait_for(timeout = 1)
def call_square(x):
   return wapp.session.call('com.example.square', x)

@wait_for(timeout = 5)
def call_slowsquare(x):
   return wapp.session.call('com.example.slowsquare', x)



## our Flask app
##
app = Flask(__name__)

@app.route('/square/submit', methods = ['POST'])
def square_submit():
   x = int(request.form.get('x', 0))
   res = call_square(x)
   return "{} squared is {}".format(x, res)


@app.route('/slowsquare/submit', methods = ['POST'])
def slowsquare_submit():
   x = int(request.form.get('x', 0))
   res = call_slowsquare(x)
   return "{} squared is {}".format(x, res)




if __name__ == '__main__':
   import sys
   import logging
   logging.basicConfig(stream = sys.stderr, level = logging.DEBUG)

   ## this will start the WAMP app on a background thread and setup communication
   ## with the main thread that runs a (blocking) Flask server
   ##
   @run_in_reactor
   def start_wamp():
      wapp.run("ws://localhost:9000", "realm1", standalone = True, start_reactor = False)

   start_wamp()

   ## now start the Flask dev server (which is a regular blocking WSGI server)
   ##
   app.run(port = 8080)
