###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from setuptools import setup, find_packages

LONGDESC = """
A WebSocket echo service implemented as a Twisted service and
deployed as a twistd plugin.
"""

setup(
    name='echows',
    version='0.1.0',
    description='Autobahn WebSocket Echo Service',
    long_description=LONGDESC,
    author='Tavendo GmbH',
    url='http://autobahn.ws/python',
    platforms=('Any'),
    install_requires=['Twisted>=Twisted-12.2',
                      'Autobahn>=0.5.9'],
    packages=find_packages() + ['twisted.plugins'],
    # packages = ['echows', 'twisted.plugins'],
    include_package_data=True,
    zip_safe=False
)
