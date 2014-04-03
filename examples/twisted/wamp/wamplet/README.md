This folder contains a minimal skeleton of a **WAMPlet** application component.

Get started by copying this folder and it's contents and begin by modifying a working base line.

## Plugin Development

All the interesting bits with our application component are in [here](wamplet1/component1.py).

For development, start a locally running WAMP router, e.g. **Crossbar**.io:

```shell
cd $HOME
crossbar init
crossbar start
```

and in a second terminal run the file containing the application component:

```shell
python wamplet1/component1.py
```

## Plugin Installation and Distribution

For installation as a local plugin in your Python package directory

```shell
python setup.py install
```

Installation of the plugin allows **Crossbar**.io to find your plugin even if no explicit Python paths are configured.

Above will also leave you an **.egg** file with your plugin packaged up as a redistributable egg file.

To make that work, the [Setup file](setup.py) contains an item

```python
   entry_points = {
      'autobahn.twisted.wamplet': [
         'component1 = wamplet1.component1:make'
      ],
   },
```

where `entry_points` must have an entry `autobahn.twisted.wamplet` that lists application components the package exposes.

Here, the factory function `make()` in the module `component1` in the package `wamplet1` is to be exposed as the WAMPlet `component1`.
