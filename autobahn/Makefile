all: clean build upload

install:
	python setup.py install

clean:
	rm -rf ./autobahn.egg-info
	rm -rf ./build
	rm -rf ./dist

build:
	python setup.py bdist_egg

upload:
	scp dist/*.egg oberstet@www.tavendo.de:/usr/local/www/pypi

publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_egg upload
	python setup.py bdist_wininst upload
