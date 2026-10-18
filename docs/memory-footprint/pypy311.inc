.. list-table::
   :header-rows: 1
   :widths: 12 46 14 14 14

   * - group
     - import
     - 25.10.2
     - 26.7.1
     - 26.10.1
   * - interpreter
     - ``bare interpreter``
     - 65.0 MB
     - 64.9 MB
     - 64.9 MB
   * - cryptography
     - ``import cryptography``
     - 64.9 MB
     - 65.0 MB
     - 65.0 MB
   * -
     - ``from cryptography.hazmat.primitives import hashes``
     - 72.5 MB
     - 72.7 MB
     - 72.7 MB
   * - numpy
     - ``import numpy``
     - 88.9 MB †
     - 88.8 MB †
     - 88.8 MB †
   * - asyncio
     - ``import asyncio``
     - 79.5 MB
     - 79.5 MB
     - 79.4 MB
   * - twisted
     - ``from twisted.internet import reactor``
     - 106.8 MB
     - 106.8 MB
     - 106.8 MB
   * - txaio
     - ``import txaio``
     - 65.0 MB
     - 65.0 MB
     - 65.0 MB
   * -
     - ``import txaio; txaio.use_asyncio()``
     - 79.8 MB
     - 79.7 MB
     - 79.8 MB
   * -
     - ``import txaio; txaio.use_twisted()``
     - 88.7 MB
     - 88.7 MB
     - 88.8 MB
   * - autobahn
     - ``import autobahn``
     - 64.9 MB
     - 88.7 MB †
     - 65.0 MB
   * -
     - ``txaio.use_asyncio(); import autobahn.wamp``
     - 93.8 MB
     - 113.0 MB †
     - 94.4 MB
   * -
     - ``txaio.use_twisted(); import autobahn.wamp``
     - 100.8 MB
     - 119.7 MB †
     - 101.3 MB
   * -
     - ``import autobahn.asyncio.websocket``
     - 99.1 MB
     - 117.9 MB †
     - 99.8 MB
   * -
     - ``import autobahn.twisted.websocket``
     - 114.0 MB
     - 134.4 MB †
     - 114.6 MB
   * - daphne
     - ``from daphne.server import Server``
     - 115.6 MB
     - 136.5 MB †
     - 116.3 MB
   * - crossbar
     - ``from crossbar.edge.worker.router import ExtRouterController``
     - n/a
     - 240.6 MB †
     - 216.5 MB †
