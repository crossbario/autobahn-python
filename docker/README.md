# Docker Images

## Using

Use one of the following variants to select the desired image variant:

```
docker run -it --rm crossbario/autobahn-python:<PYTHON>-<ARCH>-<VERSION><COMMIT>
```

with `PYTHON: cpy, pypy` and `ARCH: amd64, arm64v8`, eg

1. `docker run -it --rm crossbario/autobahn-python:cpy-amd64`
1. `docker run -it --rm crossbario/autobahn-python:cpy-amd64-21.2.2.dev2`
1. `docker run -it --rm crossbario/autobahn-python:cpy-amd64-21.2.2.dev2-20210213-7a3dce63`

To auto-select `ARCH` using Docker Manifest, eg

1. `docker run -it --rm crossbario/autobahn-python:cpy`

## Building

Docker images are built automatically from the [docker workflow](../github/workflows/docker.yml),
which is triggered after a PR was merged to master.

To manually build the Docker images, go to the root folder of this repository and set the build variables

```
source versions.sh
cd docker
make install_qemu
make copy_qemu
```

then change to the `docker` subfolder and install Qemu

```
cd docker
make install_qemu
make copy_qemu
```

To build from the wheels published to our S3 bucket

```
make clean_wheels
make download_wheels
```

To build the current library into a wheel and use that in the Docker image

```
make build_this_wheel
```

Then, to build and test a Docker image variant

```
make build_cpy_amd64
make test_cpy_amd64
```

```
make build_this_wheel build_cpy_amd64 test_cpy_amd64
```

You can mix `cpy` or `pypy` for the Python flavor, with `amd64` and `arm64` for the CPU architecture.

To repeat a development cycle

To build, test and then publish all image flavors

```
make build
make test
make publish
```
