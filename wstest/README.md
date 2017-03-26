# WebSocket compliance testing

We are testing on these Pythons

* CPython 2.7
* CPython 3.6
* PyPy 2.7
* PyPy3 (3.5 lang. level)

using these networking frameworks

* Twisted
* asyncio (or Trollius fallback)

for

* WebSocket client
* WebSocket server

This gives a total of 16 combinations being tested.

The generated reports are hosted here:

* [Client](http://autobahn.ws/testsuite/reports/clients/index.html)
* [Server](http://autobahn.ws/testsuite/reports/servers/index.html)

> Note (23.3.2016): the server reports show some fails for some WebSocket compression tests - these are timeouts of the tests, because my machine was too slow / the timeout is too tight. However, it takes too now for me to repeat.


## Testing

### Prepare

Download Pythons

```console
make downloads
```

Build Pythons and wstest (the command line tool of the Autobahn WebSocket testsuite)

```console
make build
```

Check versions:

```console
oberstet@office-corei7:~/scm/crossbario/autobahn-python/wstest$ make versions
./cpy2/bin/python -V
Python 2.7.13
./cpy3/bin/python -V
Python 3.6.0
./pypy2/bin/python -V
Python 2.7.13 (fa3249d55d15, Mar 19 2017, 20:21:48)
[PyPy 5.7.0 with GCC 6.2.0 20160901]
./pypy3/bin/python -V
Python 3.5.3 (b16a4363e930, Mar 20 2017, 16:13:46)
[PyPy 5.7.0-beta0 with GCC 6.2.0 20160901]
```

Setup dependencies

```console
make setup
```

### Client Testing

In a first console, start the fuzzing server:

```console
make wstest_server
```

In a second console, run the testee clients:

```console
make test_client
```

Reports will be generated under the folder `./reports/clients`, with the summary report `./reports/clients/index.html`.


### Server Testing


In a console, start all the testee servers:

```console
make start_server
```

> Note: this will start 8 servers in the background. To stop: `make stop_server`


Now run the fuzzing client, which will test all servers:

```console
make test_server
```

### Upload reports

To upload reports:

```console
make upload_reports
```
