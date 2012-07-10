all: clean build upload

install:
	python setup.py install

clean:
	rm -rf ./autobahn.egg-info
	rm -rf ./build
	rm -rf ./dist
	find . -name "*.pyc" -exec rm -f {} \;

build:
	python setup.py bdist_egg

deploy: clean
	/opt/python/bin/python setup.py bdist_egg
	sudo cp dist/*.egg /usr/local/www/static/autobahnws/eggs/

publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_egg upload
	python setup.py bdist_wininst upload
