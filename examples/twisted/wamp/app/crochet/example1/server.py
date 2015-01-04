###############################################################################
##
##  Copyright (C) 2014-2015 Tavendo GmbH
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


from flask import Flask
from crochet import setup, run_in_reactor, wait_for

## this MUST be called _before_ any Autobahn or Twisted imports!
setup()

from autobahn.twisted.wamp import Application


## our WAMP app
##
wapp = Application()

## this is a synchronous wrapper around the asynchronous WAMP code
##
@wait_for(timeout = 1)
def publish(topic, *args, **kwargs):
   return wapp.session.publish(topic, *args, **kwargs)



## our Flask app
##
app = Flask(__name__)
app._visits = 0

@app.route('/')
def index():
   app._visits += 1
   publish('com.example.on_visit', app._visits, msg = "hello from flask")
   return "Visit {}".format(app._visits)



if __name__ == '__main__':
   import sys
   import logging
   logging.basicConfig(stream = sys.stderr, level = logging.DEBUG)

   ## this will start the WAMP app on a background thread and setup communication
   ## with the main thread that runs a (blocking) Flask server
   ##
   @run_in_reactor
   def start_wamp():
      wapp.run("ws://127.0.0.1:8080/ws", "realm1", start_reactor = False)

   start_wamp()

   ## now start the Flask dev server (which is a regular blocking WSGI server)
   ##
   app.run(port = 8050)
