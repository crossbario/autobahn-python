## Autobahn WebSocket Echo server on multicore

This example demonstrates how to scale-up an AutobahnPython based WebSocket echo server on a multicore machine.

## Running

For system setup, please see the instructions [here](https://github.com/oberstet/scratchbox/blob/master/python/twisted/sharedsocket/README.md).

Then run the server:

	pypy server.py --wsuri ws://localhost:9000 --workers 4

Now run your WebSocket echo load client against the server.

## Usage

	$ python server.py --help
	usage: server.py [-h] [--wsuri WSURI] [--port PORT] [--workers WORKERS]
	                 [--backlog BACKLOG] [--silence] [--debug]
	                 [--interval INTERVAL] [--fd FD]
	
	Autobahn WebSocket Echo Multicore Server
	
	optional arguments:
	  -h, --help           show this help message and exit
	  --wsuri WSURI        The WebSocket URI the server is listening on, e.g.
	                       ws://localhost:9000.
	  --port PORT          Port to listen on for embedded Web server. Set to 0 to
	                       disable.
	  --workers WORKERS    Number of workers to spawn - should fit the number of
	                       (phyisical) CPU cores.
	  --backlog BACKLOG    TCP accept queue depth. You must tune your OS also as
	                       this is just advisory!
	  --silence            Silence log output.
	  --debug              Enable WebSocket debug output.
	  --interval INTERVAL  Worker stats update interval.
	  --fd FD              If given, this is a worker which will use provided FD
	                       and all other options are ignored.

