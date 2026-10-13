.. list-table::
   :header-rows: 1
   :widths: 12 46 14 14 14

   * - group
     - import
     - 25.10.2
     - 26.7.1
     - fix_1983
   * - interpreter
     - ``bare interpreter``
     - 12.0 MB
     - 12.0 MB
     - 12.0 MB
   * - cryptography
     - ``import cryptography``
     - 11.9 MB
     - 11.9 MB
     - 11.9 MB
   * -
     - ``from cryptography.hazmat.primitives import hashes``
     - 19.8 MB
     - 19.9 MB
     - 19.9 MB
   * - numpy
     - ``import numpy``
     - 28.4 MB †
     - 28.5 MB †
     - 28.5 MB †
   * - asyncio
     - ``import asyncio``
     - 18.1 MB
     - 18.1 MB
     - 18.2 MB
   * - twisted
     - ``from twisted.internet import reactor``
     - 43.3 MB
     - 43.4 MB
     - 43.4 MB
   * - txaio
     - ``import txaio``
     - 12.0 MB
     - 12.1 MB
     - 12.1 MB
   * -
     - ``import txaio; txaio.use_asyncio()``
     - 18.2 MB
     - 18.3 MB
     - 18.3 MB
   * -
     - ``import txaio; txaio.use_twisted()``
     - 26.5 MB
     - 26.5 MB
     - 26.5 MB
   * - autobahn
     - ``import autobahn``
     - 12.0 MB
     - 28.8 MB †
     - 12.0 MB
   * -
     - ``txaio.use_asyncio(); import autobahn.wamp``
     - 31.9 MB
     - 47.6 MB †
     - 33.2 MB
   * -
     - ``txaio.use_twisted(); import autobahn.wamp``
     - 38.4 MB
     - 52.8 MB †
     - 39.8 MB
   * -
     - ``import autobahn.asyncio.websocket``
     - 36.2 MB
     - 51.1 MB †
     - 37.8 MB
   * -
     - ``import autobahn.twisted.websocket``
     - 48.9 MB
     - 63.1 MB †
     - 50.2 MB
   * - daphne
     - ``from daphne.server import Server``
     - 50.2 MB
     - 64.6 MB †
     - 51.7 MB
   * - crossbar
     - ``from crossbar.edge.worker.router import ExtRouterController``
     - n/a
     - 144.7 MB †
     - 144.8 MB †
