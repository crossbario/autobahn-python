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

import os
import datetime
import sqlite3

from twisted.python import log
from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.types import PublishOptions


## WAMP application component with our app code.
##
class VoteGameBackend(ApplicationSession):

   DBFILE = "votegame.db"
   ITEMS = ['banana', 'lemon', 'grapefruit']

   def __init__(self, config):
      ApplicationSession.__init__(self)
      self.config = config
      self.init_db()


   def init_db(self):
      if not os.path.isfile(self.DBFILE):
         log.msg("Initializing database ..")

         db = sqlite3.connect(self.DBFILE)
         cur = db.cursor()

         cur.execute("""
                     CREATE TABLE votes (
                        item              TEXT     NOT NULL,
                        count             NUMBER   NOT NULL,
                        PRIMARY KEY (item))
                     """)

         for item in self.ITEMS:
            cur.execute("INSERT INTO votes (item, count) VALUES (?, ?)", [item, 0])
         db.commit()

         db.close()
         log.msg("Database initialized.")

      else:
         log.msg("Database already exists.")

      self.db = adbapi.ConnectionPool('sqlite3', self.DBFILE, check_same_thread = False)
      log.msg("Database opened.")


   @wamp.procedure("com.votegame.get_votes")
   def get_votes(self):
      def run(txn):
         txn.execute("SELECT item, count FROM votes")
         res = {}
         for row in txn.fetchall():
            res[row[0]] = row[1]
         return res
      return self.db.runInteraction(run)


   @wamp.procedure("com.votegame.vote")
   def vote(self, item):
      if not item in self.ITEMS:
         raise ApplicationError("com.votegame.error.no_such_item", "no item '{}' to vote on".format(item))

      def run(txn):
         txn.execute("UPDATE votes SET count = count + 1 WHERE item = ?", [item])         

         txn.execute("SELECT count FROM votes WHERE item = ?", [item])
         count = int(txn.fetchone()[0])

         self.publish("com.votegame.onvote", item, count,
            options = PublishOptions(excludeMe = False))

         return count

      return self.db.runInteraction(run)


   def onConnect(self):
      self.join(self.config.realm)


   @inlineCallbacks
   def onJoin(self, details):

      def onvote(item, count):
         print("New vote on '{}': {}".format(item, count))

      yield self.subscribe(onvote, 'com.votegame.onvote')

      try:
         regs = yield self.register(self)
         print("Ok, registered {} procedures.".format(len(regs)))
      except Exception as e:
         print("Failed to register procedures: {}".format(e))


   def onLeave(self, details):
      self.disconnect()


   def onDisconnect(self):
      reactor.stop()



def make(config):
   ##
   ## This component factory creates instances of the
   ## application component to run.
   ## 
   ## The function will get called either during development
   ## using the ApplicationRunner below, or as  a plugin running
   ## hosted in a WAMPlet container such as a Crossbar.io worker.
   ##
   if config:
      return VoteGameBackend(config)
   else:
      return {'label': 'VoteGame Service WAMPlet',
              'description': 'This is the backend WAMP application component of VoteGame.'}



if __name__ == '__main__':
   from autobahn.twisted.wamp import ApplicationRunner

   config = {
      "router": {
         "type": "websocket",
         "endpoint": {
            "type": "tcp",
            "host": "localhost",
            "port": 8080
         },
         "url": "ws://localhost:8080/ws",
         "realm": "realm1"
      }
   }

   ## test drive the component during development ..
   runner = ApplicationRunner(config,
      debug = False,       ## low-level WebSocket debugging
      debug_wamp = False,  ## WAMP protocol-level debugging
      debug_app = True)    ## app-level debugging
   runner.run(make)
