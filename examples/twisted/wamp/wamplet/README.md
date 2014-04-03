This folder contains a minimal skeleton of a **WAMPlet** application component.

Get started by copying this folder and it's contents and begin by modifying a working base line.

All the interesting bits with our application component are in [here](wamplet1/component1.py).

For development, just run that file

```shell
python wamplet1/component1.py
```

For installation as a local plugin in your Python package directory

```shell
python setup.py install
```

This will also leave you an **.egg** file with your plugin package as a redistributable egg file.

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
