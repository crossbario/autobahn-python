
class Wamp2Domain:

   def __init__(self):
      self._protos = set()


   def addSession(self, proto):
      pass


   def removeSession(self, proto):
      pass


   def subscribe(self, topic, handler):
      pass


   def publish(self, topic, event):
      pass

## wire format independence
## transport independence (Unix Domain Sockets, Pipes)
