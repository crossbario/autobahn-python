# Trigger DBus Desktop Notifications via WAMP

This example shows how to bridge WAMP and DBus.

The example allows to trigger Linux desktop notifications by publishing to a WAMP topic. This allows
to show Linux desktop notifications on any number of Linux desktops. Kind of alert system.

> Note: For DBus support, we will use [txdbus](https://github.com/cocagne/txdbus), a native
Python DBus binding for Twisted which does not depend on the glib reactor or libdbus Python bindings.


## Prerequisites

You'll need **txdbus** installed:

    pip install txdbus


## Running on a single Host

Run the bridge with an embedded WAMP router

    python bridge.py

and open

    http://localhost:8080/

in your browser.


## Running on multiples Hosts

On each host, start the bridge connecting to a central WAMP router

    python bridge.py --router ws://myrouter.com

and open

    http://localhost:8080/

in your browser on *any* host to send a notification that will pop up on *all* hosts.
