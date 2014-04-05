from setuptools import setup, find_packages

setup(
   name = 'wampirc',
   version = '0.0.1',
   description = 'An IRC bot service component.',
   platforms = ['Any'],
   packages = find_packages(),
   entry_points = {
      'autobahn.twisted.wamplet': [
         'bot = wampirc.service:make'
      ],
   },
   zip_safe=False,
)