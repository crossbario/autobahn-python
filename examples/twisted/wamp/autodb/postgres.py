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

import psycopg2
import psycopg2.extras
from txpostgres import txpostgres

class PG9_4():
    """
    basic postgres 9.4 driver
    """

    def __init__(self,pself):
        print("PG9_4:__init__()")
        pself.connect=self.connect
        pself.disconnect=self.disconnect
        pself.query=self.query
 
    def connect(self,dsn):
        print("PG9_4:connect({})").format(dsn)
        return

    def disconnect(self):
        print("PG9_4:disconnect()")
        return

    def query(self,s):
        print("PG9_4:query({})").format(s)
        return
