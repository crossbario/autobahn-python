###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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

import sys
import os
import pkg_resources
import StringIO
from sys import argv, executable
from socket import AF_INET

# make sure we run a capable OS/reactor
##
startupMsgs = []
if "bsd" in sys.platform:
    from twisted.internet import kqreactor

    kqreactor.install()
    startupMsgs.append("Alrighty: you run a capable kqueue platform - good job!")
elif sys.platform.startswith("linux"):
    from twisted.internet import epollreactor

    epollreactor.install()
    startupMsgs.append("Alrighty: you run a capable epoll platform - good job!")
elif sys.platform.startswith("darwin"):
    from twisted.internet import kqreactor

    kqreactor.install()
    startupMsgs.append(
        "Huh, you run OSX and have kqueue, but don't be disappointed when performance sucks;)"
    )
elif sys.platform == "win32":
    raise Exception(
        "Sorry dude, Twisted/Windows select/iocp reactors lack the necessary bits."
    )
else:
    raise Exception("Hey man, what OS are you using?")

from twisted.internet import reactor

startupMsgs.append(
    "Using Twisted reactor class %s on Twisted %s"
    % (str(reactor.__class__), pkg_resources.require("Twisted")[0].version)
)


from twisted.internet import reactor
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket.util import parse_url

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol

from autobahn.util import Stopwatch


hasStatprof = False
try:
    import statprof

    startupMsgs.append("statprof found! you may enable statistical profiling")
    hasStatprof = True
except ImportError:
    startupMsgs.append("statprof not installed - no profiling available")


class Stats:

    def __init__(self):
        # stats period
        self.period = 0

        # currently connected client
        self.clients = 0

        # total (running) stats
        self.tMsgs = 0
        self.tOctets = 0
        self.tHandshakes = 0
        self.tOctetsWireIn = 0
        self.tOctetsWireOut = 0

        self.stopwatch = Stopwatch(start=False)

        # period stats
        self._advance()

    def _advance(self):
        self.period += 1
        self.pMsgs = 0
        self.pOctets = 0
        self.pHandshakes = 0
        self.pOctetsWireIn = 0
        self.pOctetsWireOut = 0
        self.stopwatch.resume()

    def trackHandshake(self):
        self.tHandshakes += 1
        self.pHandshakes += 1

    def trackMsg(self, length):
        self.tMsgs += 1
        self.pMsgs += 1
        self.tOctets += length
        self.pOctets += length

    def trackOctetsWireIn(self, count):
        self.tOctetsWireIn += count
        self.pOctetsWireIn += count

    def trackOctetsWireOut(self, count):
        self.tOctetsWireOut += count
        self.pOctetsWireOut += count

    def stats(self, advance=True):
        elapsed = self.stopwatch.stop()

        s = (
            "Period No.        : %d\n"
            + "Period duration   : %.3f s\n"
            + "Connected clients : %d\n"
            + "\n"
            + "Period\n"
            + "  Handshakes      : %20d # %20d #/s\n"
            + "  Echo'ed msgs    : %20d # %20d #/s\n"
            + "  Echo'ed octets  : %20d B %20d B/s\n"
            + "  Wire octets in  : %20d B %20d B/s\n"
            + "  Wire octets out : %20d B %20d B/s\n"
            + "\n"
            + "Total\n"
            + "  Handshakes      : %20d #\n"
            + "  Echo'ed msgs    : %20d #\n"
            + "  Echo'ed octets  : %20d B\n"
            + "  Wire octets in  : %20d B\n"
            + "  Wire octets out : %20d B\n"
            + ""
        ) % (
            self.period,
            round(elapsed, 3),
            self.clients,
            self.pHandshakes,
            round(float(self.pHandshakes) / elapsed),
            self.pMsgs,
            round(float(self.pMsgs) / elapsed),
            self.pOctets,
            round(float(self.pOctets) / elapsed),
            self.pOctetsWireIn,
            round(float(self.pOctetsWireIn) / elapsed),
            self.pOctetsWireOut,
            round(float(self.pOctetsWireOut) / elapsed),
            self.tHandshakes,
            self.tMsgs,
            self.tOctets,
            self.tOctetsWireIn,
            self.tOctetsWireOut,
        )
        self._advance()
        return s


class EchoServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.stats.clients += 1
        self.factory.stats.trackHandshake()

    def onMessage(self, msg, binary):
        self.sendMessage(msg, binary)
        self.factory.stats.trackMsg(len(msg))

    def onClose(self, wasClean, code, reason):
        self.factory.stats.clients -= 1

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)

        self.factory.stats.trackOctetsWireIn(
            self.trafficStats.preopenIncomingOctetsWireLevel
            + self.trafficStats.incomingOctetsWireLevel
        )

        self.factory.stats.trackOctetsWireOut(
            self.trafficStats.preopenOutgoingOctetsWireLevel
            + self.trafficStats.outgoingOctetsWireLevel
        )


class EchoServerFactory(WebSocketServerFactory):

    protocol = EchoServerProtocol

    def __init__(self, wsuri):
        WebSocketServerFactory.__init__(self, wsuri)
        self.stats = Stats()


# export PYPYLOG="jit-log-opt,jit-backend:pypy.log"

# Run under "perf" and enable PyPy JIT logging
##
# Notes:
##
# - setting an env var (outside root) will NOT work (not propagated)
# - setting in code also will NOT work
##
# sudo PYPYLOG="jit-log-opt,jit-backend:pypy.log" perf record ~/pypy-20131102/bin/pypy server.py --workers 4


def master(options):
    """
    Start of the master process.
    """
    if not options.silence:
        print("Master started on PID %s" % os.getpid())

    # start embedded Web server if asked for (this only runs on master)
    ##
    if options.port:
        webdir = File(".")
        web = Site(webdir)
        web.log = lambda _: None  # disable annoyingly verbose request logging
        reactor.listenTCP(options.port, web)

    # we just need some factory like thing .. it won't be used on master anyway
    # for actual socket accept
    ##
    factory = Factory()

    # create socket, bind and listen ..
    port = reactor.listenTCP(options.wsport, factory, backlog=options.backlog)

    # .. but immediately stop reading: we only want to accept on workers, not master
    port.stopReading()

    # fire off background workers
    ##
    for i in range(options.workers):

        args = [
            executable,
            "-",
            __file__,
            "--fd",
            str(port.fileno()),
            "--cpuid",
            str(i),
        ]

        # pass on cmd line args to worker ..
        args.extend(sys.argv[1:])

        reactor.spawnProcess(
            None,
            executable,
            args,
            childFDs={0: 0, 1: 1, 2: 2, port.fileno(): port.fileno()},
            env=os.environ,
        )

    reactor.run()


PROFILER_FREQ = 2000


def worker(options):
    """
    Start background worker process.
    """
    workerPid = os.getpid()

    if not options.noaffinity:
        p = psutil.Process(workerPid)
        print("affinity [before]: ", p.cpu_affinity())
        p.cpu_affinity([options.cpuid])
        print("affinity [after]: ", p.cpu_affinity())

    factory = EchoServerFactory(options.wsuri)

    # The master already created the socket, just start listening and accepting
    ##
    reactor.adoptStreamPort(options.fd, AF_INET, factory)

    if not options.silence:
        print(
            "Worker started on PID %s using factory %s and protocol %s"
            % (workerPid, factory, factory.protocol)
        )
        # print "Worker %d PYPYLOG=%s" % (workerPid, os.environ.get('PYPYLOG', None))

    if options.profile:
        statprof.reset(PROFILER_FREQ)
        statprof.start()

    if not options.silence:

        def stat():
            if options.profile:
                statprof.stop()

            output = StringIO.StringIO()
            output.write("-" * 80 + "\n")
            output.write(
                "Worker Statistics (PID %s)\n\n%s" % (workerPid, factory.stats.stats())
            )

            if options.profile:
                output.write("\n")
                # format = statprof.DisplayFormats.ByLine
                # format = statprof.DisplayFormats.ByMethod
                # statprof.display(output, format = format)
                statprof.display(output)

            output.write("-" * 80 + "\n\n")

            sys.stdout.write(output.getvalue())

            if options.profile:
                statprof.reset(PROFILER_FREQ)
                statprof.start()

            reactor.callLater(options.interval, stat)

        reactor.callLater(options.interval, stat)

    if False:
        import cProfile

        print("RUNNING cProfile")
        cProfile.run("reactor.run()")
    else:
        reactor.run()


