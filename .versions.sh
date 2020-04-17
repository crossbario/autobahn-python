#!/bin/sh

export AUTOBAHN_PYTHON_VERSION=$(grep -E '^(__version__)' ./autobahn/_version.py | cut -d ' ' -f3 | sed -e 's|[u"'\'']||g')
export AUTOBAHN_PYTHON_VCS_REF=`git --git-dir="./.git" rev-list -n 1 v${AUTOBAHN_PYTHON_VERSION} --abbrev-commit`
export BUILD_DATE=`date -u +"%Y-%m-%d"`

echo ""
echo "Build environment configured:"
echo ""
echo "  AUTOBAHN_PYTHON_VERSION = ${AUTOBAHN_PYTHON_VERSION}"
echo "  AUTOBAHN_PYTHON_VCS_REF = ${AUTOBAHN_PYTHON_VCS_REF}"
echo "  BUILD_DATE       = ${BUILD_DATE}"
echo ""
