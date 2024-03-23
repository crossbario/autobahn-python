#!/bin/bash

set +o verbose -o errexit

# AWS_DEFAULT_REGION        : must be set in CI build context!
# AWS_S3_BUCKET_NAME        : must be set in CI build context!
# AWS_ACCESS_KEY_ID         : must be set in CI build context!
# AWS_SECRET_ACCESS_KEY     : must be set in CI build context!
# WAMP_PRIVATE_KEY          : must be set in CI build context!

echo 'AWS env vars (should be 4):'
env | grep AWS_ | wc -l

echo 'WAMP_PRIVATE_KEY env var (should be 1):'
env | grep WAMP_PRIVATE_KEY | wc -l

# set up awscli package
echo 'installing aws tools ..'
pip install awscli
which aws
aws --version

# build python source dist and wheels
echo 'building package ..'
pip install build
python -m build
ls -la ./dist

# upload to S3: https://s3.eu-central-1.amazonaws.com/crossbarbuilder/wheels/
echo 'uploading package ..'
# "aws s3 ls" will return -1 when no files are found! but we don't want our script to exit
aws s3 ls ${AWS_S3_BUCKET_NAME}/wheels/autobahn- || true

# aws s3 cp --recursive ./dist s3://${AWS_S3_BUCKET_NAME}/wheels
aws s3 rm s3://${AWS_S3_BUCKET_NAME}/wheels/autobahn-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}-py2.py3-none-any.whl
aws s3 rm s3://${AWS_S3_BUCKET_NAME}/wheels/autobahn-${AUTOBAHN_VERSION}-py2.py3-none-any.whl
aws s3 rm s3://${AWS_S3_BUCKET_NAME}/wheels/autobahn-latest-py2.py3-none-any.whl

aws s3 cp --acl public-read ./dist/autobahn-${AUTOBAHN_VERSION}-cp310-cp310-linux_x86_64.whl s3://${AWS_S3_BUCKET_NAME}/wheels/autobahn-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}-py2.py3-none-any.whl
aws s3 cp --acl public-read ./dist/autobahn-${AUTOBAHN_VERSION}-cp310-cp310-linux_x86_64.whl s3://${AWS_S3_BUCKET_NAME}/wheels/autobahn-${AUTOBAHN_VERSION}-py2.py3-none-any.whl
aws s3 cp --acl public-read ./dist/autobahn-${AUTOBAHN_VERSION}-cp310-cp310-linux_x86_64.whl s3://${AWS_S3_BUCKET_NAME}/wheels/autobahn-latest-py2.py3-none-any.whl
aws s3 cp --acl public-read ./dist/autobahn-${AUTOBAHN_VERSION}-cp310-cp310-linux_x86_64.whl s3://${AWS_S3_BUCKET_NAME}/wheels/autobahn-latest-cp310-cp310-linux_x86_64.whl

#aws s3api copy-object --acl public-read \
#    --copy-source wheels/autobahn-${AUTOBAHN_VERSION}-py2.py3-none-any.whl --bucket ${AWS_S3_BUCKET_NAME} \
#    --key wheels/autobahn-latest-py2.py3-none-any.whl

aws s3 ls ${AWS_S3_BUCKET_NAME}/wheels/autobahn-

# tell crossbar-builder about this new wheel push
# get 'wamp' command, always with latest autobahn master
pip install -q -I https://github.com/crossbario/autobahn-python/archive/master.zip#egg=autobahn[twisted,serialization,encryption]

# use 'wamp' to notify crossbar-builder
wamp --max-failures 3 \
     --authid wheel_pusher \
     --url ws://office2dmz.crossbario.com:8008/ \
     --realm webhook call builder.wheel_pushed \
     --keyword name autobahn \
     --keyword publish true

echo ''
echo 'package uploaded to:'
echo ''
echo '      https://crossbarbuilder.s3.eu-central-1.amazonaws.com/wheels/autobahn-'${AUTOBAHN_VERSION}'-py2.py3-none-any.whl'
echo '      https://crossbarbuilder.s3.eu-central-1.amazonaws.com/wheels/autobahn-latest-py2.py3-none-any.whl'
echo ''
