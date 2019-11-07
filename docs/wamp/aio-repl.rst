# asyncio REPL

.. code-block:: console

    pip install autobahn[asyncio,serialization,encryption]
    python -m asyncio


.. code-block:: python

    import txaio
    txaio.use_asyncio()

    from autobahn.wamp.types import SubscribeOptions, PublishOptions
    from autobahn.asyncio.component import Component, run
    from autobahn.asyncio.util import sleep

    comp = Component(
        transports='ws://localhost:8080/ws',
        realm='realm1'
    )

    counter = 0

    async def on_event(details=None):
        global counter
        print('Event received', details)
        counter += 1

    @comp.on_join
    async def joined(session, details):
        global counter
        print('Session joined', details)
        sub = await session.subscribe(on_event, "io.crossbar.example", options=SubscribeOptions(details=True))
        print('Session subscribed', sub)
        while counter < 10:
            pub = await session.publish("io.crossbar.example", options=PublishOptions(acknowledge=True, exclude_me=False))
            print('Event published', pub)
            await sleep(1)
        session.leave()

    run([comp], start_loop=False)


.. code-block:: console

    (cpy380_1) oberstet@intel-nuci7:~/scm$ python -m asyncio
    asyncio REPL 3.8.0 (default, Oct 18 2019, 13:51:54)
    [GCC 7.4.0] on linux
    Use "await" directly instead of "asyncio.run()".
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import asyncio
    >>> import txaio
    >>> txaio.use_asyncio()
    >>>
    >>> from autobahn.wamp.types import SubscribeOptions, PublishOptions
    >>> from autobahn.asyncio.component import Component, run
    >>> from autobahn.asyncio.util import sleep
    >>>
    >>> comp = Component(
    ...     transports='ws://localhost:8080/ws',
    ...     realm='realm1'
    ... )
    >>>
    >>> async def on_event(details=None):
    ...     print('Event received', details)
    ...
    >>> @comp.on_join
    ... async def joined(session, details):
    ...     print('Session joined', details)
    ...     sub = await session.subscribe(on_event, "io.crossbar.example", options=SubscribeOptions(details=True))
    ...     print('Session subscribed', sub)
    ...     while True:
    ...         pub = await session.publish("io.crossbar.example", options=PublishOptions(acknowledge=True, exclude_me=False))
    ...         print('Event published', pub)
    ...         await sleep(1)
    ...
    >>> run([comp], start_loop=False)
    2019-10-23T09:51:39 connecting once using transport type "websocket" over endpoint "tcp"
    >>> Session joined
    SessionDetails(realm=<realm1>,
                session=6184116312079408,
                authid=<F7FK-QQV7-F4W5-CNGX-QYHN-PLPV>,
                authrole=<anonymous>,
                authmethod=anonymous,
                authprovider=static,
                authextra={'x_cb_node_id': None, 'x_cb_peer': 'tcp4:127.0.0.1:27192', 'x_cb_pid': 21008},
                serializer=<cbor>,
                resumed=None,
                resumable=None,
                resume_token=None)
    Session subscribed Subscription(id=5518068544367384, is_active=True)
    Event published Publication(id=4151012151142491, was_encrypted=False)
    Event received EventDetails(subscription=Subscription(id=5518068544367384, is_active=True), publication=4151012151142491, publisher=None, publisher_authid=None, publisher_authrole=None, topic=<io.crossbar.example>, retained=None, enc_algo=None, forward_for=None)
    Event published Publication(id=3676179573074954, was_encrypted=False)
    Event received EventDetails(subscription=Subscription(id=5518068544367384, is_active=True), publication=3676179573074954, publisher=None, publisher_authid=None, publisher_authrole=None, topic=<io.crossbar.example>, retained=None, enc_algo=None, forward_for=None)
    Event published Publication(id=1831205249541796, was_encrypted=False)
    Event received EventDetails(subscription=Subscription(id=5518068544367384, is_active=True), publication=1831205249541796, publisher=None, publisher_authid=None, publisher_authrole=None, topic=<io.crossbar.example>, retained=None, enc_algo=None, forward_for=None)
    Event published Publication(id=6028323371359219, was_encrypted=False)
    Event received EventDetails(subscription=Subscription(id=5518068544367384, is_active=True), publication=6028323371359219, publisher=None, publisher_authid=None, publisher_authrole=None, topic=<io.crossbar.example>, retained=None, enc_algo=None, forward_for=None)
    Event published Publication(id=211622895505210, was_encrypted=False)
    Event received EventDetails(subscription=Subscription(id=5518068544367384, is_active=True), publication=211622895505210, publisher=None, publisher_authid=None, publisher_authrole=None, topic=<io.crossbar.example>, retained=None, enc_algo=None, forward_for=None)
    Event published Publication(id=6235103334995396, was_encrypted=False)
    Event received EventDetails(subscription=Subscription(id=5518068544367384, is_active=True), publication=6235103334995396, publisher=None, publisher_authid=None, publisher_authrole=None, topic=<io.crossbar.example>, retained=None, enc_algo=None, forward_for=None)
    Event published Publication(id=2482469817470784, was_encrypted=False)
    Event received EventDetails(subscription=Subscription(id=5518068544367384, is_active=True), publication=2482469817470784, publisher=None, publisher_authid=None, publisher_authrole=None, topic=<io.crossbar.example>, retained=None, enc_algo=None, forward_for=None)
    2019-10-23T09:51:46 Shutting down due to SIGINT
    (cpy380_1) oberstet@intel-nuci7:~/scm$
