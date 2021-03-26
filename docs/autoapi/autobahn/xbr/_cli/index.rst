:mod:`autobahn.xbr._cli`
========================

.. py:module:: autobahn.xbr._cli


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.xbr._cli.Client



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._cli.print_version
   autobahn.xbr._cli._main


.. data:: _COMMANDS
   :annotation: = ['version', 'get-member', 'register-member', 'register-member-verify', 'get-market', 'create-market', 'create-market-verify', 'get-actor', 'join-market', 'join-market-verify', 'get-channel', 'open-channel', 'close-channel', 'describe-schema', 'codegen-schema']

   

.. class:: Client(config=None)


   Bases: :class:`autobahn.twisted.wamp.ApplicationSession`

   WAMP application session for Twisted-based applications.

   Implements:

       * :class:`autobahn.wamp.interfaces.ITransportHandler`
       * :class:`autobahn.wamp.interfaces.ISession`

   .. method:: onUserError(self, fail, msg)

      Implements :func:`autobahn.wamp.interfaces.ISession.onUserError`


   .. method:: onConnect(self)

      Implements :func:`autobahn.wamp.interfaces.ISession.onConnect`


   .. method:: onChallenge(self, challenge)

      Implements :func:`autobahn.wamp.interfaces.ISession.onChallenge`


   .. method:: onJoin(self, details)
      :async:


   .. method:: onLeave(self, details)

      Implements :meth:`autobahn.wamp.interfaces.ISession.onLeave`


   .. method:: onDisconnect(self)

      Implements :meth:`autobahn.wamp.interfaces.ISession.onDisconnect`


   .. method:: _do_xbrnetwork_realm(self, details)
      :async:


   .. method:: _do_market_realm(self, details)
      :async:


   .. method:: _do_get_member(self, member_adr)
      :async:


   .. method:: _do_get_actor(self, market_oid, actor_adr)
      :async:


   .. method:: _do_onboard_member(self, member_username, member_email)
      :async:


   .. method:: _do_onboard_member_verify(self, vaction_oid, vaction_code)
      :async:


   .. method:: _do_create_market(self, member_oid, market_oid, marketmaker, title=None, label=None, homepage=None, provider_security=0, consumer_security=0, market_fee=0)
      :async:


   .. method:: _do_create_market_verify(self, member_oid, vaction_oid, vaction_code)
      :async:


   .. method:: _do_get_market(self, member_oid, market_oid)
      :async:


   .. method:: _do_join_market(self, member_oid, market_oid, actor_type)
      :async:


   .. method:: _do_join_market_verify(self, member_oid, vaction_oid, vaction_code)
      :async:


   .. method:: _do_get_active_payment_channel(self, market_oid, delegate_adr)
      :async:


   .. method:: _do_get_active_paying_channel(self, market_oid, delegate_adr)
      :async:


   .. method:: _do_open_channel(self, market_oid, channel_oid, channel_type, delegate, amount)
      :async:


   .. method:: _send_Allowance(self, from_adr, to_adr, amount)



.. function:: print_version()


.. function:: _main()


