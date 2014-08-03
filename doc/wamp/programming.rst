WAMP Programming
================

This guide gives an introduction to programming with `WAMP <http://wamp.ws>`__ in Python using |Ab|.

We will cover all four main interactions that WAMP provides for applications

1. **Calling** remote procedures
2. **Registering** procedures for remote calling
3. **Publishing** events to topics
4. **Subscribing** to topics for receiving events


Upgrading
---------

From < 0.8.0
............

Starting with release 0.8.0, |Ab| now supports WAMP v2, and also support both Twisted and asyncio. This required changing module naming for WAMP v1 (which is Twisted only).

Hence, WAMP v1 code for |ab| **< 0.8.0**

.. code-block:: python

   from autobahn.wamp import WampServerFactory

should be modified for |ab| **>= 0.8.0** for (using Twisted)

.. code-block:: python

   from autobahn.wamp1.protocol import WampServerFactory

.. note:: WAMPv1 will be deprecated with the 0.9.0 release.
