from setuptools import setup, find_packages

setup(
   name = 'votegame',
   version = '0.0.2',
   description = 'VoteGame Service WAMPlet',
   platforms = ['Any'],
   packages = find_packages(),
   include_package_data = True,
   zip_safe = False,
   entry_points = {
      'autobahn.twisted.wamplet': [
         'backend = votegame.backend:make'
      ],
   }
)