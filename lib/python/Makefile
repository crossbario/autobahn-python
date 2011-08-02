all: clean egg install

egg:
	python setup.py bdist_egg

install:
	easy_install -v ./dist/autobahn-0.2-py2.6.egg

clean:
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./autobahn.egg-info
