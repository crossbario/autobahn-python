import sys
sys.path.insert(0, "../../../../autobahn")

from twisted.internet.defer import returnValue

from autobahn.twisted.app import Application
app = Application('com.example')


@app.register()
def add2(a, b):
   print("add2() called")
   return a + b


@app.register('com.example.hello')
def hello():
   print("hello() called")
   res = yield app.session.call('com.example.add2', 2, 3)
   returnValue("Hello: {}".format(res))


@app.signal('onpostjoin')
def onpostjoin():
   print("realm joined!")


if __name__ == "__main__":
   app.run("ws://localhost:8080/ws", "realm1", standalone = True)
