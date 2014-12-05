## Autobahn WebSocket Echo server on multicore

This example demonstrates how to scale-up an AutobahnPython based WebSocket echo server on a multicore machine.

## Usage

Run the server with 4 workers:

	pypy server.py --wsuri ws://localhost:9000 --workers 4

In general, using more workers than CPU cores available will not improve performance, likely to the contrary.

Detailed usage:

	$ pypy server.py --help
	usage: server.py [-h] [--wsuri WSURI] [--port PORT] [--workers WORKERS]
	                 [--noaffinity] [--backlog BACKLOG] [--silence] [--debug]
	                 [--interval INTERVAL] [--profile] [--fd FD] [--cpuid CPUID]

	Autobahn WebSocket Echo Multicore Server

	optional arguments:
	  -h, --help           show this help message and exit
	  --wsuri WSURI        The WebSocket URI the server is listening on, e.g.
	                       ws://localhost:9000.
	  --port PORT          Port to listen on for embedded Web server. Set to 0 to
	                       disable.
	  --workers WORKERS    Number of workers to spawn - should fit the number of
	                       (physical) CPU cores.
	  --noaffinity         Do not set worker/CPU affinity.
	  --backlog BACKLOG    TCP accept queue depth. You must tune your OS also as
	                       this is just advisory!
	  --silence            Silence log output.
	  --debug              Enable WebSocket debug output.
	  --interval INTERVAL  Worker stats update interval.
	  --profile            Enable profiling.
	  --fd FD              If given, this is a worker which will use provided FD
	                       and all other options are ignored.
	  --cpuid CPUID        If given, this is a worker which will use provided CPU
	                       core to set its affinity.

## Load Testing

You will need some serious WebSocket load driver to get this thingy sweating. I recommend [wsperf](https://github.com/zaphoyd/wsperf) for various reasons. `wsperf` is a high-performance, C++/ASIO, multi-threaded based load driver. Caveat: currently, even when using `wsperf`, the bottleneck can still be `wsperf` when running against Autobahn/PyPy. You should give `wsperf` *more* CPU cores than Autobahn for this reason.

You should also test on non-virtualized, real-hardware and you will also need to do OS / system level tuning, please see the instructions [here](https://github.com/oberstet/scratchbox/blob/master/python/twisted/sharedsocket/README.md).

For results, please see [here](https://github.com/oberstet/wsperf_results).
