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


import jinja2
from klein import Klein

from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.wamp import Application



## This is our WAMP application
##
wampapp = Application('com.example')


@wampapp.register()
def square(x):
   print("square() called with {}".format(x))
   return x * x



## This is our Web application
##
webapp = Klein()
webapp.visits = 0
webapp.templates = jinja2.Environment(loader = jinja2.FileSystemLoader('templates'))


@webapp.route('/')
def home(request):
   webapp.visits += 1
   wampapp.session.publish('com.example.onvisit', visits = webapp.visits)
   page = webapp.templates.get_template('index.html')
   return page.render(visits = webapp.visits)


@webapp.route('/square/<int:x>')
@inlineCallbacks
def square(request, x):
   result = yield wampapp.session.call('com.example.square', x)
   page = webapp.templates.get_template('result.html')
   content = page.render(x = x, result = result)
   returnValue(content)


@webapp.route('/square/submit', methods = ['POST'])
def square_submit(request):
   x = int(request.args.get('x', [0])[0])
   return square(request, x)



if __name__ == "__main__":
   import sys
   from twisted.python import log
   from twisted.web.server import Site
   from twisted.internet import reactor
   log.startLogging(sys.stdout)

   reactor.listenTCP(8080, Site(webapp.resource()))
   wampapp.run("ws://localhost:9000", "realm1", standalone = True)
