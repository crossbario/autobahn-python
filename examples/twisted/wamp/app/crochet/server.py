import logging

from flask import Flask
from crochet import setup, run_in_reactor, wait_for
setup()

from autobahn.twisted.wamp import Application

wapp = Application()

@wapp.register('com.example.square')
def square(x):
   print("square() called with {}".format(x))
   return x * x

@wait_for(timeout = 1)
def call_square(x):
   return wapp.session.call('com.example.square', x)


from twisted.internet.defer import returnValue
from autobahn.twisted.util import sleep

@wapp.register('com.example.slowsquare')
def slowsquare(x):
   print("slowsquare() called with {}".format(x))
   yield sleep(2)
   returnValue(x * x)

@wait_for(timeout = 10)
def call_slowsquare(x):
   return wapp.session.call('com.example.slowsquare', x)


app = Flask(__name__)

@app.route('/')
def index():
   x = 2
   res = call_slowsquare(x)
   #res = call_square(x)
   return "{} squared is {}".format(x, res)


@run_in_reactor
def start_wamp():
   wapp.run("ws://localhost:9000", "realm1", standalone = True, start_reactor = False)


if __name__ == '__main__':
   import sys
   logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
   start_wamp()
   app.run()
