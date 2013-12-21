###############################################################################
##
##  Copyright 2011-2013 Tavendo GmbH
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

import asyncio

class EchoClient(asyncio.Protocol):

   message = 'This is the message. It will be echoed.'

   def connection_made(self, transport):
      transport.write(self.message.encode())
      print('data sent: {}'.format(self.message))

   def data_received(self, data):
      print('data received: {}'.format(data.decode()))

   def connection_lost(self, exc):
      print('server closed the connection')
      asyncio.get_event_loop().stop()

loop = asyncio.get_event_loop()
coro = loop.create_connection(EchoClient, '127.0.0.1', 8888)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()
