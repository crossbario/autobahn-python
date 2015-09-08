# Developers Guide

This is a guide for developers hacking on AutobahnPython.

## Python 2 / 3

AutobahnPython supports both Python 2 and Python 3.

* http://python-future.org/compatible_idioms.html

## Coding Style

> The rules and text here follows [Django](https://docs.djangoproject.com/en/1.8/internals/contributing/writing-code/coding-style/).

Please follow these coding standards when writing code for inclusion in AutobahnPython.

1. Unless otherwise specified, follow [PEP 8](https://www.python.org/dev/peps/pep-0008). However, remember that PEP 8 is only a guide, so respect the style of the surrounding code as a primary goal.
2. Use 4 spaces for indents, CamelCase for classes and snake_case for variables, functions and members. Everything that is not part of the public API must be prefixed with a single underscore.
3. Rule 2, applies to the public API exposed by AutobahnPython for **both** Twisted and asyncio users as well as everything within the library itself.
4. An exception to PEP 8 is our rules on line lengths. Don’t limit lines of code to 79 characters if it means the code looks significantly uglier or is harder to read. We allow up to 119 characters as this is the width of GitHub code review; anything longer requires horizontal scrolling which makes review more difficult. Documentation, comments, and docstrings should be wrapped at 79 characters, even though PEP 8 suggests 72.
5. Use hanging indents with each argument strictly on a separate line to limit line length (see also [here](http://stackoverflow.com/questions/15435811/what-is-pep8s-e128-continuation-line-under-indented-for-visual-indent/15435837#15435837) for an explanation why this is PEP8 compliant):

```python
raise ApplicationError(
    u"crossbar.error.class_import_failed",
    u"Session not derived of ApplicationSession"
)
```

Code must be checked for adherence to above rules using [flake8](https://flake8.readthedocs.org/en/2.4.1/):

    flake8 --max-line-length=119 autobahn

## Release Process

1. Travis is fully green
2. Run AutobahnTestsuite
3. Build and spellcheck the docs
4. Update the [doc/changelog.rst](doc/changelog.rst)
5. Tag the release
6. Publish the package to PyPi
7. Publish the docs to the Autobahn Web site
8. Announce on mailing list


### Documentation

#### Requirements

You will need to have some stuff installed to generate the docs:

```
cd ~/scm/autobahn/AutobahnPython/doc
install_deps
```

Additionally, install [SCons](http://scons.org/).

#### Test

To generate and publish the documentation to [here](http://autobahn.ws/python/):

```
cd ~/scm/autobahn/AutobahnPython
make clean
make install
cd doc
make test
```

and open [http://localhost:8080](http://localhost:8080).

#### Publish

To generate and publish the documentation to [here](http://autobahn.ws/python/):

```
cd ~/scm/autobahn/AutobahnPython
make clean
make install
cd doc
make publish
```

> The docs are published to the Autobahn Web site, which is hosted on a AWS S3 bucket is owned by Tavendo, and hence the publish can only be done by Tavendo.

### WebSocket Test Reports

[AutobahnTestsuite](http://autobahn.ws/testsuite/) provides a fully automated test suite to verify client and server implementations of the WebSocket Protocol for specification conformance and implementation robustness.

We use that to test AutobahnPython at the WebSocket level, both client and server mode.

**AutobahnPython has 100% strictly green passes on all of the >500 tests. If there is only one test failing or not strictly green, then don't do a release and fix the issue before.**

> The testsuite and the testee should both be run under PyPy on Ubuntu for now, as this is one of the most important targets. In the future, we might extend that to more platforms and Pythons.

#### Installation

Install PyPy and create a fresh virtualenv:

```
cd $HOME
wget https://bitbucket.org/pypy/pypy/downloads/pypy-2.6.1-linux64.tar.bz2
tar xvf pypy-2.6.1-linux64.tar.bz2
wget https://bootstrap.pypa.io/get-pip.py
./pypy-2.6.1-linux64/bin/pypy get-pip.py
./pypy-2.6.1-linux64/bin/pip install virtualenv
./pypy-2.6.1-linux64/bin/virtualenv $HOME/pypy261_1
```

Install AutobahnPython from source (the sources that is to be released!) and AutobahnTestsuite from PyPi:

```
source $HOME/pypy261_1/bin/activate
cd ~/scm/tavendo/autobahn/AutobahnPython
make install
pip install autobahntestsuite
```

#### Prepare for testing

We'll be generating reports in `/tmp/reports`. Make sure to remove any old stuff:

```
rm -rf reports
rm -f fuzzing*.json
```

> The `json` files are the test specs that control what tests to run. When there are no test spec files, the testsuite will generate default ones, which is what we want.

Two test runs need to be performed now: one testing AutobahnPython acting as a client, and one where is acts as a server.

#### Testing WebSocket client mode

Open a first terminal and run the following to start the WebSocket fuzzing server:

```
cd /tmp
source $HOME/pypy261_1/bin/activate
wstest -m fuzzingserver
```

Open a second terminal and run the following to start the WebSocket testee client:

```
source $HOME/pypy261_1/bin/activate
wstest -m testeeclient -w ws://127.0.0.1:9001
```

Get some coffee. It'll take some minutes. When it's done, open `/tmp/reports/servers/index.html` in you browser.

#### Testing WebSocketserver mode

Open a first terminal and run the following to start the WebSocket testee server:

```
source $HOME/pypy261_1/bin/activate
wstest -m testeeserver -w ws://127.0.0.1:9001
```

Open a second terminal and run the following to start the WebSocket fuzzing client:

```
cd /tmp
source $HOME/pypy261_1/bin/activate
wstest -m fuzzingclient -w ws://127.0.0.1:9001
```

Get some coffee. It'll take some minutes. When it's done, open `/tmp/reports/clients/index.html` in you browser.

#### Upload the results

To upload the results, you will need the [AWS CLI](http://aws.amazon.com/documentation/cli/).

To install:

```
pip install --upgrade awscli
```

We are using the [high-level commands](http://docs.aws.amazon.com/cli/latest/userguide/using-s3-commands.html).

To upload:

```
aws --region eu-west-1 s3 sync \
    /tmp/reports \
    s3://autobahn.ws/python/testreport \
    --delete \
    --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
```

> The above S3 bucket is owned by Tavendo, and hence the upload can only be done by Tavendo.

After the upload has finished, check the live pages:

* [Client Mode Reports](http://autobahn.ws/python/testreport/clients/index.html)
* [Server Mode Reports](http://autobahn.ws/python/testreport/servers/index.html)


## Roadmap

### 0.10.6

[Milestone for 0.10.6](https://github.com/tavendo/AutobahnPython/milestones/0.10.6)

* Automatic reconnection
* Configurable WAMP connecting transports
* WAMP Connection abstration
* Authentication

**0.10** will get into "maintenance mode" after **0.10.6**. We'll have a maintenance branch for that over some time. The new development will be based on **0.11** (see below).

### 0.11.0

[Milestone for 0.11.0](https://github.com/tavendo/AutobahnPython/milestones/0.11.0)

* new main development line with new, long-term API
