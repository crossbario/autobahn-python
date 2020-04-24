The XBR Protocol
================

|Docs (on CDN)| |Docs (on S3)| |Travis| |Coverage|

This repository contains the XBR smart contracts, with Ethereum as
target blockchain, and Solidity as implementation language for the **XBR
Protocol**.

Please see the `documentation <https://xbr.network/docs/index.html>`__
for more information.

XBR Client Library
------------------

The XBR Protocol - at its core - is made of the XBR smart contracts, and
the primary artifacts built are the contract ABI files (in
``./build/contracts/*.json``).

Technically, these files are all you need to interact and talk to the
XBR smart contracts.

However, doing it that way (using the raw ABI files and presumably some
generic Ethereum library) is cumbersome and error prone to maintain.

Therefore, we create wrapper libraries for XBR, currently for Python and
JavaScript, that make interaction with XBR contract super easy.

The libraries are available here:

-  `XBR client library for Python <https://pypi.org/project/xbr/>`__
-  `XBR client library for
   JavaScript/Browser <https://xbr.network/lib/xbr.min.js>`__
-  `XBR client library for
   JavaScript/NodeJS <https://www.npmjs.org/package/xbr>`__

XBR
~~~

Autobahn includes support for `XBR <https://xbr.network/>`__. To install use this flavor:

* ``xbr``:

To install:

.. code:: console

    pip install autobahn[xbr]

or (Twisted, with more bells an whistles)

.. code:: console

    pip install autobahn[twisted,encryption,serialization,xbr]

or (asyncio, with more bells an whistles)

.. code:: console

    pip install autobahn[asyncio,encryption,serialization,xbr]

-----

Copyright Crossbar.io Technologies GmbH. Licensed under the `Apache 2.0
license <https://www.apache.org/licenses/LICENSE-2.0>`__.

.. |Docs (on CDN)| image:: https://img.shields.io/badge/docs-cdn-brightgreen.svg?style=flat
   :target: https://xbr.network/docs/index.html
.. |Docs (on S3)| image:: https://img.shields.io/badge/docs-s3-brightgreen.svg?style=flat
   :target: https://s3.eu-central-1.amazonaws.com/xbr.foundation/docs/index.html
.. |Travis| image:: https://travis-ci.org/xbr/xbr-protocol.svg?branch=master
   :target: https://travis-ci.org/xbr/xbr-protocol
.. |Coverage| image:: https://img.shields.io/codecov/c/github/xbr/xbr-protocol/master.svg
   :target: https://codecov.io/github/xbr/xbr-protocol
