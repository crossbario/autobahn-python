from autobahn.twisted.wamp import Application
app = Application("ws://localhost:8080/ws", "realm1")

@app.procedure('com.example.hello')
def hello():
   return "Hello World!"

if __name__ == "__main__":
   app.run()
