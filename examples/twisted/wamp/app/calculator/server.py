###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
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

import sys
import decimal

from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession



class Calculator(ApplicationSession):

   @inlineCallbacks
   def onJoin(self, details):
      self.clear()
      yield self.register(self)
      print("Ok, calculator procedures registered!")


   @wamp.register(u'com.example.calculator.clear')
   def clear(self, arg = None):
      self.op = None
      self.current = decimal.Decimal(0)
      return str(self.current)


   @wamp.register(u'com.example.calculator.calc')
   def calc(self, op, num):
      num = decimal.Decimal(num)
      if self.op:
         if self.op == "+":
            self.current += num
         elif self.op == "-":
            self.current -= num
         elif self.op == "*":
            self.current *= num
         elif self.op == "/":
            self.current /= num
         self.op = op
      else:
         self.op = op
         self.current = num

      res = str(self.current)
      if op == "=":
         self.clear()

      return res



if __name__ == '__main__':

   decimal.getcontext().prec = 20

   import sys, argparse

   ## parse command line arguments
   ##
   parser = argparse.ArgumentParser()

   parser.add_argument("-d", "--debug", action = "store_true",
                       help = "Enable debug output.")

   parser.add_argument("--web", type = int, default = 8080,
                       help = 'Web port to use for embedded Web server. Use 0 to disable.')

   parser.add_argument("--router", type = str, default = None,
                       help = 'If given, connect to this WAMP router. Else run an embedded router on 9000.')

   args = parser.parse_args()

   if args.debug:
      from twisted.python import log
      log.startLogging(sys.stdout)     

   ## import Twisted reactor
   ##
   from twisted.internet import reactor
   print("Using Twisted reactor {0}".format(reactor.__class__))


   ## create embedded web server for static files
   ##
   if args.web:
      from twisted.web.server import Site
      from twisted.web.static import File
      reactor.listenTCP(args.web, Site(File(".")))


   ## run WAMP application component
   ##
   from autobahn.twisted.wamp import ApplicationRunner
   router = args.router or 'ws://localhost:9000'

   runner = ApplicationRunner(router, u"realm1", standalone = not args.router,
      debug = False,             # low-level logging
      debug_wamp = args.debug,   # WAMP level logging
      debug_app = args.debug     # app-level logging
   )

   ## start the component and the Twisted reactor ..
   ##
   runner.run(Calculator)
