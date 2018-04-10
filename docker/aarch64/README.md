# AutobahnPython for Docker

Here you find the Dockerfiles for creating the [AutobahnPython for Docker images](https://hub.docker.com/r/crossbario/autobahn-python/) maintained by the Crossbar.io Project.

These images come with Python, Twisted/asyncio and AutobahnPython preinstalled and are intended to base application service containers on.

## Images

Variants based on CPython (full base image, both Twisted and asyncio, all Autobahn optional dependencies):

* `crossbario/autobahn-python:cpy3` (730.5 MB container size)
* `crossbario/autobahn-python:cpy2` (726.3 MB container size)

Variants based on PyPy (full base image, both Twisted and asyncio, all Autobahn optional dependencies):

* `crossbario/autobahn-python:pypy2` (766.5 MB container size)

Variants based on CPython (Alpine Linux base image, both Twisted and asyncio, all Autobahn optional dependencies):

* **`crossbario/autobahn-python:latest` == `crossbario/autobahn-python:cpy3-alpine` (330.9 MB container size)** RECOMMENDED FOR GENERAL USE
* `crossbario/autobahn-python:cpy2-alpine` (326.3 MB container size)

Variants based on CPython (Alpine Linux base image, either Twisted or asyncio, only minimum dependencies):

* `crossbario/autobahn-python:cpy3-minimal-aio` (103.1 MB container size)
* `crossbario/autobahn-python:cpy2-minimal-aio` (81.56 MB container size)
* `crossbario/autobahn-python:cpy3-minimal-tx`  (269.8 MB container size)
* `crossbario/autobahn-python:cpy2-minimal-tx`  (262.5 MB container size)

## Build, test and deploy

To build, test and deploy the AutobahnPython images to DockerHub, do:

```console
make build
make test
make publish
```

> You will need a Crossbar.io container running. Run `make crossbar` in the `crossbar` folder of this repo.
