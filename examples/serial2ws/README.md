Serial to WebSocket/WAMP Bridge using Autobahn
==============================================

This demo shows how to shuffle data between WebSocket clients and
a device connected via a serial port.

      Arduino,
      other serial devices

         <= Serial over USB =>

      PC / Autobahn

         <= WebSocket over Internet =>

      Browser (AutobahnJS),
      Python (AutobahnPython),
      Smartphone (AutobahnAndroid),
      ...


Here are some videos - sorry, bad quality. But you should get the idea:

   * http://www.youtube.com/watch?v=va7j86thW5M
   * http://www.youtube.com/watch?v=aVJV2z-lQJE



How it works
------------

*serial device => WebSocket/WAMP client*

The Autobahn-based server will receive data from the device vi serial (over USB)
and dispatch data received as *WAMP PubSub* events on topics upon which clients
can subscribe.

*WebSocket/WAMP client => serial device*

The Autobahn-based server provides *WAMP RPC* endpoints which clients can call.
The server will then forward the commands to the device via serial (over USB)
to the device.


The protocol spoken on the serial wire is a very simple, small adhoc text based
one.



Discussion
----------

Pros:

 * Using serial means you can connect a lot of devices .. serial support is widespread.

Cons:

 * You need to invent some small custom protocol for the comms on serial wire

 * You must have a physical connection between the device and the PC/Autobahn server


For the reasons above, we plan to have a *AutobahnAndroid* implementation!

Thing is: there are (somewhat) emerging WebSocket implementations for Arduino
already.

But what we want to have is full WAMP: http://wamp.ws

Now, to do it right, we want to use the binary message payload option that
WebSocket brings, and not use JSON, but Bencode for payload format, since that
is much more resource efficient, which matters on restricted devices (like
Arduino). Therefor, we will first define a *Bencode payload format* binding
for *WAMP*.



We want How to do it yourself
---------------------

You will need AutobahnPython as server + PySerial for serial support in
Python/Twisted.

Then, connect your serial device, run

    python serial2ws.py

and open

    http://localhost:8080/

in your browser.

Note: The serial2ws.py has a number of command line options for setting
COM port, baudrate etc. Simply do a

    python serial2ws.py --help

to get information on those.



How to do it yourself
---------------------

You will need AutobahnPython as server + PySerial for serial support in
Python/Twisted.

Then, connect your serial device, run

    python serial2ws.py

and open

    http://localhost:8080/

in your browser.

Note: The serial2ws.py has a number of command line options for setting
COM port, baudrate etc. Simply do a

    python serial2ws.py --help

to get information on those.
