# AUTODB - Autobahn Database Service

Basic structure to provide a generic database service to an Autobahn realm

## Summary

The db.py contains the database interface.  The interface simply puts in place a back end that
can be used by clients.  There are two rpc calls, adm.db.start and adm.db.stop.  start is
used to fire up a database engine, stop shuts it down. An example call to start is:

yield self.call('adm.db.start', 'PG9_4', 'adm.db')

what this does is set up the rpc with a prefix of adm.db, and calls named:
connect, disconnect, query, operation, watch for the database type postgres, version
9.4.  The rpc calls do:

adm.db.connect    start a postgres connection, the dsn is passed, dsn in psycopg2 format
adm.db.disconnect stop the postgres connection
adm.db.query      run a database query async
adm.db.operation  run a database query (no results expected)
adm.db.watch      postgres has a LISTEN operator.  watch lets us specify what to listen for, and what to call when an event is triggered.

Currently I only support postgres version 9.4.  I have plans to add htsql as an engine, and I'll probably add mysql just to prove the concept works.

```sh
./db.py --help yields:
usage: db.py [-h] [-w WSOCKET] [-r REALM] [-u USER] [-s PASSWORD]

db admin manager for autobahn

optional arguments:
  -h, --help            show this help message and exit
  -w WSOCKET, --websocket WSOCKET
                        web socket ws://127.0.0.1:8080/ws
  -r REALM, --realm REALM
                        connect to websocket using "realm" realm1
  -u USER, --user USER  connect to websocket as "user" db
  -s PASSWORD, --secret PASSWORD
                        users "secret" passworddbsecret


I don't like passing the user and password on the command line, I'll have to get back to that.
```

```sh
python db.py
```

this won't do anything by itself.  I am writing an example client to show how to
setup a database engine, then call queries.
