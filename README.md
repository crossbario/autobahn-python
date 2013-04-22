AutobahnPython
==============

AutobahnPython implements **[The WebSocket Protocol](http://tools.ietf.org/html/rfc6455)** and **[The WebSocket Application Messaging Protocol (WAMP)](http://wamp.ws/)**:

* framework for WebSocket and WAMP clients and servers
* implements WebSocket RFC6455, Draft Hybi-10+, Hixie-76 and WAMP v1
* Twisted-based, runs on CPython and PyPy
* high-performance, fully asynchronous implementation
* best-in-class standards conformance (100% strict passes with *[Autobahn WebSocket Testsuite](http://autobahn.ws/testsuite)*)
* message-, frame- and streaming-APIs
* Deferred-based API for asynchronous RPC and PubSub (WAMP)
* supports TLS (secure WebSocket)
* session authentication (WAMP-CRA)
* Open-source (Apache 2 license)

You can use AutobahnPython to create clients and servers speaking either plain WebSocket or WAMP.

Using WAMP you can build applications around **asynchronous RPC** and **PubSub** messaging patterns.

Documentation
-------------

To get started quickly, check out the [examples](https://github.com/tavendo/AutobahnPython/tree/master/examples).
 For complete API documentation, please consult the [reference documentation](http://autobahn.ws/python/reference).


API Stability
-------------

> Please note that the only API that is promised to be stable is the one documented in the [reference documentation](http://autobahn.ws/python/reference). If you use anything not documented in the reference documentation, your code might break at a later AutobahnPython version.
> 

Where it runs
-------------

AutobahnPython runs under **[Python](http://www.python.org/)** (latest versions of CPython 2.6 or 2.7) and **[PyPy](http://pypy.org/)** (1.9 or later).

The only dependency is **[Twisted](http://twistedmatrix.com)** (11.1 or later).

AutobahnPython is used on "fat" platforms like **Windows**, **MacOS X**, **Linux**, ***BSD** and embedded platforms like the **[RaspberryPi](http://www.raspberrypi.org/)**.

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
