:mod:`autobahn.__main__`
========================

.. py:module:: autobahn.__main__


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.__main__._create_component
   autobahn.__main__.do_call
   autobahn.__main__.do_publish
   autobahn.__main__.do_register
   autobahn.__main__.do_subscribe
   autobahn.__main__._main
   autobahn.__main__._real_main


.. data:: top
   

   

.. data:: sub
   

   

.. data:: call
   

   

.. data:: publish
   

   

.. data:: register
   

   

.. data:: subscribe
   

   

.. function:: _create_component(options)

   Configure and return a Component instance according to the given
   `options`


.. function:: do_call(reactor, session, options)


.. function:: do_publish(reactor, session, options)


.. function:: do_register(reactor, session, options)

   run a command-line upon an RPC call


.. function:: do_subscribe(reactor, session, options)

   print events (one line of JSON per event)


.. function:: _main()

   This is a magic name for `python -m autobahn`, and specified as
   our entry_point in setup.py


.. function:: _real_main(reactor)

   Sanity check options, create a connection and run our subcommand


