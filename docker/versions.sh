#!/bin/sh

#
# CHANGE FOR NEW RELEASES (these need to be proper Git tags in the respective repo):
#
export AUTOBAHN_PYTHON_VERSION='18.9.1'
#
# END OF CONFIG
#

#
# Git working directories of all relevant repos must reside
# in parallel (as siblings) to this repository
#
export AUTOBAHN_PYTHON_VCS_REF=`git --git-dir="../.git" rev-list -n 1 v${AUTOBAHN_PYTHON_VERSION} --abbrev-commit`
export BUILD_DATE=`date -u +"%Y-%m-%d"`

echo ""
echo "The Crossbar.io Project (build date ${BUILD_DATE})"
echo ""
echo "autobahn-python ${AUTOBAHN_PYTHON_VERSION} [${AUTOBAHN_PYTHON_VCS_REF}]"
echo ""
