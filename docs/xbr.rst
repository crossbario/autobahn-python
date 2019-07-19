XBR Python API
==============

This is the **XBR Lib for Python** API reference documentation, generated from the Python source code
using `Sphinx <http://www.sphinx-doc.org>`_.

.. contents:: :local:

----------


Using the ABI files
-------------------

.. code-block:: python

    import json
    import pkg_resources
    from pprint import pprint

    with open(pkg_resources.resource_filename('xbr', 'contracts/XBRToken.json')) as f:
        data = json.loads(f.read())
        abi = data['abi']
        pprint(abi)


SimpleBuyer
-----------

.. autoclass:: autobahn.xbr.SimpleBuyer
    :members:
        start,
        stop,
        balance,
        open_channel,
        close_channel,
        unwrap

SimpleSeller
------------

.. autoclass:: autobahn.xbr.SimpleSeller
    :members:
        start,
        stop,
        wrap,
        sell,
        public_key,
        add

KeySeries
---------

.. autoclass:: autobahn.xbr.KeySeries
    :members:
        key_id,
        encrypt,
        encrypt_key,
        start,
        stop

IMarketMaker
------------

.. autoclass:: autobahn.xbr.IMarketMaker
    :members:
        status,
        offer,
        revoke,
        quote,
        buy,
        get_payment_channels,
        get_payment_channel


IProvider
---------

.. autoclass:: autobahn.xbr.IProvider
    :members:
        sell


IConsumer
---------

.. autoclass:: autobahn.xbr.IConsumer
    :members:


ISeller
-------

.. autoclass:: autobahn.xbr.ISeller
    :members:
        start,
        wrap


IBuyer
------

.. autoclass:: autobahn.xbr.IBuyer
    :members:
        start,
        unwrap
