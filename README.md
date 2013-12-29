AutobahnPython
==============

**Autobahn**|Python is a subproject of [Autobahn](http://autobahn.ws/) and provides open-source implementations of

* **[The WebSocket Protocol](http://tools.ietf.org/html/rfc6455)**
* **[The Web Application Messaging Protocol (WAMP)](http://wamp.ws/)**

WebSocket allows [bidirectional real-time messaging on the Web](http://tavendo.com/blog/post/websocket-why-what-can-i-use-it/) and WAMP adds asynchronous *Remote Procedure Calls* and *Publish & Subscribe* on top of WebSocket. 

You can use **Autobahn**|Python to create clients and servers in Python speaking just plain WebSocket or WAMP.


**Autobahn**|Python features:

* framework for [WebSocket](http://tools.ietf.org/html/rfc6455) / [WAMP](http://wamp.ws/) clients and servers
* compatible with Python 2.6, 2.7, 3.3 and 3.4
* runs on [CPython](http://python.org/), [PyPy](http://pypy.org/) and [Jython](http://jython.org/)
* runs under [Twisted](http://twistedmatrix.com/) and [asyncio](http://docs.python.org/3.4/library/asyncio.html)
* implements WebSocket [RFC6455](http://tools.ietf.org/html/rfc6455), Draft Hybi-10+, Hixie-76
* implements [WebSocket compression](http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression)
* implements [WAMPv1](http://wamp.ws/spec/) and [WAMPv2](https://github.com/tavendo/WAMP/blob/master/spec/README.md) (*upcoming*)

and more

* high-performance, fully asynchronous implementation
* best-in-class standards conformance (100% strict passes with [Autobahn Testsuite](http://autobahn.ws/testsuite))
* message-, frame- and streaming-APIs for WebSocket
* supports TLS (secure WebSocket) and proxies
* Open-source (Apache 2 [license](https://github.com/tavendo/AutobahnPython/blob/master/LICENSE))


Documentation
-------------

To get started quickly, check out the [examples](https://github.com/tavendo/AutobahnPython/tree/master/examples).
 For complete API documentation, please consult the [reference documentation](https://autobahnpython.readthedocs.org/).


API Stability
-------------

> Please note that the only API that is promised to be stable is the one documented in the [reference documentation](http://autobahn.ws/python/reference). If you use anything not documented in the reference documentation, your code might break at a later AutobahnPython version.
>

Where it runs
-------------

AutobahnPython runs under **[Python](http://www.python.org/)** (latest versions of CPython 2.6 or 2.7) and **[PyPy](http://pypy.org/)** (1.9 or later).

The only dependency is **[Twisted](http://twistedmatrix.com)** (11.1 or later).

AutobahnPython is used on "fat" platforms like **Windows**, **MacOS X**, **Linux**, **BSD** and embedded platforms like the **[RaspberryPi](http://www.raspberrypi.org/)**.

AutobahnPython also runs along [Twisted Web](http://twistedmatrix.com/documents/current/web/howto/index.html) and *any* Web framework like [Flask](http://flask.pocoo.org/) or [Django](https://www.djangoproject.com/) that runs under [WSGI](http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) containers.

You can run your favorite Web framework and AutobahnPython WebSocket and/or WAMP as *one application on one port*.

AutobahnPython also runs on **Android** under the [Scripting Layer for Android](http://code.google.com/p/android-scripting/) (SL4A).

Create a subfolder in the `/sl4a/scripts/` folder, copy the Autobahn module folder into it. Your program file (client or server) should then be a sibling to the `autobahn` folder, i.e.

    /sl4a/scripts/myapp/myapp.py
    /sl4a/scripts/myapp/autobahn/__init__.py
                ...
    /sl4a/scripts/myapp/autobahn/xormasker.py

AutobahnPython runs on **[Jython](http://www.jython.org/)** (2.7 beta1) also .. not yet supported completely, but a start. Please see the tickets [here](http://twistedmatrix.com/trac/ticket/3413#comment:21) and [here](http://bugs.jython.org/issue1521). Also: don't expect any wonders .. AutobahnPython (without `wsaccel` .. see below) running on Jython is slower (20-30%) than on CPython, and significantly slower than on PyPy.


Performance
-----------

AutobahnPython is portable, well tuned code. You can further accelerate performance by

* Run your whole application under [PyPy](http://pypy.org/)
* Accelerate hotspots via [`wsaccel`](https://github.com/methane/wsaccel)

AutobahnPython will *automatically* run [Cython](http://cython.org/) versions of UTF8 validation and WebSocket frame masking/demasking when `wsaccel` is available. Those two function are usually the hotspots within AutobahnPython.


Where to go
-----------

For more information, including getting started, tutorials and reference documentation, please visit the project's [homepage](http://autobahn.ws/python), or check out the examples in this repository.


Get in touch
------------

Get in touch on IRC #autobahn on chat.freenode.net or join the [mailing list](http://groups.google.com/group/autobahnws).
