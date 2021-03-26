:mod:`autobahn.wamp.test.test_wamp_component`
=============================================

.. py:module:: autobahn.wamp.test.test_wamp_component


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.test.test_wamp_component.CaseComponent



.. class:: CaseComponent(config)


   Bases: :class:`autobahn.twisted.wamp.ApplicationSession`

   Application code goes here. This is an example component that calls
   a remote procedure on a WAMP peer, subscribes to a topic to receive
   events, and then stops the world after some events.

   .. method:: log(self, *args)


   .. method:: finish(self)



