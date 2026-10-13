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
     - 64.4 MB
     - 64.4 MB
     - 64.3 MB
   * - cryptography
     - ``import cryptography``
     - 64.4 MB
     - 64.3 MB
     - 64.4 MB
   * -
     - ``from cryptography.hazmat.primitives import hashes``
     - 72.0 MB
     - 72.1 MB
     - 72.0 MB
   * - numpy
     - ``import numpy``
     - 88.2 MB †
     - 88.1 MB †
     - 88.3 MB †
   * - asyncio
     - ``import asyncio``
     - 78.7 MB
     - 78.7 MB
     - 78.8 MB
   * - twisted
     - ``from twisted.internet import reactor``
     - 106.0 MB
     - 106.1 MB
     - 106.0 MB
   * - txaio
     - ``import txaio``
     - 64.3 MB
     - 64.3 MB
     - 64.4 MB
   * -
     - ``import txaio; txaio.use_asyncio()``
     - 79.0 MB
     - 79.0 MB
     - 79.1 MB
   * -
     - ``import txaio; txaio.use_twisted()``
     - 87.9 MB
     - 88.0 MB
     - 88.0 MB
   * - autobahn
     - ``import autobahn``
     - 64.3 MB
     - 88.0 MB †
     - 64.4 MB
   * -
     - ``txaio.use_asyncio(); import autobahn.wamp``
     - 93.0 MB
     - 112.2 MB †
     - 93.7 MB
   * -
     - ``txaio.use_twisted(); import autobahn.wamp``
     - 100.1 MB
     - 118.9 MB †
     - 100.6 MB
   * -
     - ``import autobahn.asyncio.websocket``
     - 98.4 MB
     - 117.2 MB †
     - 99.1 MB
   * -
     - ``import autobahn.twisted.websocket``
     - 113.2 MB
     - 132.4 MB †
     - 113.7 MB
   * - daphne
     - ``from daphne.server import Server``
     - 114.7 MB
     - 135.8 MB †
     - 115.5 MB
   * - crossbar
     - ``from crossbar.edge.worker.router import ExtRouterController``
     - n/a
     - 240.1 MB †
     - 224.0 MB †
