This folder contains a minimal skeleton of a **WAMPlet** application component.

A **WAMPlet** can be thought of a reusable application component that can be deployed dynamically as needed.

Get started by copying this folder and it's contents and begin by modifying a working base line.

> This example is using **Twisted**. You can find the **asyncio** variant [here](https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/wamp/wamplet/wamplet1)
> 

## WAMPlet Development

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

## WAMPlet Installation and Distribution

For installation as a local WAMPlet in your Python package directory

```shell
python setup.py install
```

Installation of the WAMPlet allows **Crossbar**.io to find your WAMPlet even if no explicit Python paths are configured.

Above will also leave you an **.egg** file with your WAMPlet packaged up as a redistributable egg file that can be installed on other hosts. You can even publish your WAMPlet on the [Python Package Index](https://pypi.python.org).

To make *automatic WAMPlet discovery* work, the [Setup file](setup.py) contains an item

```python
   entry_points = {
      'autobahn.twisted.wamplet': [
         'component1 = wamplet1.component1:make'
      ],
   },
```

where `entry_points` must have an entry `autobahn.twisted.wamplet` that lists application components the package exposes.

Here, the factory function `make()` in the module `component1` in the package `wamplet1` is to be exposed as the WAMPlet `component1`.
