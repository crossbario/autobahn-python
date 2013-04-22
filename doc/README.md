AutobahnPython API Reference
============================

The AutobahnPython API reference is available [online](http://autobahn.ws/python/reference).


The documentation is generated automatically from the Python source file via [Sphinx](http://sphinx.pocoo.org/).

To generate the documentation yourself, you will need to install Sphinx:

	easy_install sphinx

and then

	cd doc
	make html

This will create the documentation under

	_build/html

To adjust the AutobahnPython version printed in the documentation, edit

	conf.py

for

	version = '0.5'
	release = '0.5.2'
