# Developers Guide

This is a guide for developers hacking on AutobahnPython.

## Python 2 / 3

AutobahnPython supports both Python 2 and Python 3.

* http://python-future.org/compatible_idioms.html

## Release Process

1. Travis is fully green
2. Run AutobahnTestsuite
3. Build and spellcheck the docs
4. Update the [doc/changelog.rst](doc/changelog.rst)
5. Tag the release
6. Publish the package to PyPi
7. Publish the docs to the Autobahn Web site
8. Announce on mailing list

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
