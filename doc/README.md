# Autobahn|Python Documentation

The **Autobahn**|Python documentation is generated using [Sphinx](http://sphinx.pocoo.org/) and available [online](http://autobahn.ws/python).

## Generate the Docs

To generate the documentation yourself you will need to have the following installed

```sh
pip install sphinx
pip install sphinx-bootstrap-theme
pip install sphinxcontrib-spelling
pip install repoze.sphinx.autointerface
```

and then

```sh
cd doc
make html
```

This will create the documentation under the directory `_build`.


## Publishing

> Note: this section is only relevant for administrators of the [Autobahn web site](http://autobahn.ws/).

To publish to the Autobahn web site ([here](http://autobahn.ws/python/reference/)), you will need [SCons](http://scons.org/) and [Taschenmesser](https://pypi.python.org/pypi/taschenmesser).

Then do

```sh
scons
```

to build the docs and

```sh
scons publish
```

to build and publish the docs and

```sh
scons -uc
```

to cleanup.
