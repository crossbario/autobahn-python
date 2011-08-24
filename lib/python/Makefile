all: clean egg install

egg:
	python setup.py bdist_egg

install:
	easy_install -v ./dist/autobahn-0.4.0-py2.7.egg

clean:
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./autobahn.egg-info
