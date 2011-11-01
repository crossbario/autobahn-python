###############################################################################
##
##  Copyright 2011 Tavendo GmbH
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

setup (
   name = 'autobahn',
   version = '0.4.3',
   description = 'Autobahn WebSockets',
   long_description = """Twisted-based WebSockets client and server framework.

   Autobahn provides a WebSockets (Hybi-10 to -17) Twisted-based framework for
   creating WebSockets clients and servers.

   Autobahn also includes a light-weight, asynchronous RPC/PubSub over JSON-WebSockets
   protocol implementation and a fuzzing test framework which can test WebSockets client
   and server implementations.""",
   author = 'Tavendo GmbH',
   author_email = 'autobahnws@googlegroups.com',
   url = 'http://www.tavendo.de/autobahn',
   platforms = ('Any'),
   install_requires = ['Twisted>=11.0'],
   packages = find_packages(),
   zip_safe = False,

   ## http://pypi.python.org/pypi?%3Aaction=list_classifiers
   ##
   classifiers = ["License :: OSI Approved :: Apache Software License",
                  "Development Status :: 4 - Beta",
                  "Environment :: Console",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Topic :: Internet",
                  "Topic :: Software Development :: Libraries",
                  "Topic :: Software Development :: Testing"]
)
