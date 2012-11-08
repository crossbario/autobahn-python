###############################################################################
##
##  Copyright 2012 Tavendo GmbH
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

from setuptools import setup, find_packages

LONGDESC = """
A WebSocket echo service implemented as a Twisted service and
deployed as a twistd plugin.
"""

setup (
   name = 'echows',
   version = '0.1.0',
   description = 'Autobahn WebSocket Echo Service',
   long_description = LONGDESC,
   author = 'Tavendo GmbH',
   url = 'http://autobahn.ws/python',
   platforms = ('Any'),
   install_requires = ['Twisted>=Twisted-12.2',
                       'Autobahn>=0.5.9'],
   packages = find_packages() + ['twisted.plugins'],
   #packages = ['echows', 'twisted.plugins'],
   include_package_data = True,
   zip_safe = False
)
