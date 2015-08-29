This example demonstrates the use of databases (e.g. SQLite or PostgreSQL) from WAMP application components. The example is a simple voting app packaged up as a **WAMPlet** application component.

A **WAMPlet** can be thought of a reusable application component that can be deployed dynamically as needed.

Get started by copying this folder and it's contents and begin by modifying a working base line.

## Try it

All the interesting bits with our application component are in [here](votegame/backend.py).

For development, start a locally running WAMP router, e.g. **Crossbar**.io:

```shell
cd $HOME
crossbar init
crossbar start
```

and in a second terminal run the file containing the application component:

```shell
python votegame/backend.py
```

In your browser, open the file `votegame/web/index.html`.

## Deploying

You can deploy your WAMPlet to a WAMPlet container for production.

A configuration for [**Crossbar**.io](http://crossbar.io) which runs a WAMP router, loads the VoteGame backend component and serves static Web content from the VoteGame package can be found [here](config.json).