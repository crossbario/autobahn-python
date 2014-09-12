###############################################################################
##
##  Copyright (C) 2014 Greg Fausak
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##        http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys,os
import psycopg2
import psycopg2.extras
from txpostgres import txpostgres

from twisted.internet.defer import inlineCallbacks, returnValue

def rdc(*args, **kwargs):
    kwargs['connection_factory'] = psycopg2.extras.RealDictConnection
    # this is to let everything pass through as strings
    psycopg2.extensions.string_types.clear()
    return psycopg2.connect(*args, **kwargs)

class RDC(txpostgres.Connection):
        connectionFactory = staticmethod(rdc)

class PG9_4():
    """
    basic postgres 9.4 driver
    """

    def __init__(self,pself):
        print("PG9_4:__init__()")
        self.conn = None
        self.dsn = None
        self.d = None
        return
 
    @inlineCallbacks
    def connect(self,dsn):
        print("PG9_4:connect({})").format(dsn)
        self.dsn = dsn
        self.conn = RDC()
        try:
            rv = yield self.conn.connect(self.dsn)
            print("PG9_4:connect() established")
        except Exception as err:
            print("PG9_4:connect({}),error({})").format(dsn,err)
            raise err
        return

    def disconnect(self):
        print("PG9_4:disconnect()")
        if self.conn:
            c = self.conn
            self.conn = None
            c.close()

        return

    #
    # query:
    #  s - query to run (with dictionary substitution embedded, like %(key)s
    #  a - dictionary pointing to arguments.
    # example:
    #  s = 'select * from login where id = %(id)s'
    #  a = { 'id': 100 }
    # returns:
    #  dictionary result of query
    # note:
    #  there MUST be a result, otherwise use the operation call!
    #

    @inlineCallbacks
    def query(self,s,a):
        print("PG9_4:query()")
        if self.conn:
            try:
                print("PG9_4:query().running({} with args {})").format(s,a)
                rv = yield self.conn.runQuery(s,a)
                print("PG9_4:query().results({})").format(rv)
                returnValue(rv)
            except Exception as err:
                print("PG9_4:query({}),error({})").format(s,err)
                raise err

        # error here, probably should raise exception
        return

    #
    # operation:
    #  identical to query, except, there is no result returned.
    # note:
    #  it is important that your query does NOT return anything!  If it does,
    #  use the query call!
    #

    @inlineCallbacks
    def operation(self,s,a):
        print("PG9_4:operation()")
        if self.conn:
            try:
                print("PG9_4:query().running({} with args {})").format(s,a)
                rv = yield self.conn.runOperation(s,a)
                print("PG9_4:query().results({})").format(rv)
                returnValue(rv)
            except Exception as err:
                print("PG9_4:query({}),error({})").format(s,err)
                raise err

        # error here, probably should raise exception
        return

