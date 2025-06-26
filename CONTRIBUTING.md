# Developers Guide

This is a guide for developers hacking on AutobahnPython.

## Python 2 / 3

AutobahnPython supports both Python 2 and Python 3.

- http://python-future.org/compatible_idioms.html

## Coding Style

> The rules and text here follows
> [Django](https://docs.djangoproject.com/en/1.8/internals/contributing/writing-code/coding-style/).

Please follow these coding standards when writing code for
inclusion in AutobahnPython.

1. Unless otherwise specified, follow
   [PEP 8](https://www.python.org/dev/peps/pep-0008). However,
   remember that PEP 8 is only a guide, so respect the style of
   the surrounding code as a primary goal.
2. Use 4 spaces for indents.
3. Use CamelCase for classes and snake_case for variables,
   functions and members, and UPPERCASE for constants.
4. Everything that is not part of the public API must be prefixed
   with a single underscore.
5. Rules 3 and 4 apply to the public API exposed by
   AutobahnPython for **both** Twisted and asyncio users as well
   as everything within the library itself.
6. An exception to PEP 8 is our rules on line lengths. Don’t
   limit lines of code to 79 characters if it means the code
   looks significantly uglier or is harder to read. We allow up
   to 119 characters as this is the width of GitHub code review;
   anything longer requires horizontal scrolling which makes
   review more difficult. Documentation, comments, and docstrings
   should be wrapped at 79 characters, even though PEP 8
   suggests 72.
7. Use hanging indents with each argument strictly on a separate
   line to limit line length (see also
   [here](http://stackoverflow.com/questions/15435811/what-is-pep8s-e128-continuation-line-under-indented-for-visual-indent/15435837#15435837)
   for an explanation why this is PEP8 compliant):

```python
raise ApplicationError(
    u"crossbar.error.class_import_failed",
    u"Session not derived of ApplicationSession"
)
```

Code must be checked for PEP8 compliance using
[flake8](https://flake8.readthedocs.org/en/2.4.1/) with
[pyflakes](https://pypi.python.org/pypi/pyflakes) and
[pep8-naming](http://pypi.python.org/pypi/pep8-naming) plugins
installed:

    flake8 autobahn

There is no automatic checker for rule 4, hence reviewers of PRs
should manually inspect code for compliance.

Note that AutobahnPython currently does not fully comply to above
rules:

```console
(python279_1)oberstet@thinkpad-t430s:~/scm/autobahn/AutobahnPython$ flake8 --statistics -qq autobahn
388     E501 line too long (131 > 119 characters)
4       N801 class names should use CapWords convention
296     N802 function name should be lowercase
80      N803 argument name should be lowercase
1       N805 first argument of a method should be named 'self'
69      N806 variable in function should be lowercase
```

It also does not comply fully to rule 4. This will get addressed
in the next major release (0.11).

### API Stability Level

We distinbuish three levels of API in AutobahnPython:

1. public user API
2. private library API
3. private non-API

The **Public User API** is what (third party) application
developers should rely on _exclusively_. It is the only API we
make any kind of stability guarantees. The **Public User API** is

- defined via ABC interfaces (when that makes sense)
- has docstring including the tag `@public`
- has docs generated and published
- follow the PEP8 naming convention (stuff does not start with a
  `_`)
- is versioned using semver

The **Private Library API** is for library internal use, crossing
files, classes and such. Application developers should not use
this API, and we make no guarantees whatsoever. Any minor version
bump might change anything here. We might rip out anything here
or add stuff. This API may be used from our companion projects
(Autobahn <-> Crossbar). The reason **we** are allowed to use
that API is simple: we know what we are doing, and we are able to
coordinate across projects and can rectify issues that arise.
This **Private Library API** does NOT mark things with a starting
`_`.

The **Private non-API** isn't an API at all: like class members
which may only be used within that class, or functions which may
only be used in the same module where the function is defined.

### Public API

The new rule for the public API is simple: if something is
exported from the modules below, then it is public. Otherwise
not.

- [Top](https://github.com/crossbario/autobahn-python/blob/master/autobahn/__init__.py)
- [WebSocket](https://github.com/crossbario/autobahn-python/blob/master/autobahn/websocket/__init__.py)
- [WAMP](https://github.com/crossbario/autobahn-python/blob/master/autobahn/wamp/__init__.py)
- [Asyncio](https://github.com/crossbario/autobahn-python/blob/master/autobahn/asyncio/__init__.py)
- [Twisted](https://github.com/crossbario/autobahn-python/blob/master/autobahn/twisted/__init__.py)

### Cross-platform Considerations

Autobahn supports many different platforms and both major async
frameworks. One thing that helps with this is the
[txaio](https://github.com/crossbario/txaio) library. This is
used for all Deferred/Future operations throughout the code and
more recently for logging.

Here is a recommended way to do **logging**:

```python
class Foo(object):
    log = txaio.make_logger()

    def connect(self):
        try:
            self.log.info("Connecting")
            raise Exception("an error")
        except:
            fail = txaio.create_failure()
            self.log.error("Connection failed: {msg}", msg=txaio.failure_message(fail))
            self.log.debug("{traceback}", traceback=txaio.failure_format_traceback(fail))
            # Exception instance in fail.value
```

Note that `create_failure()` can (and should) be called without
arguments when inside an `except` block; this will give it a
valid traceback instance. The only attribute you can depend on is
`fail.value` which is the `Exception` instance. Otherwise use
`txaio.failre_*` methods.

How to **handler async methods** with txaio:

```python
f = txaio.as_future(mightReturnDeferred, 'arg0')

def success(result):
    print("It worked! {}".format(result))

def error(fail):
    print("It failed! {}".format(txaio.failure_message(fail)))
txaio.add_callbacks(f, success, error)
```

Either the success or error callback can be `None` (e.g. if you
just need to add an error-handler). `fail` must implement
`txaio.IFailedFuture` (but only that; don't depend on any other
methods). You cannot use `@asyncio.coroutine` or
`@inlineCallbacks`.

### Use of assert vs Exceptions

> See the discussion
> [here](https://github.com/crossbario/autobahn-python/issues/99).

`assert` is for telling fellow programmers: "When I wrote this, I
thought X could/would never really happen, and if it does, this
code will very likely do the wrong thing".

That is, **use an assert if the following holds true: if the
assert fails, it means we have a bug within the library itself**.

In contrast, to check e.g. for user errors, such as application
code using the wrong type when calling into the library, use
Exceptions:

```python
def foo(uri):
    if type(uri) != str:
        raise RuntimeError(u"URIs for foo() must be unicode - got {} instead".format(type(uri)))
```

In this specific example, we also have a WAMP defined error
(which would be preferred compared to the generic exception used
above):

```python
from autobahn.wamp import ApplicationError

def foo(uri):
    if type(uri) != str:
        raise ApplicationError(ApplicationError.INVALID_URI,
                               u"URIs for foo() must be unicode - got {} instead".format(type(uri)))
```

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

To generate and publish the documentation to
[here](http://autobahn.readthedocs.io/en/latest/):

```
cd ~/scm/autobahn/AutobahnPython
make clean
make install
cd doc
make test
```

and open [http://localhost:8080](http://localhost:8080).

#### Publish

To generate and publish the documentation to
[here](http://autobahn.readthedocs.io/en/latest/):

```
cd ~/scm/autobahn/AutobahnPython
make clean
make install
cd doc
make publish
```

### WebSocket Test Reports

[AutobahnTestsuite](http://crossbar.io/autobahn#testsuite)
provides a fully automated test suite to verify client and server
implementations of the WebSocket Protocol for specification
conformance and implementation robustness.

We use that to test AutobahnPython at the WebSocket level, both
client and server mode.

**AutobahnPython has 100% strictly green passes on all of
the >500 tests. If there is only one test failing or not strictly
green, then don't do a release and fix the issue before.**

> The testsuite and the testee should both be run under PyPy on
> Ubuntu for now, as this is one of the most important targets.
> In the future, we might extend that to more platforms and
> Pythons.

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

Install AutobahnPython from source (the sources that is to be
released!) and AutobahnTestsuite from PyPi:

```
source $HOME/pypy261_1/bin/activate
cd ~/scm/crossbario/autobahn-python
make install
pip install autobahntestsuite
```

#### Prepare for testing

We'll be generating reports in `/tmp/reports`. Make sure to
remove any old stuff:

```
rm -rf reports
rm -f fuzzing*.json
```

> The `json` files are the test specs that control what tests to
> run. When there are no test spec files, the testsuite will
> generate default ones, which is what we want.

Two test runs need to be performed now: one testing
AutobahnPython acting as a client, and one where is acts as a
server.

#### Testing WebSocket client mode

Open a first terminal and run the following to start the
WebSocket fuzzing server:

```
cd /tmp
source $HOME/pypy261_1/bin/activate
wstest -m fuzzingserver
```

Open a second terminal and run the following to start the
WebSocket testee client:

```
source $HOME/pypy261_1/bin/activate
wstest -m testeeclient -w ws://127.0.0.1:9001
```

Get some coffee. It'll take some minutes. When it's done, open
`/tmp/reports/servers/index.html` in you browser.

#### Testing WebSocketserver mode

Open a first terminal and run the following to start the
WebSocket testee server:

```
source $HOME/pypy261_1/bin/activate
wstest -m testeeserver -w ws://127.0.0.1:9001
```

Open a second terminal and run the following to start the
WebSocket fuzzing client:

```
cd /tmp
source $HOME/pypy261_1/bin/activate
wstest -m fuzzingclient -w ws://127.0.0.1:9001
```

Get some coffee. It'll take some minutes. When it's done, open
`/tmp/reports/clients/index.html` in you browser.

#### Upload the results

To upload the results, you will need the
[AWS CLI](http://aws.amazon.com/documentation/cli/).

To install:

```
pip install --upgrade awscli
```

We are using the
[high-level commands](http://docs.aws.amazon.com/cli/latest/userguide/using-s3-commands.html).

To upload:

```
aws --region eu-west-1 s3 sync \
    /tmp/reports \
    s3://autobahn.ws/python/testreport \
    --delete \
    --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
```

After the upload has finished, check the live pages:

- [Client Mode Reports](http://autobahn.readthedocs.io/en/latest/testreport/clients/index.html)
- [Server Mode Reports](http://autobahn.readthedocs.io/en/latest/testreport/servers/index.html)

## Roadmap

### 0.10.6

[Milestone for 0.10.6](https://github.com/crossbario/autobahn-python/milestones/0.10.6)

- Automatic reconnection
- Configurable WAMP connecting transports
- WAMP Connection abstration
- Authentication

**0.10** will get into "maintenance mode" after **0.10.6**. We'll
have a maintenance branch for that over some time. The new
development will be based on **0.11** (see below).

### 0.11.0

[Milestone for 0.11.0](https://github.com/crossbario/autobahn-python/milestones/0.11.0)

- new main development line with new, long-term API
