:mod:`autobahn.twisted.choosereactor`
=====================================

.. py:module:: autobahn.twisted.choosereactor


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.twisted.choosereactor.current_reactor_klass
   autobahn.twisted.choosereactor.install_optimal_reactor
   autobahn.twisted.choosereactor.install_reactor


.. function:: current_reactor_klass()

   Return class name of currently installed Twisted reactor or None.


.. function:: install_optimal_reactor(require_optimal_reactor=True)

   Try to install the optimal Twisted reactor for this platform:

   - Linux:   epoll
   - BSD/OSX: kqueue
   - Windows: iocp
   - Other:   select

   Notes:

   - This function exists, because the reactor types selected based on platform
     in `twisted.internet.default` are different from here.
   - The imports are inlined, because the Twisted code base is notorious for
     importing the reactor as a side-effect of merely importing. Hence we postpone
     all importing.

   See: http://twistedmatrix.com/documents/current/core/howto/choosing-reactor.html#reactor-functionality

   :param require_optimal_reactor: If ``True`` and the desired reactor could not be installed,
       raise ``ReactorAlreadyInstalledError``, else fallback to another reactor.
   :type require_optimal_reactor: bool

   :returns: The Twisted reactor in place (`twisted.internet.reactor`).


.. function:: install_reactor(explicit_reactor=None, verbose=False, log=None, require_optimal_reactor=True)

   Install Twisted reactor.

   :param explicit_reactor: If provided, install this reactor. Else, install
       the optimal reactor.
   :type explicit_reactor: obj

   :param verbose: If ``True``, log (at level "info") the reactor that is
       in place afterwards.
   :type verbose: bool

   :param log: Explicit logging to this txaio logger object.
   :type log: obj

   :param require_optimal_reactor: If ``True`` and the desired reactor could not be installed,
       raise ``ReactorAlreadyInstalledError``, else fallback to another reactor.
   :type require_optimal_reactor: bool

   :returns: The Twisted reactor in place (`twisted.internet.reactor`).


