#!/usr/bin/python

import os
import sys
import json
import subprocess
from pprint import pprint

REGISTRY = 'crossbar.local:5000'

try:
    BUILD_DATE = os.environ['BUILD_DATE']
    CROSSBAR_VERSION = os.environ['CROSSBAR_VERSION']
    AUTOBAHN_JS_VERSION = os.environ['AUTOBAHN_JS_VERSION']
    AUTOBAHN_PYTHON_VERSION = os.environ['AUTOBAHN_PYTHON_VERSION']
    AUTOBAHN_CPP_VERSION = os.environ['AUTOBAHN_CPP_VERSION']
except KeyError:
    print('Autobahn/Crossbar.io Docker image versions not set: you need to run "source versions.sh" first!')
    sys.exit(1)

PACKAGE_TO_VERSION = {
    # need to remove leading "v", as GitHub version tags do have "vX.Y.Z", but
    # Docker image tags do NOT have the leading "v"
    'crossbar': CROSSBAR_VERSION.replace('v', ''),
    'autobahn-js': AUTOBAHN_JS_VERSION.replace('v', ''),
    'autobahn-python': AUTOBAHN_PYTHON_VERSION.replace('v', ''),
    'autobahn-cpp': AUTOBAHN_CPP_VERSION.replace('v', ''),
}


#
# add these 3rd party images by default
#
IMAGES = [
    # Debian Stretch
    'debian:stretch',
    'aarch64/debian:stretch',
    'armhf/debian:stretch',

    # Debian Jessie
    'debian:jessie',
    'aarch64/debian:jessie',
    'armhf/debian:jessie',

    # Alpine
    'alpine',
    'armhf/alpine',
    'aarch64/alpine',

    # Ubuntu Xenial
    'ubuntu:xenial',
    'armhf/ubuntu:xenial',
    'aarch64/ubuntu:xenial',

    # Ubuntu Trusty
    'ubuntu:trusty',
    'armhf/ubuntu:trusty',
    'aarch64/ubuntu:trusty',

    # Python
    'python',
    'python:2',
    'armhf/python',
    'armhf/python:2',
    'aarch64/python',
    'aarch64/python:2',

    # Node
    'node',
    'armhf/node',
    'aarch64/node',

    # Node RED
    'nodered/node-red-docker',
]


#
# expand list with all our Autobahn/Crossbar.io images
#
with open('images.json') as f_in:
    data = f_in.read()
    obj = json.loads(data)
    for image in obj.get('images', []):
        package = image.get('package', None)
        architectures = image.get('architectures', None)
        tags = image.get('tags', [])
        for architecture in architectures:
            for _tag in tags:
                if package in PACKAGE_TO_VERSION:
                    _tag = _tag.format(version=PACKAGE_TO_VERSION[package])
                arch = '-{}'.format(architecture) if architecture != 'x86_64' else ''
                image_id = 'crossbario/{package}{arch}:{tag}'.format(package=package, tag=_tag, arch=arch)
                IMAGES.append(image_id)


PUSHED_IMAGES = []

#
# now actually pull the images, and push to the private registry
#
if True:
    for image in IMAGES:
        try:
            tag = '{registry}/{image}'.format(image=image, registry=REGISTRY)
            subprocess.check_output(['docker', 'pull', image], stderr=subprocess.STDOUT)
            subprocess.check_output(['docker', 'tag', image, tag], stderr=subprocess.STDOUT)
            subprocess.check_output(['docker', 'push', tag], stderr=subprocess.STDOUT)
        except Exception as e:
            print('\nWARNING: failed to process image "{}":'.format(image))
            print(e.output)
        else:
            print('OK: image "{}" pushed!'.format(image))
            PUSHED_IMAGES.append(image)

#
# generate a user help file for the images
#
if True:
    with open('pushed_images.md', 'w') as f:
        f.write("# Docker images available in the private Docker registry\n\n")
        f.write("The private Docker registry at `crossbar.local:5000` contains dozens of images. For convenience, the following list contains the full commands to pull these images to your local system.\n\n")
        for image in PUSHED_IMAGES:
            f.write('1. `docker pull crossbar.local:5000/{}`\n'.format(image))
