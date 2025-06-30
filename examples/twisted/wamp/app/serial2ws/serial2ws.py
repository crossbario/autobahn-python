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

from os import environ

from twisted.internet.defer import inlineCallbacks
from twisted.internet.serialport import SerialPort
from twisted.protocols.basic import LineReceiver

from autobahn.twisted.wamp import ApplicationSession


class McuProtocol(LineReceiver):
    """
    MCU serial communication protocol.
    """

    # need a reference to our WS-MCU gateway factory to dispatch PubSub events
    def __init__(self, session):
        self.session = session

    def connectionMade(self):
        print("Serial port connected.")

    def lineReceived(self, line):
        print("Serial RX: {0}".format(line))

        try:
            # parse data received from MCU
            data = [int(x) for x in line.split()]
        except ValueError:
            print("Unable to parse value {0}".format(line))
        else:
            # create payload for WAMP event
            payload = {"id": data[0], "value": data[1]}

            # publish WAMP event to all subscribers on topic
            self.session.publish("com.myapp.mcu.on_analog_value", payload)

    def controlLed(self, turnOn):
        """
        This method is exported as RPC and can be called by connected clients
        """
        if turnOn:
            payload = b"1"
        else:
            payload = b"0"
        print("Serial TX: {0}".format(payload))
        self.transport.write(payload)


class McuComponent(ApplicationSession):
    """
    MCU WAMP application component.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("Component ready! Configuration: {}".format(self.config.extra))

        port = self.config.extra["port"]
        baudrate = self.config.extra["baudrate"]

        serialProtocol = McuProtocol(self)

        print("About to open serial port {0} [{1} baud] ..".format(port, baudrate))
        try:
            serialPort = SerialPort(serialProtocol, port, reactor, baudrate=baudrate)
        except Exception as e:
            print("Could not open serial port: {0}".format(e))
            self.leave()
        else:
            yield self.register(serialProtocol.controlLed, "com.myapp.mcu.control_led")


if __name__ == "__main__":

    import sys
    import argparse

    # parse command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--baudrate",
        type=int,
        default=9600,
        choices=[300, 1200, 2400, 4800, 9600, 19200, 57600, 115200],
        help="Serial port baudrate.",
    )

    parser.add_argument(
        "--port",
        type=str,
        default="/dev/ttyACM0",
        help="Serial port to use (e.g. 3 for a COM port on Windows, /dev/ttyATH0 for Arduino Yun, /dev/ttyACM0 for Serial-over-USB on RaspberryPi.",
    )

    parser.add_argument(
        "--web",
        type=int,
        default=8000,
        help="Web port to use for embedded Web server. Use 0 to disable.",
    )

    router_default = environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/ws")
    parser.add_argument(
        "--router",
        type=str,
        default=router_default,
        help='WAMP router URL (a WAMP-over-WebSocket endpoint, default: "{}")'.format(
            router_default
        ),
    )

    parser.add_argument(
        "--realm",
        type=str,
        default="crossbardemo",
        help='WAMP realm to join (default: "crossbardemo")',
    )

    args = parser.parse_args()

    # import Twisted reactor
    if sys.platform == "win32":
        # on Windows, we need to use the following reactor for serial support
        # http://twistedmatrix.com/trac/ticket/3802
        from twisted.internet import win32eventreactor

        win32eventreactor.install()

        # on Windows, we need port to be an integer
        args.port = int(args.port)

    from twisted.internet import reactor

    print("Using Twisted reactor {0}".format(reactor.__class__))

    # create embedded web server for static files
    if args.web:
        from twisted.web.server import Site
        from twisted.web.static import File

        reactor.listenTCP(args.web, Site(File(".")))

    # run WAMP application component
    from autobahn.twisted.wamp import ApplicationRunner

    runner = ApplicationRunner(
        args.router, args.realm, extra={"port": args.port, "baudrate": args.baudrate}
    )

    # start the component and the Twisted reactor ..
    runner.run(McuComponent)
