# Running the Examples

## Setting up a Router

To run the following examples, you need a WAMP router.

By default, **all examples are set up to use a local Crossbar instance**. You can change the URI used with the environment variable AUTOBAHN_DEMO_ROUTER (by default it is `ws://localhost:8080/ws`). Please see [Running Crossbar Locally] below.


## Creating a virtualenv

If you do not yet have a `virtualenv` to run the examples with, you can do something like:

```shell
git clone https://github.com/crossbario/autobahn-python.git
cd ./autobahn-python/
virtualenv venv-autobahn
source venv-autobahn/bin/activate
pip install -e ./
```

For all the examples, we presume that you are in the `./examples` directory of your autobahn clone, and that the virtualenv in which you've installed Autobahn is activated. If you're running your own Crossbar, it runs from `./examples/router` in its own virtualenv.

The examples usually contain two components:

 * frontend
 * backend

Each component is (usually) provided in two languages:

 * Python
 * JavaScript

The JavaScript version can run on the browser or in NodeJS.

To run an example, you can have two (or three) terminal sessions open with:

 1. frontend
 2. backend
 3. the router (e.g. `crossbar`)

You can also run the frontend/backend in the same shell by putting one in the background. This makes the examples less clear, however:

```shell
python twisted/wamp/pubsub/basic/frontend.py &
python twisted/wamp/pubsub/basic/backend.py
```

Some **things to try**: open a new terminal and run a second frontend;  leave the backend running for a while and then run the frontend; disconnect a frontend and reconnect (re-run) it; mix and match the examples (e.g. twisted/wamp/pubsub/basic/backend.py with twisted/wamp/pubsub/decorators/frontend.py) to see how the topic URIs interact.


## Running Crossbar Locally

If you want to use your own local [Crossbar](http://crossbar.io) instance you must have a Python2-based virtualenv and `pip install crossbar` in it. See also [crossbar.io's platform-specific installation instructions](http://crossbar.io/docs/Local-Installation/) as you may need to install some native libraries as well.

Your crossbar instance will serve the [Autobahn JS](http://autobahn.ws/js) code to browser clients. To easily download a recent release, run the following in the `./examples` directory:

```shell
curl --location -O https://github.com/crossbario/autobahn-js-built/raw/master/autobahn.min.js
```

Once you have crossbar installed, use the provided router configuration in `examples/router/.crossbar/config.json`. Starting your router is then:

```shell
cd ./examples/router
crossbar start
```

There should now be a router listening on `localhost:8080`.

By default all the examples are set up to run against this address. You may set the environment variable `AUTOBAHN_DEMO_ROUTER=ws://localhost:8080/ws` if you configured yours differently from the defaults. Obviously, this environment variable isn't used by in-browser JavaScript so you'll have to change .js files by hand.

If you are running the router successfully, you should see a Crossbar page at `http://localhost:8080/`. We've added enough configuration to serve the HTML, JavaScript and README files from all the examples; you should see a list of links at the page.


## Hosting

Crossbar.io is a WAMP router that can also act as a host for WAMP application components. So, for example, to let Crossbar.io host one of the examples as a backend application component, you can add a `"components"` section to `examples/router/.crossbar/config.json` at the same level as `"realms"`:

```javascript

{
         ...
         "options": {
             "pythonpath": ["../../twisted/wamp/"]
         },
         "components": [
            {
               "type": "class",
               "classname": "pubsub.complex.backend.Component",
               "realm": "crossbardemo"
            }
         ],
         ...
}
```

For the above exact configuration to work you'll need the `./examples/twisted/wamp/` directory in your PYTHONPATH (that configuration is provided in the `"options"` above).
