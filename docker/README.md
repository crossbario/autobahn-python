# Image Building

## Requirements

This assumes you have Docker already [installed](https://docs.docker.com/install/linux/docker-ce/ubuntu/).

Further, the commands shown assume that you are able to run Docker without `sudo`. The latter can be done by

```console
sudo usermod -aG docker oberstet
```

and relogin.

Further, Qemu is required for building armhf an aarch64 images:

```
sudo apt-get update
sudo apt-get install -y --no-install-recommends qemu-user-static binfmt-support
sudo update-binfmts --enable qemu-arm
sudo update-binfmts --enable qemu-aarch64
sudo update-binfmts --display qemu-arm
sudo update-binfmts --display qemu-aarch64
```

This should give you:

```
oberstet@crossbar1:~/scm/crossbario/autobahn-python/docker$ which qemu-aarch64-static
/usr/bin/qemu-aarch64-static
oberstet@crossbar1:~/scm/crossbario/autobahn-python/docker$ qemu-aarch64-static --version
qemu-aarch64 version 2.11.1(Debian 1:2.11+dfsg-1ubuntu7.4)
Copyright (c) 2003-2017 Fabrice Bellard and the QEMU Project developers
oberstet@crossbar1:~/scm/crossbario/autobahn-python/docker$ which qemu-arm-static
/usr/bin/qemu-arm-static
oberstet@crossbar1:~/scm/crossbario/autobahn-python/docker$ qemu-arm-static --version
qemu-arm version 2.11.1(Debian 1:2.11+dfsg-1ubuntu7.4)
Copyright (c) 2003-2017 Fabrice Bellard and the QEMU Project developers
```

Copy over those binaries:

```
mkdir aarch64/.qemu
cp `which qemu-aarch64-static` aarch64/.qemu
mkdir armhf/.qemu
cp `which qemu-arm-static` armhf/.qemu
```

## Building the Images

For building a new set of images, edit [versions.sh](versions.sh), and then

```console
source versions.sh
make build
```
