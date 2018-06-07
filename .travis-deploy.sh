#!/bin/sh

# build the docs, source package and binary (executable). this will produce:
#
#  - $HOME/crossbar-docs
#
# upload to "crossbar.io" company S3 bucket

# only show number of env vars .. should be 4 on master branch!
# https://docs.travis-ci.com/user/pull-requests/#Pull-Requests-and-Security-Restrictions
# Travis CI makes encrypted variables and data available only to pull requests coming from the same repository.
echo 'aws env vars (should be 4 - but only on master branch!):'
env | grep AWS | wc -l

# set up awscli package
echo 'installing aws tools ..'
pip install awscli
which aws
aws --version
aws s3 ls ${AWS_S3_BUCKET_NAME}

# build and deploy latest docs
echo 'building and uploading docs ..'
tox -c tox.ini -e sphinx
aws s3 cp --recursive --acl public-read ${HOME}/crossbar-docs s3://${AWS_S3_BUCKET_NAME}/docs-latest
