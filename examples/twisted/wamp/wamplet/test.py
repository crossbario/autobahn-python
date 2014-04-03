import os
import sys
import pkg_resources  # setuptools specific

OPERATORS = {}
ENTRYPOINT = 'plugin_tutorial.s_tools'  # same name as in setup.py

class Plugin(object):
   _shared_states = {}
   def __init__(self):
      self.__dict__ = self._shared_states

def init_plugins(expression):
   Plugin().expression = expression  # fixing the wart
   load_plugins()

def load_plugins():
   for entrypoint in pkg_resources.iter_entry_points(ENTRYPOINT):
      plugin_class = entrypoint.load()
      OPERATORS[plugin_class.symbol] = plugin_class


for entrypoint in pkg_resources.iter_entry_points('autobahn.twisted.wamplet'):
   print entrypoint
   print entrypoint.name
   print entrypoint.module_name
   print entrypoint.dist
   print dir(entrypoint)
   res = entrypoint.load()
   print res
   r = res(None)
   print r
   #print res.symbol
