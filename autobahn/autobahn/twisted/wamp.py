###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
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

from __future__ import absolute_import

__all__ = ['WampAppSession',
           'WampAppFactory',
           'WampRouterSession',
           'WampRouterFactory']

from autobahn.wamp import protocol


class WampAppSession(protocol.WampAppSession):
   """
   WAMP application session for Twisted-based applications.
   """


class WampAppFactory(protocol.WampAppFactory):
   """
   WAMP application session factory for Twisted-based applications.
   """


class WampRouterSession(protocol.WampRouterSession):
   """
   WAMP router session for Twisted-based applications.
   """


class WampRouterSessionFactory(protocol.WampRouterSessionFactory):
   """
   WAMP router session factory for Twisted-based applications.
   """
