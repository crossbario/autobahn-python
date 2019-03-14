#
# USAGE: clear && time make clean build cloc
#

# input .fbs files for schema
FILES=*.fbs

# flatc compiler to use
FLATC=flatc


default:
	@echo "targets: clean version build"

clean:
	-rm -rf ./_build

version:
	$(FLATC) --version

build: bfbs cpp csharp go java js php python ts


cloc: build
	cloc --read-lang-def=cloc.def --exclude-dir=_build .
	cloc ./_build


# generate schema type library (.bfbs binary)
bfbs:
	$(FLATC) -o ./_build/schema/ --binary --schema --bfbs-comments --bfbs-builtin-attrs $(FILES)


# generate schema language bindings
cpp:
	$(FLATC) -o ./_build/cpp/ --cpp $(FILES)

csharp:
	$(FLATC) -o ./_build/csharp/ --csharp $(FILES)

go:
	$(FLATC) -o ./_build/go/ --go $(FILES)

java:
	$(FLATC) -o ./_build/java/ --java $(FILES)

js:
	$(FLATC) -o ./_build/js/ --js $(FILES)

php:
	$(FLATC) -o ./_build/php/ --php $(FILES)

python:
	$(FLATC) -o ./_build/python/ --python $(FILES)
	find ./_build/python/

ts:
	$(FLATC) -o ./_build/ts/ --ts $(FILES)
