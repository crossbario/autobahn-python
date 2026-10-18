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
     - 12.0 MB
     - 12.0 MB
     - 12.0 MB
   * - cryptography
     - ``import cryptography``
     - 12.0 MB
     - 12.0 MB
     - 12.1 MB
   * -
     - ``from cryptography.hazmat.primitives import hashes``
     - 20.0 MB
     - 19.9 MB
     - 19.9 MB
   * - numpy
     - ``import numpy``
     - 28.5 MB †
     - 28.5 MB †
     - 28.6 MB †
   * - asyncio
     - ``import asyncio``
     - 18.2 MB
     - 18.2 MB
     - 18.2 MB
   * - twisted
     - ``from twisted.internet import reactor``
     - 43.5 MB
     - 43.5 MB
     - 43.5 MB
   * - txaio
     - ``import txaio``
     - 12.1 MB
     - 12.1 MB
     - 12.1 MB
   * -
     - ``import txaio; txaio.use_asyncio()``
     - 18.3 MB
     - 18.3 MB
     - 18.4 MB
   * -
     - ``import txaio; txaio.use_twisted()``
     - 26.6 MB
     - 26.6 MB
     - 26.6 MB
   * - autobahn
     - ``import autobahn``
     - 12.1 MB
     - 28.9 MB †
     - 12.1 MB
   * -
     - ``txaio.use_asyncio(); import autobahn.wamp``
     - 32.0 MB
     - 47.8 MB †
     - 33.3 MB
   * -
     - ``txaio.use_twisted(); import autobahn.wamp``
     - 38.6 MB
     - 52.9 MB †
     - 39.9 MB
   * -
     - ``import autobahn.asyncio.websocket``
     - 36.3 MB
     - 51.2 MB †
     - 38.0 MB
   * -
     - ``import autobahn.twisted.websocket``
     - 49.0 MB
     - 63.3 MB †
     - 50.4 MB
   * - daphne
     - ``from daphne.server import Server``
     - 50.4 MB
     - 64.8 MB †
     - 51.8 MB
   * - crossbar
     - ``from crossbar.edge.worker.router import ExtRouterController``
     - n/a
     - 145.2 MB †
     - 145.2 MB †
