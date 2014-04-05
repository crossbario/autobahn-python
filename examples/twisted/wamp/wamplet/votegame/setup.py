from setuptools import setup, find_packages

setup(
   name = 'votegame',
   version = '0.0.1',
   description = 'VoteGame Service WAMPlet',
   platforms = ['Any'],
   packages = find_packages(),
   entry_points = {
      'autobahn.twisted.wamplet': [
         'backend = votegame.backend:make'
      ],
   },
   zip_safe=False,
)