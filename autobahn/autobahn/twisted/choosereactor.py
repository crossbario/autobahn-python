###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

__all__ = (
   'install_optimal_reactor',
   'install_reactor'
)


def install_optimal_reactor(verbose = False):
   """
   Try to install the optimal Twisted reactor for platform.

   :param verbose: If ``True``, print what happens.
   :type verbose: bool
   """
   import sys
   from twisted.python import reflect

   ## determine currently installed reactor, if any
   ##
   if 'twisted.internet.reactor' in sys.modules:
      current_reactor = reflect.qual(sys.modules['twisted.internet.reactor'].__class__).split('.')[-1]
   else:
      current_reactor = None

   ## depending on platform, install optimal reactor
   ##
   if 'bsd' in sys.platform or sys.platform.startswith('darwin'):

      ## *BSD and MacOSX
      ##
      if current_reactor != 'KQueueReactor':
         try:
            v = sys.version_info
            if v[0] == 1 or (v[0] == 2 and v[1] < 6) or (v[0] == 2 and v[1] == 6 and v[2] < 5):
               raise Exception("Python version too old ({0}) to use kqueue reactor".format(sys.version))
            from twisted.internet import kqreactor
            kqreactor.install()
         except Exception as e:
            print("WARNING: Running on *BSD or MacOSX, but cannot install kqueue Twisted reactor ({0}).".format(e))            
         else:
            if verbose:
               print("Running on *BSD or MacOSX and optimal reactor (kqueue) was installed.")
      else:
         if verbose:
            print("Running on *BSD or MacOSX and optimal reactor (kqueue) already installed.")

   elif sys.platform in ['win32']:

      ## Windows
      ##
      if current_reactor != 'IOCPReactor':
         try:
            from twisted.internet.iocpreactor import reactor as iocpreactor
            iocpreactor.install()
         except Exception as e:
            print("WARNING: Running on Windows, but cannot install IOCP Twisted reactor ({0}).".format(e))
         else:
            if verbose:
               print("Running on Windows and optimal reactor (ICOP) was installed.")
      else:
         if verbose:
            print("Running on Windows and optimal reactor (ICOP) already installed.")

   elif sys.platform.startswith('linux'):

      ## Linux
      ##
      if current_reactor != 'EPollReactor':
         try:
            from twisted.internet import epollreactor
            epollreactor.install()
         except Exception as e:
            print("WARNING: Running on Linux, but cannot install Epoll Twisted reactor ({0}).".format(e))
         else:
            if verbose:
               print("Running on Linux and optimal reactor (epoll) was installed.")
      else:
         if verbose:
            print("Running on Linux and optimal reactor (epoll) already installed.")

   else:
      try:
         from twisted.internet import default as defaultreactor
         defaultreactor.install()
      except Exception as e:
         print("WARNING: Could not install default Twisted reactor for this platform ({0}).".format(e))



def install_reactor(explicitReactor = None, verbose = False):
   """
   Install Twisted reactor.

   :param explicitReactor: If provided, install this reactor. Else, install optimal reactor.
   :type explicitReactor: obj
   :param verbose: If ``True``, print what happens.
   :type verbose: bool
   """
   import sys

   if explicitReactor:
      ## install explicitly given reactor
      ##
      from twisted.application.reactors import installReactor
      print("Trying to install explicitly specified Twisted reactor '%s'" % explicitReactor)
      try:
         installReactor(explicitReactor)
      except Exception as e:
         print("Could not install Twisted reactor %s%s" % (explicitReactor, ' ["%s"]' % e if verbose else ''))
         sys.exit(1)
   else:
      ## automatically choose optimal reactor
      ##
      if verbose:
         print("Automatically choosing optimal Twisted reactor")
      install_optimal_reactor(verbose)

   ## now the reactor is installed, import it
   from twisted.internet import reactor

   if verbose:
      from twisted.python.reflect import qual
      print("Running Twisted reactor %s" % qual(reactor.__class__))

   return reactor
