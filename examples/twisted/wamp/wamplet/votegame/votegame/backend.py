###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
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


# WAMP application component with our app code.
##
class VoteGameBackend(ApplicationSession):

    def __init__(self, config):
        ApplicationSession.__init__(self)
        self.config = config
        self.init_db()

    def init_db(self):
        if not os.path.isfile(self.config.extra['dbfile']):
            log.msg("Initializing database ..")

            db = sqlite3.connect(self.config.extra['dbfile'])
            cur = db.cursor()

            cur.execute("""
                     CREATE TABLE votes (
                        item              TEXT     NOT NULL,
                        count             NUMBER   NOT NULL,
                        PRIMARY KEY (item))
                     """)

            for item in self.config.extra['items']:
                cur.execute("INSERT INTO votes (item, count) VALUES (?, ?)", [item, 0])
            db.commit()

            db.close()
            log.msg("Database initialized.")

        else:
            log.msg("Database already exists.")

        self.db = adbapi.ConnectionPool('sqlite3', self.config.extra['dbfile'], check_same_thread=False)
        log.msg("Database opened.")

    @wamp.register("com.votegame.get_votes")
    def get_votes(self):
        def run(txn):
            txn.execute("SELECT item, count FROM votes")
            res = {}
            for row in txn.fetchall():
                res[row[0]] = row[1]
            return res
        return self.db.runInteraction(run)

    @wamp.register("com.votegame.vote")
    def vote(self, item):
        if item not in self.config.extra['items']:
            raise ApplicationError("com.votegame.error.no_such_item", "no item '{}' to vote on".format(item))

        def run(txn):
            # FIXME: make the following into 1 (atomic) SQL statement
            # => does SQLite feature "UPDATE .. RETURNING"?
            txn.execute("UPDATE votes SET count = count + 1 WHERE item = ?", [item])
            txn.execute("SELECT count FROM votes WHERE item = ?", [item])
            count = int(txn.fetchone()[0])

            self.publish("com.votegame.onvote", item, count,
                         options=PublishOptions(excludeMe=False))

            return count

        return self.db.runInteraction(run)

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

        print("VoteGame Backend ready!")

    def onDisconnect(self):
        reactor.stop()


def make(config):
    ##
    # This component factory creates instances of the
    # application component to run.
    ##
    # The function will get called either during development
    # using the ApplicationRunner below, or as  a plugin running
    # hosted in a WAMPlet container such as a Crossbar.io worker.
    ##
    if config:
        return VoteGameBackend(config)
    else:
        # if no config given, return a description of this WAMPlet ..
        return {'label': 'VoteGame Service WAMPlet',
                'description': 'This is the backend WAMP application component of VoteGame.'}


if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner

    extra = {
        "dbfile": "votegame.db",
        "items": ["banana", "lemon", "grapefruit"]
    }

    # test drive the component during development ..
    runner = ApplicationRunner(
        url="ws://127.0.0.1:8080/ws",
        realm="realm1",
        extra=extra,
        debug=False,  # low-level WebSocket debugging
        debug_wamp=False,  # WAMP protocol-level debugging
        debug_app=True)  # app-level debugging

    runner.run(make)