# /usr/include/valgrind/valgrind.h
# valgrind --tool=callgrind python server.py --wsuri ws://127.0.0.1:9000

# http://valgrind.org/docs/manual/cg-manual.html
# http://valgrind.org/docs/manual/cl-manual.html

# https://bitbucket.org/pypy/jitviewer
# http://morepypy.blogspot.de/2011/08/visualization-of-jitted-code.html
# http://people.cs.uct.ac.za/~tmullins/work/writeup.pdf

# list(range(psutil.NUM_CPUS))
# p.get_cpu_affinity()

# p.set_cpu_affinity([0])
# p.set_nice(psutil.HIGH_PRIORITY_CLASS)


if __name__ == "__main__":

    import argparse
    import psutil

    DEFAULT_WORKERS = psutil.cpu_count()

    parser = argparse.ArgumentParser(
        description="Autobahn WebSocket Echo Multicore Server"
    )
    parser.add_argument(
        "--wsuri",
        dest="wsuri",
        type=str,
        default="ws://127.0.0.1:9000",
        help="The WebSocket URI the server is listening on, e.g. ws://localhost:9000.",
    )
    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=8080,
        help="Port to listen on for embedded Web server. Set to 0 to disable.",
    )
    parser.add_argument(
        "--workers",
        dest="workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="Number of workers to spawn - should fit the number of (physical) CPU cores.",
    )
    parser.add_argument(
        "--noaffinity",
        dest="noaffinity",
        action="store_true",
        default=False,
        help="Do not set worker/CPU affinity.",
    )
    parser.add_argument(
        "--backlog",
        dest="backlog",
        type=int,
        default=8192,
        help="TCP accept queue depth. You must tune your OS also as this is just advisory!",
    )
    parser.add_argument(
        "--silence",
        dest="silence",
        action="store_true",
        default=False,
        help="Silence log output.",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Enable WebSocket debug output.",
    )
    parser.add_argument(
        "--interval",
        dest="interval",
        type=int,
        default=5,
        help="Worker stats update interval.",
    )
    parser.add_argument(
        "--profile",
        dest="profile",
        action="store_true",
        default=False,
        help="Enable profiling.",
    )

    parser.add_argument(
        "--fd",
        dest="fd",
        type=int,
        default=None,
        help="If given, this is a worker which will use provided FD and all other options are ignored.",
    )
    parser.add_argument(
        "--cpuid",
        dest="cpuid",
        type=int,
        default=None,
        help="If given, this is a worker which will use provided CPU core to set its affinity.",
    )

    options = parser.parse_args()

    if options.profile and not hasStatprof:
        raise Exception("profiling requested, but statprof not installed")

    # parse WS URI into components and forward via options
    # FIXME: add TLS support
    isSecure, host, wsport, resource, path, params = parse_url(options.wsuri)
    options.wsport = wsport

    # if not options.silence:
    #   log.startLogging(sys.stdout)

    if options.fd is not None:
        # run worker
        worker(options)
    else:
        if not options.silence:
            for m in startupMsgs:
                print(m)
        # run master
        master(options)
