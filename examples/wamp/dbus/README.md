Trigger DBus Desktop Notifications via WebSocket/WAMP
=====================================================

This example shows how to bridge WebSocket/WAMP and DBus.

For DBus support, we will use [txdbus](https://github.com/cocagne/txdbus),
a new native Python DBus binding for Twisted which does not depend on the glib
reactor or libdbus Python bindings.

The example consists of 3 parts:

  * client.py
  * server.py
  * index.html

The **client.py** runs on a Linux desktop  and subscribes to 2 PubSub topics:

 * user specific topic
 * the "all" topic (for notifications to all)

Upon receiving an event over WAMP for one of above topics, a desktop notification is triggered via *txdbus*.

The **server.py** runs on an arbitrary machine and provides the PubSub message brokering. It also provides an embedded web server for the Web UI.

The **index.html** is the Web UI used to trigger desktop notifications. It is a WAMP client using AutobahnJS and publishes notification events to topics for the **server.py** to forward to connected Linux desktops.


Running
-------

Run the server by doing

    python server.py debug

and open

    http://<Server IP>:8080/

in your browser.

Open a terminal on a Linux desktop and

	python client.py ws://<Server IP>:9000 user1 secret

Optionally, open a second terminal on another Linux desktop and

	python client.py ws://<Server IP>:9000 user2 geheim

Now, from the Web UI, send desktop notifications to

 * all
 * user1
 * user2

