#!/bin/sh

export AUTOBAHN_BUILD_DATE=`date -u +"%Y-%m-%d"`
export AUTOBAHN_BUILD_ID=$(date --utc +%Y%m%d)-$(git rev-parse --short HEAD)
export AUTOBAHN_VCS_REF=`git rev-parse --short HEAD`
export AUTOBAHN_VERSION=$(grep -E '^(__version__)' ./autobahn/_version.py | cut -d ' ' -f3 | sed -e 's|[u"'\'']||g')

echo ""
echo "Build environment configured:"
echo ""
echo "  AUTOBAHN_BUILD_DATE     = ${AUTOBAHN_BUILD_DATE}"
echo "  AUTOBAHN_BUILD_ID       = ${AUTOBAHN_BUILD_ID}"
echo "  AUTOBAHN_VCS_REF        = ${AUTOBAHN_VCS_REF}"
echo "  AUTOBAHN_VERSION        = ${AUTOBAHN_VERSION}"
echo ""
