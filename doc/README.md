AutobahnPython API Reference
============================

The AutobahnPython API reference is available [online](http://autobahn.ws/python/reference/index.html).


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



Deployment to Tavendo Web site
..............................

The generated contents of above folder then needs to
be checked into the

   wwwtavendo

repository in this directory

   tavendo/tavendo/static/autobahn/doc/python

The repository change has to be pulled on the
Web site production host www.tavendo.de
