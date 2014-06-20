from twisted.web.client import Agent
from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner


class Component1(ApplicationSession):

   @inlineCallbacks
   def onJoin(self, details):

      from twisted.internet import reactor
      self._agent = Agent(reactor)

      reg = yield self.register(self)
      print("Procedures registered")


   @wamp.register('com.myapp.httpget')
   def httpget(self, url):
      d = self._agent.request('GET', str(url))

      def cbResponse(ignored):
         return "got response"
      d.addCallback(cbResponse)

      return d



if __name__ == '__main__':

   runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
   runner.run(Component1)
